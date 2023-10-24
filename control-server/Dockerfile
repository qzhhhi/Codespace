FROM ubuntu:22.04

WORKDIR /root

# Change bash as default shell
SHELL ["/bin/bash", "-c"]

# Install python
RUN apt-get update && apt-get -y install \
    curl unzip python3.10 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Add tini
RUN curl -o /usr/bin/tini -fL https://github.com/krallin/tini/releases/download/v0.19.0/tini && \
    chmod +x /usr/bin/tini

# Install frpc latest
RUN FRP_LATEST_VER=$(curl -fsSL https://api.github.com/repos/fatedier/frp/releases/latest | grep "tag_name" | cut -d'v' -f2 | cut -d'"' -f1) && \
    echo "Get frp latest version: ${FRP_LATEST_VER}" && \
    curl -o frp.tar.gz -fL "https://github.com/fatedier/frp/releases/download/v${FRP_LATEST_VER}/frp_${FRP_LATEST_VER}_linux_amd64.tar.gz" && \
    mkdir frp-temp && tar -zxf frp.tar.gz -C frp-temp --strip-components 1 && \
    mkdir /etc/frpc && mv frp-temp/frpc /etc/frpc/ && rm -f frp.tar.gz && rm -rf frp-temp

# Install python packages
RUN pip3 install hypercorn quart pymongo aiofiles psutil

# Install aiodocker (add a feature that allow custom event loops)
RUN curl -o aiodocker.zip -fL https://github.com/qzhhhi/aiodocker/archive/refs/heads/master.zip && \
    unzip aiodocker.zip && \
    pip3 install ./aiodocker-master && \
    rm -rf ./aiodocker-master && rm -f ./aiodocker.zip

RUN mkdir -p /var/log/frpc-log/

COPY ./*.py /www/
COPY ./frpc.toml /etc/frpc/
COPY ./entry-point.sh /usr/bin/entry-point.sh

ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD [ "/usr/bin/entry-point.sh" ]