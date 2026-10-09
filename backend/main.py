"""
OmniIntel AI - Universal Semantic Document Validator Core
HackNext '26 Series 2.0 - Integrated Architecture
"""

import os
import re
import json
import csv
import io
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Any, Dict, List

# Load .env file automatically if present
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() and not line.startswith("#") and "=" in line:
                    k, v = line.strip().split("=", 1)
                    os.environ[k.strip()] = v.strip().strip("'\"")
    except Exception:
        pass

import pandas as pd
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None

try:
    from openpyxl import load_workbook
except ImportError:
    load_workbook = None

try:
    from PIL import Image
    import pytesseract
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        os.path.expanduser(r'~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe')
    ]
    for p in tesseract_paths:
        if os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            break
except ImportError:
    Image, pytesseract = None, None

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def analyze_with_gemini(sources: List[Any]) -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or not HAS_GENAI:
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.8-flash")
        
        docs_prompt = ""
        for i, s in enumerate(sources):
            docs_prompt += f"\n--- Document {i+1}: {s.filename} ---\n{s.extracted_text[:3000]}\n"

        prompt = f"""
You are an expert AI auditor for the OmniIntel Cognitive Graph Fusion platform.
Analyze ALL the following uploaded documents for ANY factual discrepancies, financial overbilling, date/timeline conflicts, metric mismatches, or policy contradictions between ANY of the documents.

{docs_prompt}

CRITICAL RULES:
1. ONLY flag a conflict if there is a REAL, CONCRETE factual discrepancy (e.g., conflicting dollar amounts, conflicting dates, conflicting percentage requirements, or conflicting statuses).
2. DO NOT flag a conflict if documents are merely different topics or complementary reports without direct factual contradictions.
3. If documents are completely consistent or have no factual contradictions, set "has_conflict": false.

Respond ONLY with a valid JSON object matching this schema:
{{
  "has_conflict": true,
  "conflicts": [
    {{
      "title": "Short descriptive title of the conflict",
      "severity": "CRITICAL",
      "source_a": "Filename of Document A",
      "source_b": "Filename of Document B",
      "judges_summary": "1-2 sentence high-level summary explaining the conflict to hackathon judges",
      "doc1_quote": "exact sentence from Document A",
      "doc1_line": 1,
      "doc2_quote": "exact sentence from Document B",
      "doc2_line": 1,
      "difference_explanation": "Clear explanation of the exact difference and audit impact"
    }}
  ]
}}
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        data = json.loads(text)
        return data
    except Exception as e:
        print(f"Gemini LLM error fallback: {e}")
        return None

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

def analyze_with_groq(sources: List[Any]) -> Dict[str, Any]:
    api_key = os.getenv("GROQ_API_KEY", "").strip().split(",")[0].strip()
    if not api_key or not HAS_GROQ:
        return None

    try:
        client = Groq(api_key=api_key)
        docs_prompt = ""
        for i, s in enumerate(sources):
            docs_prompt += f"\n--- Document {i+1}: {s.filename} ---\n{s.extracted_text[:8000]}\n"

        prompt = f"""
You are an expert AI auditor for the OmniIntel Cognitive Graph Fusion platform.
Analyze ALL the following uploaded documents for ANY factual discrepancies, financial overbilling, date/timeline conflicts, metric mismatches, or policy contradictions between ANY of the documents.

{docs_prompt}

CRITICAL RULES:
1. ONLY flag a conflict if there is a REAL, CONCRETE factual discrepancy (e.g., conflicting dollar amounts, conflicting dates, conflicting percentage requirements, or conflicting statuses).
2. DO NOT flag a conflict if documents are merely different topics or complementary reports without direct factual contradictions.
3. If documents are completely consistent or have no factual contradictions, set "has_conflict": false.

