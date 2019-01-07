FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN apt-get update \
        && apt-get install -y aptitude \
        && aptitude install -y mecab libmecab-dev mecab-ipadic-utf8 git make curl xz-utils file swig \
        && mkdir /usr/lib/x86_64-linux-gnu/mecab \
        && mkdir /usr/lib/x86_64-linux-gnu/mecab/dic \
        && cd tmp \
        && git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git \
        && cd mecab-ipadic-neologd \
        && ./bin/install-mecab-ipadic-neologd -n -y \
        && sed -i -e "s%/var/lib/mecab/dic/debian%/usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd%g" /etc/mecabrc \
        && cd /
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ADD . /code/
COPY ./wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh
