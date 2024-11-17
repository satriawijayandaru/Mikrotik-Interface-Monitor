FROM python:3.11.10-slim-bullseye

COPY requirements.txt .
COPY mqtt-env.py .

RUN pip install -r requirements.txt

CMD ["python", "mqtt-env.py"]
