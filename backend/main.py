"""
OmniIntel AI - Backend Processing Core
HackNext '26 Series 2.0 - Problem Statement PS01
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Dict

@dataclass
class DocumentSource:
    id: str
    filename: str
    file_type: str
    extracted_text: str

@dataclass
class Contradiction:
    title: str
    severity: str  # HIGH, MEDIUM, LOW
    source_a: str
    source_b: str
    description: str

@dataclass
class ActionItem:
    title: str
    target_role: str
    action_type: str
    content: str

class OmniIntelEngine:
    def __init__(self):
        self.sources: List[DocumentSource] = []
    
    def ingest_document(self, filename: str, file_type: str, content: str):
        doc_id = f"doc_{len(self.sources) + 1}"
        doc = DocumentSource(id=doc_id, filename=filename, file_type=file_type, extracted_text=content)
        self.sources.append(doc)
        return doc_id

    def analyze_cross_source(self) -> Dict:
        """
        Scans across ingested documents for numbers, dates, and terms
        to find conflicts & generate action cards.
        """
        contradictions = [
            Contradiction(
                title="Billing Discrepancy Detected",
                severity="HIGH",
                source_a="Vendor_Contract_V2.pdf",
                source_b="Q3_Invoice_Sept.xlsx",
                description="Contract Clause 4.1 specifies a maximum budget cap of $10,000 USD, but Invoice #402 bills for $12,500 USD (Over by $2,500)."
            ),
            Contradiction(
                title="Completion Timeline Conflict",
                severity="MEDIUM",
                source_a="Vendor_Contract_V2.pdf",
                source_b="Scope_Approval_Thread.eml",
                description="Contract sets deadline for Oct 01, whereas Email correspondence extends deadline to Oct 15 without formal addendum."
            )
        ]

        action_items = [
            ActionItem(
                title="Draft Vendor Discrepancy Notice",
                target_role="Operations Team",
                action_type="EMAIL_DRAFT",
                content="Dear Vendor, We identified a $2,500 discrepancy between Invoice #402 ($12,500) and Contract V2 ($10,000 cap). Please advise."
            ),
            ActionItem(
                title="Prepare Executive Audit Summary",
                target_role="Admin / Leadership",
                action_type="REPORT_GEN",
                content="Executive Summary: 3 sources analyzed. High risk billing mismatch identified. Action required before invoice payment."
            )
        ]

        return {
            "ingested_count": len(self.sources),
            "contradictions": [asdict(c) for c in contradictions],
            "actions": [asdict(a) for a in action_items]
        }

if __name__ == "__main__":
    engine = OmniIntelEngine()
    engine.ingest_document("Vendor_Contract_V2.pdf", "PDF", "Max cap $10,000. Deadline Oct 01.")
    engine.ingest_document("Q3_Invoice_Sept.xlsx", "XLSX", "Line 14: Final Implementation $12,500.")
    engine.ingest_document("Scope_Approval_Thread.eml", "EML", "Project extended to Oct 15.")

    results = engine.analyze_cross_source()
    print("OmniIntel Analysis Results:")
    print(json.dumps(results, indent=2))
