# Use Ubuntu 20.04 LTS as the base image
FROM moodsick/ml_model:latest

WORKDIR /ml_model/src

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

