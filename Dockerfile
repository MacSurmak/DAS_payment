# Use an official Python runtime as a parent image
FROM python:3.12-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Set timezone
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Run bot.py when the container launches
#Отличный анализ, ты попал в самую точку. Проблема именно в конфликте версий зависимостей, и твое упоминание `pip-compile` — это ключ к решению.

### Анализ ошибки

Давай разберем лог, который выдал GitHub Actions:

```
ERROR: Could not find a version that satisfies the requirement typing-inspection==0.9.0
ERROR: No matching distribution found for typing-inspection Use exec form to handle signals properly
CMD ["python3", "bot.py"]