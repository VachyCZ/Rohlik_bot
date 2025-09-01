FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt \
 && playwright install --with-deps
COPY bot.py .
EXPOSE 10000
CMD ["python","bot.py"]
