# Use a minimal base image with Python
FROM python:3.10-slim

# Define the Chrome/Chromedriver version to install
ENV CHROME_VERSION=114.0.5735.90

# Install system dependencies and download Chrome for Testing v114 
RUN apt-get update && apt-get install -y \
      wget \
      curl \
      unzip \
      gnupg \
      libglib2.0-0 \
      libnss3 \
      libgconf-2-4 \
      libfontconfig1 \
      libxss1 \
      libappindicator3-1 \
      libasound2 \
      libatk-bridge2.0-0 \
      libgtk-3-0 \
      libgbm1 \
      libx11-xcb1 \
      libxcomposite1 \
      libxdamage1 \
      libxrandr2 \
      libu2f-udev \
      fonts-liberation \
      libxcb-dri3-0 \
      xdg-utils \
      --no-install-recommends \
  && wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}/linux64/chrome-linux64.zip \
  && unzip chrome-linux64.zip \
  && mv chrome-linux64 /opt/chrome \
  && rm chrome-linux64.zip

# Symlink the fresh Chromium and install matching ChromeDriver from Google’s storage bucket
RUN rm -f /usr/bin/chromium \
  && ln -s /opt/chrome/chrome /usr/bin/chromium \
  \
  && wget https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip \
     -O chromedriver_linux64.zip \
  && unzip chromedriver_linux64.zip \
  && mv chromedriver /usr/bin/chromedriver \
  && chmod +x /usr/bin/chromedriver \
  && rm chromedriver_linux64.zip \
  \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Verify that both are v114.0.5735.90
RUN /usr/bin/chromium --version \
  && /usr/bin/chromedriver --version

# Expose Chrome binary in the env
ENV CHROME_BIN=/usr/bin/chromium  
ENV PATH="/usr/bin:$PATH"

# Application setup
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "chatgpt_v5.3.py", "--server.port=8501", "--server.address=0.0.0.0"]
