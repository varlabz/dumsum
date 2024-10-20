FROM python:3.12-slim
# error: Host header is specified and is not an IP address or localhost
# ENV CDP_HOST='http://host.docker.internal:9222' 
ENV CDP_HOST='http://192.168.65.254:9222'
WORKDIR /app
COPY src/ .
COPY requirements.txt .
RUN pip install -r requirements.txt 
RUN playwright install chromium
CMD ["python", "linkedin.py"]
