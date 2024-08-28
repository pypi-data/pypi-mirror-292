use std::collections::HashMap;
use std::net::{IpAddr, Ipv4Addr, Ipv6Addr, SocketAddr};
use std::ops::Deref;
use std::str::FromStr;
use std::sync::Arc;
use std::time::Duration;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyFunction;
use tokio::sync::{mpsc, Mutex};
use tokio::sync::mpsc::{channel as mpsc_channel, Receiver, Sender};
use tokio::sync::oneshot::channel as oneshot_channel;
use tonic::transport::Server as TonicServer;
use uuid::Uuid;
use workflow_core::prelude::spawn;

use kaspa_notify::subscription::AsAny;
use kaspa_p2p_lib::{Adaptor, ConnectionInitializer, dequeue_with_timeout, Hub, KaspadHandshake, KaspadMessagePayloadType, make_message};
use kaspa_p2p_lib::common::ProtocolError;
use kaspa_p2p_lib::core::{connection_handler::{ConnectionHandler, P2P_MAX_MESSAGE_SIZE}, hub::HubEvent};
use kaspa_p2p_lib::echo::{EchoFlow, EchoFlowInitializer};
use kaspa_p2p_lib::pb::{AddressesMessage, kaspad_message, KaspadMessage, RequestAddressesMessage, VersionMessage};
use kaspa_p2p_lib::pb::kaspad_message::Payload;
use kaspa_p2p_lib::pb::p2p_server::P2pServer as ProtoP2pServer;
use kaspa_utils::channel::Channel;
use kaspa_utils::hex::ToHex;
use kaspa_utils::networking::PeerId;
use kaspa_utils_tower::{
    counters::TowerConnectionCounters,
    middleware::{CountBytesBody, MapResponseBodyLayer, measure_request_body_size_layer},
};

#[derive(Debug, Clone, Default)]
#[pyclass]
pub struct PeerProperties {
    #[pyo3(get)]
    pub user_agent: String,
    #[pyo3(get)]
    pub advertised_protocol_version: u32,
    #[pyo3(get)]
    pub protocol_version: u32,
    #[pyo3(get)]
    pub disable_relay_tx: bool,
    #[pyo3(get)]
    pub subnetwork_id: Option<String>,
    #[pyo3(get)]
    pub time_offset: i64,
}

#[pyclass]
pub struct ActivePeer {
    #[pyo3(get)]
    pub identity: String,
    #[pyo3(get)]
    pub net_address: String,
    #[pyo3(get)]
    pub is_outbound: bool,
    #[pyo3(get)]
    pub connection_started: u64,
    #[pyo3(get)]
    pub properties: PeerProperties,
    #[pyo3(get)]
    pub last_ping_duration: u64,
}

macro_rules! listen_event {
    ($self:ident, $py:ident, $event:expr, $callback:expr) => {{
        let adaptor = Arc::clone(&$self.adaptor.as_ref().unwrap());
        let receiver = Arc::clone(&$self.receiver.as_ref().unwrap());
        let listeners = Arc::clone(&$self.listeners);

        $py.allow_threads(|| {
            let mut listeners = listeners.lock().unwrap();
            listeners.insert($event.to_string(), $callback);
        });

        pyo3_asyncio::tokio::future_into_py($py, async move {
            let mut receiver = receiver.lock().await;
            while let Some(msg) = receiver.recv().await {
                if let Some(ref payload) = msg.payload {
                    if payload.payload_type().to_string() == $event {
                        Python::with_gil(|py| {
                            let listeners = listeners.lock().unwrap();
                            if let Some(callback) = listeners.get(&$event.to_string()) {
                                callback.call1(py, (msg.clone(),)).map_err(|e| e.print(py)).ok();
                            }
                        });
                    }
                }
            }
            Ok(())
        })
    }};
}

#[pyclass]
pub struct P2P {
    address: String,
    adaptor: Option<Arc<Adaptor>>,
    initializer: Option<Arc<EchoFlowInitializer>>,
    counters: Option<Arc<TowerConnectionCounters>>,
    hub: Option<Hub>,
    connection_handler: Option<ConnectionHandler>,
    receiver: Option<Arc<Mutex<mpsc::Receiver<KaspadMessage>>>>,
    listeners: Arc<Mutex<HashMap<String, Py<PyFunction>>>>,
}

