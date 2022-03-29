FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ADD . /crypto
WORKDIR /crypto
COPY requirements.txt /crypto/
#why??
RUN pip install -r requirements.txt
COPY . /crypto/
#why??