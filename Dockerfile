FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install flask werkzeug
EXPOSE 8050
CMD ["python", "app.py"]
