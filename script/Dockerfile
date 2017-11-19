FROM python:3.6

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip3 install --trusted-host pypi.python.org -r /app/requirements.txt

# Make port 5006 available to the world outside this container
EXPOSE 5006

# Run app when the container launches
CMD ["bokeh", "serve", "--allow-websocket-origin=localhost:4000", "--show", "/app/ui"]
