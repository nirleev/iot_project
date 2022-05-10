FROM python:3.10-alpine
WORKDIR /iot_app
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY static/ ./static/
COPY templates/ ./templates/
COPY app.py ./

CMD ["python3", "./app.py"]