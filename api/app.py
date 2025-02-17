from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import os
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline
import logging
import uvicorn

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

# Initialize Presidio
presidio_analyzer = AnalyzerEngine()

# Enhance NRIC detection
nric_pattern = Pattern(name="nric_pattern", regex=r"[A-Za-z]\d{7}[A-Za-z]", score=0.9)
nric_recognizer = PatternRecognizer(supported_entity="NRIC", patterns=[nric_pattern])
presidio_analyzer.registry.add_recognizer(nric_recognizer)

# Enhance PHONE detection
phone_pattern = Pattern(name="sg_phone_pattern", regex=r"(\+65\s?\d{8})|(\b\d{8}\b)", score=0.9)
phone_recognizer = PatternRecognizer(supported_entity="PHONE", patterns=[phone_pattern])
presidio_analyzer.registry.add_recognizer(phone_recognizer)

# Enhance EMAIL detection
email_pattern = Pattern(name="email_pattern", regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}(\.[A-Za-z]{2,3})?\b", score=0.9)
email_recognizer = PatternRecognizer(supported_entity="EMAIL", patterns=[email_pattern])
presidio_analyzer.registry.add_recognizer(email_recognizer)

# Improve NAME detection (based on "My name is")
name_pattern = Pattern(
    name="name_after_my_name_is_or_Im",
    regex=r"(?<=\b(My name is)\s)([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,3})(?=[,.\s])(?!\s(?:looking|working|trying|planning|studying|thinking|considering|applying|currently|previously|formerly|acting))",
    score=0.9
)
name_recognizer = PatternRecognizer(supported_entity="NAME", patterns=[name_pattern])
presidio_analyzer.registry.add_recognizer(name_recognizer)

# Improve ADDRESS detection
address_pattern = Pattern(
    name="sg_address_pattern",
    regex=r"(\b(?:Blk\s\d{1,3},\s)?(?:\d{1,5}[A-Za-z]?|[A-Za-z]?\d{1,5})\s[A-Za-z]+(?:\s[A-Za-z]+)*,?\s(?:#\d{1,3}-\d{1,3},\s)?[A-Za-z]+(?:\s[A-Za-z]+)*,\sSingapore\s\d{6}\b|\b(?:BLK\s\d{1,3},\s)?(?:\d{1,5}[A-Z]?|[A-Z]?\d{1,5})\s[A-Z]+(?:\s[A-Z]+)*,?\s(?:#\d{1,3}-\d{1,3},\s)?[A-Z]+(?:\s[A-Z]+)*,\sSINGAPORE\s\d{6}\b)",
    score=0.9
)
address_recognizer = PatternRecognizer(supported_entity="ADDRESS", patterns=[address_pattern])
presidio_analyzer.registry.add_recognizer(address_recognizer)

# Initialize BERT & RoBERTa
model_paths = {
    "BERT": "/app/bert-ner",
    "RoBERTa": "/app/roberta-ner"
}
tokenizers = {name: AutoTokenizer.from_pretrained(path) for name, path in model_paths.items()}
models = {name: AutoModelForTokenClassification.from_pretrained(path, ignore_mismatched_sizes=True) for name, path in model_paths.items()}
pipelines = {name: pipeline("ner", model=models[name], tokenizer=tokenizers[name], aggregation_strategy="simple") for name in models}

# Database connection
DATABASE_URL = "dbname=pii user=postgres password=postgres host=postgres port=5432"
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS pii_data (
        id SERIAL PRIMARY KEY,
        user_input TEXT,
        redacted_text TEXT
    )
""")
conn.commit()

class PIIRequest(BaseModel):
    text: str

@app.post("/redact")
def redact_text(request: PIIRequest):
    text = request.text
    entity_map = {}

    # Detect PII using Presidio
    presidio_results = presidio_analyzer.analyze(text=text, entities=["NAME", "EMAIL", "PHONE", "NRIC", "ADDRESS"], language='en')
    for entity in presidio_results:
        entity_type = entity.entity_type
        word = text[entity.start:entity.end]
        entity_map[word] = entity_type

    # Supplement NAME detection with BERT/RoBERTa
    bert_results = pipelines["BERT"](text)
    roberta_results = pipelines["RoBERTa"](text)

    for model_results in [bert_results, roberta_results]:
        for entity in model_results:
            word = entity["word"]
            if word not in entity_map:
                entity_map[word] = "NAME"

    # Replace detected PII with placeholders
    redacted_text = text
    for word, pii_type in entity_map.items():
        redacted_text = redacted_text.replace(word, f"[{pii_type}]")

    # Store the redacted text in the database
    cur.execute("INSERT INTO pii_data (user_input, redacted_text) VALUES (%s, %s)", (text, redacted_text))
    conn.commit()

    return {"original": text, "redacted": redacted_text}

@app.get("/history")
def get_history():
    cur.execute("SELECT * FROM pii_data ORDER BY id DESC LIMIT 10")
    rows = cur.fetchall()
    return [{"id": r[0], "user_input": r[1], "redacted_text": r[2]} for r in rows]

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, log_level="debug")
