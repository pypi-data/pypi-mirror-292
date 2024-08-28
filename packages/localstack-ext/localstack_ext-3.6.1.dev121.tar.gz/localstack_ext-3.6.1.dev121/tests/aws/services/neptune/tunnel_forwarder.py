import select
import socketserver as SocketServer

from localstack.utils.threads import FuncThread, start_worker_thread


class ForwardServer(SocketServer.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


class Handler(SocketServer.BaseRequestHandler):
    def handle(self):
        chan = self.ssh_transport.open_channel(
            "direct-tcpip",
            (self.chain_host, self.chain_port),
            self.request.getpeername(),
        )
        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)

        chan.close()
        self.request.close()


def forward_tunnel(local_port, remote_host, remote_port, transport):
    class SubHandler(Handler):
        chain_host = remote_host
        chain_port = remote_port
        ssh_transport = transport

    ForwardServer(("", local_port), SubHandler).serve_forever()


def start_tunnel_thread(
    local_port: int,
    remote_host: str,
    remote_port: int,
    host: str,
    host_port: int = 22,
    username: str = None,
    password: str = None,
    keyfile: str = None,
) -> FuncThread:
    # local import, to enable running "make docker-test" from MacOS
    import paramiko

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    client.connect(
        host,
        host_port,
        username=username,
        key_filename=keyfile,
        password=password,
    )

    def _forward_tunnel(*a, **kw):
        forward_tunnel(local_port, remote_host, remote_port, client.get_transport())

    return start_worker_thread(_forward_tunnel, "port_tunnel")
