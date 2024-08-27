use pyo3::{pyclass, pymethods, pymodule, Bound, PyResult};
use pyo3::types::PyModule;
use pyo3::types::PyModuleMethods;
use crate::smx::{Key, SMX};

mod smx;
mod error;

#[pyclass]
struct LessCodeEncryption {}


#[pymethods]
impl LessCodeEncryption {
    #[staticmethod]
    fn sm2_gen_keypair() -> Key {
        SMX::sm2_gen_keypair()
    }
    #[staticmethod]
    fn sm2_encrypt(pk: String, data: String) -> String {
        SMX::sm2_encrypt(pk, data)
    }
    #[staticmethod]
    fn sm2_decrypt(sk: String, data: String) -> String {
        SMX::sm2_decrypt(sk, data)
    }

    #[staticmethod]
    fn sm3_hex(data: String) -> String {
        SMX::sm3_hex(data)
    }
    #[staticmethod]
    fn sm4_encrypt(mode: String, data: String, key: String, iv: String) -> String {
        SMX::sm4_encrypt(mode, data, key, iv).unwrap()
    }
    #[staticmethod]
    fn sm4_decrypt(mode: String, data: String, key: String, iv: String) -> String {
        SMX::sm4_decrypt(mode, data, key, iv).unwrap()
    }
}

#[pymodule]
fn lesscode_encryption(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<LessCodeEncryption>()?;
    module.add_class::<Key>()?;
    Ok(())
}
