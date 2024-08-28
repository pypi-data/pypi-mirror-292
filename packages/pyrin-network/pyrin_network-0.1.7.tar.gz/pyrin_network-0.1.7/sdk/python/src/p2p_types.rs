use pyo3::pyclass;

#[pyclass]
pub struct NetAddress {
    #[pyo3(get)]
    pub timestamp: i64,
    #[pyo3(get)]
    pub ip: String,
    #[pyo3(get)]
    pub port: u32,
}