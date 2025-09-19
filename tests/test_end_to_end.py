
# Basic test (do not run in CI) - demonstrates encryption/decryption works with identical key
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import json
AES_KEY = b"0123456789abcdef"
def encrypt(data):
    c = AES.new(AES_KEY, AES.MODE_ECB)
    return c.encrypt(pad(data,16))
def decrypt(enc):
    c = AES.new(AES_KEY, AES.MODE_ECB)
    return unpad(c.decrypt(enc),16)
if __name__ == "__main__":
    payload = json.dumps({"t":1,"temp":40}).encode('utf-8')
    enc = encrypt(payload)
    dec = decrypt(enc)
    assert dec == payload
    print("encryption roundtrip OK")
