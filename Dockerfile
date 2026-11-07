# 1. Hafif ve optimize edilmiş resmi Python imajını taban alıyoruz
FROM python:3.11-slim

# 2. Python'un bytecode (.pyc) yazmasını engelliyor ve çıktıları doğrudan konsola basmasını sağlıyoruz
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Konteyner içinde çalışma dizinini belirliyoruz
WORKDIR /app

# 4. Sistem bağımlılıklarını güncelliyoruz
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /lib/apt/lists/*

# 5. Önce sadece requirements.txt dosyasını kopyalıyoruz (Layer Caching optimization)
COPY requirements.txt .

# 6. Bağımlılıkları yüklüyoruz
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7. Projedeki tüm kodları konteynerin /app dizinine kopyalıyoruz
COPY . .

# 8. Konteynerin dış dünyaya açacağı portu belirtiyoruz
EXPOSE 8000

# 9. Uygulamayı başlatacak varsayılan komut (Uvicorn ASGI sunucusu)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]