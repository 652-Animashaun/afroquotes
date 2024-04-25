# get python3.8 image 
FROM python:3.10

# set working directory
RUN mkdir /app-server
WORKDIR /app-server

# install dependencies
COPY requirements.txt /app-server

ENV VIRTUAL_ENV=/opt/venv

RUN python3 -m venv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --no-cache-dir -r requirements.txt

# RUN apt-get update && apt-get install nano -y

# copy script to folder
COPY ./afroquotes /app-server

# CMD ["python", "manage.py", "runserver"]
EXPOSE 5000

RUN echo 'export PS1="\[\e[36m\]zappashell>\[\e[m\]"' >> /root/.bashrc

CMD ["bash"]