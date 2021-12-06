FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install -y clang-3.4 llvm-3.4
COPY llvm-3.4_compile.sh compile.sh
RUN chmod +x compile.sh
ENTRYPOINT ["./compile.sh"]
CMD [""]
