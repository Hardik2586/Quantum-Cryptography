from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Load SAME AES key
with open("aes_key.bin", "rb") as f:
    key = f.read()

# Read tampered encrypted file
with open("tampered_image.enc", "rb") as f:

    iv = f.read(16)
    ciphertext = f.read()

cipher = AES.new(key, AES.MODE_CBC, iv)

try:

    plaintext = unpad(
        cipher.decrypt(ciphertext),
        AES.block_size
    )

    with open("tampered_decrypted.jpeg", "wb") as f:

        f.write(plaintext)

    print("Tampered image decrypted.")

except Exception as e:

    print("Decryption failed.")

    print("Error:", e)