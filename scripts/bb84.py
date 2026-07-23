import random

# Number of qubits to transmit
n = 1024

# Step 1: Alice generates random bits
alice_bits = [random.randint(0, 1) for _ in range(n)]

# Step 2: Alice chooses random bases
alice_bases = [random.choice(['+', 'x']) for _ in range(n)]

# Step 3: Bob chooses random bases
bob_bases = [random.choice(['+', 'x']) for _ in range(n)]

# Step 4: Bob measures the qubits
bob_results = []

for i in range(n):

    if alice_bases[i] == bob_bases[i]:
        bob_results.append(alice_bits[i])

    else:
        bob_results.append(random.randint(0, 1))


# Step 5: Sifting process
alice_key = []
bob_key = []

for i in range(n):

    if alice_bases[i] == bob_bases[i]:

        alice_key.append(alice_bits[i])

        bob_key.append(bob_results[i])


# Step 6: Calculate QBER
errors = 0

for i in range(len(alice_key)):

    if alice_key[i] != bob_key[i]:

        errors += 1


qber = errors / len(alice_key) if len(alice_key) > 0 else 0


print("\n===== BB84 SIMULATION =====")

print("\nAlice Bits:")
print(alice_bits)

print("\nAlice Bases:")
print(alice_bases)

print("\nBob Bases:")
print(bob_bases)

print("\nBob Results:")
print(bob_results)

print("\nSifted Key (Alice):")
print(alice_key)

print("\nSifted Key (Bob):")
print(bob_key)

print("\nFinal Key Length:", len(alice_key))

print("QBER:", round(qber * 100, 2), "%")

key_string = ''.join(map(str, alice_key))

with open("bb84_key.txt", "w") as file:
    file.write(key_string)

print("\nKey saved to bb84_key.txt")
