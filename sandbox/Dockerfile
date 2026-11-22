# Minimal isolated Lean 4 execution runner for untrusted repository verification.
# Security invariants (see sandbox/README.md):
#   - Untrusted repo builds ALWAYS run with:
#       --network=none --user 65534:65534 --cap-drop=ALL
#       --security-opt=no-new-privileges:true
#   - Toolchains and pre-fetched Mathlib caches are mounted read-only at runtime.
#   - Build scratch space lives solely inside ephemeral /work (destroyed on --rm).
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive \
    ELAN_HOME=/opt/elan \
    PATH=/opt/elan/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    HOME=/tmp \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      git \
      libgmp10 \
      python3 \
      tar \
      xz-utils \
      zstd \
    && rm -rf /var/lib/apt/lists/*

# Install elan binary into /opt/elan-bin (separate from the bind-mounted /opt/elan toolchain store
# so /opt/elan can be mounted read-only from the host cache without hiding elan itself).
RUN mkdir -p /opt/elan-bootstrap /opt/elan /work \
    && curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
         | ELAN_HOME=/opt/elan-bootstrap sh -s -- -y --default-toolchain none --no-modify-path \
    && mv /opt/elan-bootstrap/bin /opt/elan-bin \
    && rm -rf /opt/elan-bootstrap \
    && chmod -R a+rX /opt/elan-bin /opt/elan \
    && chown 65534:65534 /work

ENV PATH=/opt/elan-bin:/opt/elan/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

COPY check_axioms.lean /opt/sandbox/check_axioms.lean
COPY container_entry.py /opt/sandbox/container_entry.py
RUN chmod -R a+rX /opt/sandbox

WORKDIR /work
ENTRYPOINT ["python3", "/opt/sandbox/container_entry.py"]
