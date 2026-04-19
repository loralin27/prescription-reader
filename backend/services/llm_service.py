import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Load .env from backend root
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError(
        "\n\n❌ GROQ_API_KEY not found!\n"
        "Make sure your .env file has:\n"
        "GROQ_API_KEY=gsk_your-groq-key-here\n"
    )

client = Groq(api_key=api_key)
MODEL = "llama-3.3-70b-versatile"  # Free, fast, highly accurate

SYSTEM_PROMPT = """You are a medical prescription parser.
Your job is to extract medicine information from raw OCR text of doctor prescriptions.

Rules:
- Fix OCR spelling errors (e.g., "Paracitamol" → "Paracetamol")
- Identify medicine names, dosage, and frequency
- Return ONLY a valid JSON array, no extra text, no markdown, no backticks
- Frequency should be human-readable (e.g., "Once daily", "Twice daily", "Three times daily")
- If dosage or frequency is missing, use null
- Common abbreviations: OD=Once daily, BD=Twice daily, TDS=Three times daily, QID=Four times daily
- Tab = Tablet, Cap = Capsule, Inj = Injection, Syr = Syrup

Output format (JSON array only, nothing else):
[
  {
    "medicine": "Paracetamol",
    "form": "Tablet",
    "dosage": "500mg",
    "frequency": "Twice daily",
    "duration": "5 days",
    "notes": ""
  }
]"""


def extract_medicines_from_text(raw_text: str) -> list:
    if not raw_text.strip():
        return []

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Extract medicines from this prescription text:\n\n{raw_text}"}
            ],
            temperature=0.1,
            max_tokens=1000
        )

        content = response.choices[0].message.content.strip()

        # Clean markdown if model wraps in code blocks
        content = re.sub(r"```json|```", "", content).strip()

        medicines = json.loads(content)
        return medicines if isinstance(medicines, list) else []

    except json.JSONDecodeError:
        return [{
            "medicine": "Parse error",
            "form": None,
            "dosage": None,
            "frequency": None,
            "duration": None,
            "notes": raw_text
        }]
    except Exception as e:
        raise RuntimeError(f"LLM extraction failed: {str(e)}")