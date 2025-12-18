# Simple container for running the coloring-book scripts
FROM python:3.11-slim

# Install system packages needed by Pillow for image formats (JPEG/PNG)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libjpeg62-turbo-dev \
       zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files into the image
COPY . /app

# Install required Python dependency
RUN pip install --no-cache-dir Pillow Flask

# Default command starts the simple web UI; override to run CLI scripts
CMD ["python", "web_app.py"]
