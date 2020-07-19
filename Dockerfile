FROM python:3.7

# Install Chrome binary
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add \
	&& echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
	&& apt-get -y update \
	&& apt-get -y install google-chrome-stable

# Install chromedriver
RUN  wget -N https://chromedriver.storage.googleapis.com/84.0.4147.30/chromedriver_linux64.zip -P ~/ \
	&& unzip ~/chromedriver_linux64.zip -d ~/ \
	&& rm ~/chromedriver_linux64.zip \
	&& mv -f ~/chromedriver /usr/local/bin/chromedriver \
	&& chown root:root /usr/local/bin/chromedriver \
	&& chmod 0755 /usr/local/bin/chromedriver

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENV CHROME_DRIVER_PATH=/usr/local/bin/chromedriver

CMD ["python3", "main.py"]
