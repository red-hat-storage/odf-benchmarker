# Use an official lightweight Python base image
FROM python:3.9-slim

# Install benchmarking tools and required utilities
RUN apt-get update && apt-get install -y \
    sysbench \
    hping3 \
    iperf3 \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the Python benchmark code and dependencies
COPY src/ /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Define the command to run the benchmark script
ENTRYPOINT ["python", "benchmarker.py"]

# Allow passing metrics.json as an argument dynamically
CMD []
