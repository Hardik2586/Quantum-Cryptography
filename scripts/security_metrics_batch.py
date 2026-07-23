"""
Computes Entropy, NPCR, and UACI for EVERY image in the dataset
(original vs. its AES-256-CBC ciphertext, visualized as a same-size
byte array), then reports the dataset-wide average — this is the
number that belongs in Table V of the paper, not a single-image value.

Run AFTER batch_encrypt.py.

Because ciphertext is raw encrypted bytes (not a valid image container),
we reconstruct a same-dimension "cipher image" from the first W*H bytes
of ciphertext (skipping the 16-byte IV header), exactly like the
comparison used in Section VII of the paper.
"""

import os
from math import log2
import numpy as np
from PIL import Image

resized_root = r"dataset/resized"
encrypted_root = r"encrypted_images"

W, H = 256, 256  # must match resize_images.py target_size

def entropy_of(arr):
    hist, _ = np.histogram(arr, bins=256, range=(0, 256))
    prob = hist / np.sum(hist)
    return -np.sum([p * log2(p) for p in prob if p > 0])

results = []

for category in ["NORMAL", "PNEUMONIA"]:
    orig_folder = os.path.join(resized_root, category)
    enc_folder = os.path.join(encrypted_root, category)

    for filename in os.listdir(orig_folder):
        orig_path = os.path.join(orig_folder, filename)
        enc_path = os.path.join(enc_folder, filename + ".enc")

        if not os.path.exists(enc_path):
            continue

        A = np.array(Image.open(orig_path).convert('L'), dtype=np.uint8)

        with open(enc_path, "rb") as f:
            f.read(16)  # skip IV
            cipher_bytes = f.read(W * H)

        if len(cipher_bytes) < W * H:
            cipher_bytes = cipher_bytes + bytes(W * H - len(cipher_bytes))

        B = np.frombuffer(cipher_bytes, dtype=np.uint8).reshape(H, W)

        ent = entropy_of(B)
        diff = (A != B)
        npcr = np.sum(diff) / diff.size * 100
        uaci = np.mean(np.abs(A.astype(np.int16) - B.astype(np.int16)) / 255.0) * 100

        results.append((filename, category, ent, npcr, uaci))

entropies = [r[2] for r in results]
npcrs = [r[3] for r in results]
uacis = [r[4] for r in results]

print("\n===== DATASET-WIDE SECURITY METRICS =====")
print(f"Images evaluated : {len(results)}")
print(f"Entropy  - mean: {np.mean(entropies):.4f}  min: {np.min(entropies):.4f}  max: {np.max(entropies):.4f}")
print(f"NPCR (%) - mean: {np.mean(npcrs):.4f}  min: {np.min(npcrs):.4f}  max: {np.max(npcrs):.4f}")
print(f"UACI (%) - mean: {np.mean(uacis):.4f}  min: {np.min(uacis):.4f}  max: {np.max(uacis):.4f}")

# also save per-image CSV for full transparency
import csv
with open("security_metrics_full_dataset.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["filename", "category", "entropy", "npcr_percent", "uaci_percent"])
    writer.writerows(results)

print("\nPer-image results saved to security_metrics_full_dataset.csv")
