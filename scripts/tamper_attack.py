import random

input_file = r"encrypted_images\NORMAL"

import os

sample = os.listdir(input_file)[0]

input_path = os.path.join(input_file, sample)

output_path = "tampered_image.enc"

with open(input_path, "rb") as f:
    data = bytearray(f.read())

# Modify 1% of bytes
tamper_percent = 0.01

num_bytes = int(len(data) * tamper_percent)

for _ in range(num_bytes):

    idx = random.randint(0, len(data)-1)

    data[idx] ^= 0xFF

with open(output_path, "wb") as f:
    f.write(data)

print("Tampered file created.")