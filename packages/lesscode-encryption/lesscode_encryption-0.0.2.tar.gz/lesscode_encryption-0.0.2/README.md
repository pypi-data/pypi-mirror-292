# lesscode_encryption

lesscode_encryption是基于Rust语言开发的加密算法库

```python
# sm2
from lesscode_encryption import LessCodeEncryption

key = LessCodeEncryption.sm2_gen_keypair()
origin_str = "hello navysummer"
sm2_encrypt_str = LessCodeEncryption.sm2_encrypt(key.pk, origin_str)
sm2_decrypt_str = LessCodeEncryption.sm2_decrypt(key.sk, sm2_encrypt_str)
assert sm2_decrypt_str == origin_str

# sm3
sm3_str = LessCodeEncryption.sm3_hex(origin_str)

# sm4
key = "8A3F8665AAEE6F7A0CB8F40B971E3373"
iv = "88BA27B390F466ABE7C4327E1E60270B"
sm4_ecb_encrypt_str = LessCodeEncryption.sm4_encrypt("ecb", origin_str, key)
sm4_ecb_decrypt_str = LessCodeEncryption.sm4_decrypt("ecb", sm4_ecb_encrypt_str, key)
assert sm4_ecb_decrypt_str == origin_str
sm4_cbc_encrypt_str = LessCodeEncryption.sm4_encrypt("cbc", origin_str, key, iv)
sm4_cbc_decrypt_str = LessCodeEncryption.sm4_decrypt("cbc", sm4_cbc_encrypt_str, key, iv)
assert sm4_cbc_decrypt_str == origin_str
```