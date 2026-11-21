import subprocess
import time
import paramiko
import pytest

server_ip = "172.20.10.9"
username = "mac"
password = ""
port = 22


@pytest.fixture(scope="function")
def server():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    server_error = ""
    channel = None

    try:
        ssh.connect(
            hostname=server_ip,
            port=port,
            username=username,
            password=password,
            timeout=10,
            look_for_keys=False,
            allow_agent=False,
        )
        transport = ssh.get_transport()
        channel = transport.open_session()
        cmd = "export PATH=/usr/local/bin:/opt/homebrew/bin:$PATH; iperf3 -s -1"
        channel.exec_command(cmd)
        time.sleep(2.0)

        if channel.exit_status_ready() and channel.recv_exit_status() != 0:
            err_out = channel.recv_stderr(1024).decode("utf-8", errors="ignore").strip()
            server_error = err_out or "iperf3 server exited with non-zero status"
    except Exception as exc:
        server_error = str(exc)

    yield server_error

    try:
        if ssh.get_transport() and ssh.get_transport().is_active():
            ssh.exec_command("pkill -f 'iperf3 -s -1' || true", timeout=5)
    except Exception:
        pass
    finally:
        if channel is not None and not channel.closed:
            channel.close()
        ssh.close()


@pytest.fixture(scope="function")
def client(server):
    if server:
        return "", f"Server connection error: {server}"

    process = subprocess.Popen(
        ["iperf3", "-c", server_ip, "-i", "1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0 and not stderr:
        stderr = f"iperf3 завершився з кодом {process.returncode}"
    return stdout, stderr