"""
OmniIntel AI - Backend Server & API Engine
HackNext '26 Series 2.0 - Problem Statement PS01 (Smart Automation)
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

PORT = 8000

class OmniIntelHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._set_headers(200)
            response = {
                "status": "online",
                "system": "OmniIntel AI Core",
                "engine": "Cognitive Graph Fusion (CGF) v2.0",
                "pillars_active": 4
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        elif parsed.path == "/api/analyze":
            self._set_headers(200)
            data = {
                "status": "success",
                "ingested_sources": [
                    {"name": "Vendor_Contract_V2.pdf", "type": "PDF", "status": "Parsed"},
                    {"name": "Q3_Invoice_Sept.xlsx", "type": "Tabular", "status": "Parsed"},
                    {"name": "Scope_Approval_Thread.eml", "type": "Email", "status": "Parsed"}
                ],
                "cognitive_graph_nodes": 14,
                "contradiction_alerts": [
                    {
                        "id": "c1",
                        "title": "Financial Mismatch ($2,500 Over-Billed)",
                        "severity": "CRITICAL",
                        "source_a": "Vendor_Contract_V2.pdf (Clause 4.1)",
                        "source_b": "Q3_Invoice_Sept.xlsx (Row #14)",
                        "details": "Contract sets budget cap at $10,000 USD, but Invoice billed $12,500 USD."
                    },
                    {
                        "id": "c2",
                        "title": "Delivery Timeline Conflict",
                        "severity": "MEDIUM",
                        "source_a": "Vendor_Contract_V2.pdf",
                        "source_b": "Scope_Approval_Thread.eml",
                        "details": "Email thread requests extension to Oct 15, while contract states Oct 01."
                    }
                ],
                "action_synthesizer": [
                    {"type": "EMAIL", "title": "Vendor Discrepancy Notice Draft"},
                    {"type": "REPORT", "title": "Executive Audit Memo PDF"},
                    {"type": "TASKS", "title": "Ops Verification Checklist"}
                ]
            }
            self.wfile.write(json.dumps(data).encode('utf-8'))
    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b''

        if parsed.path == "/api/upload":
            try:
                payload = json.loads(post_data.decode('utf-8')) if post_data else {}
                filename = payload.get("filename", "document.txt")
                file_type = payload.get("file_type", "UNKNOWN")
                file_size = payload.get("file_size", "0 KB")
                
                # Format parser assignment
                ext = filename.split('.')[-1].upper() if '.' in filename else 'TXT'
                engine_map = {
                    "PDF": "PyMuPDF Hybrid Parser",
                    "XLSX": "Tabular Transformer Engine",
                    "XLS": "Tabular Transformer Engine",
                    "CSV": "Structured Data Ingester",
                    "EML": "Email MIME Parser",
                    "MSG": "Email MIME Parser",
                    "DOCX": "Word Structural Parser",
                    "DOC": "Word Structural Parser",
                    "TXT": "Plaintext Clause Tokenizer",
                    "JSON": "JSON Schema Synthesizer",
                    "PNG": "Vision OCR Engine",
                    "JPG": "Vision OCR Engine",
                    "JPEG": "Vision OCR Engine"
                }
                engine = engine_map.get(ext, "Universal Document Reader")

                self._set_headers(200)
                response = {
                    "status": "success",
                    "message": f"Successfully ingested {filename}",
                    "file": {
                        "name": filename,
                        "ext": ext,
                        "size": file_size,
                        "engine": engine,
                        "status": "Parsed & Indexed"
                    }
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
        elif parsed.path == "/api/analyze":
            self.do_GET()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode('utf-8'))

def run_server():
    server = HTTPServer(('0.0.0.0', PORT), OmniIntelHandler)
    print(f"OmniIntel AI Backend API running on http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")

if __name__ == '__main__':
    run_server()
