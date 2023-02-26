FROM python:3.11

WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:/app"

ADD . /app


RUN pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org pip --upgrade
RUN pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org -r requirements.txt
RUN touch .dockerenv

CMD ["tail","-f", "requirements.txt"]
