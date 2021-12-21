#FROM ubuntu:16.04

#RUN apt-get update
#RUN apt-get install -y clang-3.6 llvm-3.6
#RUN ln -s /usr/bin/clang-3.6 /usr/bin/clang
FROM silkeh/clang:3.6
COPY llvm-3.4_compile.sh compile.sh
RUN chmod +x compile.sh
ENTRYPOINT ["./compile.sh"]
CMD [""]
