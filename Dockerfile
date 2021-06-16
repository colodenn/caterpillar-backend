# Use the Python3.7.2 image
FROM python

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app 
ADD . /app
# Install the dependencies

RUN pip install -r requirements.txt

#
RUN apt-get update && apt-get -y install graphviz graphviz-dev

# run the command to start uWSGI
CMD ["uwsgi", "wsgi.ini"]