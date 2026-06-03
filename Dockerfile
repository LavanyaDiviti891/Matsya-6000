# Use a modern Python version for FastHTML compatibility
FROM python:3.11-slim

# Create a non-root user for security (required by Hugging Face)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy and install dependencies first (optimizes build speed)
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of your application code
COPY --chown=user . /app

# The key: FastHTML needs to run on port 7860 for Hugging Face Spaces
# Replace 'main:app' with 'app:app' if your file is named app.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]