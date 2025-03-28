FROM python:3.9

# Set working directory
WORKDIR /app

# Install system dependencies required for OpenCV, dlib, and libGL
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgl1-mesa-glx \
    wget \
    bzip2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
# Note: We are installing dlib directly, not using dlib-binary
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create src/model directory structure
RUN mkdir -p /app/src/model

# Download shape predictor file and place it in the correct location
RUN wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2 && \
    bzip2 -d shape_predictor_68_face_landmarks.dat.bz2 && \
    mv shape_predictor_68_face_landmarks.dat /app/src/model/

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO
ENV PORT=8000

# Expose the FastAPI port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]