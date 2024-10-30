FROM python:3.12-slim
# error: Host header is specified and is not an IP address or localhost
# ENV CDP_HOST='http://host.docker.internal:9222' 
ENV CDP_HOST='http://192.168.65.254:9222'
ENV OLLAMA_HOST='http://192.168.65.254:11434'
WORKDIR /app
COPY src/*.py ./src/
# check code how to ignore resume.md 
COPY data/*.md .            
COPY requirements.txt .
RUN pip install -r requirements.txt 
RUN playwright install chromium
ENTRYPOINT ["python", "src/linkedin.py"]
LABEL usage1="docker run -it --rm --add-host host.docker.internal:host-gateway -v ./data:/app/data -e GROQ_API_KEY=\${GROQ_API_KEY} linkedin-pw [--matcher NUMBER]"
LABEL usage2="docker run -it --rm --add-host host.docker.internal:host-gateway -v ./data:/app/data -e OPENAI_API_KEY=\${OPENAI_API_KEY} linkedin-pw  [--matcher NUMBER]"
LABEL usage3="docker run -it --rm --add-host host.docker.internal:host-gateway -v ./data:/app/data -e ANTHROPIC_API_KEY=\${ANTHROPIC_API_KEY} linkedin-pw  [--matcher NUMBER]"
