FROM python:3.11-slim

WORKDIR /plataforma_educacional

COPY . /plataforma_educacional

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /plataforma_educacional/app.py

EXPOSE 5000

CMD ["python", "app.py"]
