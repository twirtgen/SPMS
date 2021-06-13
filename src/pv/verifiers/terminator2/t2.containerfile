FROM ubuntu:18.04

RUN set -xe
RUN apt-get update 
RUN apt-get install -y binutils
RUN apt-get install -y gnupg gnupg2 gnupg1
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
RUN echo "deb https://download.mono-project.com/repo/ubuntu stable-bionic/snapshots/5.18 main" | tee /etc/apt/sources.list.d/mono-official-stable.list
RUN apt-get update 
RUN apt-get install -y python
RUN apt-get install -y python3
RUN apt-get install -y gcc
RUN apt-get install -y make
RUN apt-get install -y clang-4.0
RUN apt-get install -y mono-complete
RUN apt-get install -y --fix-missing build-essential python mono-complete mono-xbuild fsharp
RUN apt-get install -y git
RUN apt-get install -y wget
RUN git clone https://github.com/mmjb/T2
RUN git clone https://bitbucket.org/spacer/code/src/spacer/
#RUN wget http://nuget.org/nuget.exe
RUN wget https://dist.nuget.org/win-x86-commandline/latest/nuget.exe
RUN chmod +x nuget.exe
WORKDIR spacer/
RUN git checkout spacer-t2
RUN CXX=clang++-4.0 ./configure 
WORKDIR build/
RUN make -j10
RUN make -j10 install
WORKDIR ../src/api/dotnet/
RUN xbuild Microsoft.Z3.csproj
RUN cp obj/Debug/Microsoft.Z3.* /T2/src/
RUN cp ../../../build/libz3.* /T2/src/
WORKDIR /
RUN mozroots --import --sync
WORKDIR /T2/src/
RUN mono /nuget.exe restore
RUN chmod +x packages/FsLexYacc.*/build/*exe 
RUN xbuild 
WORKDIR /T2/src/obj/x86/Debug/
RUN cp /T2/src/Microsoft.Z3.* /T2/src/obj/x86/Debug/
RUN cp /T2/src/libz3.* /T2/src/obj/x86/Debug/
RUN mono /nuget.exe install FsLexYacc.Runtime -Version 7.0.6
RUN cp FsLexYacc.Runtime.7.0.6/lib/portable-net45+netcore45+wpa81+wp8+MonoAndroid10+MonoTouch10/FsLexYacc.Runtime.dll ./
WORKDIR /T2/Mono.Options/
RUN cp bin/Debug/Mono.Options.dll /T2/src/obj/x86/Debug/
WORKDIR /T2/src/obj/x86/Debug/
#RUN ls /T2/src
# mono T2.exe
#ENTRYPOINT ["mono", "/T2/src/obj/x86/Debug/T2.exe"]
COPY t2.sh .
RUN chmod +x t2.sh
ENTRYPOINT ["./t2.sh"]
CMD [""]

