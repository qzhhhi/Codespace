#!/usr/bin/env python3
import os
import pathlib


def main():
    # parse frp server list
    frp_server_list = os.environ["API_FRP_SERVER_LIST"].split(";")
    for i, server in enumerate(frp_server_list):
        server = server.split(":")
        if len(server) == 1:
            frp_server_list[i] = [server[0], "7000"]
        elif len(server) == 2:
            pass
        else:
            raise RuntimeError("unable to resolve frp server list.")

    # make directory
    config_folder_path = f"/tmp/frpc-config/api/"
    pathlib.Path(config_folder_path).mkdir(parents=True, exist_ok=True)

    # clear directory
    for filename in os.listdir(config_folder_path):
        path = os.path.join(config_folder_path, filename)
        if os.path.isfile(path) or os.path.islink(path):
            os.unlink(path)

    # write configuration file
    for i, (host, port) in enumerate(frp_server_list):
        with open(os.path.join(config_folder_path, f"{i}.toml"), "w") as file:
            file.write(
                f"\nserverAddr = '{host}'"
                f"\nserverPort = {port}"
                f"\ntransport.tls.enable = true"
                f"\ntransport.tls.certFile = '/etc/cert/frp-client.crt'"
                f"\ntransport.tls.keyFile = '/etc/cert/frp-client.key'"
                f"\ntransport.tls.trustedCaFile = '/etc/cert/frp-ca.crt'"
                f"\nlog.to = 'console'"
                f"\n[[proxies]]"
                f"\nname = 'web-api'"
                f"\ntype = 'http'"
                f"\nlocalIP = '127.0.0.1'"
                f"\nlocalPort = 5000"
                f"\nsubdomain = 'api'"
            )


if __name__ == "__main__":
    main()
