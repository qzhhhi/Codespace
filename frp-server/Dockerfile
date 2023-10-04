FROM ubuntu:22.04

# Install nginx
RUN apt-get update && apt-get -y install \
    nginx curl && \
    rm -rf /var/lib/apt/lists/*

# Add tini
RUN curl -o /usr/bin/tini -fL https://github.com/krallin/tini/releases/download/v0.19.0/tini && \
    chmod +x /usr/bin/tini

# Install frps latest
RUN FRP_LATEST_VER=$(curl -fsSL https://api.github.com/repos/fatedier/frp/releases/latest | grep "tag_name" | cut -d'v' -f2 | cut -d'"' -f1) && \
    echo "Get frp latest version: ${FRP_LATEST_VER}" && \
    curl -o frp.tar.gz -fL "https://github.com/fatedier/frp/releases/download/v${FRP_LATEST_VER}/frp_${FRP_LATEST_VER}_linux_amd64.tar.gz" && \
    mkdir frp-temp && tar -zxf frp.tar.gz -C frp-temp --strip-components 1 && \
    mkdir /etc/frps && mv frp-temp/frps /etc/frps/ && rm -f frp.tar.gz && rm -rf frp-temp

COPY nginx.conf /etc/nginx/nginx.conf
COPY frps.ini 404.html /etc/frps/

COPY ./entry-point.sh /usr/bin/entry-point.sh

EXPOSE 7000
EXPOSE 80
EXPOSE 443

ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD [ "/usr/bin/entry-point.sh" ]