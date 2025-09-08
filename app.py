from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline
import openai
import os
import json
from dotenv import load_dotenv
from postprocess import postprocess_entities
import re

load_dotenv()

app = FastAPI(title="NER + AI Text Generation")
templates = Jinja2Templates(directory="templates")

# OpenAI API Key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY ortam değişkeni eksik!")
openai.api_key = openai_api_key

# NER model ve tokenizer yükle
model_path = "./ner_model/checkpoint-1100"
model = AutoModelForTokenClassification.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)
ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

# Thresholdları JSON dosyasından oku
threshold_path = "visual_results/best_entity_thresholds.json"
try:
    with open(threshold_path, "r", encoding="utf-8") as f:
        raw_thresholds = json.load(f)
        ENTITY_THRESHOLDS = {k.upper(): float(v) for k, v in raw_thresholds.items()}
    print(f"\n✅ Thresholdlar yüklendi: {ENTITY_THRESHOLDS}")
except Exception as e:
    print(f"\n⚠️ Threshold dosyası okunamadı. Hata: {e}")
    ENTITY_THRESHOLDS = {
        "PERSON": 0.25,
        "ORG": 0.30,
        "TCNO": 0.80,
        "PHONE": 0.60,
        "DATE": 0.20,
    }

class InputData(BaseModel):
    text: str

class Entity(BaseModel):
    word: str
    entity_group: str
    start: int
    end: int
    score: float

class OutputData(BaseModel):
    entities: List[Entity]

@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "entities": None, "input_text": ""})

@app.post("/", response_class=HTMLResponse)
def predict(request: Request, input_text: str = Form(...)):
    # Token bazında etiketleri göster
    tokens = tokenizer(input_text, return_offsets_mapping=True, return_tensors="pt")
    offsets = tokens.pop("offset_mapping")  # offset_mapping'i model inputundan çıkar
    outputs = model(**tokens)
    predictions = outputs.logits.argmax(dim=-1).squeeze().tolist()
    offsets = offsets.squeeze().tolist()
    id2label = model.config.id2label

    print("=== Token Bazında Etiketler ===")
    for idx, (start, end) in enumerate(offsets):
        if start == 0 and end == 0:
            continue  # special tokens
        token_text = input_text[start:end]
        label = id2label[predictions[idx]]
        print(f"Token: '{token_text}' | Start: {start} | End: {end} | Label: {label}")

    results = ner_pipeline(input_text)

    # Threshold uygulanmadan önce sonuçları al
    entities = [
        {
            "word": ent["word"].replace("##", ""),
            "entity_group": (ent.get("entity_group") or ent.get("entity") or "UNKNOWN").upper(),
            "start": ent["start"],
            "end": ent["end"],
            "score": round(ent["score"], 4)
        }
        for ent in results
    ]

    # Ardışık entity'leri birleştir + TCNO/PHONE düzeltmeleri
    merged_entities = postprocess_entities(entities)

    # Threshold filtresi uygula
    filtered_entities = [
        ent for ent in merged_entities
        if ent["entity_group"] in ["TCNO", "PHONE"] or ent["score"] >= ENTITY_THRESHOLDS.get(ent["entity_group"], 0.5)
    ]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "entities": filtered_entities,
        "input_text": input_text
    })

@app.post("/generate_sentence")
def generate_sentence(data: InputData):
    prompt = (
        "Lütfen tamamen yapay ve doğal Türkçe, içinde rastgele TC Kimlik No, telefon, kişi isimleri, kurum ve tarih ifadeleri olan "
        "tek bir cümle üret. Cümle doğal ve anlamlı görünüsün."
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150,
        )
        sentence = response.choices[0].message.content.strip()
        return {"sentence": sentence}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
