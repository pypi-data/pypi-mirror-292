import os
import paramiko
import winrm
from utils.send_json import send_json_linux, send_json_windows
from config import LINUX_INSTALL_COMMAND, LINUX_INIT_AGENT_COMMAND, LINUX_PERMISSIONS_COMMAND, WINDOWS_DOWNLOAD_URL, WINDOWS_INSTALL_COMMAND, SSH_USER, SSH_KEY_PATH, WINDOWS_USER, WINDOWS_PASSWORD, LOCALE_PATH_LINUX, LOCALE_PATH_WINDOWS, WINDOWS_INIT_AGENT_COMMAND

def install_linux(instance):
    """
    Instala el agente de CloudWatch en una instancia Linux.
    """
    ip_address = instance.public_ip_address
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip_address, username=SSH_USER, key_filename=SSH_KEY_PATH)

    command = LINUX_INSTALL_COMMAND + " && " + LINUX_PERMISSIONS_COMMAND

    stdin, stdout, stderr = ssh.exec_command(command)
    print(stdout.read().decode())
    print(stderr.read().decode())

    path = os.path.join(os.path.dirname(__file__), LOCALE_PATH_LINUX)

    send_file = send_json_linux(ssh, path)

    if send_file:
        print("Archivo JSON enviado con éxito")
        stdin, stdout, stderr = ssh.exec_command(LINUX_INIT_AGENT_COMMAND)
        print(stdout.read().decode())
        print(stderr.read().decode())

    ssh.close()

def install_windows(instance):
    """
    Instala el agente de CloudWatch en una instancia Windows.
    """
    command = WINDOWS_DOWNLOAD_URL + "; " + WINDOWS_INSTALL_COMMAND

    ip_address = instance.public_ip_address
    session = winrm.Session(f'http://{ip_address}:5985/wsman', auth=(WINDOWS_USER, WINDOWS_PASSWORD), transport='ntlm')
    result = session.run_ps(command)
    
    if result.status_code == 0:
        print("Agente de CloudWatch instalado con éxito")
        print("Output: ", result.std_out.decode())
    else:
        print("Error al instalar CloudWatch Agent")
        print("Output: ", result.std_err.decode())

    path = os.path.join(os.path.dirname(__file__), LOCALE_PATH_WINDOWS)

    send_file = send_json_windows(session, path)

    print(send_file)

    result = session.run_ps(WINDOWS_INIT_AGENT_COMMAND)

    if result.status_code == 0:
        print("Agente de CloudWatch iniciado con éxito")
        print("Output: ", result.std_out.decode())
    else:
        print("Error al iniciar CloudWatch Agent")
        print("Output: ", result.std_err.decode())