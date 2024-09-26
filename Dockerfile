# Use the official Python 3.12 image as the base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any necessary Python packages
RUN pip install --no-cache-dir -r requirements.txt

# TODO: we might want to pass it to Streamlit
EXPOSE 8501
# Command to run the application
CMD ["python", "-m", "streamlit", "run", "./main.py"]
