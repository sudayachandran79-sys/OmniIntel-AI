import os
import io
import fitz  # PyMuPDF

os.makedirs("multiformat_test_files", exist_ok=True)

# -------------------------------------------------------------
# PACKAGE 1: FINANCIAL OVERBILLING (PDF + EML + TXT)
# -------------------------------------------------------------

# 1. Purchase_Order_Cap.pdf (REAL PDF)
doc1 = fitz.open()
page1 = doc1.new_page(width=595, height=842)
pdf_text_1 = """CORPORATE PURCHASE ORDER #PO-2026-9041
Company: Enterprise Systems Corp
Vendor Name: TechGlobal Solutions Inc.
Order Date: October 01, 2026

APPROVED SERVICE TERMS:
1. Maximum Approved Budget Cap for Phase 1 Implementation: $15,000
2. Agreed Delivery Deadline: November 15, 2026
3. Payment Terms: Net 30 Days

Authorized Signature: Procurement Director"""
page1.insert_text((50, 60), pdf_text_1, fontsize=11)
doc1.save("multiformat_test_files/Purchase_Order_Cap.pdf")
doc1.close()

# 2. Vendor_Invoice_Email.eml (EMAIL MIME)
eml_content_1 = """From: Billing Dept <billing@techglobalsolutions.com>
To: Accounts Payable <ap@enterprise.com>
Subject: INVOICE #INV-8831 Billed Amount - Phase 1 Deliverables
Date: Mon, 01 Nov 2026 10:00:00 +0530

Dear Enterprise Finance Team,

Please find billed the final total invoice amount due of $22,500 for the completed Phase 1 implementation.

Invoice Summary:
- Service Billed: Phase 1 Cloud Migration & Integration
- Total Amount Due: $22,500
- Due Date: November 15, 2026

Please process payment within 15 days.

Thank you,
TechGlobal Solutions Billing Team"""
with open("multiformat_test_files/Vendor_Invoice_Email.eml", "w", encoding="utf-8") as f:
    f.write(eml_content_1)

# 3. Audit_Policy_Terms.txt (TXT)
txt_content_1 = """FINANCIAL AUDIT REGULATION 2026
Clause 7.1: All vendor invoices exceeding approved Purchase Order budget caps by more than $1,000 must be flagged for Critical Overbilling Audit.
Target Completion Deadline: November 15, 2026."""
with open("multiformat_test_files/Audit_Policy_Terms.txt", "w", encoding="utf-8") as f:
    f.write(txt_content_1)


# -------------------------------------------------------------
# PACKAGE 2: ACADEMIC ATTENDANCE AUDIT (PDF + EML + CSV)
# -------------------------------------------------------------

# 1. University_Academic_Policy.pdf (REAL PDF)
doc2 = fitz.open()
page2 = doc2.new_page(width=595, height=842)
pdf_text_2 = """OFFICIAL ACADEMIC REGULATION 2026-2027
University Examination Board

SECTION 4: EXAMINATION ELIGIBILITY CRITERIA
1. Minimum mandatory attendance threshold required for all registered students to sit for semester final examinations is 80%.
2. Students recording overall attendance below 80% shall be automatically disqualified from writing final examinations.

Issued by: Controller of Examinations"""
page2.insert_text((50, 60), pdf_text_2, fontsize=11)
doc2.save("multiformat_test_files/University_Academic_Policy.pdf")
doc2.close()

# 2. Student_Disqualification_Alert.eml (EMAIL MIME)
eml_content_2 = """From: Exam Controller <exams@university.edu>
To: Faculty Board <faculty@university.edu>
Subject: Attendance Record Summary - Student Vikram R
Date: Wed, 05 Oct 2026 14:00:00 +0530

Dear Faculty Members,

Please note the attendance record summary for Vikram R (Reg No: REG-2026-881).
Recorded overall student attendance for the current semester is 65%.

Regards,
Exam Control Office"""
with open("multiformat_test_files/Student_Disqualification_Alert.eml", "w", encoding="utf-8") as f:
    f.write(eml_content_2)

# 3. Student_Attendance_Register.csv (CSV)
csv_content_2 = """Register_No,Student_Name,Attendance_Pct,Exam_Eligible
REG-2026-881,Vikram R,65%,DISQUALIFIED
REG-2026-882,Ananya M,85%,ELIGIBLE
REG-2026-883,Karthik S,90%,ELIGIBLE"""
with open("multiformat_test_files/Student_Attendance_Register.csv", "w", encoding="utf-8") as f:
    f.write(csv_content_2)

print("All multi-format sample files (PDF, EML, CSV, TXT) generated successfully in multiformat_test_files/")
