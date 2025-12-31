# 1. Use a slim Python base image to keep the footprint small
FROM python:3.9-slim

# 2. Set environment variables to optimize Python performance
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Install Poppler and other system utilities
# We combine update and install to reduce image layers
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 4. Set the working directory inside the container
WORKDIR /app

# 5. Install Python dependencies first (for better caching)
# This way, Docker only reruns this if requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your application code
COPY . .

# 7. Create a temporary folder for uploads (for stateless processing)
RUN mkdir -p /app/temp_uploads && chmod 777 /app/temp_uploads

# 8. Define the command to run your app
# Assuming main.py is your entry point
CMD ["python", "main.py"]
