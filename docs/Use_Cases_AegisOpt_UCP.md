# Use Cases for AegisOpt (with UCP Calculation)
**Version 1.1**  
**Prepared by:** Jayachandra Nelauturi (24CSB0B49), Nikhitha Kandasamy (24CSB0B50), Palchami Rithwik (24CSB0B52)  
**Date:** January 29, 2026 (Updated for UCP Assignment)

---

## 1. REVISION HISTORY

| Name | Date | Reason for Changes | Version |
|------|------|-------------------|---------|
| Nikhitha, JayaChandra, Rithwik | 29/01/2026 | Initial Draft created | 1.0 |
| Nikhitha, JayaChandra, Rithwik | 05/03/2026 | Added use cases 16–20; UCP calculation section | 1.1 |

---

## 2. Primary Actors and Use Cases

| Primary Actor | Use Cases |
|---------------|-----------|
| **Software Developer** | 1. Optimize Code Performance, 2. Analyze Code Metrics, 3. Generate Optimization Report, 4. Configure Optimization Rules, 5. Compare Optimization Results, **16. View Optimization History**, **17. Export Report (PDF/JSON)** |
| **System Administrator** | 6. Deploy Optimization Framework, 7. Monitor System Performance, 8. Configure Build Environment, **18. Run Baseline Benchmark** |
| **Research Engineer** | 9. Test Optimization Algorithms, 10. Analyze Feature Extraction, 11. Validate Optimization Quality, 12. Generate Research Reports, **19. Manage Agent Configuration** |
| **Domain Specialist (Fintech)** | 13. Apply Domain-Specific Optimizations, 14. Validate Domain Requirements, 15. Generate Domain-Specific Reports, **20. Rollback to Previous Optimization** |

---

## 3. New Use Cases Added (for UCP)

### Use Case ID: 16 — View Optimization History
| Field | Details |
|-------|---------|
| **Use Case Name** | View Optimization History |
| **Actors** | Software Developer |
| **Description** | Developer views a chronological list of past optimization runs, with key metrics and applied strategies. |
| **Preconditions** | User logged in; at least one optimization run exists. |
| **Postconditions** | History list displayed; user can drill down into any run. |
| **Normal Flow** | 1. Open dashboard. 2. Navigate to History. 3. View list with filters. |
| **Complexity** | **Simple** (1–3 transactions) |

### Use Case ID: 17 — Export Report (PDF/JSON)
| Field | Details |
|-------|---------|
| **Use Case Name** | Export Report (PDF/JSON) |
| **Actors** | Software Developer |
| **Description** | Export optimization or metrics report in PDF or JSON format for sharing or tooling. |
| **Preconditions** | A report has been generated. |
| **Postconditions** | File downloaded in selected format. |
| **Normal Flow** | 1. Open report. 2. Select Export. 3. Choose format (PDF/JSON). 4. Set options. 5. Download file. |
| **Complexity** | **Average** (4–7 transactions) |

### Use Case ID: 18 — Run Baseline Benchmark
| Field | Details |
|-------|---------|
| **Use Case Name** | Run Baseline Benchmark |
| **Actors** | System Administrator |
| **Description** | Execute baseline (e.g. -O3) compilation and run to establish performance baseline. |
| **Preconditions** | Build environment configured; source available. |
| **Postconditions** | Baseline metrics recorded; available for comparison. |
| **Normal Flow** | 1. Select source/project. 2. Choose baseline profile. 3. Run compile. 4. Execute benchmark. 5. Record metrics. 6. Store in knowledge base. |
| **Complexity** | **Average** (4–7 transactions) |

