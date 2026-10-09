import os
import fitz  # PyMuPDF

base_dir = "multiformat_test_files"
os.makedirs(base_dir, exist_ok=True)

pkg1_dir = os.path.join(base_dir, "Package1_Corporate_Financial_Overbilling")
pkg2_dir = os.path.join(base_dir, "Package2_University_Exam_Attendance")
pkg3_dir = os.path.join(base_dir, "Package3_SupplyChain_SLA_Mismatch")

os.makedirs(pkg1_dir, exist_ok=True)
os.makedirs(pkg2_dir, exist_ok=True)
os.makedirs(pkg3_dir, exist_ok=True)

# Helper to save files in both package dir and base dir with clear prefix
def save_file(pkg_folder, base_filename, content, is_pdf=False):
    pkg_path = os.path.join(pkg_folder, base_filename)
    root_path = os.path.join(base_dir, base_filename)
    
    if is_pdf:
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        page.insert_text((50, 60), content, fontsize=11)
        doc.save(pkg_path)
        doc.save(root_path)
        doc.close()
    else:
        with open(pkg_path, "w", encoding="utf-8") as f:
            f.write(content)
        with open(root_path, "w", encoding="utf-8") as f:
            f.write(content)

# -------------------------------------------------------------
# PACKAGE 1: FINANCIAL OVERBILLING AUDIT
# -------------------------------------------------------------
po_pdf = """CORPORATE PURCHASE ORDER #PO-2026-9041
Enterprise Systems Corp - Procurement Dept
Date: October 01, 2026

CONTRACTUAL TERMS & BUDGET CAP:
1. Maximum Approved Budget Cap for Phase 1 Implementation: $15,000
2. Agreed Delivery Deadline: November 15, 2026
3. Payment Terms: Net 30 Days

Approved by: Procurement Director"""
save_file(pkg1_dir, "01_Purchase_Order_Cap.pdf", po_pdf, is_pdf=True)

inv_eml = """From: Billing Dept <billing@techglobalsolutions.com>
To: Accounts Payable <ap@enterprise.com>
Subject: INVOICE #INV-8831 Billed Amount - Phase 1 Deliverables
Date: Mon, 01 Nov 2026 10:00:00 +0530

Dear Finance Team,

Please find billed the final total invoice amount due of $22,500 for the completed Phase 1 implementation.

Invoice Summary:
- Service Billed: Phase 1 Cloud Migration & Integration
- Total Amount Billed: $22,500
- Due Date: November 15, 2026

Please process payment within 15 days.

Thank you,
TechGlobal Solutions Billing Team"""
save_file(pkg1_dir, "02_Vendor_Invoice_Email.eml", inv_eml)

policy_txt = """FINANCIAL AUDIT REGULATION 2026
Clause 7.1: All vendor invoices exceeding approved Purchase Order budget caps by more than $1,000 must be flagged for Critical Overbilling Audit.
Target Completion Deadline: November 15, 2026."""
save_file(pkg1_dir, "03_Audit_Policy_Terms.txt", policy_txt)

ledger_csv = """Item_ID,Description,Approved_Cap,Billed_Amount,Variance
ITEM-101,Phase 1 Cloud Migration,$15000,$22500,+$7500 OVERBILLING
ITEM-102,Database Indexing,$5000,$5000,$0 MATCH"""
save_file(pkg1_dir, "04_Financial_Ledger_Data.csv", ledger_csv)


# -------------------------------------------------------------
# PACKAGE 2: UNIVERSITY ACADEMIC ATTENDANCE AUDIT
# -------------------------------------------------------------
academic_pdf = """OFFICIAL ACADEMIC REGULATION 2026-2027
University Examination Board

SECTION 4: EXAMINATION ELIGIBILITY CRITERIA
1. Minimum mandatory attendance threshold required for all registered students to sit for semester final examinations is 80%.
2. Students recording overall attendance below 80% shall be automatically disqualified from writing final examinations.

Issued by: Controller of Examinations"""
save_file(pkg2_dir, "01_Academic_Policy.pdf", academic_pdf, is_pdf=True)

disq_eml = """From: Exam Controller <exams@university.edu>
To: Faculty Board <faculty@university.edu>
Subject: Attendance Record Summary - Student Vikram R
Date: Wed, 05 Oct 2026 14:00:00 +0530

Dear Faculty Members,

Please note the attendance record summary for Vikram R (Reg No: REG-2026-881).
Recorded overall student attendance for the current semester is 65%.

Regards,
Exam Control Office"""
save_file(pkg2_dir, "02_Disqualification_Alert.eml", disq_eml)

attendance_csv = """Register_No,Student_Name,Attendance_Pct,Exam_Eligible
REG-2026-881,Vikram R,65%,DISQUALIFIED
REG-2026-882,Ananya M,85%,ELIGIBLE
REG-2026-883,Karthik S,90%,ELIGIBLE"""
save_file(pkg2_dir, "03_Attendance_Register.csv", attendance_csv)

faculty_txt = """FACULTY AUDIT NOTE 2026
Student REG-2026-881 Vikram R requested exam hall ticket.
Current Attendance: 65%. Mandatory Requirement: 80%. Status: Disqualified."""
save_file(pkg2_dir, "04_Faculty_Audit_Memo.txt", faculty_txt)


# -------------------------------------------------------------
# PACKAGE 3: SUPPLY CHAIN SLA & TIMELINE MISMATCH
# -------------------------------------------------------------
sla_pdf = """GLOBAL SUPPLY CHAIN SERVICE LEVEL AGREEMENT (SLA 2026)
Logistics Operations Division

SECTION 2: DELIVERY TIMELINE MANDATE
1. All Critical Raw Material Shipments (Shipment Batch #LOG-9921) must be delivered to Central Warehouse by October 15, 2026.
2. Delayed deliveries past October 15, 2026 trigger a 5% per day penalty clause."""
save_file(pkg3_dir, "01_SupplyChain_SLA_Agreement.pdf", sla_pdf, is_pdf=True)

dispatch_eml = """From: Carrier Dispatch <dispatch@fastlogistics.com>
To: Operations Lead <ops@manufacturing.com>
Subject: Delivery Notice - Shipment Batch #LOG-9921
Date: Thu, 08 Oct 2026 09:00:00 +0530

Dear Operations Team,

Please be advised that Shipment Batch #LOG-9921 estimated delivery date is October 25, 2026 due to transit customs delays.

Regards,
FastLogistics Dispatch"""
save_file(pkg3_dir, "02_Dispatch_Email_Notice.eml", dispatch_eml)

shipment_csv = """Batch_ID,Item_Description,Mandated_SLA_Date,Actual_Expected_Date,Delay_Days
LOG-9921,Industrial Steel Coils,October 15 2026,October 25 2026,10 Days Delay"""
save_file(pkg3_dir, "03_Shipment_Log_Data.csv", shipment_csv)

sla_txt = """SUPPLY CHAIN DISCREPANCY AUDIT
Shipment #LOG-9921 SLA Delivery Date: October 15, 2026.
Carrier Notification Date: October 25, 2026.
Violation: 10-Day SLA Delay detected."""
save_file(pkg3_dir, "04_SLA_Violation_Memo.txt", sla_txt)

print("ALL MULTI-FORMAT TEST PACKAGES GENERATED SUCCESSFULLY!")
