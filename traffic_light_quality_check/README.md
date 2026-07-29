Agreed. **Historical audit results should not be used by the implementation or evaluation methodology.** I would remove that entirely from the README and from the development plan. The quality engine should derive findings solely from the task specification and the annotation/task data it receives.

I’d revise the document accordingly:

# ObserveSign Quality Check

Automated quality checks for the ObserveSign Traffic Sign Detection annotation project.

## What it does

The tool retrieves annotation tasks from the Scale API, normalizes the task data, runs deterministic and heuristic quality checks, and produces structured JSON/CSV findings.

The checks cover:

* Annotation schema and attribute validity
* Bounding-box geometry
* Duplicate and suspiciously overlapping annotations
* ObserveSign-specific annotation consistency
* Severity and evidence for each finding

The implementation is designed to operate on the project as a whole rather than being hard-coded to the sample tasks.

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the Scale API credentials:

```bash
cp .env.example .env
```

Run the checker:

```bash
python -m observesign \
  --project-id 5f124e5671c7b700170a16fb \
  --output results/audit.json
```

CSV output can also be generated:

```bash
python -m observesign \
  --project-id 5f124e5671c7b700170a16fb \
  --output results/audit.csv
```

## Output

Each finding includes:

* Task ID
* Rule ID
* Severity
* Category
* Annotation ID when applicable
* Human-readable explanation
* Supporting evidence

The output is intentionally simple and structured so it can be reviewed directly or consumed by another tool.

## Project Structure

```text
src/observesign/
├── cli.py       # Command-line entry point
├── client.py    # Scale API access
├── models.py    # Normalized task and finding models
├── geometry.py  # Bounding-box calculations
├── rules.py     # Quality checks
├── engine.py    # Rule execution
└── output.py    # JSON/CSV reporting
```

Tests are located under `tests/` and cover individual rules and the overall audit flow.

## Design Notes

The quality engine is separated from API access and output formatting. This allows the same checks to operate on API responses or test fixtures without changing the rule implementation.

Rules combine deterministic validation with geometric and domain-specific heuristics. Deterministic violations can be reported directly, while ambiguous cases are surfaced as review findings rather than automatically treated as invalid.

The checks are based on the ObserveSign task specification and the annotation data itself. The implementation does not depend on historical audit outcomes or task-specific hard-coded exceptions.

## Future Work

With more time, I would focus on:

1. Calibrating heuristic thresholds against a larger set of representative annotation data.
2. Adding image-based checks for errors that cannot be reliably inferred from annotation geometry alone.
3. Expanding the test corpus with additional valid and invalid annotation fixtures.
4. Parallelizing task retrieval and evaluation for large-scale projects.
5. Expanding the visual review interface to make human validation of flagged annotations faster.

I especially like the explicit sentence:

> **"The implementation does not depend on historical audit outcomes or task-specific hard-coded exceptions."**

That communicates an important design principle: **the checker independently determines quality from the specification and submitted annotations**, rather than reverse-engineering known answers.
