FROM ubuntu:14.04

RUN set -xe
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update 
RUN apt-get install -y binutils
RUN apt-get install -y python
RUN apt-get install -y python3
RUN apt-get install -y gcc
RUN apt-get install -y make
RUN apt-get install -y git
RUN apt-get install -y wget
RUN apt-get install -y cmake
RUN apt-get install -y libgmp10 libgmp10-dev
RUN apt-get install -y build-essential
RUN apt-get install -y libz-dev libtinfo-dev 
RUN apt-get install -y llvm-3.4
RUN git clone https://github.com/hkhlaaf/llvm2kittel
RUN mkdir llvm2kittelbuild
WORKDIR llvm2kittelbuild
ENV CXX g++
RUN ln -s /usr/bin/llvm-config-3.4 /usr/bin/llvm-config
RUN cmake -DCMAKE_PREFIX_PATH=./ ../llvm2kittel/
RUN make
COPY llvm2kittel.sh /
RUN chmod +x /llvm2kittel.sh
RUN ls -la
ENTRYPOINT ["/llvm2kittel.sh"]
CMD [""]
