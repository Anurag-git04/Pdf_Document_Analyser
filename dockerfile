# Dockerfile

# 1. Use an official Python runtime as a parent image
# Using a 'slim' version keeps the image size smaller
FROM python:3.11-slim-bookworm

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the dependencies file first to leverage Docker layer caching
# This step only re-runs if requirements.txt changes
COPY requirements.txt .

# 4. Install any needed packages specified in requirements.txt
# --no-cache-dir reduces image size
# The Spacy model will be downloaded here during the build
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_sm

# 5. Copy the rest of the application's code into the container
COPY . .

# 6. Expose the port Streamlit runs on
EXPOSE 8501

# 7. Define the command to run your app
# The --server.address=0.0.0.0 flag is crucial to make the app accessible
# from outside the container (i.e., from your browser)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]