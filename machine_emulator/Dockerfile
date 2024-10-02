# Use the official Python 3.12 image as the base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY ../ ./

# Install any necessary Python packages

# TODO: we might want to pass it to Streamlit
EXPOSE 8502
# Command to run the application
# https://discuss.streamlit.io/t/how-to-set-a-different-port-number-for-different-streamlit-program-in-a-same-machine/8693/2
CMD ["python", "-m", "streamlit", "run", "./machine_emulator/main.py", "--server.port", "8502"]
