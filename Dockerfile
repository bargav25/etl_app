FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

ENV NAME World

# Run script.py when the container launches
CMD ["python", "./main.py"]
