# Use official Python image as base
FROM python:3.10-slim

# Install necessary packages and wkhtmltopdf
RUN apt-get update && \
    apt-get install -y \
    wget \
    xfonts-75dpi \
    xfonts-base \
    wkhtmltopdf && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the FastAPI application
COPY main.py .

# Expose the port FastAPI will run on
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
