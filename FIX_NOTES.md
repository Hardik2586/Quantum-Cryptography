# Fix Notes (after reviewing your RESULTS_SUMMARY.txt)

Your run looked great except for one thing: **Entropy 1.49 / NPCR 96.4% / UACI 46.6%**
instead of the expected ~7.99 / >99% / ~33%. Everything else (BB84, MITM,
intercept-resend, recovery rate, classical SVM) was right in the expected range.

## Root cause

`batch_encrypt.py` encrypts the **raw file bytes** of each resized image. If
`resize_images.py` saved those images as JPEG (the default, since it just
re-saves with the original extension), the file on disk is *compressed* —
typically 15-25 KB for a 256×256 X-ray, not the 65,536 bytes (256×256) of raw
pixel data.

`security_metrics_batch.py` assumes the ciphertext is at least W×H = 65,536
bytes long (one byte per pixel) so it can reshape it into a same-size "cipher
image" for comparison. When the actual ciphertext was only ~15-25 KB, the
script silently zero-padded the missing ~40-50 KB — so most of the "encrypted
image" it was comparing against was artificial zeros, not real ciphertext.
That's exactly what tanks entropy (a huge spike at value 0), and skews NPCR/UACI.

## Fix

`batch_encrypt.py` and `batch_decrypt.py` now operate on the **raw decoded
pixel bytes** (`img.tobytes()`) instead of the compressed file bytes. This is
also the more standard approach in the image-encryption literature (NPCR/UACI
are defined over the pixel matrix, not a compressed container format). Decrypted
output is now saved as `.png` (lossless) instead of `.jpeg`, since we're
reconstructing a raw pixel buffer, not a JPEG-encoded file.

Because the decrypted files are now `.png` instead of `.jpeg`, a raw byte
comparison against the original JPEG in `verify_lossless.py` would falsely
report a mismatch even though the pixels are identical — the file *formats*
differ even when the pixel data doesn't. `verify_lossless.py` now compares
decoded pixel arrays instead of raw file bytes.

## What you need to re-run

Only the encryption-side steps are affected. You do **not** need to redo BB84,
MITM, intercept-resend, or the QML/SVM steps — those numbers were already
correct.

```bash
rm -rf encrypted_images decrypted_images tampered_image.enc tampered_decrypted.jpeg
python scripts/batch_encrypt.py
python scripts/batch_decrypt.py
python scripts/verify_lossless.py
python scripts/tamper_attack.py
python scripts/decrypt_tampered.py
python scripts/security_metrics_batch.py
python scripts/collect_results.py
```

Tested locally with a small synthetic dataset before sending this to you —
after the fix: entropy ≈ 7.997, NPCR ≈ 99.62%, UACI ≈ 33.4%, right in line
with the paper's target values.

## About the QSVC step showing "N/A (step not run)"

This almost certainly means `run_all.py`'s 30-minute timeout was hit before
`train_qsvc.py` finished — not that Qiskit is missing. `FidelityQuantumKernel`
has to evaluate a quantum circuit for every pair of training samples (roughly
800×800/2 ≈ 320,000 circuit evaluations for an 800-sample training set), which
on a statevector simulator can genuinely take anywhere from 30 minutes to a
few hours depending on your machine. The old `run_all.py` silently discarded
any output when a step timed out, which is why you got a bare "N/A" instead
of an error message.

Two fixes are included:

1. **`run_all.py` now gives the QSVC step up to 4 hours**, and saves whatever
   partial output exists even if it still times out (so you'll get a real
   error message next time, not silence).
2. **Recommended: run it standalone instead of through `run_all.py`**, so it
   isn't bound by any script timeout at all:

   ```bash
   python scripts/train_qsvc.py > logs/15_train_qsvc.log 2>&1
   ```

   On Linux/Mac you can let it run in the background so you can close the
   terminal:

   ```bash
   nohup python scripts/train_qsvc.py > logs/15_train_qsvc.log 2>&1 &
   ```

   Then check `logs/15_train_qsvc.log` periodically. Once it's done (you'll
   see `===== QSVC RESULTS =====` at the end), re-run
   `python scripts/collect_results.py` to fold it into the summary.

If it fails immediately (within seconds) rather than timing out, that's a
different problem — most likely a Qiskit version mismatch. Run this and send
me the output if so:

```bash
python -c "import qiskit; print(qiskit.__version__)"
python -c "from qiskit_machine_learning.kernels import FidelityQuantumKernel; print('ok')"
python -c "from qiskit.circuit.library import ZZFeatureMap; print('ok')"
```
