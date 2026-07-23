"""
Reads every log file in logs/ (produced by run_all.py) and assembles a
single RESULTS_SUMMARY.txt with the same tables that appear in the
paper (Tables II-V), populated with YOUR machine's actual numbers.

Run this LAST, after run_all.py has finished.
"""

import os
import re

LOGDIR = "logs"

def read_log(name):
    path = os.path.join(LOGDIR, f"{name}.log")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return f.read()

def grab(pattern, text, default="N/A"):
    if text is None:
        return "N/A (step not run)"
    m = re.search(pattern, text)
    return m.group(1) if m else default

lines = []
lines.append("=" * 70)
lines.append("RESULTS SUMMARY -- reproduced on this machine")
lines.append("=" * 70)

# ---- BB84 no attack ----
t = read_log("03_bb84_no_attack")
lines.append("\nTable: BB84 Key Distribution (No Attack)")
lines.append(f"  Sifted key length : {grab(r'Final Key Length:\s*(\d+)', t)}")
lines.append(f"  QBER              : {grab(r'QBER:\s*([\d.]+)\s*%', t)}%")

# ---- Lossless recovery ----
t = read_log("07_verify_lossless")
lines.append("\nTable: Secure Transmission / Recovery Rate")
lines.append(f"  Images checked    : {grab(r'Total images checked\s*:\s*(\d+)', t)}")
lines.append(f"  Recovery rate     : {grab(r'Recovery rate\s*:\s*([\d.]+)%', t)}%")

# ---- Intercept-resend ----
t = read_log("08_bb84_intercept")
lines.append("\nTable II: Intercept-Resend Attack")
lines.append(f"  Sifted key length : {grab(r'Sifted key length\s*:\s*(\d+)', t)}")
lines.append(f"  Errors            : {grab(r'Errors\s*:\s*(\d+)', t)}")
lines.append(f"  QBER              : {grab(r'QBER\s*:\s*([\d.]+)\s*%', t)}%")

# ---- MITM ----
t = read_log("09_bb84_mitm")
lines.append("\nTable III: MITM Attack")
lines.append(f"  Alice key length  : {grab(r'Alice Key Length:\s*(\d+)', t)}")
lines.append(f"  Bob key length    : {grab(r'Bob Key Length:\s*(\d+)', t)}")
lines.append(f"  Mismatch rate     : {grab(r'Mismatch Rate:\s*([\d.]+)\s*%', t)}%")

# ---- Security metrics (dataset-wide) ----
t = read_log("12_security_metrics")
lines.append("\nTable V: Security Metrics (dataset-wide average)")
m = re.search(r"Entropy\s*-\s*mean:\s*([\d.]+)", t) if t else None
lines.append(f"  Entropy (mean)    : {m.group(1) if m else 'N/A'}")
m = re.search(r"NPCR \(%\) - mean:\s*([\d.]+)", t) if t else None
lines.append(f"  NPCR % (mean)     : {m.group(1) if m else 'N/A'}")
m = re.search(r"UACI \(%\) - mean:\s*([\d.]+)", t) if t else None
lines.append(f"  UACI % (mean)     : {m.group(1) if m else 'N/A'}")

# ---- Classical SVM ----
t = read_log("14_svm_baseline")
lines.append("\nTable: Classical SVM Baseline")
lines.append(f"  Accuracy          : {grab(r'Accuracy:\s*([\d.]+)', t)}")
lines.append(f"  Precision         : {grab(r'Precision:\s*([\d.]+)', t)}")
lines.append(f"  Recall            : {grab(r'Recall:\s*([\d.]+)', t)}")
lines.append(f"  F1                : {grab(r'F1:\s*([\d.]+)', t)}")
cm = re.search(r"\[\[(\d+)\s+(\d+)\]\s*\n?\s*\[\s*(\d+)\s+(\d+)\]\]", t) if t else None
if cm:
    lines.append(f"  Confusion matrix  : [[{cm.group(1)}, {cm.group(2)}], [{cm.group(3)}, {cm.group(4)}]]")
else:
    lines.append("  Confusion matrix  : N/A")

# ---- QSVC ----
t = read_log("15_train_qsvc")
lines.append("\nTable: QSVC (Qiskit) -- your local run")
lines.append(f"  Accuracy          : {grab(r'Accuracy\s*:\s*([\d.]+)', t)}")
lines.append(f"  Precision         : {grab(r'Precision:\s*([\d.]+)', t)}")
lines.append(f"  Recall            : {grab(r'Recall\s*:\s*([\d.]+)', t)}")
lines.append(f"  F1 Score          : {grab(r'F1 Score\s*:\s*([\d.]+)', t)}")
cm = re.search(r"\[\[(\d+)\s+(\d+)\]\s*\n?\s*\[\s*(\d+)\s+(\d+)\]\]", t) if t else None
if cm:
    lines.append(f"  Confusion matrix  : [[{cm.group(1)}, {cm.group(2)}], [{cm.group(3)}, {cm.group(4)}]]")
else:
    lines.append("  Confusion matrix  : N/A (qiskit / qiskit-machine-learning not installed or step failed -- check logs/15_train_qsvc.log)")

lines.append("\n" + "=" * 70)
lines.append("NOTE: BB84/MITM/intercept numbers will differ slightly from the")
lines.append("paper on every run -- they depend on random bit/basis choices.")
lines.append("That run-to-run variation (e.g. QBER ~24-26%, MITM mismatch")
lines.append("~35-40%) is expected and is itself evidence the simulation is")
lines.append("behaving correctly, not a discrepancy to worry about.")
lines.append("=" * 70)

summary = "\n".join(lines)
print(summary)

with open("RESULTS_SUMMARY.txt", "w") as f:
    f.write(summary)

print("\nSaved to RESULTS_SUMMARY.txt")
