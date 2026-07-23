import hashlib

# Read BB84 key
with open("bb84_key.txt", "r") as f:
    bb84_key = f.read().strip()

# Generate AES-256 key using SHA-256
aes_key = hashlib.sha256(bb84_key.encode()).digest()

# Save key
with open("aes_key.bin", "wb") as f:
    f.write(aes_key)

print("AES-256 key generated successfully.")
print("Key length:", len(aes_key), "bytes")