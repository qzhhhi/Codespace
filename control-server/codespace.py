import asyncio
import os
import pathlib
import uuid

import aiodocker
import aiofiles
import aiohttp
import psutil

frp_server_list = os.environ["CODE_FRP_SERVER_LIST"].split(";")
for i, server in enumerate(frp_server_list):
    server = server.split(":")
    if len(server) == 1:
        frp_server_list[i] = [server[0], "7000"]
    elif len(server) == 2:
        pass
    else:
        raise RuntimeError("unable to resolve frp server list.")


class CodespaceController:
    def __init__(self, loop: asyncio.AbstractEventLoop, logger: object) -> None:
        self.loop = loop
        self.logger = logger
        self.docker = aiodocker.Docker(loop=loop)
        self.container_inactivity_times = {}

    async def run_or_fetch(self, account_data) -> dict:
        acc_id = account_data["_id"]
        container_name = f"alliance-code-server-{account_data['_id']}"

        subdomain = account_data["subdomain"]
        try:
            container = await self.docker.containers.get(container_name)
        except aiodocker.exceptions.DockerError as ex:
            if ex.status != 404:
                raise ex
            token = uuid.uuid4()
            container = await self.docker.containers.create(
                config={
                    "Hostname": "alliance",
                    "Env": [f"LOGIN_TOKEN={token}"],
                    "Image": "qzhhhi/alliance-code-server:latest",
                    "HostConfig": {
                        "CpuPeriod": 100000,
                        "CpuQuota": 200000,
                        "Memory": 2147483648,
                        "MemorySwap": 4294967296,
                        "Binds": [
                            f"/codespace/userdata/{acc_id}:/home/ubuntu/workspace",
                            "/codespace/check-release:/etc/check:ro",
                        ],
                    },
                },
                name=container_name,
            )
            await container.start()
            self.logger.info(f"[{acc_id}] Created & start a container")
            container = await self.docker.containers.get(container._id)
        else:
            env = dict(
                (line.split("=", 1) for line in container._container["Config"]["Env"])
            )
            token = env["LOGIN_TOKEN"]

            status = container._container["State"]["Status"]
            if status == "running":
                pass
            elif status == "exited":
                await container.start()
                self.logger.info(f"[{acc_id}] restarted the container")
                container = await self.docker.containers.get(container._id)
            else:
                raise RuntimeError(f"Unknown container status: {status}.")

        if acc_id in self.container_inactivity_times.keys():
            self.container_inactivity_times[acc_id] = 0
            is_active = True
        else:
            self.container_inactivity_times[acc_id] = 0
            frpc_process = await self.start_frpc(account_data, container, subdomain)
            self.loop.create_task(
                self.monitor_container(account_data, container, frpc_process)
            )
            is_active = False

        return {"active": is_active, "subdomain": subdomain, "token": token}

    async def start_frpc(self, account_data, container, subdomain: str) -> None:
        config_folder_path = f"/tmp/frpc-config/{account_data['_id']}/"
        log_path = f"/var/log/frpc-log/{account_data['_id']}.log"

        # make directory
        pathlib.Path(config_folder_path).mkdir(parents=True, exist_ok=True)

        # clear directory
        for filename in os.listdir(config_folder_path):
            path = os.path.join(config_folder_path, filename)
            if os.path.isfile(path) or os.path.islink(path):
                os.unlink(path)

        # write configuration file
        container_ip = container._container["NetworkSettings"]["IPAddress"]
        for i, (host, port) in enumerate(frp_server_list):
            async with aiofiles.open(
                os.path.join(config_folder_path, f"{i}.toml"), "w"
            ) as f:
                await f.write(
                    f"\nserverAddr = '{host}'"
                    f"\nserverPort = {port}"
                    f"\ntransport.tls.enable = true"
                    f"\ntransport.tls.certFile = '/etc/cert/frp-client.crt'"
                    f"\ntransport.tls.keyFile = '/etc/cert/frp-client.key'"
                    f"\ntransport.tls.trustedCaFile = '/etc/cert/frp-ca.crt'"
                    f"\nlog.to = '{log_path}'"
                    f"\n[[proxies]]"
                    f"\nname = 'web-{subdomain}'"
                    f"\ntype = 'http'"
                    f"\nlocalIP = '{container_ip}'"
                    f"\nlocalPort = 8080"
                    f"\nsubdomain = '{subdomain}'"
                )

        # start frpc process
        process = await asyncio.create_subprocess_exec(
            "/etc/frpc/frpc",
            "--config_dir",
            config_folder_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        self.logger.info(
            f"[{account_data['_id']}] Frpc process pid={process.pid} is started to penetrate {container_ip}"
        )

        return process

    async def monitor_container(
        self, account_data, container, frpc_process: asyncio.subprocess.Process
    ):
        try:
            acc_id = account_data["_id"]
            container_ip = container._container["NetworkSettings"]["IPAddress"]

            p = psutil.Process(frpc_process.pid)

            while True:
                try:
                    await container.wait(
                        timeout=aiohttp.ClientTimeout(
                            total=10 * 60,
                            connect=None,
                            sock_connect=None,
                            sock_read=None,
                        )
                    )
                except asyncio.exceptions.TimeoutError:
                    conn_count = 0
                    for conn in p.connections():
                        conn_count += (
                            conn.raddr.ip == container_ip
                            and conn.status == "ESTABLISHED"
                        )
                    if conn_count == 0:
                        self.container_inactivity_times[acc_id] += 1
                        self.logger.info(
                            f"[{acc_id}] Container is inactive for {self.container_inactivity_times[acc_id]} time(s)"
                        )
                        if self.container_inactivity_times[acc_id] >= 2:
                            await container.stop()
                            self.logger.info(
                                f"[{acc_id}] Container is stopped due to inactivity"
                            )
                            break
                    else:
                        self.container_inactivity_times[acc_id] = 0
                else:
                    break
        finally:
            try:
                frpc_process.terminate()
                self.logger.info(
                    f"[{acc_id}] Frpc process pid={frpc_process.pid} is terminated"
                )
            except ProcessLookupError:
                pass
            del self.container_inactivity_times[acc_id]
