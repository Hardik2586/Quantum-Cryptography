# Reproducing the Paper's Results On Your Own Machine (with Qiskit)

This package lets you regenerate **every number in the paper** — including
the QSVC results, which I could not run on my end because this sandbox has
no internet access to install `qiskit-machine-learning`. Since you already
have Qiskit installed, you can get the one number I couldn't verify myself.

## 0. What's in this folder

```
repro/
  requirements.txt
  run_all.py                       <- runs the whole pipeline in order
  REPRODUCTION_GUIDE.md            <- this file
  scripts/
    resize_images.py               <- your original scripts
    bb84.py
    bb84_intercept.py              <- new: standalone intercept-resend attack
    bb84_mitm.py
    generate_aes_key.py
    batch_encrypt.py
    batch_decrypt.py
    verify_lossless.py             <- new: confirms 200/200 recovery rate
    tamper_attack.py
    decrypt_tampered.py
    security_metrics_batch.py      <- new: entropy/NPCR/UACI over ALL 200 images
    generate_qml_dataset.py
    svm_baseline.py
    train_qsvc.py                  <- the one that needs Qiskit
    collect_results.py             <- new: parses every log into one summary
    entropy_analysis.py / npcr.py / encrypt_single_image.py /
    decrypt_single_image.py / check_dataset.py   <- original single-image utilities
```

Two scripts are new (not in your original zip) because the paper needed them
and they weren't included: `bb84_intercept.py` (the standalone intercept-resend
attack — your original `bb84_mitm.py` covers MITM but there wasn't a separate
intercept-resend script) and `verify_lossless.py` / `security_metrics_batch.py`
(your originals only checked *one* image at a time; these check all 200 and
average them, which is what the paper's tables actually report).

## 1. Environment setup

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
```

If you already have Qiskit installed globally, you can skip the venv and just:

```bash
pip install pycryptodome scikit-learn pandas Pillow matplotlib
pip install qiskit qiskit-machine-learning qiskit-aer   # if not already present
```

Check your Qiskit version matches what `train_qsvc.py` expects:

```bash
python -c "import qiskit; print(qiskit.__version__)"
python -c "import qiskit_machine_learning; print('qiskit-machine-learning OK')"
```

`train_qsvc.py` uses `FidelityQuantumKernel` from `qiskit_machine_learning.kernels`
and `ZZFeatureMap` from `qiskit.circuit.library` — these are stable in
Qiskit ML 0.7+. If you're on an older Qiskit (pre-1.0, using `QuantumInstance`
instead of primitives), the import will fail — run
`pip install --upgrade qiskit qiskit-machine-learning` first.

## 2. Get the dataset

The paper uses 100 NORMAL + 100 PNEUMONIA chest X-ray images. If you don't
already have your original dataset folder, the standard public source is the
**Chest X-Ray Images (Pneumonia)** dataset on Kaggle
(`paultimothymooney/chest-xray-pneumonia`). Download it, then pick any 100
images from `NORMAL/` and 100 from `PNEUMONIA/` (the train split has far more
than 100 of each) and place them here:

```
repro/
  dataset/
    original/
      NORMAL/       <- 100 .jpeg/.png files
      PNEUMONIA/    <- 100 .jpeg/.png files
```

**Important — path separators:** your original scripts (`batch_encrypt.py`,
`encrypt_single_image.py`, `entropy_analysis.py`) hardcode Windows-style
paths like `r"dataset\resized"`. If you're on Windows, leave them as-is. If
you're on macOS/Linux, either run everything inside WSL, or do a quick
find-and-replace of `\` → `/` in those three files before running.

## 3. Run everything in one shot

```bash
cd repro
python run_all.py
```

This runs, **in the correct order**, and logs every step's output to
`logs/<step>.log`:

1. Resize/grayscale the dataset
2. BB84 (no attack) → sifted key + 0% QBER baseline
3. Derive the AES-256 key (SHA-256 of the BB84 key)
4. Encrypt all 200 images
5. Decrypt all 200 images
6. Verify every decrypted image is byte-identical to the original
7. Intercept-resend attack → ~25% QBER
8. MITM attack → ~35-40% key mismatch
9. Ciphertext tampering + attempted decryption of the tampered file
10. Dataset-wide entropy / NPCR / UACI (averaged over all 200 images)
11. Generate the 1000-sample QML training dataset
12. Classical SVM baseline
13. **QSVC training on your local Qiskit install** — this is the step that
    needed your machine

If a step fails (most likely candidates: dataset not found, or Qiskit
import error on step 13), `run_all.py` keeps going and tells you exactly
which log file to check. You can always re-run a single step manually:

```bash
python scripts/train_qsvc.py
```

## 4. Collect everything into one summary

```bash
python scripts/collect_results.py
```

This reads every log in `logs/` and writes `RESULTS_SUMMARY.txt` — a single
file with the same tables that appear in the paper (BB84 no-attack, intercept-resend,
MITM, dataset-wide entropy/NPCR/UACI, classical SVM, and QSVC), populated with
**your machine's actual numbers**, plus a per-image CSV
(`security_metrics_full_dataset.csv`) if you want to inspect individual images
rather than just the averages.

## 5. What to expect vs. the paper

| Result | Paper value | Should you expect exact match? |
|---|---|---|
| BB84 QBER, no attack | 0.00% | Yes — always 0% absent noise/attack |
| Intercept-resend QBER | 24.56% | No — random each run, expect ~22-28% |
| MITM mismatch rate | 38.49% | No — random each run, expect ~35-40% |
| Recovery rate | 100% | Yes — AES-CBC round-trip is deterministic |
| Entropy (dataset avg.) | ~7.99 | Yes, very close — depends on your actual images |
| NPCR (dataset avg.) | >99% | Yes, very close |
| UACI (dataset avg.) | ~30-34% | Close — depends on your specific 200 images |
| Classical SVM accuracy | 100% | Yes, typically — this feature set is easily separable |
| **QSVC accuracy** | 88.5% | **This is the number only your machine can give you.** Expect it to land somewhere in the mid-80s to low-90s — exact value depends on Qiskit version, simulator backend, and the random train/test split seed (fixed at 42, so it should be fairly stable run-to-run on the same Qiskit version). |

If your QSVC number comes out meaningfully different from 88.5% (say, below
70% or above 98%), that's worth double-checking rather than assuming it's
just normal variance — start by checking `logs/15_train_qsvc.log` for
warnings and confirm `qml_attack_dataset.csv` has the expected 1000 rows
with a balanced 500/500 class split.

## 6. Once you have your numbers

Send me `RESULTS_SUMMARY.txt` (and `security_metrics_full_dataset.csv` if
you want dataset-wide figures instead of the single demo image I used) and
I'll update the paper's tables and figures to reflect your actual Qiskit
run instead of the reported values from your Executive Summary.
