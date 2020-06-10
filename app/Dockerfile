FROM python:3.7-slim-buster

COPY requirements.txt /opt/app/
COPY *.py /opt/app/
COPY api /opt/app/api
COPY conf /opt/app/conf
COPY models /opt/app/models
COPY sklearn_model /opt/app/sklearn_model


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --compile -r /opt/app/requirements.txt && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/* /tmp/* /var/tmp/*


WORKDIR /opt

EXPOSE 8000

CMD uvicorn app.main:app --host 0.0.0.0 --port 8000




