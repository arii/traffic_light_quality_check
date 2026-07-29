# ObserveSign Quality Check
**Ariel Anders** | Takehome Assignment

---

### 1. Approach & Scoping Safekeeping
- **Visual Problem Exploration:** I started with a web-based visualizer tool to overlay annotations directly onto S3 images. This helped map constraints visually and identify that the database dump contained a mixture of legacy traffic light tasks, retail/invoice linter data, and current target traffic sign tasks.
- **Scoping Safeguard:** Parameterizing the CLI with `--project-id 5f124e5671c7b700170a16fb` isolates the checker to only validate the 8 target *Traffic Sign Detection* tasks, preventing legacy project schemas from contaminating the results.
- **Agentic Orchestration:** Designed a task-specification layout (`plan.md`) to guide the module boundaries, then leveraged autonomous agent workflows to update and implement the checker files.
- **Verification Loop:** Verifying check outputs inside the visualizer exposed key anomalies, such as undetected false-positive empty bounding boxes in night-time images (e.g. task `5f127f699740b80017f9b170`).

### 2. Overview
This tool performs automated, deterministic, per-task quality checks for the ObserveSign Traffic Sign Detection pipeline. All findings map natively to Scale's Fixless Audits schema properties (`type` [error/flag] and `category`), ensuring results can be ingested directly back into Scale's audit feedback loop.

### 3. Quality Checks (Summary of Categories)
- **Taxonomy Checks (TAX):** Confirms labels and attributes align with target classes. Downgrades legacy classes to warning flags.
- **Geometry Checks (GEO):** Validates bounding box positioning. Uses **Pillow dimension header-streaming** to fetch true resolution dynamically from image headers, avoiding out-of-bounds false positives without full-image download latency.
- **Overlap Checks (OVL):** Identifies near-duplicate boxes (using Intersection-over-Union thresholds) and nesting containment anomalies.

### 4. Future Roadmap (Reflection)
1. **CV-Based False Positive Auditing:** Flag empty boxes drawn over night-time shadow regions (as seen in task `5f127f699740b80017f9b170`).
2. **Density Outlier Detection:** Flag images with abnormally high annotation densities to catch spamming or systematic labeling errors.
3. **Cross-Task Consensus:** Use perceptual image hashing to find duplicate frames and flag labeling mismatches.
4. **Active Verification:** Crop annotation bounds to run OCR text verification and dominant color checks.
5. **Async Processing:** Transition task streaming to async generators to handle 250,000 tasks concurrently.

---

### 5. Detailed Quality Rules Reference Table

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

### 6. Scoped Audit Results (8 Assigned Tasks)

The audit was executed against the **Traffic Sign Detection** project tasks:
- **Summary:** Out of the 8 assigned tasks, **5 tasks were clean** (0 findings), **2 tasks triggered warning flags**, and **1 task contained severe duplicate errors**. 

| Task ID | Findings | Project Source | Notable Issues |
| :--- | :--- | :--- | :--- |
| `5f127f6f26831d0010e985e5` | 0 findings | `Traffic Sign Detection` | **Clean:** Bounding box coordinates and attributes match the target taxonomy. |
| `5f127f6c3a6b1000172320ad` | 0 findings | `Traffic Sign Detection` | **Clean:** Bounding box coordinates and attributes match the target taxonomy. |
| `5f127f699740b80017f9b170` | 0 findings | `Traffic Sign Detection` | **Clean (Visual False Positives Present):** Passed all geometric/taxonomic rules, but visual inspection reveals empty bounding boxes placed in pitch-black areas of the night image. |
| `5f127f671ab28b001762c204` | 19 findings | `Traffic Sign Detection` | **Severe Overlaps:** 15 severe `OVL-001` duplicate annotation errors (IoU > 0.98) on stop signs; 4 `OVL-002` containment flags. Density is due to 6 duplicate annotations overlaid on the same sign region. |
| `5f127f643a6b1000172320a5` | 0 findings | `Traffic Sign Detection` | **Clean:** Bounding box coordinates and attributes match the target taxonomy. |
| `5f127f5f3a6b100017232099` | 2 findings | `Traffic Sign Detection` | **Warnings:** 2 `OVL-002` suspicious containment flags (bounding box nested within another). |
| `5f127f5ab1cb1300109e4ffc` | 0 findings | `Traffic Sign Detection` | **Clean:** Bounding box coordinates and attributes match the target taxonomy. |
| `5f127f55fdc4150010e37244` | 7 findings | `Traffic Sign Detection` | **Warnings:** 7 `GEO-002` micro box warnings (bounding box dimensions are extremely small, under `3.0` pixels). |
