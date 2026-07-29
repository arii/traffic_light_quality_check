# ObserveSign Quality Check
**Ariel Anders** | Takehome Assignment

Automated quality checks for the ObserveSign Traffic Sign Detection project.

## 1. Overview

This tool performs automated, deterministic, per-task quality checks for the ObserveSign Traffic Sign Detection pipeline. All checks map natively to Scale's Fixless Audits schema properties (`type` [error/flag] and `category`), ensuring findings can be ingested directly back into Scale's audit feedback loop. Given the time constraints, this implementation focuses on deterministic geometry, taxonomy, and overlap validation rules rather than predictive heuristics.

---

## 2. Quality Rules & Implementation Notes

### Taxonomy Rules (TAX)

| Rule ID | Category | Rule Name | Severity | Fixless Category | Short Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TAX-001** | Taxonomy | Legacy/Invalid Label | `flag` / `error` | `label` | Warning flag for legacy traffic light labels; severe error for completely foreign labels. |
| **TAX-002** | Taxonomy | Legacy Attributes | `flag` / `error` | `attribute` | Warning flag for legacy attributes (e.g. `traffic_light_status`) instead of sign spec. |
| **TAX-003** | Taxonomy | Non-Visible Face Color | `error` | `attribute` | Severe error if `non_visible_face` background color is not `not_applicable`. |

* **Taxonomy Transition Handling:** The demo dataset contains legacy "Traffic Light" labels (such as `Traffic lights`) and attributes (such as `traffic_light_status`) rather than the target "Traffic Sign" specification (e.g. `traffic_control_sign`). Legacy terms are dynamically downgraded to `flag` warnings rather than triggering severe errors, keeping validation functional instead of rejecting all legacy tasks.

### Geometry Rules (GEO)

| Rule ID | Category | Rule Name | Severity | Fixless Category | Short Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GEO-001** | Geometry | Out of Bounds | `error` | `geometry` | Bounding box exceeds image bounds or contains invalid coordinates. |
| **GEO-002** | Geometry | Micro Box | `flag` | `geometry` | Warning flag if box width, height, or area is suspiciously small. |
| **GEO-003** | Geometry | Giant Box | `flag` | `geometry` | Warning flag if box covers > 80% of total image area. |
| **GEO-004** | Geometry | Extreme Aspect Ratio | `flag` | `geometry` | Warning flag if box aspect ratio is excessively wide/tall (> 10.0 or < 0.1). |
| **GEO-005** | Geometry | Degenerate Box | `error` | `geometry` | Severe error if box has exactly 0 width or height, indicating a structural error. |

* **Pillow Dimension Header-Streaming:** Bounding box coordinates cannot be validated without knowing image dimensions, which are frequently omitted from task payloads. Rather than falling back to arbitrary dimensions, bounds-checking uses a `Pillow`-based header streaming lookup. It fetches only the initial image URL metadata bytes to resolve resolution, eliminating out-of-bounds false positives without full-image download bottlenecks.

### Overlap Rules (OVL)

| Rule ID | Category | Rule Name | Severity | Fixless Category | Short Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OVL-001** | Overlap | Duplicate Annotations | `error` | `extraneous` | Severe error if overlapping boxes have IoU > 0.90 (duplicate labels). |
| **OVL-002** | Overlap | Suspicious Containment | `flag` | `position` | Warning flag if one bounding box is fully nested inside another. |

---

## 3. Scope Safeguard

The validator CLI is parameterized by `project_id`. This scoping design isolates evaluation to the requested project pipeline. In a shared demo account containing multiple active tasks from retail, invoice, or other object linter experiments, it prevents cross-project annotation schemas from contaminating the results at scale.

---

## 4. Execution & Results (Assigned Project Tasks)

### Setup & Run Instructions

Install dependencies:
```bash
pip install -r requirements.txt
```

Configure Scale API credentials:
```bash
cp .env.example .env
```

Run the quality checker:
```bash
PYTHONPATH=src python3 -m traffic_light \
  --file ../output.json \
  --output results/audit.json \
  --html results/report_output.html \
  --project-id 5f124e5671c7b700170a16fb
```

Console Output:
```text
Audit complete. Found 28 issues across 8 tasks.
Results written to results/audit.json
Visualization report generated at results/report_output.html
```

### Audit Results

The audit results below are scoped specifically to the **Traffic Sign Detection** project containing the 8 assigned tasks (5 tasks were clean, 2 tasks triggered warnings, and 1 task contained severe duplicate errors):

| Task ID | Findings | Project Source | Notable Issues |
| :--- | :--- | :--- | :--- |
| `5f127f6f26831d0010e985e5` | 0 findings | `Traffic Sign Detection` | **Clean:** Bounding box coordinates and attributes match the target taxonomy. |
| `5f127f6c3a6b1000172320ad` | 0 findings | `Traffic Sign Detection` | **Clean:** Bounding box coordinates and attributes match the target taxonomy. |
| `5f127f699740b80017f9b170` | 0 findings | `Traffic Sign Detection` | **Clean:** Bounding box coordinates and attributes match the target taxonomy. |
| `5f127f671ab28b001762c204` | 19 findings | `Traffic Sign Detection` | **Severe Overlaps:** 15 severe `OVL-001` duplicate annotation errors (IoU > 0.98) on stop signs; 4 `OVL-002` containment flags. Density is due to 6 duplicate annotations overlaid on the same sign region. |
| `5f127f643a6b1000172320a5` | 0 findings | `Traffic Sign Detection` | **Clean:** Bounding box coordinates and attributes match the target taxonomy. |
| `5f127f5f3a6b100017232099` | 2 findings | `Traffic Sign Detection` | **Warnings:** 2 `OVL-002` suspicious containment flags (bounding box nested within another). |
| `5f127f5ab1cb1300109e4ffc` | 0 findings | `Traffic Sign Detection` | **Clean:** Bounding box coordinates and attributes match the target taxonomy. |
| `5f127f55fdc4150010e37244` | 7 findings | `Traffic Sign Detection` | **Warnings:** 7 `GEO-002` micro box warnings (bounding box dimensions are extremely small, under `3.0` pixels). |

---

## 5. Reflection: Future Roadmap

If given more time to scale this checker for production workloads (e.g. 250,000 tasks):

1. **Cross-Task Consensus Checks:** Implement perceptual image hashing to automatically identify duplicate images labeled by different annotators and flag discrepancies in labeling.
2. **Dominant Color Verification:** Add cropping pipelines to extract sign or traffic light bounding box regions and programmatically verify that the labeled color attribute matches actual pixel colors (e.g., green/red lights).
3. **Targeted & Global OCR Auditing:** Integrate OCR to read cropped sign text (e.g., matching speed limit values against labels) and scan the global canvas to flag text (e.g. "STOP" signs) that does not have a bounding box annotation.
4. **Proactive Project Fingerprint Checks:** Generalize the project scope safeguard by checking a queried project's schemas against a fingerprint registry, generating a diagnostic alert if labels look mismatched before running geometry logic.
5. **Asynchronous Processing:** Re-architect client fetches and dimensions lookups to utilize an asynchronous task generator (e.g., `aiohttp`), ensuring concurrent audits don't hit network or memory execution bottlenecks.
