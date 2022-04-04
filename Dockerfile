FROM python:3.11.0a5-alpine
COPY . /ghs
WORKDIR /ghs
RUN pip install .
CMD ghs --help
