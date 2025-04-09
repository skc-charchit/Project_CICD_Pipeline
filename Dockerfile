FROM python:3.9-slim

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir --upgrade -r requirements.txt

ENV PORT=8001
EXPOSE 8001

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port $PORT"]
