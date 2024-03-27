# Use a base image that includes both Python and a C++ build environment
FROM python:3.8-buster

# Set the working directory in the Docker container
WORKDIR /app

# Copy your C++ source file and compile it
COPY main.cpp /app
RUN g++ -o dormbot_app main.cpp

# Copy the Python source file
COPY main.py /app

# Copy the text files your application uses for storage
COPY queue_list.txt /app
COPY shopping_list.txt /app
COPY user_actions.txt /app
COPY water_list.txt /app

# Copy the Python requirements file and install dependencies
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Create an entrypoint script and make it executable
RUN echo '#!/bin/bash\n./dormbot_app &\npython main.py' > /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set the default command for the container to your entrypoint script
CMD ["/app/entrypoint.sh"]
