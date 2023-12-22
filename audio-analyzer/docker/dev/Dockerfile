# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install FFmpeg and other dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavformat-dev \
    libavcodec-dev \
    libavutil-dev \
    libswresample-dev \
    libfftw3-dev \
    build-essential \
    git \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Clone and build libkeyfinder
RUN git clone https://github.com/mixxxdj/libkeyfinder.git \
    && cd libkeyfinder \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make \
    && make install

# Set LD_LIBRARY_PATH to include /usr/local/lib where libkeyfinder.so.2 is installed
ENV LD_LIBRARY_PATH=/usr/local/lib:${LD_LIBRARY_PATH}

# Compile libkeyfinder wrapper
COPY libkeyfinder/wrapper.cpp libkeyfinder/wrapper.cpp
RUN cd libkeyfinder && g++ -shared -o wrapper.so -fPIC wrapper.cpp -lkeyfinder
ENV LIBFINDER_WRAPPER_PATH=/usr/src/app/libkeyfinder/wrapper.so

# Install cython and numpy
RUN pip3 install --no-cache-dir cython numpy

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install madmom from source
RUN git clone https://github.com/CPJKU/madmom.git \
    && cd madmom \
    && git submodule update --init --remote \
    && pip3 install .

# Copy the current directory contents into the container at /usr/src/app
COPY ./src .
COPY ./files files

# Run the Python application on container startup
CMD ["python3", "./main.py"]
