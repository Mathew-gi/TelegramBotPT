FROM python:3.9-slim
WORKDIR /bot_image
COPY . .
RUN pip install -r requirments.txt --no-cache-dir
CMD ["python", "./bot.py"]
