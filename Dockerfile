# Use the Python3.7.2 image
FROM python

# Set the working directory to /app
RUN mkdir /app
WORKDIR /app
# Install the dependencies
COPY . .

RUN pip install -r requirements.txt

#
RUN apt-get update && apt-get -y install graphviz graphviz-dev


# run the command to start uWSGI
CMD ["uwsgi", "wsgi.ini"]
#CMD ["python","app.py"]