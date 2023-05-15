FROM node:18-alpine
WORKDIR /src
COPY . .
CMD ["node", "python3", "adbs.py"]

