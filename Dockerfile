FROM python:3.12-slim
COPY *.py requirements.txt ./
RUN pip install -r requirements.txt
ENTRYPOINT uvicorn main:app --host=0.0.0.0
