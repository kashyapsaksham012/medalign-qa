# Independent Validation of Path B Qwen2.5-7B Results

## Purpose

This report documents an independent fresh inference run used to
cross-check the original Path B Qwen2.5-7B-Instruct results.

This is a validation run, not a replacement of the original experiment.
The original prediction namespace remains `qwen25-7b-local`; the fresh
validation run is stored separately under `qwen25-7b-validation`.

## Fixed experimental setup

- Model: `Qwen/Qwen2.5-7B-Instruct`
- Hugging Face revision:
  `a09a35458c702b33eeacc393d103063234e8bc28`
- Dataset: MedQA 4-option test
- Questions: 1,273
- GPU: 2 × Tesla T4
- dtype: float16
- Tensor parallelism: 2
- GPU memory utilization: 0.80
- Global seed: 0
- Same project code and evaluation pipeline
- Separate validation output namespace

## Results

| Strategy | Original | Fresh validation | Difference |
|---|---:|---:|---:|
| Few-shot | 59.4% | 59.4% | +0.0 pp |
| CoT | 60.5% | 60.6% | +0.2 pp |
| Self-consistency | 63.3% | 63.2% | -0.1 pp |

## Per-question agreement

### Few-shot

- Rows: 1273 old / 1273 new
- Parsed-answer agreement: 100.00%
- Correctness agreement: 100.00%

### Chain-of-thought

- Rows: 1273 old / 1273 new
- Parsed-answer agreement: 99.61%
- Correctness agreement: 99.69%

### Self-consistency

Self-consistency produces 11 sampled generations per question, so its
final answer is reconstructed as the majority vote over the parsed
responses.

- Rows: 1273 old / 1273 new
- Final majority-vote agreement: 99.14%
- Correctness agreement: 99.45%

## Interpretation

The fresh model run strongly corroborates the original MedQA results:

- Few-shot reproduced the original 59.4% exactly.
- CoT reproduced the original result within 0.1 percentage point.
- Self-consistency reproduced the original result within 0.1 percentage point.
- Per-question agreement exceeded 99% for the deterministic and
  majority-vote comparisons.

The self-consistency result is stochastic and therefore should not be
expected to be bit-identical. Its 63.2% fresh result is consistent with
the original 63.3% result and the previously measured run-to-run
variation.

## Provenance limitation

This validation substantially strengthens confidence that the original
prediction artifacts are consistent with the pinned model, dataset,
prompts, and evaluation pipeline. It is not a cryptographic proof of
the provenance of the historical prediction files.

## Conclusion

The original MedQA few-shot, CoT, and self-consistency results were
independently cross-validated using a fresh inference run on the same
pinned Qwen2.5-7B-Instruct revision and the same benchmark.

Machine-readable details are stored in:

- `results/validation_comparison.json`
- `results/validation_predictions_sha256.json`

Fresh prediction files are stored separately under:

- `derived_data/predictions/qwen25-7b-validation/`
