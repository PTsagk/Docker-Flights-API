FROM python

ADD main.py .

RUN pip install flask pymongo

CMD ["python","./main.py"]