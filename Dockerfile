FROM node:18-alpine
WORKDIR /src
COPY . .
RUN pip install -r requirements.txt
CMD ["node", "python3", "adbs.py"]

