# get python3.8 image 
FROM python:3.8

# set working directory
WORKDIR /app

# install dependencies
COPY ./requirements.txt /app

ENV VIRTUAL_ENV=/opt/venv

RUN python3 -m venv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --no-cache-dir -r requirements.txt

# copy script to folder
COPY . /app

# CMD ["python", "manage.py", "runserver"]
EXPOSE 8000

RUN echo 'export PS1="\[\e[36m\]zappashell>\[\e[m\]"' >> /root/.bashrc

CMD ["bash"]