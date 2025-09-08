# Python 3.10 slim tabanlı imaj
FROM python:3.10-slim

WORKDIR /app

COPY requirements2.txt .

RUN pip install --no-cache-dir -r requirements2.txt


COPY app.py .
COPY ner_model ./ner_model

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