#[pymethods]
impl P2P {
    #[new]
    fn new(address: String) -> Self {
        P2P {
            address,
            adaptor: None,
            initializer: None,
            counters: None,
            hub: None,
            connection_handler: None,
            receiver: None,
            listeners: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub fn connect<'a>(&mut self, py: Python<'a>) -> PyResult<&'a PyAny> {
        self.initializer = Some(Arc::new(EchoFlowInitializer::new()));
        let initializer = self.initializer.clone().unwrap();
        self.counters = Some(Arc::new(TowerConnectionCounters::default()));
        let counters = self.counters.clone().unwrap();
        self.hub = Some(Hub::new());
        let hub = self.hub.clone().unwrap();

        let (tx, rx) = mpsc::channel(1024);
        self.receiver = Some(Arc::new(Mutex::new(rx)));
        let listener: Sender<KaspadMessage> = tx;

        let (hub_sender, mut hub_receiver) = mpsc_channel(Adaptor::hub_channel_size());
        self.connection_handler = Some(ConnectionHandler::new(hub_sender, initializer.clone(), counters.clone(), Some(listener)));
        let connection_handler = self.connection_handler.clone().unwrap();

        let (termination_sender, termination_receiver) = oneshot_channel::<()>();

        let bytes_tx = counters.bytes_tx.clone();
        let bytes_rx = counters.bytes_rx.clone();

        // let adaptor = self.adaptor.clone().unwrap();
        let address = self.address.clone();

        let proto_server = ProtoP2pServer::new(connection_handler.clone())
            .accept_compressed(tonic::codec::CompressionEncoding::Gzip)
            .send_compressed(tonic::codec::CompressionEncoding::Gzip)
            .max_decoding_message_size(P2P_MAX_MESSAGE_SIZE);

        let address_clone = address.clone();

        // spawn(async move {
            let serve_result = TonicServer::builder()
                .layer(measure_request_body_size_layer(bytes_rx, |b| b))
                .layer(MapResponseBodyLayer::new(move |body| CountBytesBody::new(body, bytes_tx.clone())))
                .add_service(proto_server)
                .serve(SocketAddr::from_str(address_clone.as_str())?);
                // .await;
        // });

        self.adaptor = Some(Arc::new(Adaptor::new(Some(termination_sender), connection_handler, hub.clone())));
        let adaptor = self.adaptor.clone().unwrap();

        pyo3_asyncio::tokio::future_into_py(py, async move {
            // start event loop
            spawn(async move {
                while let Some(new_event) = hub_receiver.recv().await {
                    // match new_event {
                    //     HubEvent::NewPeer(new_router) => {
                    //         // new_router.
                    //
                    //         new_router.enqueue(make_message!(
                    //             Payload::RequestAddresses,
                    //             RequestAddressesMessage { include_all_subnetworks: false, subnetwork_id: None }
                    //         )).await.unwrap();
                    //
                    //         // let mut message_receiver = new_router.subscribe(vec![KaspadMessagePayloadType::RequestAddresses]);
                    //         // let message = dequeue_with_timeout!(message_receiver, Payload::Version, Duration::from_secs(4)).unwrap();
                    //         // println!("accepted message: {message:?}");
                    //
                    //         // If peer is outbound then connection initialization was already performed as part of the connect logic
                    //         if new_router.is_outbound() {
                    //             println!("P2P Connected to outgoing peer {}", new_router);
                    //             hub.insert_new_router(new_router).await;
                    //         } else {
                    //
                    //             let mut handshake = KaspadHandshake::new(&new_router);
                    //
                    //             // We start the router receive loop only after we registered to handshake routes
                    //             new_router.start();
                    //
                    //             // Build the local version message
                    //             let self_version_message = VersionMessage {
                    //                 protocol_version: 5,
                    //                 services: 0,
                    //                 timestamp: std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs() as i64,
                    //                 address: None,
                    //                 id: Vec::from(Uuid::new_v4().as_ref()),
                    //                 user_agent: String::new(),
                    //                 disable_relay_tx: false,
                    //                 subnetwork_id: None,
                    //                 network: "pyrin-mainnet".to_string(),
                    //             };
                    //
                    //             // Perform the handshake
                    //             let peer_version_message = handshake.handshake(self_version_message).await.unwrap();
                    //             println!("protocol versions - self: {}, peer: {}", 5, peer_version_message.protocol_version);
                    //
                    //             let receiver = new_router.subscribe(vec![
                    //                 KaspadMessagePayloadType::Addresses,
                    //                 KaspadMessagePayloadType::Block,
                    //                 KaspadMessagePayloadType::Transaction,
                    //                 KaspadMessagePayloadType::BlockLocator,
                    //                 KaspadMessagePayloadType::RequestAddresses,
                    //                 KaspadMessagePayloadType::RequestRelayBlocks,
                    //                 KaspadMessagePayloadType::RequestTransactions,
                    //                 KaspadMessagePayloadType::IbdBlock,
                    //                 KaspadMessagePayloadType::InvRelayBlock,
                    //                 KaspadMessagePayloadType::InvTransactions,
                    //                 KaspadMessagePayloadType::Ping,
                    //                 KaspadMessagePayloadType::Pong,
                    //                 // KaspadMessagePayloadType::Verack,
                    //                 // KaspadMessagePayloadType::Version,
                    //                 // KaspadMessagePayloadType::Ready,
                    //                 KaspadMessagePayloadType::TransactionNotFound,
                    //                 KaspadMessagePayloadType::Reject,
                    //                 KaspadMessagePayloadType::PruningPointUtxoSetChunk,
                    //                 KaspadMessagePayloadType::RequestIbdBlocks,
                    //                 KaspadMessagePayloadType::UnexpectedPruningPoint,
                    //                 KaspadMessagePayloadType::IbdBlockLocator,
                    //                 KaspadMessagePayloadType::IbdBlockLocatorHighestHash,
                    //                 KaspadMessagePayloadType::RequestNextPruningPointUtxoSetChunk,
                    //                 KaspadMessagePayloadType::DonePruningPointUtxoSetChunks,
                    //                 KaspadMessagePayloadType::IbdBlockLocatorHighestHashNotFound,
                    //                 KaspadMessagePayloadType::BlockWithTrustedData,
                    //                 KaspadMessagePayloadType::DoneBlocksWithTrustedData,
                    //                 KaspadMessagePayloadType::RequestPruningPointAndItsAnticone,
                    //                 KaspadMessagePayloadType::BlockHeaders,
                    //                 KaspadMessagePayloadType::RequestNextHeaders,
                    //                 KaspadMessagePayloadType::DoneHeaders,
                    //                 KaspadMessagePayloadType::RequestPruningPointUtxoSet,
                    //                 KaspadMessagePayloadType::RequestHeaders,
                    //                 KaspadMessagePayloadType::RequestBlockLocator,
                    //                 KaspadMessagePayloadType::PruningPoints,
                    //                 KaspadMessagePayloadType::RequestPruningPointProof,
                    //                 KaspadMessagePayloadType::PruningPointProof,
                    //                 KaspadMessagePayloadType::BlockWithTrustedDataV4,
                    //                 KaspadMessagePayloadType::TrustedData,
                    //                 KaspadMessagePayloadType::RequestIbdChainBlockLocator,
                    //                 KaspadMessagePayloadType::IbdChainBlockLocator,
                    //                 KaspadMessagePayloadType::RequestAntipast,
                    //                 KaspadMessagePayloadType::RequestNextPruningPointAndItsAnticoneBlocks,
                    //             ]);
                    //
                    //             let mut echo_flow = EchoFlow { router: new_router.clone(), receiver };
                    //
                    //             spawn(async move {
                    //                 while let Some(mut msg) = echo_flow.receiver.recv().await {
                    //                     println!("msg: {:?}", msg);
                    //
                    //                     if let Some(payload) = msg.payload.take() {
                    //                         match payload {
                    //                             Payload::Addresses(AddressesMessage { address_list }) => {
                    //                                 for address in address_list {
                    //                                     println!("{}, {}, {}", address.timestamp, address.ip.to_hex(), address.port);
                    //                                 }
                    //                             }
                    //                             _ => {}
                    //                         }
                    //                     }
                    //
                    //                     if !(echo_flow.call(msg).await) {
                    //                         println!("EchoFlow, receive loop - call failed");
                    //                         break;
                    //                     }
                    //                 }
                    //                 println!("EchoFlow, exiting message dispatch loop");
                    //             });
                    //
                    //             // Send a ready signal
                    //             handshake.exchange_ready_messages().await.unwrap();
                    //
                    //             // match initializer.initialize_connection(new_router.clone()).await {
                    //             //     Ok(()) => {
                    //             //         println!("P2P Connected to incoming peer {}", new_router);
                    //             //         hub.insert_new_router(new_router).await;
                    //             //     }
                    //             //     Err(err) => {
                    //             //         new_router.try_sending_reject_message(&err).await;
                    //             //         // Ignoring the new router
                    //             //         new_router.close().await;
                    //             //         if matches!(err, ProtocolError::LoopbackConnection(_) | ProtocolError::PeerAlreadyExists(_)) {
                    //             //             println!("P2P, handshake failed for inbound peer {}: {}", new_router, err);
                    //             //         } else {
                    //             //             println!("P2P, handshake failed for inbound peer {}: {}", new_router, err);
                    //             //         }
                    //             //     }
                    //             // }
                    //         }
                    //     }
                    //     HubEvent::PeerClosing(router) => {
                    //         // if let Occupied(entry) = hub.peers.write().entry(router.key()) {
                    //         //     // We search for the router by identity, but make sure to delete it only if it's actually the same object.
                    //         //     // This is extremely important in cases of duplicate connection rejection etc.
                    //         //     if Arc::ptr_eq(entry.get(), &router) {
                    //         //         entry.remove_entry();
                    //         //     }
                    //         // }
                    //     }
                    // }
                }
            });

            let result = adaptor.connect_peer(address.clone()).await;

            if result.is_ok() {
                Ok(result.unwrap().to_string())
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyException, _>(result.err().unwrap().to_string()))
            }

            // Ok(())
        })
    }

    pub fn listen<'a>(&self, py: Python<'a>, callback: Py<PyFunction>) -> PyResult<&'a PyAny> {
        let receiver = match &self.receiver {
            Some(arc_receiver) => Arc::clone(arc_receiver),
            None => return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Receiver not initialized")),
        };
        let listeners = Arc::clone(&self.listeners);
        let locals = pyo3_asyncio::TaskLocals::with_running_loop(py)?.copy_context(py)?;

        pyo3_asyncio::tokio::future_into_py_with_locals(py, locals.clone(), async move {
            let fut = async move {
                let mut receiver = receiver.lock().await;
                while let Some(msg) = receiver.recv().await {

                    fn ip_vec_to_string(ip: Vec<u8>) -> String {
                        match ip.len() {
                            4 => {
                                // IPv4
                                let ip_addr = Ipv4Addr::new(ip[0], ip[1], ip[2], ip[3]);
                                IpAddr::V4(ip_addr).to_string()
                            }
                            16 => {
                                // IPv6
                                let ip_addr = Ipv6Addr::from(
                                    <[u8; 16]>::try_from(ip).expect("Vec should have exactly 16 elements")
                                );
                                IpAddr::V6(ip_addr).to_string()
                            }
                            _ => panic!("Invalid IP address length"),
                        }
                    }

                    match msg.payload.unwrap() {
                        Payload::Addresses(AddressesMessage { address_list }) => {
                            let mut addresses = vec![];

                            for address in address_list {
                                addresses.push(crate::p2p_types::NetAddress {
                                    timestamp: address.timestamp,
                                    ip: ip_vec_to_string(address.ip),
                                    port: address.port,
                                });

                                // print!("{}, {},  {}", address.timestamp, address.ip.to_hex(), address.port);
                            }

                            let callback_clone = callback.clone();

                            pyo3_asyncio::tokio::scope(locals.clone(), async move {
                                let coroutine = Python::with_gil(|py| {
                                    pyo3_asyncio::into_future_with_locals(
                                        &pyo3_asyncio::tokio::get_current_locals(py)?,
                                        callback_clone.call1(py, (addresses,)).map_err(|e| e.print(py)).unwrap().downcast::<PyAny>(py).unwrap()
                                    )
                                }).unwrap();

                                coroutine.await;
                            }).await;

                            // Python::with_gil(|py| {
                            //     callback.call1(py, (addresses,)).map_err(|e| e.print(py)).ok();
                            // })

                            // let coroutine = Python::with_gil(|py| {
                            //     // convert the coroutine into a Rust future
                            //     pyo3_asyncio::into_future_with_locals(&locals, callback.call1(py, (addresses,).unwrap()))
                            // }).unwrap();
                            //
                            //
                            // coroutine.await.unwrap();
                        }

                        _  => {}
                    }
                }
                Ok(())
            };
            fut.await
        })
    }

    // pub fn on<'a>(&mut self, py: Python<'a>, event: String, callback: Py<PyFunction>) -> PyResult<()> {
    //     let mut listeners = self.listeners.lock().unwrap();
    //     listeners.insert(event, callback);
    //     Ok(())
    // }

    pub fn active_peers<'a>(&mut self, py: Python<'a>) -> PyResult<&'a PyAny> {
        let adaptor = self.adaptor.clone().unwrap();

        pyo3_asyncio::tokio::future_into_py(py, async move {

            let mut peers: Vec<ActivePeer> = Vec::with_capacity(adaptor.active_peers().len());

            for peer in adaptor.active_peers() {
                let properties = peer.properties().clone();
                peers.push(ActivePeer {
                    identity: peer.identity().to_string(),
                    net_address: peer.net_address().to_string(),
                    is_outbound: peer.is_outbound(),
                    connection_started: peer.time_connected(),
                    properties: PeerProperties {
                        user_agent: String::from(properties.user_agent.as_str()),
                        advertised_protocol_version: properties.advertised_protocol_version,
                        protocol_version: properties.protocol_version,
                        disable_relay_tx: properties.disable_relay_tx,
                        subnetwork_id: properties.subnetwork_id.as_ref().map(|id| id.to_string()),
                        time_offset: properties.time_offset,
                    },
                    last_ping_duration: peer.last_ping_duration(),
                });
            }

            Ok(peers)
        })
    }

    /*pub fn on_addresses<'a>(&mut self, py: Python<'a>, callback: Py<PyFunction>) -> PyResult<&'a PyAny> {
        listen_event!(self, py, "Addresses", callback)
    }

    pub fn on_block<'a>(&mut self, py: Python<'a>, callback: Py<PyFunction>) -> PyResult<&'a PyAny> {
        listen_event!(self, py, "Block", callback)
    }

    pub fn on_transaction<'a>(&mut self, py: Python<'a>, callback: Py<PyFunction>) -> PyResult<&'a PyAny> {
        listen_event!(self, py, "Transaction", callback)
    }

    pub fn on_block_locator<'a>(&mut self, py: Python<'a>, callback: Py<PyFunction>) -> PyResult<&'a PyAny> {
        listen_event!(self, py, "BlockLocator", callback)
    }

    pub fn on_request_addresses<'a>(&mut self, py: Python<'a>, callback: Py<PyFunction>) -> PyResult<&'a PyAny> {
        listen_event!(self, py, "RequestAddresses", callback)
    }

    pub fn on_request_relay_blocks<'a>(&mut self, py: Python<'a>, callback: Py<PyFunction>) -> PyResult<&'a PyAny> {
        listen_event!(self, py, "RequestRelayBlocks", callback)
    }

    pub fn on_request_transactions<'a>(&mut self, py: Python<'a>, callback: Py<PyFunction>) -> PyResult<&'a PyAny> {
        listen_event!(self, py, "RequestTransactions", callback)
    }

    pub fn on_ibd_block<'a>(&mut self, py: Python<'a>, callback: Py<PyFunction>) -> PyResult<&'a PyAny> {
        listen_event!(self, py, "IbdBlock", callback)
    }

    pub fn on_inv_relay_block<'a>(&mut self, py: Python<'a>, callback: Py<PyFunction>) -> PyResult<&'a PyAny> {
        listen_event!(self, py, "InvRelayBlock", callback)
    }

    pub fn on_inv_transactions<'a>(&mut self, py: Python<'a>, callback: Py<PyFunction>) -> PyResult<&'a PyAny> {
        listen_event!(self, py, "InvTransactions", callback)
    }

    pub fn on_ping<'a>(&mut self, py: Python<'a>, callback: Py<PyFunction>) -> PyResult<&'a PyAny> {
        listen_event!(self, py, "Ping", callback)
    }

    pub fn on_pong<'a>(&mut self, py: Python<'a>, callback: Py<PyFunction>) -> PyResult<&'a PyAny> {
        listen_event!(self, py, "Pong", callback)
    }

    pub fn on_transaction_not_found<'a>(&mut self, py: Python<'a>, callback: Py<PyFunction>) -> PyResult<&'a PyAny> {
        listen_event!(self, py, "TransactionNotFound", callback)
    }

    pub fn on_reject<'a>(&mut self, py: Python<'a>, callback: Py<PyFunction>) -> PyResult<&'a PyAny> {
        listen_event!(self, py, "Reject", callback)
    }

    // ... (continue for all other KaspadMessagePayloadTypes)

    pub fn on_request_next_pruning_point_and_its_anticone_blocks<'a>(&mut self, py: Python<'a>, callback: Py<PyFunction>) -> PyResult<&'a PyAny> {
        listen_event!(self, py, "RequestNextPruningPointAndItsAnticoneBlocks", callback)
    }*/
}