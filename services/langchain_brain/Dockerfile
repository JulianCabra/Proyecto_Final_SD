FROM python:3.10-slim
WORKDIR /app
COPY app.py .
RUN pip install pika
CMD ["python", "-u", "app.py"]
