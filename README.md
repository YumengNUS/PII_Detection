# PII-Detection-Redaction-API

## How to Run


```
git clone https://github.com/YumengNUS/PII_Detection

cd pii-detection

docker-compose up -d --build
```

Then visit:

```
API Docs  http://localhost:8000/docs

Web UI  http://localhost:7860
```

Due to my limited computational resources, the BERT and RoBERTa models are relatively large and run slower. Therefore, I have **commented out their implementation by default** and only use Presidio in the code to prevent the API from crashing due to insufficient memory.

For details on the performance evaluation of these two models, please refer to Section2.md.


