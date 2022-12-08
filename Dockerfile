FROM python:3.8.10

WORKDIR /home/user/

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
    
CMD ["python3", "philosophy_api.py"]