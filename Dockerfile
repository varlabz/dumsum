FROM python:3.12-slim AS dev
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

RUN adduser --disabled-password --gecos '' appuser
USER appuser

FROM dev AS final
COPY src/*.py ./src/
# check code how to ignore resume.md 
COPY data/*.md .            
CMD ["python", "src/linkedin.py", "--click-apply", "--click-easy-apply", "--matcher", "70", "--speed", "0"]

LABEL description="LinkedIn Bot" \
      usage.build="docker build -t linkedin-pw ."  \
      usage.run="docker run -it --rm --net=host -v <directory with resume>:/app/data \
            --env-file .key linkedin-pw [--matcher NUM] [--matcher-ignore NUM] [--speed 0/1] [--click-apply] [--click-easy-apply] \
            [--debug-easy-apply-form] [--debug-matcher] [--debug-1page]" 
