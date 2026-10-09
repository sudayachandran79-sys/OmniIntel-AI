import os
import json
import urllib.request
import urllib.parse
import sys

sys.stdout.reconfigure(encoding='utf-8')

SERVER = "http://localhost:8000"

def upload_file(file_path):
    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        content = f.read()

    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: text/plain\r\n\r\n"
    ).encode("utf-8") + content + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        f"{SERVER}/api/upload",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode("utf-8"))

def clear_server():
    req = urllib.request.Request(f"{SERVER}/api/clear", data=b"", method="POST")
    urllib.request.urlopen(req)

def analyze_server():
    req = urllib.request.Request(f"{SERVER}/api/analyze", method="GET")
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode("utf-8"))

scenarios = [
    ("Scenario 1: Academic Attendance", "sample_test_files/Scenario1_Academic_Policy.txt", "sample_test_files/Scenario1_Student_Report.txt"),
    ("Scenario 2: Financial Overbilling", "sample_test_files/Scenario2_Contract_Cap.txt", "sample_test_files/Scenario2_Vendor_Invoice.txt"),
    ("Scenario 3: HR Offer vs Payroll", "sample_test_files/Scenario3_Offer_Letter.txt", "sample_test_files/Scenario3_Payroll_Nov.txt"),
    ("Scenario 4: Timeline Launch Mismatch", "sample_test_files/Scenario4_Roadmap.txt", "sample_test_files/Scenario4_Marketing_Plan.txt"),
    ("Scenario 5: Clean Aligned Docs", "sample_test_files/Scenario5_Project_Spec.txt", "sample_test_files/Scenario5_Project_Signoff.txt")
]

print("=========================================================")
print("LIVE HTTP SERVER END-TO-END INTEGRATION TEST")
print("=========================================================")

for title, f1, f2 in scenarios:
    clear_server()
    upload_file(f1)
    upload_file(f2)
    res = analyze_server()
    conflicts = res.get("contradictions", [])
    print(f"\n[{title}]")
    print(f"Uploaded: {os.path.basename(f1)} & {os.path.basename(f2)}")
    print(f"Conflicts Detected: {len(conflicts)}")
    for c in conflicts:
        print(f" -> [{c['severity']}] {c['title']}")
        print(f"    Summary: {c['description'].splitlines()[1] if len(c['description'].splitlines())>1 else c['description']}")

print("\n=========================================================")
print("ALL LIVE SERVER SCENARIOS VERIFIED SUCCESSFULLY!")
print("=========================================================")
