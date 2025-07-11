# Use official Python image
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Ensure /app exists and is writable
RUN mkdir -p /app && chmod 777 /app

# Copy backend code directly into /app
# COPY ./backend/ ./

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 