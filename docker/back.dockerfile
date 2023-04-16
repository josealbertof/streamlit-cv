FROM python:3.11-slim-buster


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY model model
COPY src src

CMD ["python3", "src/model/main.py"]