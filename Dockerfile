FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/

EXPOSE 8501

# Seit 0.15.1: start.py startet Streamlit wie bisher und dazu den Vorlade-Helfer (app/vorladen.py)
CMD ["python", "start.py", "--server.address=0.0.0.0", "--server.port=8501"]

