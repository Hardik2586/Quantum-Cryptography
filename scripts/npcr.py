from PIL import Image
import numpy as np

img1 = Image.open(
    "original.jpeg"
).convert('L')

img2 = Image.open(
    "decrypted_image.jpeg"
).convert('L')

A = np.array(img1)

B = np.array(img2)

diff = (A != B)

npcr = (
    np.sum(diff)
    /
    diff.size
) * 100

print(
    "NPCR:",
    npcr
)
