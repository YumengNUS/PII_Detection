FROM python:3.9

WORKDIR /app
COPY app.py .

# Install dependencies
RUN pip install fastapi uvicorn presidio-analyzer presidio-anonymizer transformers torch torchvision torchaudio psycopg2-binary

# Pre-download Hugging Face models and save them locally

#RUN python -c "from transformers import AutoModel, AutoTokenizer; \
#               AutoModel.from_pretrained('dslim/bert-base-NER').save_pretrained('/app/bert-ner'); \
#               AutoTokenizer.from_pretrained('dslim/bert-base-NER').save_pretrained('/app/bert-ner')"

#RUN python -c "from transformers import AutoModel, AutoTokenizer; \
#               AutoModel.from_pretrained('Jean-Baptiste/roberta-large-ner-english').save_pretrained('/app/roberta-ner'); \
#               AutoTokenizer.from_pretrained('Jean-Baptiste/roberta-large-ner-english').save_pretrained('/app/roberta-ner')"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
