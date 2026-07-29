# ObserveSign Quality Check
**Ariel Anders** | Takehome Assignment

---

### Installation

```bash
cd traffic_light_quality_check
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

**From a pre-collected JSON file** (scoped to the target project):
```bash
PYTHONPATH=src python3 -m traffic_light \
  --file ../output.json \
  --output results/audit.json \
  --html results/report_output.html \
  --project-id 5f124e5671c7b700170a16fb
```

**Directly from the Scale API** (live, requires `SCALE_API_KEY` in `.env`):
```bash
PYTHONPATH=src python3 -m traffic_light \
  --project-id 5f124e5671c7b700170a16fb \
  --output results/audit.json \
  --html results/report_output.html
```

### Output
- **Audit JSON:** [results/audit.json](results/audit.json)
- **Interactive Visualizer Report:** [results/report_output.html](results/report_output.html) — open in a browser to inspect bounding boxes, findings, and task annotations side-by-side.

---

### 1. Approach
- **Visual Problem Exploration:** I started with a web-based visualizer tool to overlay annotations directly onto S3 images. This helped map constraints visually and identify that the database dump contained a mixture of legacy traffic light tasks, retail/invoice linter data, and current target traffic sign tasks.
- **Scoping Safeguard:** Parameterizing the CLI with `--project-id 5f124e5671c7b700170a16fb` isolates the checker to only validate the 8 target *Traffic Sign Detection* tasks, preventing legacy project schemas from contaminating the results.
- **Agentic Orchestration:** I drafted a comprehensive task-specification layout (`plan.md`) to guide the module boundaries and system architecture, then directed autonomous agent coding tools to implement the helper files and checker modules under my direct supervision.
- **Verification Loop:** Verifying check outputs inside the visualizer exposed key anomalies, such as undetected false-positive empty bounding boxes in night-time images (e.g. task `5f127f699740b80017f9b170`).

### 2. Overview
This tool performs automated, deterministic, per-task quality checks for the ObserveSign Traffic Sign Detection pipeline. All findings map natively to Scale's Fixless Audits schema properties (`type` [error/flag] and `category`), ensuring results can be ingested directly back into Scale's audit feedback loop.

### 3. Quality Checks (Summary of Categories)
- **Taxonomy Checks (TAX):** Confirms labels and attributes align with target classes. Downgrades legacy classes to warning flags.
- **Geometry Checks (GEO):** Validates bounding box positioning. Uses **Pillow dimension header-streaming** to fetch true resolution dynamically from image headers, avoiding out-of-bounds false positives without full-image download latency.
- **Overlap Checks (OVL):** Identifies near-duplicate boxes (using Intersection-over-Union thresholds) and nesting containment anomalies.

### 4. Performance & Known Limitations
To verify the software's efficiency on standard consumer hardware, benchmarks were executed locally on an Intel Core i5-1035G1 laptop (4 cores, 8 threads, 8GB RAM):
- **Scoped Run (8 target tasks):** **2.71 seconds** total execution (includes network roundtrips to stream Pillow headers for image dimensions).
- **Full Run (24 mixed tasks):** **5.86 seconds** total execution.
- **Scaling Dynamics:** Latency averages **~0.25 seconds** per task due to sequential I/O and HTTP metadata requests.

*Because the workload is strictly I/O-bound rather than CPU-bound, implementing an asynchronous thread pool will bypass sequential networking bottlenecks — fully leveraging the CPU's 8 hardware threads to drive execution times down to < 0.05 seconds per task.*

**Known Limitation — Undetected False Positives:** The checker currently cannot detect visually empty bounding boxes whose coordinates are geometrically valid. Task `5f127f699740b80017f9b170` (a low-light night scene) passed all rules with 0 findings, yet visual inspection confirmed several boxes drawn over pitch-black background regions containing no sign content. This class of error requires image-content inspection and is targeted as the top future roadmap item.

### 5. Future Roadmap (Reflection)
1. **CV-Based False Positive Auditing:** Flag empty boxes drawn over night-time shadow regions (as seen in task `5f127f699740b80017f9b170`).
2. **Density Outlier Detection:** Flag images with abnormally high annotation densities to catch spamming or systematic labeling errors.
3. **Cross-Task Consensus:** Use perceptual image hashing to find duplicate frames and flag labeling mismatches.
4. **Active Verification:** Crop annotation bounds to run OCR text verification and dominant color checks.
5. **Async Processing:** Transition task streaming to async generators to handle 250,000 tasks concurrently.

---

### 6. Detailed Quality Rules Reference Table

| Rule ID | Category | Rule Name | Severity | Fixless Category | Short Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TAX-001** | Taxonomy | Legacy/Invalid Label | `flag`/`error` | `label` | Warning flag for legacy traffic light labels; severe error for completely foreign labels. |
| **TAX-002** | Taxonomy | Legacy Attributes | `flag`/`error` | `attribute` | Warning flag for legacy attributes (e.g. `traffic_light_status`) instead of sign spec. |
| **TAX-003** | Taxonomy | Non-Visible Face Color | `error` | `attribute` | Severe error if `non_visible_face` background color is not `not_applicable`. |
| **GEO-001** | Geometry | Out of Bounds | `error` | `geometry` | Bounding box exceeds image bounds or contains invalid coordinates. |
| **GEO-002** | Geometry | Micro Box | `flag` | `geometry` | Warning flag if box width, height, or area is suspiciously small. |
| **GEO-003** | Geometry | Giant Box | `flag` | `geometry` | Warning flag if box covers > 80% of total image area. |
| **GEO-004** | Geometry | Extreme Aspect Ratio | `flag` | `geometry` | Warning flag if box aspect ratio is excessively wide/tall (> 10.0 or < 0.1). |
| **GEO-005** | Geometry | Degenerate Box | `error` | `geometry` | Severe error if box has exactly 0 width or height, indicating a structural error. |
| **OVL-001** | Overlap | Duplicate Annotations | `error` | `extraneous` | Severe error if overlapping boxes have IoU > 0.90 (duplicate labels). |
| **OVL-002** | Overlap | Suspicious Containment | `flag` | `position` | Warning flag if one bounding box is fully nested inside another. |

### 7. Scoped Audit Results (8 Assigned Tasks)

```
Audit complete. Found 28 issues across 8 tasks.
```

| Task ID | Findings | Notable Issues |
| :--- | :--- | :--- |
| `5f127f6f26831d0010e985e5` | 0 | **Clean** |
| `5f127f6c3a6b1000172320ad` | 0 | **Clean** |
| `5f127f699740b80017f9b170` | 0 | **Clean (Visual False Positives Present):** Passed all rules, but visual inspection reveals empty boxes in a pitch-black night scene — undetectable by coordinate-only validators. |
| `5f127f671ab28b001762c204` | 19 | **Severe Overlaps:** 15 `OVL-001` errors (triggered IoU > 0.90, reaching up to 0.98); 4 `OVL-002` containment flags. 6 duplicate annotations stacked on the same stop sign region. |
| `5f127f643a6b1000172320a5` | 0 | **Clean** |
| `5f127f5f3a6b100017232099` | 2 | **Warnings:** 2 `OVL-002` suspicious containment flags. |
| `5f127f5ab1cb1300109e4ffc` | 0 | **Clean** |
| `5f127f55fdc4150010e37244` | 7 | **Warnings:** 7 `GEO-002` micro box warnings (dimensions < 3px). |
