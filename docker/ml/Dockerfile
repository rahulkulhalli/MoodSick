# Use Ubuntu 20.04 LTS as the base image
FROM moodsick/ml_model:latest

WORKDIR /ml_model

COPY /app .
COPY requirements.txt .


# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

