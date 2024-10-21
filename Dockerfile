FROM python:3.13-alpine

# Create appgroup and appuser
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py ./

# Change ownership of /app directory to appuser
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose the port FastAPI will run on
EXPOSE 80

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
