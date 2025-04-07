FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "hyperscan.py", "-u", "http://example.com", "-w", "wordlists/common.txt", "-t", "10"]
