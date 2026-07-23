import random
import pandas as pd

# Parameters
NUM_SAMPLES = 500        # Normal samples + Attack samples
N_QUBITS = 1024          # Number of transmitted qubits

dataset = []


def simulate_bb84(with_eve=False, noise_probability=0.02):


    alice_bits = [random.randint(0, 1) for _ in range(N_QUBITS)]

    alice_bases = [random.choice(['+', 'x']) for _ in range(N_QUBITS)]


    if with_eve:

        eve_bases = [random.choice(['+', 'x']) for _ in range(N_QUBITS)]

        eve_results = []

        for i in range(N_QUBITS):

            if eve_bases[i] == alice_bases[i]:

                eve_results.append(alice_bits[i])

            else:

                eve_results.append(random.randint(0, 1))

        transmitted_bits = eve_results
        transmitted_bases = eve_bases

    else:

        transmitted_bits = alice_bits
        transmitted_bases = alice_bases

 
    bob_bases = [random.choice(['+', 'x']) for _ in range(N_QUBITS)]

    bob_results = []

    for i in range(N_QUBITS):

        if bob_bases[i] == transmitted_bases[i]:

            measured_bit = transmitted_bits[i]

            # Channel noise
            if random.random() < noise_probability:

                measured_bit = 1 - measured_bit

            bob_results.append(measured_bit)

        else:

            bob_results.append(random.randint(0, 1))

  
    alice_key = []

    bob_key = []

    for i in range(N_QUBITS):

        if alice_bases[i] == bob_bases[i]:

            alice_key.append(alice_bits[i])

            bob_key.append(bob_results[i])


    errors = 0

    for a, b in zip(alice_key, bob_key):

        if a != b:

            errors += 1

    qber = errors / len(alice_key) if len(alice_key) > 0 else 0

    return len(alice_key), errors, qber



print("Generating normal samples...")

for _ in range(NUM_SAMPLES):

    # Realistic QKD channel noise (0.5–3%)
    noise = random.uniform(0.005, 0.03)

    key_length, errors, qber = simulate_bb84(
        with_eve=False,
        noise_probability=noise
    )

    dataset.append([
        qber * 100,     
        key_length,
        errors,
        0               
    ])



print("Generating attack samples...")

for _ in range(NUM_SAMPLES):

    # Same channel noise plus Eve
    noise = random.uniform(0.005, 0.03)

    key_length, errors, qber = simulate_bb84(
        with_eve=True,
        noise_probability=noise
    )

    dataset.append([
        qber * 100,
        key_length,
        errors,
        1            
    ])



df = pd.DataFrame(
    dataset,
    columns=[
        "QBER",
        "Key_Length",
        "Errors",
        "Attack"
    ]
)

df.to_csv("qml_attack_dataset.csv", index=False)



print("\nDataset Created Successfully!")

print("\nDataset Shape:")
print(df.shape)

print("\nClass Distribution:")
print(df['Attack'].value_counts())

print("\nQBER Statistics:")
print(df.groupby('Attack')['QBER'].describe())

print("\nDataset saved as:")
print("qml_attack_dataset.csv")
