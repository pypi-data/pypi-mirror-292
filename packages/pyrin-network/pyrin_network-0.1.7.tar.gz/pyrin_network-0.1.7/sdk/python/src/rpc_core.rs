use pyo3::{IntoPy, Py, PyAny, PyErr, Python};
use pyo3::types::PyDict;
use kaspa_consensus_core::BlueWorkType;
use kaspa_consensus_core::tx::ScriptPublicKey;

pub struct RpcCore {

}

impl RpcCore {
    pub fn get_dict_item<'a>(dict: &'a PyDict, key: &str) -> &'a PyAny {
        dict.get_item(key).unwrap()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!("Missing key: {}", key)))
            .unwrap()
    }
}