from PIL import Image
import os

input_dir = r"dataset/original"
output_dir = r"dataset/resized"

target_size = (256, 256)

for category in ["NORMAL", "PNEUMONIA"]:

    input_folder = os.path.join(input_dir, category)

    output_folder = os.path.join(output_dir, category)

    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):

        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):

            input_path = os.path.join(input_folder, filename)

            output_path = os.path.join(output_folder, filename)

            img = Image.open(input_path)

            img = img.convert('L')

            img = img.resize(target_size)

            img.save(output_path)

print("All images resized successfully.")