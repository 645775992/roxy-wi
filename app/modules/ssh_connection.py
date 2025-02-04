import paramiko
from paramiko import SSHClient


class SshConnection:
    def __init__(self, server_ip, ssh_port, ssh_user_name, ssh_user_password, ssh_enable, ssh_key_name=None):
        self.ssh = SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.server_ip = server_ip
        self.ssh_port = ssh_port
        self.ssh_user_name = ssh_user_name
        self.ssh_user_password = ssh_user_password
        self.ssh_enable = ssh_enable
        self.ssh_key_name = ssh_key_name

    def __enter__(self):
        try:
            if self.ssh_enable == 1:
                k = paramiko.pkey.load_private_key_file(self.ssh_key_name)
                self.ssh.connect(
                    hostname=self.server_ip,
                    port=self.ssh_port,
                    username=self.ssh_user_name, pkey=k,
                    timeout=11,
                    banner_timeout=200
                )
            else:
                self.ssh.connect(
                    hostname=self.server_ip,
                    port=self.ssh_port,
                    username=self.ssh_user_name,
                    password=self.ssh_user_password,
                    timeout=11,
                    banner_timeout=200
                )
        except paramiko.AuthenticationException:
            raise paramiko.SSHException('error: Authentication failed, please verify your credentials')
        except paramiko.SSHException as sshException:
            raise paramiko.SSHException(f'error: Unable to establish SSH connection: {sshException}')
        except paramiko.PasswordRequiredException as e:
            raise paramiko.SSHException(f'error: {e}')
        except paramiko.BadHostKeyException as badHostKeyException:
            raise paramiko.SSHException(f'error: Unable to verify server\'s host key: {badHostKeyException}')
        except Exception as e:
            if e == "No such file or directory":
                raise paramiko.SSHException(f'error: {e}. Check SSH key')
            elif e == "Invalid argument":
                raise paramiko.SSHException('error: Check the IP of the server')
            else:
                raise paramiko.SSHException(str(e))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ssh.close()

    def run_command(self, command):
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command, get_pty=True, timeout=2)
        except Exception as e:
            raise paramiko.SSHException(str(e))

        return stdin, stdout, stderr

    def get_sftp(self, config_path, cfg):
        try:
            sftp = self.ssh.open_sftp()
        except Exception as e:
            raise paramiko.SSHException(str(e))

        try:
            sftp.get(config_path, cfg)
        except Exception as e:
            sftp.close()
            raise paramiko.SSHException(str(e))

        try:
            sftp.close()
        except Exception as e:
            raise paramiko.SSHException(str(e))

    def put_sftp(self, file, full_path):
        try:
            sftp = self.ssh.open_sftp()
        except Exception as e:
            raise paramiko.SSHException(str(e))

        try:
            sftp.put(file, full_path)
        except Exception as e:
            raise paramiko.SSHException(str(e))

        try:
            sftp.close()
        except Exception as e:
            raise paramiko.SSHException(str(e))
