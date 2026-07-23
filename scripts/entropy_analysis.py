from PIL import Image
import numpy as np
from math import log2

image_path = r"dataset\resized\NORMAL"

import os

sample = os.listdir(image_path)[0]

img = Image.open(
    os.path.join(image_path, sample)
).convert('L')

pixels = np.array(img).flatten()

hist, _ = np.histogram(
    pixels,
    bins=256,
    range=(0,256)
)

prob = hist / np.sum(hist)

entropy = -np.sum(
    [p * log2(p)
     for p in prob
     if p > 0]
)

print(
    "Original Image Entropy:",
    entropy
)

