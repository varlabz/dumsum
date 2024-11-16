FROM python:3.12-slim AS dev
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

FROM dev AS final
COPY src/*.py ./src/
# check code how to ignore resume.md 
COPY data/*.md .            
ENTRYPOINT ["python", "src/linkedin.py"]

LABEL description="LinkedIn Bot" \
      usage.build="docker build -t linkedin-pw ."  \
      usage.run="docker run -it --rm --net=host -v ./data:/app/data --env-file .key linkedin-pw [--matcher NUMBER]" 
