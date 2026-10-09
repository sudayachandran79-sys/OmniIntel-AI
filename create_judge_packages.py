import os
import fitz  # PyMuPDF

base_dir = os.path.join(os.path.dirname(__file__), "multiformat_test_files")
os.makedirs(base_dir, exist_ok=True)

# ── 1. Create Package_100Percent_ALIGNED_CORRECT ──
aligned_dir = os.path.join(base_dir, "Package_100Percent_ALIGNED_CORRECT")
os.makedirs(aligned_dir, exist_ok=True)

clean_text = "Purchase Order PO-2026-100 is approved for $15,000 with Net 30 payment terms."

# PDF
doc1 = fitz.open()
page1 = doc1.new_page()
page1.insert_text((50, 50), clean_text, fontsize=12)
doc1.save(os.path.join(aligned_dir, "01_Approved_PO_15k.pdf"))
doc1.close()

# EML
eml_content = f"""From: billing@acuityglobal.com
To: accounts@enterprise.com
Subject: Purchase Order PO-2026-100 Approved
Date: Thu, 08 Oct 2026 10:00:00 +0000

{clean_text}
"""
with open(os.path.join(aligned_dir, "02_Vendor_Compliant_Invoice.eml"), "w", encoding="utf-8") as f:
    f.write(eml_content)

# TXT
with open(os.path.join(aligned_dir, "03_Standard_Audit_Policy.txt"), "w", encoding="utf-8") as f:
    f.write(clean_text)

# CSV
csv_content = f"PO_ID,Amount,Terms,Status\nPO-2026-100,15000,Net 30,Approved\n"
with open(os.path.join(aligned_dir, "04_Verified_Financial_Ledger.csv"), "w", encoding="utf-8") as f:
    f.write(csv_content)


# ── 2. Create Package1_Corporate_Financial_Overbilling ──
conflict_dir = os.path.join(base_dir, "Package1_Corporate_Financial_Overbilling")
os.makedirs(conflict_dir, exist_ok=True)

# PDF
doc2 = fitz.open()
page2 = doc2.new_page()
page2.insert_text((50, 50), "CORPORATE PURCHASE ORDER - BUDGET CAP\nPO ID: PO-2026-88\nApproved Budget Cap: $15,000\nPayment Terms: Net 30 Days\nVendor: Nexus Tech Inc\nStatus: CAP APPROVED AT $15,000", fontsize=12)
doc2.save(os.path.join(conflict_dir, "01_Purchase_Order_Cap.pdf"))
doc2.close()

# EML
conflict_eml = """From: billing@nexustech.com
To: accounts@enterprise.com
Subject: Urgent: Invoice INV-2026-99 for Phase 1 Delivery
Date: Thu, 08 Oct 2026 14:00:00 +0000

Dear Accounts,

Please process invoice INV-2026-99 for Phase 1 Software Delivery.
Invoice Amount Billed: $22,500
Payment Terms: Net 15 Days

Note: Invoice amount exceeds PO budget cap by $7,500.
"""
with open(os.path.join(conflict_dir, "02_Vendor_Invoice_Email.eml"), "w", encoding="utf-8") as f:
    f.write(conflict_eml)

# TXT
conflict_txt = """AUDIT COMPLIANCE POLICY & FINANCIAL RULES (CLAUSE 7.1)
Audit Policy Rules:
- PO budget cap approved for Phase 1 is $15,000.
- Any vendor invoice overbilling exceeding $1,000 over the PO cap must be flagged as a Critical Overbilling Audit Discrepancy.
- Payment terms mismatch (Net 15 vs Net 30) violates corporate compliance guidelines.
"""
with open(os.path.join(conflict_dir, "03_Audit_Policy_Terms.txt"), "w", encoding="utf-8") as f:
    f.write(conflict_txt)

# CSV
conflict_csv = """Transaction_ID,Document,Amount,Terms,Status
TX-801,01_Purchase_Order_Cap.pdf,15000,Net 30,CAP_APPROVED
TX-802,02_Vendor_Invoice_Email.eml,22500,Net 15,OVERBILLING_DISCREPANCY
TX-803,03_Audit_Policy_Terms.txt,15000,Net 30,CRITICAL_VIOLATION_TRIGGERED
"""
with open(os.path.join(conflict_dir, "04_Financial_Ledger_Data.csv"), "w", encoding="utf-8") as f:
    f.write(conflict_csv)

print("SUCCESS: Judge test packages generated in multiformat_test_files!")
