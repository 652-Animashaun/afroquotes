docker run -ti -e AWS_PROFILE=zappa_user -p 8000:8000 -v "$(pwd):/app/" -v ~/.aws:/root/.aws --rm afroquotes_app
# RUN /bin/bash -c 'zappashel.sh'

# echo "PWD: "$PWD
# source /opt/venv/bin/activate