### Use Case ID: 19 — Manage Agent Configuration
| Field | Details |
|-------|---------|
| **Use Case Name** | Manage Agent Configuration |
| **Actors** | Research Engineer |
| **Description** | Configure and tune AI agents (e.g. RL agent, LLM strategist, pass ordering) and their parameters. |
| **Preconditions** | Admin/research access; agents deployed. |
| **Postconditions** | Agent settings updated; behavior reflected in next run. |
| **Normal Flow** | 1. Open agent settings. 2. Select agent (Performance/Size/Security). 3. Adjust parameters. 4. Set constraints. 5. Validate config. 6. Save. 7. Run smoke test. 8. Confirm. |
| **Complexity** | **Complex** (8+ transactions) |

### Use Case ID: 20 — Rollback to Previous Optimization
| Field | Details |
|-------|---------|
| **Use Case Name** | Rollback to Previous Optimization |
| **Actors** | Domain Specialist |
| **Description** | Revert to a previously applied optimization version when current results are unsatisfactory. |
| **Preconditions** | Optimization history available; previous version exists. |
| **Postconditions** | Code/build reverted; metrics updated. |
| **Normal Flow** | 1. Open optimization history. 2. Select target version. 3. Confirm rollback. 4. Restore artifacts. 5. Re-run verification. |
| **Complexity** | **Average** (4–7 transactions) |

---

## 4. UCP Classification of Use Cases and Actors

### 4.1 Use Case Classification (for Unadjusted Use Case Weight)

| Use Case Classification | Type / Description | Weight |
|--------------------------|-------------------|--------|
| **Simple** | Use cases with 1–3 transactions in the main flow | 5 |
| **Average** | Use cases with 4–7 transactions in the main flow | 10 |
| **Complex** | Use cases with 8 or more transactions in the main flow | 15 |

### 4.2 Use Case Count for AegisOpt (20 use cases)

| Complexity | Use Cases | Count | Weight | Contribution |
|------------|-----------|-------|--------|--------------|
| **Simple** | 5, 15, **16** | 3 | 5 | 15 |
| **Average** | 3, 4, 7, 8, 10, 11, 12, 14, **17**, **18**, **20** | 11 | 10 | 110 |
| **Complex** | 1, 2, 6, 9, 13, **19** | 6 | 15 | 90 |

### 4.3 Actor Classification (for Unadjusted Actor Weight)

| Actor Classification | Type of Actor | Weight |
|----------------------|---------------|--------|
| **Simple** | External system that must interact with the system using a well-defined API | 1 |
| **Average** | External system that must interact with the system using standard communication protocols (e.g., TCP/IP, FTP, HTTP, database) | 2 |
| **Complex** | Human actor using a GUI application interface | 3 |

### 4.4 Actor Count for AegisOpt

| Actor | Classification | Reason | Count | Weight | Contribution |
|-------|----------------|--------|-------|--------|--------------|
| Software Developer | Complex | Human using GUI/CLI | 1 | 3 | 3 |
| System Administrator | Complex | Human using GUI/CLI | 1 | 3 | 3 |
| Research Engineer | Complex | Human using GUI/CLI | 1 | 3 | 3 |
| Domain Specialist | Complex | Human using GUI/CLI | 1 | 3 | 3 |

*Per the slide: “Human actor using a GUI application interface” = Complex (weight 3). So for AegisOpt all four primary actors are Complex.*

- **Simple actors:** 0  
- **Average actors:** 0  
- **Complex actors:** 4  
- **UAW = (0×1) + (0×2) + (4×3) = 12**

---

## 5. UCP Calculation for AegisOpt

### 5.1 Unadjusted Use Case Weight (UUCW)

**Use Case Classification (reference):**

| Use Case Classification | Type / Description | Weight |
|--------------------------|-------------------|--------|
| Simple | 1–3 transactions in main flow | 5 |
| Average | 4–7 transactions in main flow | 10 |
| Complex | 8 or more transactions in main flow | 15 |

**Formula:** UUCW = (Total No. of Simple use cases × 5) + (Total No. of Average use cases × 10) + (Total No. of Complex use cases × 15)

