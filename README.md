# ObserveSign Quality Check
**Ariel Anders** | Takehome Assignment

See [REFLECTION.md](REFLECTION.md) for approach, quality checks, per-task results, and future work.

---

### Installation

```bash
pip install -e .
# or
pip install -r requirements.txt
```

### Environment Setup (for live API usage)

Create a `.env` file in the `traffic_light_quality_check/` directory:

```bash
echo "SCALE_API_KEY=your_api_key_here" > .env
```

This is only required when running against the live Scale API (i.e. without `--file`). When using `--file` with a pre-collected JSON dump, no API key is needed.

### Running the CLI

**From the Scale API** (primary — requires `SCALE_API_KEY` in `.env`):
```bash
PYTHONPATH=src python3 -m observe_sign \
  --project-id <your-project-id> \
  --output results/audit.json \
  --html results/report_output.html
```

**Save a local snapshot for offline reuse** (add `--save-tasks`):
```bash
PYTHONPATH=src python3 -m observe_sign \
  --project-id <your-project-id> \
  --output results/audit.json \
  --save-tasks tasks_snapshot.json
```

**Re-run from a saved snapshot** (no API key needed):
```bash
PYTHONPATH=src python3 -m observe_sign \
  --file tasks_snapshot.json \
  --project-id <your-project-id> \
  --output results/audit.json \
  --html results/report_output.html
```

### Output
- **Audit JSON:** [results/audit.json](results/audit.json)
- **Interactive Visualizer Report:** [results/report_output.html](results/report_output.html) — open in a browser to inspect bounding boxes, findings, and task annotations side-by-side.

> **Note:** The committed results in `results/` were generated for project ID `5f124e5671c7b700170a16fb` (the 8 assigned Traffic Sign Detection tasks). To run against a different project, pass `--project-id <id>` and specify new output paths.
