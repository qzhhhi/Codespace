FROM ubuntu:22.04

WORKDIR /root

# Change bash as default shell
SHELL ["/bin/bash", "-c"]

# Set timezone
RUN export TZ="Asia/Shanghai" && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

# Unminimize ubuntu, install tools & dependencies, virtual screen & desktop
RUN yes | unminimize && \
    apt-get update && apt-get -y install \
    apt-transport-https \
    git \
    vim nano \
    wget curl gpg \
    unzip \
    build-essential \
    clang clangd \
    cmake \
    make ninja-build \
    zsh \
    sudo \
    x11vnc xvfb fluxbox \
    && rm -rf /var/lib/apt/lists/*

# Install cs50 library
RUN curl -s https://packagecloud.io/install/repositories/cs50/repo/script.deb.sh | bash && \
    apt-get install libcs50 && rm -rf /var/lib/apt/lists/*

# Install vscode latest
RUN wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg && \
    install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg && \
    sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list' && \
    rm -f packages.microsoft.gpg && \
    sudo apt-get update && \
    sudo apt-get -y install code

# Install frpc latest
RUN FRP_LATEST_VER=$(curl -fsSL https://api.github.com/repos/fatedier/frp/releases/latest | grep "tag_name" | cut -d'v' -f2 | cut -d'"' -f1) && \
    echo "Get frp latest version: ${FRP_LATEST_VER}" && \
    curl -o frp.tar.gz -fL "https://github.com/fatedier/frp/releases/download/v${FRP_LATEST_VER}/frp_${FRP_LATEST_VER}_linux_amd64.tar.gz" && \
    mkdir frp-temp && tar -zxf frp.tar.gz -C frp-temp --strip-components 1 && \
    mkdir /etc/frpc && mv frp-temp/frpc /etc/frpc/ && rm -f frp.tar.gz && rm -rf frp-temp

# Add tini
RUN wget -O /usr/bin/tini https://github.com/krallin/tini/releases/download/v0.19.0/tini && \
    chmod +x /usr/bin/tini

# Add user
RUN useradd -m ubuntu && echo "ubuntu:ubuntu" | chpasswd && adduser ubuntu sudo && \
    echo "ubuntu ALL=(ALL:ALL)  NOPASSWD:ALL" >> /etc/sudoers

# Set user
USER ubuntu
WORKDIR /home/ubuntu
ENV USER=ubuntu
ENV WORKDIR=/home/ubuntu

# Install oh my zsh & change theme to af-magic
RUN set -eo pipefail && \
    curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh | sh && \
    sed -i 's/ZSH_THEME=\"[a-z0-9\-]*\"/ZSH_THEME="af-magic"/g' .zshrc && \
    echo "$USER" | chsh -s $(which bash)

# Install vscode extensions
RUN code --extensions-dir  .vscode-server/extensions \
    --install-extension MS-CEINTL.vscode-language-pack-zh-hans \
    --install-extension llvm-vs-code-extensions.vscode-clangd \
    --install-extension twxs.cmake \
    --install-extension ms-vscode.cmake-tools \
    --install-extension ms-vscode.hexeditor \
    --install-extension yzhang.markdown-all-in-one \
    --install-extension Gruntfuggly.global-config

# Install vscode extension: codelldb
RUN curl -o codelldb.vsix -fL https://github.com/vadimcn/codelldb/releases/download/v1.10.0/codelldb-x86_64-linux.vsix && \
    code --extensions-dir .vscode-server/extensions --install-extension codelldb.vsix && \
    rm codelldb.vsix

# Download latest vscode-server cli data
RUN code serve-web --cli-data-dir ~/.vscode-server/cli --host 0.0.0.0 --port 8080 --without-connection-token --accept-server-license-terms & \
    sleep 1 && curl --noproxy '*' -fsSL 127.0.0.1:8080 && \
    while curl --noproxy '*' -fsSL 127.0.0.1:8080 | grep 'is downloading, please wait'; do sleep 5; done

# Copy files
COPY --chown=ubuntu:ubuntu ./vscode/config/settings.json .vscode-server/data/Machine/
COPY  --chown=ubuntu:ubuntu ./vscode/config/launch.json ./vscode/config/tasks.json .vscode-server/config/
COPY ./fluxbox/styles/ /usr/share/fluxbox/styles/
COPY ./fluxbox/wallpapers/ /usr/share/images/fluxbox/
COPY  --chown=ubuntu:ubuntu ./fluxbox/userconfig/ .fluxbox/
COPY ./frpc/ /etc/frpc
# COPY ./stm32cubemx .stm32cubemx

COPY ./entry-point.sh /usr/bin/entry-point.sh

EXPOSE 8080
EXPOSE 5900

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/usr/bin/entry-point.sh"]