- UUCW = (3 × 5) + (11 × 10) + (6 × 15) = **15 + 110 + 90 = 215**

### 5.2 Unadjusted Actor Weight (UAW)

**Actor Classification (reference):**

| Actor Classification | Type of Actor | Weight |
|----------------------|---------------|--------|
| Simple | External system that must interact with the system using a well-defined API | 1 |
| Average | External system that must interact using standard communication protocols (e.g., TCP/IP, FTP, HTTP, database) | 2 |
| Complex | Human actor using a GUI application interface | 3 |

**Formula:** UAW = (Total No. of Simple actors × 1) + (Total No. of Average actors × 2) + (Total No. of Complex actors × 3)

- For AegisOpt: 0 Simple, 0 Average, 4 Complex (all human users with GUI).
- UAW = (0 × 1) + (0 × 2) + (4 × 3) = **12**

### 5.3 Technical Complexity Factor (TCF)

**Technical factors (each factor rated 0–5; TF = sum of (rating × weight)):**

| Factor | Description | Weight |
|--------|-------------|--------|
| T1 | Distributed system | 2.0 |
| T2 | Response time/performance objectives | 1.0 |
| T3 | End-user efficiency | 1.0 |
| T4 | Internal processing complexity | 1.0 |
| T5 | Code reusability | 1.0 |
| T6 | Easy to install | 0.5 |
| T7 | Easy to use | 0.5 |
| T8 | Portability to other platforms | 2.0 |
| T9 | System maintenance | 1.0 |
| T10 | Concurrent/parallel processing | 1.0 |
| T11 | Security features | 1.0 |
| T12 | Access for third parties | 1.0 |
| T13 | End user training | 1.0 |

**Formula:** TCF = 0.6 + (TF / 100)

- For AegisOpt, assumed total **TF = 48** (e.g. distributed, performance, internal complexity, reuse, concurrency, security relevant).
- TCF = 0.6 + (48 / 100) = **1.08**

### 5.4 Environmental Complexity Factor (ECF)

**Environmental factors (each factor rated 0–5; EF = sum of (rating × weight)):**

| Factor | Description | Weight |
|--------|-------------|--------|
| E1 | Familiarity with development process used | 1.5 |
| E2 | Application experience | 0.5 |
| E3 | Object-oriented experience of team | 1.0 |
| E4 | Lead analyst capability | 0.5 |
| E5 | Motivation of the team | 1.0 |
| E6 | Stability of requirements | 2.0 |
| E7 | Part-time staff | -1.0 |
| E8 | Difficult programming language | -1.0 |

**Formula:** ECF = 1.4 + (−0.03 × EF)

- For AegisOpt, assumed **EF = 22** (e.g. experienced team, stable requirements).
- ECF = 1.4 − (0.03 × 22) = 1.4 − 0.66 = **0.74**

### 5.5 Use Case Points (UCP)
**Formula:** UCP = (UUCW + UAW) × TCF × ECF

- UCP = (215 + 12) × 1.08 × 0.74 = **227 × 1.08 × 0.74 ≈ 181.42**

**UCP for AegisOpt: 181.42** (rounded to 181 if integer required).

### 5.6 Estimated Effort (optional)
If **20 person-hours per UCP** is used:
- **Estimated Effort = 181.42 × 20 ≈ 3,628 person-hours** (approx.).

---

## 6. Summary Statistics (Updated)

- **Total Use Cases:** 20 (15 original + 5 new)
- **Primary Actors:** 4 (all Complex — human with GUI)
- **Detailed Use Cases:** 6 | Brief/New: 14
- **UCP (AegisOpt):** 181.42
- **Use Case Weights:** Simple 3, Average 11, Complex 6 → UUCW = 215
- **Actor Weights:** Complex 4 → UAW = 12

---

*This document extends the original AegisOpt use case document with additional use cases (16–20) and the Use Case Points (UCP) calculation for the system.*
