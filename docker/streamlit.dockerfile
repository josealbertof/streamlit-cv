FROM python:3.11-slim-buster

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src src

CMD ["streamlit", "run", "src/streamlit/main.py"]