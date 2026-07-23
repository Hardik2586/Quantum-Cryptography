from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from PIL import Image
import os

# Load AES key
with open("aes_key.bin", "rb") as f:
    key = f.read()

input_root = r"dataset/resized"
output_root = r"encrypted_images"

for category in ["NORMAL", "PNEUMONIA"]:

    input_folder = os.path.join(input_root, category)

    output_folder = os.path.join(output_root, category)

    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):

        input_path = os.path.join(input_folder, filename)

        output_path = os.path.join(
            output_folder,
            filename + ".enc"
        )

    
        img = Image.open(input_path).convert('L')
        image_data = img.tobytes()

        cipher = AES.new(key, AES.MODE_CBC)

        ciphertext = cipher.encrypt(
            pad(image_data, AES.block_size)
        )

        with open(output_path, "wb") as f:

            f.write(cipher.iv)

            f.write(ciphertext)

print("All images encrypted successfully.")
