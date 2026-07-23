import random

n = 1024


alice_bits = [random.randint(0,1) for _ in range(n)]

alice_bases = [
    random.choice(['+','x'])
    for _ in range(n)
]


eve_bases_A = [
    random.choice(['+','x'])
    for _ in range(n)
]

eve_results_A = []

for i in range(n):

    if eve_bases_A[i] == alice_bases[i]:

        eve_results_A.append(
            alice_bits[i]
        )

    else:

        eve_results_A.append(
            random.randint(0,1)
        )


eve_bits_to_bob = eve_results_A

eve_bases_B = [
    random.choice(['+','x'])
    for _ in range(n)
]

bob_bases = [
    random.choice(['+','x'])
    for _ in range(n)
]

bob_results = []

for i in range(n):

    if bob_bases[i] == eve_bases_B[i]:

        bob_results.append(
            eve_bits_to_bob[i]
        )

    else:

        bob_results.append(
            random.randint(0,1)
        )


alice_key = []

bob_key = []

for i in range(n):

    if alice_bases[i] == bob_bases[i]:

        alice_key.append(
            alice_bits[i]
        )

        bob_key.append(
            bob_results[i]
        )


errors = sum(
    a != b
    for a,b in zip(
        alice_key,
        bob_key
    )
)

mismatch_rate = (
    errors /
    len(alice_key)
) * 100

print("\n===== MITM ATTACK =====")

print(
    "Alice Key Length:",
    len(alice_key)
)

print(
    "Bob Key Length:",
    len(bob_key)
)

print(
    "Mismatch Rate:",
    round(
        mismatch_rate,
        2
    ),
    "%"
)

if mismatch_rate > 0:

    print(
        "Authentication Failed"
    )

else:

    print(
        "Authentication Successful"
    )
