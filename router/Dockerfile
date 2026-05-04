FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD sh -c "alembic -c router/db/alembic.ini upgrade head && uvicorn routing:app --host 0.0.0.0 --port 8001"