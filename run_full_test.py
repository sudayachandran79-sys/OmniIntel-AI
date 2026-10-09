import sys
import json
import io
from pprint import pprint

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('backend')
from main import MultiEnginePipeline

def test_scenario(title, doc1_name, doc1_text, doc2_name, doc2_text):
    print(f"\n=======================================================")
    print(f"TESTING: {title}")
    print(f"=======================================================")
    engine = MultiEnginePipeline()
    engine.ingest_document(doc1_name, "TXT", doc1_text)
    engine.ingest_document(doc2_name, "TXT", doc2_text)
    
    res = engine.analyze_cross_source()
    conflicts = res.get("contradictions", [])
    print(f"Total Conflicts Detected: {len(conflicts)}")
    for i, c in enumerate(conflicts):
        print(f"\n--- Conflict {i+1}: {c['title']} ({c['severity']}) ---")
        print(c['description'])
    return res

# 1. Academic Attendance Scenario
doc1_acad = "ACADEMIC REGULATION: Minimum attendance requirement for all registered students to sit for semester final examinations is 75%."
doc2_acad = "STUDENT REPORT: Overall student attendance recorded for Rahul Sharma in current semester is 60%."
test_scenario("Academic & Attendance Requirement", "Academic_Policy.txt", doc1_acad, "Student_Report.txt", doc2_acad)

# 2. Financial Budget Scenario
doc1_fin = "SERVICE CONTRACT: Maximum total budget cap allocated for Phase 1 implementation is $10,000."
doc2_fin = "VENDOR INVOICE: Phase 1 Migration Service Fee billed total amount due is $12,500."
test_scenario("Financial Overbilling", "Contract_Cap.txt", doc1_fin, "Vendor_Invoice.txt", doc2_fin)

# 3. HR Offer vs Payroll Scenario
doc1_hr = "EXECUTIVE OFFER LETTER: Approved annual base salary offered for Priya Venkatesh is $85,000. Joining date: November 01, 2026."
doc2_hr = "PAYROLL DISBURSEMENT: Employee Priya Venkatesh annual base salary processed in payroll is $95,000. Joining date: November 01, 2026."
test_scenario("HR Offer vs Payroll", "Offer_Letter.pdf", doc1_hr, "Payroll_Nov.xlsx", doc2_hr)

# 4. Timeline Launch Scenario
doc1_time = "PRODUCT ROADMAP: Production deployment and global launch date strictly scheduled for October 15, 2026."
doc2_time = "MARKETING PLAN: Press release and public marketing launch scheduled for October 25, 2026."
test_scenario("Timeline Launch Date Mismatch", "Roadmap.txt", doc1_time, "Marketing_Plan.txt", doc2_time)

# 5. Clean Aligned Scenario
doc1_clean = "PROJECT SPEC: Target completion date is November 30, 2026. Approved budget is $50,000."
doc2_clean = "PROJECT SIGNOFF: Project delivered on November 30, 2026. Total expenditure incurred is $50,000."
test_scenario("Clean Aligned Documents (0 Conflicts)", "Project_Spec.txt", doc1_clean, "Project_Signoff.txt", doc2_clean)
