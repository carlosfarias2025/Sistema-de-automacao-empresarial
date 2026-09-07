FROM python:3.14

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

LABEL authors="Carlos Eduardo Farias"


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]