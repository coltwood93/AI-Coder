FROM python:3.13-rc-slim

WORKDIR /app

# Install system dependencies needed for numpy and pygame
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libsdl2-2.0-0 \
    libsdl2-ttf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables to handle SDL audio and display
ENV SDL_AUDIODRIVER=dummy
ENV SDL_VIDEODRIVER=dummy

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the application
COPY . .

# Run tests by default, override with different command if needed
CMD ["python", "-m", "pytest", "tests/"]