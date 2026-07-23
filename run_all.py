"""
Runs the full pipeline end-to-end, in the correct order, and saves the
console output of every stage into logs/<NN_step>.log so nothing has to
be re-typed or copy-pasted by hand.

USAGE:
    1. Put your dataset at dataset/original/NORMAL and
       dataset/original/PNEUMONIA (see REPRODUCTION_GUIDE.md).
    2. From this folder, run:  python run_all.py
    3. When it's done, run:    python scripts/collect_results.py
       to get a single RESULTS_SUMMARY.txt matching every table in the
       paper.

If a step fails (e.g., qiskit not installed, dataset missing), run_all.py
prints a clear message and moves on to the remaining steps where
possible, so you still get partial results.
"""

import subprocess
import sys
import os

os.makedirs("logs", exist_ok=True)

STEPS = [
    ("01_resize",            "scripts/resize_images.py"),
    ("02_check_dataset_pre", "scripts/check_dataset.py"),   # will just error/skip if csv not made yet — see note
    ("03_bb84_no_attack",    "scripts/bb84.py"),
    ("04_generate_aes_key",  "scripts/generate_aes_key.py"),
    ("05_batch_encrypt",     "scripts/batch_encrypt.py"),
    ("06_batch_decrypt",     "scripts/batch_decrypt.py"),
    ("07_verify_lossless",   "scripts/verify_lossless.py"),
    ("08_bb84_intercept",    "scripts/bb84_intercept.py"),
    ("09_bb84_mitm",         "scripts/bb84_mitm.py"),
    ("10_tamper_attack",     "scripts/tamper_attack.py"),
    ("11_decrypt_tampered",  "scripts/decrypt_tampered.py"),
    ("12_security_metrics",  "scripts/security_metrics_batch.py"),
    ("13_generate_qml_data", "scripts/generate_qml_dataset.py"),
    ("14_svm_baseline",      "scripts/svm_baseline.py"),
    ("15_train_qsvc",        "scripts/train_qsvc.py"),      # needs qiskit + qiskit-machine-learning
]

skip = {"02_check_dataset_pre"}  # this one is only useful AFTER step 13; run manually if wanted

print("=" * 60)
print("RUNNING FULL PIPELINE")
print("=" * 60)

failures = []

for name, script in STEPS:
    if name in skip:
        continue
    print(f"\n--- {name} ({script}) ---")
    log_path = os.path.join("logs", f"{name}.log")
    # QSVC's quantum-kernel training is O(n^2) circuit evaluations and
    # can legitimately take a couple of hours on a statevector simulator
    # for an 800-sample training set. Give it much more room than the
    # other (fast) steps, and ALWAYS write whatever we have to the log
    # even on timeout, so you're never left with a silent "N/A".
    step_timeout = 14400 if name == "15_train_qsvc" else 1800
    if name == "15_train_qsvc":
        print("  (this step can take 30 min - several hours; please be patient)")
    try:
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True, text=True, timeout=step_timeout
        )
        with open(log_path, "w") as f:
            f.write(result.stdout)
            if result.stderr:
                f.write("\n----- STDERR -----\n")
                f.write(result.stderr)

        if result.returncode != 0:
            print(f"  [FAILED] see {log_path} for details")
            failures.append(name)
        else:
            print(f"  [OK] log saved to {log_path}")
    except subprocess.TimeoutExpired as e:
        with open(log_path, "w") as f:
            f.write((e.stdout or "") if isinstance(e.stdout, str) else "")
            f.write(f"\n----- TIMED OUT after {step_timeout}s -----\n")
            if e.stderr:
                f.write(str(e.stderr))
        print(f"  [TIMEOUT] exceeded {step_timeout}s - see {log_path}")
        print(f"  Try running it standalone with no timeout: python {script}")
        failures.append(name)
    except Exception as e:
        print(f"  [ERROR] could not run {script}: {e}")
        failures.append(name)

print("\n" + "=" * 60)
if failures:
    print(f"Completed with {len(failures)} step(s) failing: {failures}")
    print("Check the corresponding logs/*.log files, fix the issue (usually")
    print("a missing dependency or missing dataset folder), and re-run that")
    print("single script directly, e.g.:  python scripts/train_qsvc.py")
else:
    print("All steps completed successfully.")
print("Next: run  python scripts/collect_results.py")
print("=" * 60)
