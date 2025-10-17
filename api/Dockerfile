FROM python:3.10-slim
WORKDIR /app
COPY api.py .
RUN pip install flask psycopg2-binary pyjwt
CMD ["python", "api.py"]