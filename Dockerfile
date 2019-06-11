FROM python:3.7

WORKDIR /app
COPY . /app

COPY requirements.txt /python_requirements.txt
RUN pip3 install --no-cache -r /python_requirements.txt

EXPOSE 5000

ENV FLASK_APP nazgul.py
ENV FLASK_ENV production

CMD ["python3", "nazgul/api.py"]