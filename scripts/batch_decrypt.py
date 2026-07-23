from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from PIL import Image
import os

# Load AES key
with open("aes_key.bin", "rb") as f:
    key = f.read()

input_root = r"encrypted_images"
output_root = r"decrypted_images"

# Must match resize_images.py's target_size
IMG_SIZE = (256, 256)

for category in ["NORMAL", "PNEUMONIA"]:

    input_folder = os.path.join(input_root, category)

    output_folder = os.path.join(output_root, category)

    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):

        input_path = os.path.join(input_folder, filename)

        base_name = os.path.splitext(filename.replace(".enc", ""))[0]

        # Saved as PNG (lossless) since we now decrypt back to a raw
        # pixel buffer, not a JPEG-encoded file.
        output_path = os.path.join(
            output_folder,
            base_name + ".png"
        )

        with open(input_path, "rb") as f:

            iv = f.read(16)

            ciphertext = f.read()

        cipher = AES.new(key, AES.MODE_CBC, iv)

        plaintext = unpad(
            cipher.decrypt(ciphertext),
            AES.block_size
        )

        img = Image.frombytes('L', IMG_SIZE, plaintext)

        img.save(output_path)

print("All images decrypted successfully.")
