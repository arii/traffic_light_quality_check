# Reflection — ObserveSign Quality Check
**Ariel Anders** | Takehome Assignment

---

## 1. Approach

- **Visual Problem Exploration:** I started with a web-based visualizer tool to overlay annotations directly onto S3 images (see [results/report_output.html](results/report_output.html) — open in a browser). This helped map constraints visually and identify that the dataset contained a mixture of legacy traffic light tasks and the target Traffic Sign Detection tasks.
- **Scoping Safeguard:** Parameterizing the CLI with `--project-id` isolates the checker to only validate the target *Traffic Sign Detection* tasks, preventing legacy project schemas from contaminating the results.
- **Agentic Orchestration:** I drafted a comprehensive task-specification layout to guide the module boundaries and system architecture, then directed autonomous agent coding tools to implement the helper files and checker modules under my direct supervision.
- **Verification Loop:** Verifying check outputs inside the visualizer exposed key anomalies, such as undetected false-positive empty bounding boxes in night-time images (e.g. task `5f127f699740b80017f9b170`).

## 2. Overview

This tool performs automated, deterministic, per-task quality checks for the ObserveSign Traffic Sign Detection pipeline. All findings map natively to Scale's Fixless Audits schema properties (`type` [error/flag] and `category`), ensuring results can be ingested directly back into Scale's audit feedback loop.

## 3. Quality Checks

### Summary of Check Categories

- **Taxonomy Checks (TAX):** Confirms labels and attributes align with target classes. Downgrades legacy classes to warning flags.
- **Geometry Checks (GEO):** Validates bounding box positioning. Uses **Pillow dimension header-streaming** to fetch true resolution dynamically from image headers, avoiding out-of-bounds false positives without full-image download latency.
- **Overlap Checks (OVL):** Identifies near-duplicate boxes (using Intersection-over-Union thresholds) and nesting containment anomalies.

### Detailed Quality Rules Reference

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

## 4. Per-Task Results (Project `5f124e5671c7b700170a16fb`)

```
Audit complete. Found 28 issues across 8 tasks.
```

| Task ID | Findings | Notable Issues |
| :--- | :--- | :--- |
| `5f127f6f26831d0010e985e5` | 0 | **Clean** |
| `5f127f6c3a6b1000172320ad` | 0 | **Clean** |
| `5f127f699740b80017f9b170` | 0 | **Clean (Visual False Positives Present):** Passed all rules, but visual inspection reveals empty boxes in a pitch-black night scene — undetectable by coordinate-only validators. |
| `5f127f671ab28b001762c204` | 19 | **Severe Overlaps:** 15 `OVL-001` errors (IoU up to 0.98); 4 `OVL-002` containment flags. 6 duplicate annotations stacked on the same stop sign region. **Visual False Negative:** an unlabeled green traffic light is visible in the image and was not caught by any rule. |
| `5f127f643a6b1000172320a5` | 0 | **Clean** |
| `5f127f5f3a6b100017232099` | 2 | **Warnings:** 2 `OVL-002` suspicious containment flags. |
| `5f127f5ab1cb1300109e4ffc` | 0 | **Clean** |
| `5f127f55fdc4150010e37244` | 7 | **Warnings:** 7 `GEO-002` micro box warnings (dimensions < 3px). |

## 5. Performance & Known Limitations

Benchmarked on an Intel Core i5-1035G1 laptop (4 cores, 8 threads, 8GB RAM):

- **8-task scoped run:** ~2.0 seconds total (includes HTTP header-streaming for image dimensions).
- **Per-task average:** ~0.25 seconds, dominated by sequential I/O.

*The workload is strictly I/O-bound. An async thread pool would drive this below 0.05 seconds per task by parallelizing HTTP requests across hardware threads.*

**Known Limitation — Undetected Visual False Positives:** The checker cannot detect visually empty bounding boxes whose coordinates are geometrically valid. Task `5f127f699740b80017f9b170` (a low-light night scene) passed all rules with 0 findings, yet visual inspection confirmed several boxes drawn over pitch-black regions containing no sign content. This class of error requires image-content inspection and is the top future roadmap item.

**Known Limitation — Undetected False Negatives (Missing Annotations):** Coordinate-only validators cannot flag objects that were never labeled. Task `5f127f671ab28b001762c204` — despite being the most problematic task in the set (19 overlap findings) — also contains an unlabeled green traffic light visible in the image. No rule can surface a missing annotation without a reference ground-truth or object-detection model.

## 6. Future Work

1. **CV-Based False Positive Auditing:** Flag empty boxes over night-time shadow regions (as seen in task `5f127f699740b80017f9b170`).
2. **Density Outlier Detection:** Flag images with abnormally high annotation densities to catch spamming or systematic labeling errors.
3. **Cross-Task Consensus:** Use perceptual image hashing to find duplicate frames and flag labeling mismatches.
4. **Active Verification:** Crop annotation bounds to run OCR text verification and dominant color checks.
5. **Async Processing:** Transition task streaming to async generators to handle 250,000 tasks concurrently.
