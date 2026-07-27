FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/generated_images data/sample_posts data/style_profiles

CMD ["python", "-m", "app.main"]
