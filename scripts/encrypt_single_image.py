from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os

# Load AES key
with open("aes_key.bin", "rb") as f:
    key = f.read()

# Choose one image
image_path = r"dataset\resized\NORMAL"

filename = os.listdir(image_path)[0]

full_path = os.path.join(image_path, filename)

# Read image bytes
with open(full_path, "rb") as f:
    image_data = f.read()

# Create cipher
cipher = AES.new(key, AES.MODE_CBC)

ciphertext = cipher.encrypt(
    pad(image_data, AES.block_size)
)

# Save encrypted file
with open("encrypted_image.bin", "wb") as f:

    f.write(cipher.iv)

    f.write(ciphertext)

print("Encrypted:", filename)

print("Saved as encrypted_image.bin")