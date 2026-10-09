import sys
sys.path.append('backend')
from main import MultiEnginePipeline, extract_facts

doc1 = "Executive Offer Letter: Annual base salary offered is $85,000. Joining date: November 01, 2026. Employee ID: EMP-8821."
doc2 = "Monthly Payroll Disbursement: Annual base salary processed is $95,000. Joining date: November 01, 2026. Employee ID: EMP-8821."

e = MultiEnginePipeline()
e.ingest_document("Offer_Letter.pdf", "PDF", doc1)
e.ingest_document("Payroll_Oct.xlsx", "XLSX", doc2)

res = e.analyze_cross_source()
import pprint
pprint.pprint(res)
