FROM python:3.12-slim
WORKDIR /app
COPY src/linkedin_pw.py .
RUN pip install playwright 
RUN playwright install chromium
CMD ["python", "linkedin_pw.py"]
