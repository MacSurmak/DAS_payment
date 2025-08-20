FROM buildpack-deps:bookworm

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./requirements.txt .
RUN apt update
RUN apt install python3-pip -y
RUN pip install -r ./requirements.txt --break-system-packages
COPY . .
CMD python3 bot.py