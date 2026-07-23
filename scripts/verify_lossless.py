"""
Verifies that every decrypted image is pixel-for-pixel identical to its
original — confirms the "200/200 images recovered, 100% recovery rate"
claim in Table IV of the paper.

Compares DECODED PIXEL ARRAYS rather than raw file bytes, because the
original is a JPEG/PNG file but the decrypted output is saved as PNG
from a raw pixel buffer — the file formats differ even when the pixel
content is identical, so a raw byte comparison is not meaningful here.

Run AFTER batch_encrypt.py and batch_decrypt.py.
"""

import os
import numpy as np
from PIL import Image

original_root = r"dataset/resized"
decrypted_root = r"decrypted_images"

total = 0
matched = 0
mismatches = []

for category in ["NORMAL", "PNEUMONIA"]:
    orig_folder = os.path.join(original_root, category)
    dec_folder = os.path.join(decrypted_root, category)

    for filename in os.listdir(orig_folder):
        base = os.path.splitext(filename)[0]
        orig_path = os.path.join(orig_folder, filename)
        dec_path = os.path.join(dec_folder, base + ".png")

        total += 1

        if os.path.exists(dec_path):
            A = np.array(Image.open(orig_path).convert('L'))
            B = np.array(Image.open(dec_path).convert('L'))

            if A.shape == B.shape and np.array_equal(A, B):
                matched += 1
            else:
                mismatches.append(filename)
        else:
            mismatches.append(filename)

recovery_rate = (matched / total * 100) if total else 0

print("\n===== LOSSLESS DECRYPTION VERIFICATION (pixel-exact) =====")
print(f"Total images checked : {total}")
print(f"Pixel-exact matches  : {matched}")
print(f"Recovery rate         : {recovery_rate:.2f}%")

if mismatches:
    print(f"\nMismatched files ({len(mismatches)}):")
    for m in mismatches:
        print("  -", m)
else:
    print("\nAll images recovered without loss.")
