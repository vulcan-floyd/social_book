FROM ubuntu:20.04

RUN apt-get update

MAINTAINER shivendra singh

# Install Python
RUN apt-get install libmysqlclient-dev -y
RUN apt-get install python3.8-dev python3-pip -y
RUN ln -svf /usr/bin/python3.8 /usr/bin/python

#Set Working Dir
WORKDIR /var/social_book

#Copy Code
COPY . .

#Install Requirement.txt
RUN pip install -r requirements.txt

# RUN python manage.py migrate

EXPOSE 80

CMD ["python", "manage.py", "runserver", "127.0.0.1:8000"]