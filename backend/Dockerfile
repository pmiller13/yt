FROM python:3.13-slim

RUN groupadd -r scrubber && useradd -r -g scrubber -u 1000 scrubber

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg ca-certificates curl unzip && \
    curl --version && \
    curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local sh && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir /downloads && chown scrubber:scrubber /downloads && chmod 755 /downloads

RUN chown -R scrubber:scrubber /app

USER scrubber

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]