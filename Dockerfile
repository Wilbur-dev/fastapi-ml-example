FROM python:3.11-slim

COPY requirements.txt /app/
COPY app /app/app
COPY training /app/training
COPY models /app/models
COPY tests /app/tests

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]




