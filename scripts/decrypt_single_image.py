from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Load AES key
with open("aes_key.bin", "rb") as f:
    key = f.read()

# Read encrypted file
with open("encrypted_image.bin", "rb") as f:

    iv = f.read(16)

    ciphertext = f.read()

cipher = AES.new(key, AES.MODE_CBC, iv)

plaintext = unpad(
    cipher.decrypt(ciphertext),
    AES.block_size
)

# Save recovered image
with open("decrypted_image.jpeg", "wb") as f:

    f.write(plaintext)

print("Image successfully decrypted.")