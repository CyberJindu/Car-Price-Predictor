FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

EXPOSE 10000

CMD ["gunicorn", "--chdir", "Server", "app:app", "--bind", "0.0.0.0:10000"]
