FROM python:3.7-stretch

RUN groupadd --gid 10001 app && \
    useradd -g app --uid 10001 --shell /usr/sbin/nologin --create-home --home-dir /app app

WORKDIR /app

EXPOSE 8000

ENV FLASK_APP nazgul.py
ENV FLASK_ENV production
ENV DATABASE_URL=host.docker.internal
ENV AUTH_USERS="{}"

COPY requirements.txt /python_requirements.txt
RUN pip install --require-hashes --no-cache -r /python_requirements.txt

COPY . /app

RUN python setup.py install

USER app

CMD ["./run"]
