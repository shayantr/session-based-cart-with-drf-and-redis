FROM python:3.12.3

# جلوگیری از بافر شدن خروجی‌ها (مناسب برای لاگ‌گیری در docker)
ENV PYTHONUNBUFFERED=1




# set working directory
WORKDIR /app

# copy project files
COPY app/requirements.txt .

#installdependencies
RUN pip install --no-cache-dir -r requirements.txt