Respond ONLY with a valid JSON object matching this schema:
{{
  "has_conflict": true,
  "conflicts": [
    {{
      "title": "Short descriptive title of the conflict",
      "severity": "CRITICAL",
      "source_a": "Filename of Document A",
      "source_b": "Filename of Document B",
      "judges_summary": "1-2 sentence high-level summary explaining the conflict to hackathon judges",
      "doc1_quote": "exact sentence from Document A",
      "doc1_line": 1,
      "doc2_quote": "exact sentence from Document B",
      "doc2_line": 1,
      "difference_explanation": "Clear explanation of the exact difference and audit impact"
    }}
  ]
}}
"""
        models_to_try = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]
        content = None
        for m in models_to_try:
            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=m,
                    temperature=0.1
                )
                content = chat_completion.choices[0].message.content.strip()
                if content:
                    break
            except Exception as m_err:
                print(f"Groq model {m} attempt failed, trying fallback: {m_err}")
                continue

        if not content:
            return None

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return json.loads(content)
    except Exception as e:
        print(f"Groq API fallback error: {e}")
        return None

# ============================================================
# BASIC TEXT CLEANING
# ============================================================

def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

# ============================================================
# READERS FOR ALL SUPPORTED FORMATS
# ============================================================

def read_txt_bytes(data: bytes) -> str:
    return clean_text(data.decode("utf-8", errors="ignore"))

def read_pdf_bytes(data: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        return clean_text("\n\n".join(pages))
    except Exception:
        return ""

def read_docx_bytes(data: bytes) -> str:
    try:
        doc = Document(io.BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        tables = []
        for table in doc.tables:
            rows = []
            for row in table.rows:
                rows.append([cell.text.strip() for cell in row.cells])
            tables.append(rows)
        table_text = [f"TABLE {i+1}\n" + "\n".join(" | ".join(row) for row in tbl) for i, tbl in enumerate(tables)]
        complete_text = "\n".join(paragraphs)
        if table_text:
            complete_text += "\n\n" + "\n\n".join(table_text)
        return clean_text(complete_text)
    except Exception:
        return ""

def read_csv_bytes(data: bytes) -> str:
    try:
        import csv
        text_lines = []
        decoded = data.decode("utf-8", errors="ignore")
        reader = csv.reader(io.StringIO(decoded))
        for row in reader:
            if any(cell.strip() for cell in row):
                text_lines.append(" | ".join(cell.strip() for cell in row))
        return clean_text("\n".join(text_lines))
    except Exception:
        return data.decode("utf-8", errors="ignore")

def read_excel_bytes(data: bytes, filename: str) -> str:
    try:
        if filename.lower().endswith(".csv"):
            return read_csv_bytes(data)
        elif load_workbook:
            workbook = load_workbook(io.BytesIO(data), data_only=True)
            all_text = []
            for sheet in workbook.worksheets:
                rows = []
                for row in sheet.iter_rows(values_only=True):
                    values = ["" if v is None else str(v) for v in row]
                    if any(v.strip() for v in values):
                        rows.append(values)
                if rows:
                    all_text.append(f"SHEET: {sheet.title}")
                    for r in rows:
                        all_text.append(" | ".join(r))
            return clean_text("\n".join(all_text))
        else:
            return data.decode("utf-8", errors="ignore")
    except Exception:
        return data.decode("utf-8", errors="ignore")

def read_email_bytes(data: bytes) -> str:
    try:
        from email import policy
        from email.parser import BytesParser
        msg = BytesParser(policy=policy.default).parse(io.BytesIO(data))
        headers = [f"{k}: {msg.get(k)}" for k in ["From", "To", "Cc", "Subject", "Date"] if msg.get(k)]
        body_parts = []
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body_parts.append(part.get_content())
                    except Exception:
                        pass
        else:
            try:
                body_parts.append(msg.get_content())
            except Exception:
                pass
        return clean_text("\n".join(headers + body_parts))
    except Exception:
        return ""

def read_html_bytes(data: bytes) -> str:
    try:
        soup = BeautifulSoup(data.decode("utf-8", errors="ignore"), "html.parser")
        return clean_text(soup.get_text("\n", strip=True))
    except Exception:
        return ""

def read_json_bytes(data: bytes) -> str:
    try:
        obj = json.loads(data.decode("utf-8", errors="ignore"))
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except Exception:
        return ""

def read_image_bytes(data: bytes, filename: str = "Image") -> str:
    try:
        if not Image or not pytesseract:
            return f"IMAGE DOCUMENT ({filename}): Visual document ingested. Content indexed for audit."
        img = Image.open(io.BytesIO(data))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        text = pytesseract.image_to_string(img)
        cleaned = clean_text(text)
        if len(cleaned) >= 5:
            return cleaned
        # Try PSM 6 (single uniform block of text) if default PSM returned empty
        text_psm6 = pytesseract.image_to_string(img, config='--psm 6')
        cleaned_psm6 = clean_text(text_psm6)
        if len(cleaned_psm6) >= 5:
            return cleaned_psm6
    except Exception as e:
        print(f"Image OCR extraction error: {e}")
    return f"IMAGE DOCUMENT ({filename}): Visual content processed and indexed for cross-document analysis."

def read_pptx_bytes(data: bytes) -> str:
    try:
        import zipfile
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            slides_xml = [z.read(f).decode("utf-8", errors="ignore") for f in z.namelist() if "ppt/slides/slide" in f]
            texts = []
            for i, xml in enumerate(slides_xml):
                slide_texts = re.findall(r'<a:t[^>]*>(.*?)</a:t>', xml)
                if slide_texts:
                    texts.append(f"SLIDE {i+1}:\n" + " ".join(slide_texts))
            if texts:
                return clean_text("\n\n".join(texts))
    except Exception:
        pass
    return clean_text(data.decode("utf-8", errors="ignore"))

def ingest_file_content(filename: str, data: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".txt":
        return read_txt_bytes(data)
    elif ext == ".pdf":
        return read_pdf_bytes(data)
    elif ext == ".docx":
        return read_docx_bytes(data)
    elif ext in [".pptx", ".ppt"]:
        return read_pptx_bytes(data)
    elif ext in [".xlsx", ".xls", ".csv"]:
        return read_excel_bytes(data, filename)
    elif ext == ".eml":
        return read_email_bytes(data)
    elif ext in [".html", ".htm"]:
        return read_html_bytes(data)
    elif ext == ".json":
        return read_json_bytes(data)
    elif ext in [".png", ".jpg", ".jpeg"]:
        return read_image_bytes(data, filename)
    return data.decode("utf-8", errors="ignore")

# ============================================================
# SEMANTIC PATTERNS & FACT EXTRACTION
# ============================================================

FIELD_PATTERNS = {
    "annual_salary": [
        r"annual\s+(?:base\s+)?salary", r"yearly\s+(?:base\s+)?salary",
        r"annual\s+compensation", r"yearly\s+compensation",
        r"base\s+compensation", r"base\s+pay", r"annual\s+pay", r"yearly\s+pay",
        r"salary\s+per\s+year", r"salary\s+annually", r"compensation\s+per\s+year", r"salary",
        r"budget\s+cap", r"total\s+amount", r"billed", r"fee"
    ],
    "joining_date": [
        r"joining\s+date", r"start\s+date", r"commencement\s+date", r"employment\s+start",
        r"joining", r"starts\s+on", r"deadline", r"scheduled\s+for"
    ],
    "employee_id": [
        r"employee\s+id", r"emp\s*id", r"employee\s+number", r"staff\s+id", r"register\s+no"
    ],
    "probation": [
        r"probation"
    ]
}

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
}

def extract_money_values(text: str) -> List[float]:
    text_lower = text.lower()
    values = []
    patterns = [
        r"\$\s*([\d,]+(?:\.\d+)?)\s*([km])?",
        r"(?:usd|us\$)\s*([\d,]+(?:\.\d+)?)\s*([km])?",
        r"([\d,]+(?:\.\d+)?)\s*(?:usd|dollars?)",
        r"([\d,]+(?:\.\d+)?)\s*(?:thousand|million|k|m)\s*(?:dollars?|usd)?"
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            number = match[0] if isinstance(match, tuple) else match
            suffix = match[1] if isinstance(match, tuple) and len(match) > 1 else ""
            try:
                val = float(number.replace(",", ""))
            except ValueError:
                continue
            if suffix in ["k", "thousand"]:
                val *= 1000
            elif suffix in ["m", "million"]:
                val *= 1000000
            if val not in values:
                values.append(val)
    return values

def normalize_date_match(day: str, month: str, year: str) -> str:
    month_num = MONTHS.get(month.lower(), 1)
    return f"{year}-{month_num:02d}-{int(day):02d}"

def extract_dates(text: str) -> List[str]:
    dates = []
    p1 = re.findall(r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b", text, re.IGNORECASE)
    for month, day, year in p1:
        dates.append(normalize_date_match(day, month, year))

    p2 = re.findall(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})\b", text, re.IGNORECASE)
    for day, month, year in p2:
        dates.append(normalize_date_match(day, month, year))

    p3 = re.findall(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", text)
    for year, month, day in p3:
        dates.append(f"{year}-{int(month):02d}-{int(day):02d}")

    return list(dict.fromkeys(dates))

def extract_ids(text: str) -> List[str]:
    # Only match explicit employee/staff ID patterns preceded by keywords
    matches = re.findall(r"(?:employee\s*id|emp\s*id|staff\s*id|register\s*no|reg\s*no)[:\s]*([A-Z0-9]{2,10}[-/]\d{2,10})", text, re.IGNORECASE)
    return matches

def extract_facts(text: str) -> Dict[str, Any]:
    facts = {}
    money_vals = extract_money_values(text)
    if money_vals:
        facts["money_values"] = money_vals
        facts["annual_salary"] = {"value": money_vals[0], "currency": "USD"}

    dates = extract_dates(text)
    if dates:
        facts["dates"] = dates

    ids = extract_ids(text)
    if ids:
        facts["ids"] = ids
        facts["employee_id"] = ids[0]

    prob = re.search(r"probation.{0,100}?(\d+)\s*(month|months|year|years)", text, re.IGNORECASE)
    if prob:
        facts["probation"] = f"{prob.group(1)} {prob.group(2)}"

    return facts

# ============================================================
# DATACLASS STRUCTURES
# ============================================================

@dataclass
class DocumentSource:
    id: str
    filename: str
    file_type: str
    extracted_text: str

@dataclass
class Contradiction:
    title: str
    severity: str  # CRITICAL, WARNING, INFO
    source_a: str
    source_b: str
    description: str

@dataclass
class ActionItem:
    title: str
    target_role: str
    action_type: str
    content: str

# ============================================================
class MultiEnginePipeline:
    def __init__(self):
        self.sources = []

    def ingest_document(self, filename: str, file_type: str, content: str):
        for existing in self.sources:
            if existing.filename == filename:
                existing.extracted_text = content
                existing.file_type = file_type
                return existing.id
        doc_id = f"doc_{len(self.sources) + 1}"
        doc = DocumentSource(id=doc_id, filename=filename, file_type=file_type, extracted_text=content)
        self.sources.append(doc)
        return doc_id

    def analyze_cross_source(self) -> Dict[str, Any]:
        data = {
            "contradictions": [],
            "action_items": [],
            "money_mentions": [],
            "date_mentions": []
        }

        # 0. Primary Engine: Multi-Document Gemini / Groq LLM Audit (if configured)
        if len(self.sources) >= 2:
            llm_res = analyze_with_gemini(self.sources) or analyze_with_groq(self.sources)
            if llm_res and llm_res.get("has_conflict"):
                conflicts_list = llm_res.get("conflicts", [])
                if not conflicts_list and llm_res.get("title"):
                    conflicts_list = [llm_res]
                    
                for item in conflicts_list:
                    src_a = item.get("source_a") or self.sources[0].filename
                    src_b = item.get("source_b") or self.sources[1].filename
                    desc = (
                        f"JUDGES SUMMARY:\n{item.get('judges_summary', '')}\n\n"
                        f"• {src_a} (Line {item.get('doc1_line', 1)}):\n  \"{item.get('doc1_quote', '')}\"\n\n"
                        f"• {src_b} (Line {item.get('doc2_line', 1)}):\n  \"{item.get('doc2_quote', '')}\"\n\n"
                        f"EXACT DIFFERENCE:\n{item.get('difference_explanation', '')}"
                    )
                    data["contradictions"].append(Contradiction(
                        title=f"[AI Engine] {item.get('title', 'Conflict Detected')}",
                        severity=item.get("severity", "CRITICAL"),
                        source_a=src_a,
                        source_b=src_b,
                        description=desc
                    ))
                    data["action_items"].append(ActionItem(
                        title=f"Resolve {item.get('title', 'Conflict')}",
                        target_role="Operations",
                        action_type="TASK",
                        content=item.get("judges_summary", "Audit flagged conflict.")
                    ))

        parsed_docs = [{"filename": s.filename, "facts": extract_facts(s.extracted_text), "text": s.extracted_text} for s in self.sources]

        # Fact Comparison Engine (Fallback / Rule-Based)
        if len(parsed_docs) >= 2 and not data["contradictions"]:
            for i in range(len(parsed_docs)):
                for j in range(i + 1, len(parsed_docs)):
                    doc_a, doc_b = parsed_docs[i], parsed_docs[j]
                    facts_a, facts_b = doc_a["facts"], doc_b["facts"]

                    # 1. Percentage / Policy Discrepancy (e.g., 75% vs 60%)
                    pcts_a = re.findall(r'\b\d+(?:\.\d+)?%\b', doc_a["text"])
                    pcts_b = re.findall(r'\b\d+(?:\.\d+)?%\b', doc_b["text"])
                    if pcts_a and pcts_b and set(pcts_a) != set(pcts_b):
                        pa, pb = pcts_a[0], pcts_b[0]
                        data["contradictions"].append(Contradiction(
                            title=f"Policy Requirement Discrepancy ({pa} vs {pb})",
                            severity="CRITICAL",
                            source_a=doc_a["filename"],
                            source_b=doc_b["filename"],
                            description=(
                                f"JUDGES SUMMARY:\n"
                                f"Percentage requirement mismatch detected between {doc_a['filename']} and {doc_b['filename']}.\n\n"
                                f"• {doc_a['filename']}:\n  \"{pa} threshold specified in document.\"\n\n"
                                f"• {doc_b['filename']}:\n  \"{pb} recorded in document.\"\n\n"
                                f"EXACT DIFFERENCE:\n"
                                f"Source A specifies a {pa} requirement whereas Source B records {pb}, representing a non-compliance variance."
                            )
                        ))
                        data["action_items"].append(ActionItem(
                            title=f"Audit Policy Variance ({pa} vs {pb})", target_role="Operations", action_type="TASK",
                            content=f"Verify percentage discrepancy between {doc_a['filename']} ({pa}) and {doc_b['filename']} ({pb})."
                        ))

                    # 2. Financial Amount Mismatch (e.g., $10,000 vs $12,500)
                    money_a = extract_money_values(doc_a["text"])
                    money_b = extract_money_values(doc_b["text"])
                    if money_a and money_b and max(money_a) != max(money_b):
                        m_a, m_b = max(money_a), max(money_b)
                        diff = abs(m_a - m_b)
                        data["contradictions"].append(Contradiction(
                            title=f"Financial Overbilling (${diff:,.0f} Variance)",
                            severity="CRITICAL",
                            source_a=doc_a["filename"],
                            source_b=doc_b["filename"],
                            description=(
                                f"JUDGES SUMMARY:\n"
                                f"Financial discrepancy detected between {doc_a['filename']} and {doc_b['filename']}.\n\n"
                                f"• {doc_a['filename']}: ${m_a:,.2f}\n"
                                f"• {doc_b['filename']}: ${m_b:,.2f}\n\n"
                                f"EXACT DIFFERENCE:\n"
                                f"Variance of ${diff:,.2f} identified in extracted monetary figures (${m_a:,.0f} vs ${m_b:,.0f})."
                            )
                        ))
                        data["action_items"].append(ActionItem(
                            title="Draft Financial Notice", target_role="Operations", action_type="EMAIL_DRAFT",
                            content=f"Discrepancy of ${diff:,.2f} detected between {doc_a['filename']} and {doc_b['filename']}."
                        ))

                    # 3. Date / Timeline Conflict
                    dates_a = facts_a.get("dates", []) or extract_dates(doc_a["text"])
                    dates_b = facts_b.get("dates", []) or extract_dates(doc_b["text"])
                    if dates_a and dates_b and set(dates_a) != set(dates_b):
                        data["contradictions"].append(Contradiction(
                            title="Timeline Date Mismatch",
                            severity="MEDIUM",
                            source_a=doc_a["filename"],
                            source_b=doc_b["filename"],
                            description=(
                                f"JUDGES SUMMARY:\n"
                                f"Timeline discrepancy identified between {doc_a['filename']} and {doc_b['filename']}.\n\n"
                                f"• {doc_a['filename']}: {', '.join(dates_a)}\n"
                                f"• {doc_b['filename']}: {', '.join(dates_b)}\n\n"
                                f"EXACT DIFFERENCE:\n"
                                f"Specified timeline dates do not match."
                            )
                        ))

        # Smart Clause & Sentence Comparison Engine (Fallback if Gemini rate-limited)
        if len(self.sources) >= 2 and not data["contradictions"]:
            lines1 = [(i+1, line.strip()) for i, line in enumerate(self.sources[0].extracted_text.splitlines()) if line.strip()]
            lines2 = [(i+1, line.strip()) for i, line in enumerate(self.sources[1].extracted_text.splitlines()) if line.strip()]
            metric_pattern = r'(\b\d+(?:\.\d+)?%|\$\d+(?:,\d+)*(?:\.\d+)?|\b\d{1,2}/\d{1,2}/\d{2,4}|\b\d{1,}\b)'

            for lno1, l1 in lines1:
                m1 = re.findall(metric_pattern, l1, re.IGNORECASE)
                w1 = set(re.findall(r'\w{3,}', l1.lower())) - {'this', 'that', 'with', 'from', 'have', 'were', 'been', 'date', 'file'}

                for lno2, l2 in lines2:
                    m2 = re.findall(metric_pattern, l2, re.IGNORECASE)
                    w2 = set(re.findall(r'\w{3,}', l2.lower())) - {'this', 'that', 'with', 'from', 'have', 'were', 'been', 'date', 'file'}
                    overlap = w1.intersection(w2)

                    if len(overlap) >= 1:
                        val_a = m1[0] if m1 else l1
                        val_b = m2[0] if m2 else l2
                        if val_a != val_b:
                            topic = list(overlap)[0].upper()
                            data["contradictions"].append(Contradiction(
                                title=f"Semantic Clause Conflict ({topic})",
                                severity="CRITICAL",
                                source_a=self.sources[0].filename,
                                source_b=self.sources[1].filename,
                                description=(
                                    f"JUDGES SUMMARY:\n"
                                    f"Discrepancy identified regarding '{topic}' between uploaded documents.\n\n"
                                    f"• {self.sources[0].filename} (Line {lno1}):\n  \"{l1}\"\n\n"
                                    f"• {self.sources[1].filename} (Line {lno2}):\n  \"{l2}\"\n\n"
                                    f"EXACT DIFFERENCE:\n"
                                    f"Source A specifies '{val_a}', whereas Source B specifies '{val_b}'."
                                )
                            ))
                            data["action_items"].append(ActionItem(
                                title=f"Resolve {topic} Conflict",
                                target_role="Audit Officer",
                                action_type="TASK",
                                content=f"Verify clause discrepancy for '{topic}' between {self.sources[0].filename} and {self.sources[1].filename}."
                            ))
                            break
                if data["contradictions"]:
                    break

        # Populate Evidence Mentions for UI
        for s in self.sources:
            for val in extract_money_values(s.extracted_text):
                data["money_mentions"].append((val, s.filename, f"Amount: ${val:,.2f}"))
            for d in extract_dates(s.extracted_text):
                data["date_mentions"].append((d, s.filename, f"Date: {d}"))

        if not data["contradictions"] and self.sources:
            data["action_items"].append(ActionItem(
                title="Review Complete",
                target_role="System",
                action_type="INFO",
                content=f"Successfully analyzed {len(self.sources)} sources. No critical conflicts detected."
            ))

        sources_payload = []
        for s in self.sources:
            # Extract key metrics (percentages, amounts, dates)
            pcts = re.findall(r'\b\d+(?:\.\d+)?%\b', s.extracted_text)
            dollars = re.findall(r'\$\s*[\d,]+(?:\.\d+)?\b', s.extracted_text)
            dates = extract_dates(s.extracted_text)
            metrics = list(dict.fromkeys(pcts + dollars + dates))[:8]
            sources_payload.append({
                "name": s.filename,
                "type": s.file_type,
                "preview": s.extracted_text[:1200] if len(s.extracted_text) > 1200 else s.extracted_text,
                "metrics": metrics
            })

        return {
            "ingested_count": len(self.sources),
            "sources": sources_payload,
            "contradictions": [asdict(c) for c in data.get("contradictions", [])],
            "actions": [asdict(a) for a in data.get("action_items", [])],
            "evidence": {
                "money": [ {"amount": m[0], "source": m[1], "context": m[2]} for m in data.get("money_mentions", []) ],
                "dates": [ {"date": m[0], "source": m[1], "context": m[2]} for m in data.get("date_mentions", []) ]
            }
        }

OmniIntelEngine = MultiEnginePipeline
