FROM python:3.7-stretch

WORKDIR /app

COPY requirements.txt /python_requirements.txt
RUN pip3 install --no-cache -r /python_requirements.txt

EXPOSE 5000

ENV FLASK_APP nazgul.py
ENV FLASK_ENV production
ENV DATABASE_URL=host.docker.internal
ENV AUTH_USERS="{\"admin\":\"admin\"}"

COPY . /app
CMD ["python3", "main.py"]
