import pandas as pd

df = pd.read_csv("qml_attack_dataset.csv")

print("\nNormal Communication:")
print(df[df['Attack'] == 0]['QBER'].describe())

print("\nAttack Communication:")
print(df[df['Attack'] == 1]['QBER'].describe())
