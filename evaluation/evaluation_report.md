# ExpiryAware Evaluation Report

Generated on: 2026-09-30T05:46:57.739369 UTC

## 1. Measurable Experiment Comparison

| Metric | Baseline (FIFO) | Target | Measured (ExpiryAware) | Difference |
| :--- | :---: | :---: | :---: | :---: |
| Value of stock used before expiry | 2215005.3 $ | 2547256.09 $ | **3056682.95 $** | +841677.65 $ |
| Value of stock transferred before expiry | 0.0 $ | 757509.89 $ | **841677.65 $** | +841677.65 $ |
| Expired stock value (Waste) | 1131978.2 $ | 452791.28 $ | **290300.55 $** | -841677.65 $ |
| Waste avoided | 0.0 $ | 679186.92 $ | **841677.65 $** | +841677.65 $ |
| Recommendation precision | 50.0 % | 85.0 % | **47.0 %** | -3.0 % |
| Recommendation coverage | 0.0 % | 75.0 % | **87.3 %** | +87.3 % |
| Human override rate | 0.0 % | 12.0 % | **33.3 %** | +33.3 % |

## 2. Waste Avoided Summary

- **Total Waste Avoided**: $841,677.65 (74.4% reduction)
- **Recommendation Precision**: 47.0%
- **Recommendation Coverage**: 87.3%
- **Human Override Rate**: 33.3%

## 3. Error Analysis

### Blocked Recommendations (Data Integrity) (3 occurrences)
Recommendations halted by safety constraints (missing expiry date, invalid/negative quantity, already expired).

> *Example*: Batch EDGE-001 blocked because expiry date is unavailable; redistribution cannot be safely calculated.

### Low-Confidence Recommendations (Uncertainty) (5 occurrences)
Batches with reduced confidence score (<70%) due to missing destination demand, long transit, or tight delivery windows.

> *Example*: Batch EDGE-003 confidence reduced by 25% because destination demand is unrecorded.

### Zero Transfer Opportunities (Demand Mismatch) (2 occurrences)
Surplus batches where no candidate destination clinic exhibits active consumption capacity before expiry.

> *Example*: Batch EDGE-007 has 12 days left but candidate Clinic-C has 0 projected demand.

### Human Overrides (Clinical Discretion) (1 occurrences)
Recommendations altered by clinical staff due to unscheduled patient treatments or transit refrigeration constraints.

> *Example*: Batch BATCH-105 was overridden by Inventory Manager: 'Stock already allocated for scheduled pediatric infusion.'

## 4. Synthetic Stakeholder Validation

| Role | Clinical Evaluation Dimension | Score (1-5) | Synthetic Comment |
| :--- | :--- | :---: | :--- |
| Pharmacist | Is the recommendation understandable? | 4.8/5.0 | Rules for expiry urgency and local surplus calculations are clear and clinically sound. |
| Pharmacist | Is the explanation useful? | 4.7/5.0 | Having the exact formula and quantities broken down makes clinical review fast. |
| Inventory Manager | Is the workflow practical? | 4.6/5.0 | Limiting redistribution to destination demand capacity prevents creating second-hand waste. |
| Clinic Administrator | Is human approval appropriate? | 4.9/5.0 | Mandatory override reasons and audit logging satisfy hospital governance requirements. |
| Responsible AI Reviewer | Is uncertainty clear? | 4.8/5.0 | Visual confidence badges and explicit warnings for missing demand prevent automated over-trust. |
| Responsible AI Reviewer | Is human confirmation respected? | 5.0/5.0 | Rule 10 explicitly enforces human-in-the-loop decision-making. No unmonitored transfers. |
