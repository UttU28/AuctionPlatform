FROM python:3.9-slim
ARG ENV DEBIAN_FRONTEND=noninteractive

ENV ACCEPT_EULA=Y

# Update and install system dependencies
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    gnupg \
    unixodbc-dev \
    build-essential \
    python3-pip \
    wget \
    git \
    unzip \
    gnupg2 \
    apt-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC drivers and tools
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends --allow-unauthenticated \
    msodbcsql17 \
    mssql-tools && \
    echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile && \
    echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt update
RUN apt -y upgrade

# Set working directory and copy application files
WORKDIR /app
COPY . /app

# Upgrade pip and install Python dependencies
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt

# Define the command to run the application
# CMD ["python3", "app.py"]
EXPOSE 50505
ENTRYPOINT ["gunicorn", "app:app"]