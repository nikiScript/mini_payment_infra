FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD sh -c "alembic -c gateway/db/alembic.ini upgrade head && uvicorn gateway:app --host 0.0.0.0 --port 8003"