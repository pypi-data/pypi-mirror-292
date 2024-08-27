use gmsm::sm2::{sm2_decrypt_c1c3c2, sm2_encrypt_c1c3c2, sm2_generate_key_hex};
use gmsm::sm3::sm3_hex;
use gmsm::sm4::{sm4_cbc_decrypt_hex, sm4_cbc_encrypt_hex, sm4_ecb_decrypt_hex, sm4_ecb_encrypt_hex};
use pyo3::pyclass;
use crate::error::SMXError;

#[pyclass]
pub struct Key {
    #[pyo3(get, set)]
    pub sk: String,
    #[pyo3(get, set)]
    pub pk: String,
}


pub struct SMX {}
impl SMX {
    pub fn sm2_gen_keypair() -> Key {
        let keypair = sm2_generate_key_hex();
        let pri_key = keypair.pri_hex;
        let pub_key = keypair.pub_hex;
        Key { sk: pri_key, pk: pub_key }
    }

    pub fn sm2_encrypt(pk: String, data: String) -> String {
        sm2_encrypt_c1c3c2(&data, &pk)
    }
    pub fn sm2_decrypt(sk: String, data: String) -> String {
        sm2_decrypt_c1c3c2(&data, &sk)
    }
    pub fn sm3_hex(data: String) -> String {
        sm3_hex(&data)
    }
    pub fn sm4_encrypt(mode: String, data: String, key: String, iv: String) -> Result<String, SMXError> {
        if mode == "ecb" {
            Ok(sm4_ecb_encrypt_hex(&data, &key))
        } else if mode == "cbc" {
            Ok(sm4_cbc_encrypt_hex(&data, &key, &iv))
        } else {
            Err(SMXError::InvalidMode)
        }
    }

    pub fn sm4_decrypt(mode: String, data: String, key: String, iv: String) -> Result<String, SMXError> {
        if mode == "ecb" {
            Ok(sm4_ecb_decrypt_hex(&data, &key))
        } else if mode == "cbc" {
            Ok(sm4_cbc_decrypt_hex(&data, &key, &iv))
        } else {
            Err(SMXError::InvalidMode)
        }
    }
}
