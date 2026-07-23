import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from qiskit.circuit.library import ZZFeatureMap
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from qiskit_machine_learning.algorithms import QSVC

# ======================================
# Load Dataset
# ======================================

df = pd.read_csv("qml_attack_dataset.csv")

print("\nDataset Shape:")
print(df.shape)

# ======================================
# Features and Labels
# ======================================

X = df[['QBER', 'Key_Length', 'Errors']]

y = df['Attack']

# ======================================
# Train-Test Split
# ======================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ======================================
# Feature Scaling
# ======================================

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)

X_test = scaler.transform(X_test)

# ======================================
# Quantum Feature Map
# ======================================

feature_map = ZZFeatureMap(
    feature_dimension=X_train.shape[1],
    reps=2
)

# ======================================
# Quantum Kernel
# ======================================

quantum_kernel = FidelityQuantumKernel(
    feature_map=feature_map
)

# ======================================
# QSVC Model
# ======================================

qsvc = QSVC(
    quantum_kernel=quantum_kernel
)

print("\nTraining QSVC...")

qsvc.fit(X_train, y_train)

print("Training Complete!")

# ======================================
# Predictions
# ======================================

y_pred = qsvc.predict(X_test)

# ======================================
# Evaluation
# ======================================

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(y_test, y_pred)

recall = recall_score(y_test, y_pred)

f1 = f1_score(y_test, y_pred)

print("\n===== QSVC RESULTS =====")

print(f"Accuracy : {accuracy:.4f}")

print(f"Precision: {precision:.4f}")

print(f"Recall   : {recall:.4f}")

print(f"F1 Score : {f1:.4f}")

print("\nConfusion Matrix:")

print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")

print(classification_report(y_test, y_pred))