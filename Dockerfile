FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app
COPY training /app/training
COPY models /app/models
COPY tests /app/tests
COPY mlruns /app/mlruns
COPY scripts /app/scripts
COPY artifacts /app/artifacts


EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]




