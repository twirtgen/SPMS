FROM seahorn/seahorn-llvm10:nightly

WORKDIR /opt
COPY seahorn.sh .

WORKDIR /host
COPY pquic-formal-model/verifier pquic-formal-model/verifier
COPY pquic-formal-model/checks pquic-formal-model/checks
COPY pquic-formal-model/pquic/picoquic pquic/picoquic

ENTRYPOINT ["/opt/seahorn.sh"]
