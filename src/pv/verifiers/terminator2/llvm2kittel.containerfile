FROM ubuntu:16.04

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
RUN apt-get install -y llvm-3.6
RUN apt-get install -y libedit-dev
RUN git clone https://github.com/hkhlaaf/llvm2kittel
RUN mkdir llvm2kittelbuild
WORKDIR llvm2kittelbuild
#ENV CXX clang-3.6
RUN apt-get install -y clang-3.6
RUN ln -s /usr/bin/llvm-config-3.6 /usr/bin/llvm-config
RUN cmake -DCMAKE_BUILD_TYPE=Release \
          -DLLVM_CONFIG_EXECUTABLE=/usr/bin/llvm-config-3.6 \
          -DCMAKE_C_COMPILER=clang-3.6 \
          -DCMAKE_CXX_COMPILER=clang++-3.6 \
	  -DCMAKE_PREFIX_PATH=./ ../llvm2kittel/
RUN make
COPY llvm2kittel.sh /
RUN chmod +x /llvm2kittel.sh
RUN ls -la
ENTRYPOINT ["/llvm2kittel.sh"]
CMD [""]
