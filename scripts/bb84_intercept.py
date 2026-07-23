
import random

n = 1024

# Alice
alice_bits = [random.randint(0, 1) for _ in range(n)]
alice_bases = [random.choice(['+', 'x']) for _ in range(n)]

eve_bases = [random.choice(['+', 'x']) for _ in range(n)]
eve_results = []
for i in range(n):
    if eve_bases[i] == alice_bases[i]:
        eve_results.append(alice_bits[i])
    else:
        eve_results.append(random.randint(0, 1))

bob_bases = [random.choice(['+', 'x']) for _ in range(n)]
bob_results = []
for i in range(n):
    if bob_bases[i] == eve_bases[i]:
        bob_results.append(eve_results[i])
    else:
        bob_results.append(random.randint(0, 1))

alice_key, bob_key = [], []
for i in range(n):
    if alice_bases[i] == bob_bases[i]:
        alice_key.append(alice_bits[i])
        bob_key.append(bob_results[i])

errors = sum(a != b for a, b in zip(alice_key, bob_key))
qber = errors / len(alice_key) * 100 if alice_key else 0

print("\n===== INTERCEPT-RESEND ATTACK =====")
print("Qubits sent       :", n)
print("Sifted key length :", len(alice_key))
print("Errors            :", errors)
print("QBER              :", round(qber, 2), "%")
