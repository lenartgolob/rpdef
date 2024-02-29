FROM python:3.9.10

WORKDIR /app

COPY requirements.txt .
COPY . .

RUN pip install -r requirements.txt

RUN apt-get update && \
   apt-get install -y wget unzip && \
   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
   apt install -y ./google-chrome-stable_current_amd64.deb && \
   wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/121.0.6167.85/linux64/chromedriver-linux64.zip && \
   unzip chromedriver-linux64.zip && \
   mv chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
   rm -rf chromedriver-linux64.zip chrome-stable_current_amd64.deb

CMD ["/bin/bash"]