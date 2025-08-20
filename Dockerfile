FROM python:3.13-slim-bookworm

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./requirements.txt .
# We don't need to install python3-pip as it's already in the python image
# We also use --no-cache-dir for smaller image size
RUN pip install --no-cache-dir -r ./requirements.txt

COPY . .

# Use JSON array format for CMD
CMD ["python3", "bot.py"]