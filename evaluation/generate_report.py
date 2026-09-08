"""Evaluation Report Generator CLI for ExpiryAware.

Runs the measurable simulation comparing Baseline (FIFO local) vs Proposed (ExpiryAware),
evaluates edge cases, outputs metrics diffs, and saves evaluation_report.json and evaluation_report.md.
"""
import sys
import json
from pathlib import Path
from datetime import datetime

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

from app.database import init_db, SessionLocal
from app.evaluation import run_evaluation_simulation


def generate_cli_report():
    print("=" * 70)
    print("  EXPIRY-AWARE RECOMMENDER: COMPREHENSIVE EVALUATION REPORT")
    print("=" * 70)

    init_db(seed_if_empty=True)
    db = SessionLocal()

    try:
        report = run_evaluation_simulation(db)

        print("\n[1] EXECUTIVE METRIC COMPARISON (BASELINE FIFO vs PROPOSED EXPIRY-AWARE):")
        print("-" * 70)
        print(f"{'Metric':<38} {'Baseline':>10} {'Target':>10} {'Measured':>10} {'Diff':>10}")
        print("-" * 70)
        for row in report["comparison_table"]:
            unit = row["unit"]
            b_str = f"{row['baseline']:.1f}{unit}"
            t_str = f"{row['target']:.1f}{unit}"
            m_str = f"{row['measured']:.1f}{unit}"
            d_str = f"{row['difference']:+.1f}{unit}"
            print(f"{row['metric']:<38} {b_str:>10} {t_str:>10} {m_str:>10} {d_str:>10}")
        print("-" * 70)

        print("\n[2] FINANCIAL & CLINICAL WASTE IMPACT:")
        print(f"  • Total Baseline Expired Waste:   ${report['baseline_summary']['stock_expired_waste']:,.2f}")
        print(f"  • Total Proposed Expired Waste:   ${report['proposed_summary']['stock_expired_waste']:,.2f}")
        print(f"  • Net Waste Avoided (Protected):  ${report['waste_avoided_amount']:,.2f} ({report['waste_avoided_percentage']:.1f}%)")
        print(f"  • Recommendation Precision:       {report['recommendation_precision']:.1f}%")
        print(f"  • Recommendation Coverage:        {report['recommendation_coverage']:.1f}%")
        print(f"  • Human Override Rate:            {report['human_override_rate']:.1f}%")

        print("\n[3] ERROR ANALYSIS & UNCERTAINTY PROFILE:")
        for item in report["error_analysis"]:
            print(f"\n  Category: {item['category']} (Count: {item['count']})")
            print(f"  Description: {item['description']}")
            print(f"  Clinical Case: {item['example']}")

        print("\n[4] SYNTHETIC STAKEHOLDER VALIDATION RATINGS (Likert 1-5):")
        for s in report["stakeholder_validation"]:
            print(f"  [{s['role']}] {s['question']} -> {s['score']}/5.0")
            print(f"    Feedback: \"{s['feedback']}\"")

        # Save to JSON
        eval_dir = BASE_DIR / "evaluation"
        eval_dir.mkdir(parents=True, exist_ok=True)
        json_file = eval_dir / "evaluation_report.json"
        with open(json_file, "w") as f:
            json.dump(report, f, indent=2)

        # Save to Markdown
        md_file = eval_dir / "evaluation_report.md"
        with open(md_file, "w") as f:
            f.write("# ExpiryAware Evaluation Report\n\n")
            f.write(f"Generated on: {datetime.utcnow().isoformat()} UTC\n\n")
            f.write("## 1. Measurable Experiment Comparison\n\n")
            f.write("| Metric | Baseline (FIFO) | Target | Measured (ExpiryAware) | Difference |\n")
            f.write("| :--- | :---: | :---: | :---: | :---: |\n")
            for row in report["comparison_table"]:
                f.write(f"| {row['metric']} | {row['baseline']} {row['unit']} | {row['target']} {row['unit']} | **{row['measured']} {row['unit']}** | {row['difference']:+} {row['unit']} |\n")
            f.write("\n## 2. Waste Avoided Summary\n\n")
            f.write(f"- **Total Waste Avoided**: ${report['waste_avoided_amount']:,.2f} ({report['waste_avoided_percentage']:.1f}% reduction)\n")
            f.write(f"- **Recommendation Precision**: {report['recommendation_precision']:.1f}%\n")
            f.write(f"- **Recommendation Coverage**: {report['recommendation_coverage']:.1f}%\n")
            f.write(f"- **Human Override Rate**: {report['human_override_rate']:.1f}%\n\n")
            f.write("## 3. Error Analysis\n\n")
            for item in report["error_analysis"]:
                f.write(f"### {item['category']} ({item['count']} occurrences)\n")
                f.write(f"{item['description']}\n\n")
                f.write(f"> *Example*: {item['example']}\n\n")
            f.write("## 4. Synthetic Stakeholder Validation\n\n")
            f.write("| Role | Clinical Evaluation Dimension | Score (1-5) | Synthetic Comment |\n")
            f.write("| :--- | :--- | :---: | :--- |\n")
            for s in report["stakeholder_validation"]:
                f.write(f"| {s['role']} | {s['question']} | {s['score']}/5.0 | {s['feedback']} |\n")

        print("\n" + "=" * 70)
        print(f"Report saved to:\n  - {json_file}\n  - {md_file}")
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    generate_cli_report()
