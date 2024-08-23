import unittest
import os
import paramiko
from dotenv import load_dotenv

load_dotenv()

path = os.path.abspath(__file__)

old_path = os.path.dirname(path)

father_path = os.path.dirname(old_path)

directory = os.getenv("LOCAL_PATH")

new_path = os.path.join(father_path, directory)

def install_linux():
    """
    Instala el agente de CloudWatch en una instancia Linux.
    """

    try:
        ip_address = os.getenv("TEST_HOSTNAME")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip_address, username=os.getenv("SSH_USER"), key_filename=os.getenv("SSH_KEY_PATH"))

        # stdin, stdout, stderr = ssh.exec_command(LINUX_INSTALL_COMMAND)
        # print(stdout.read().decode())
        # print(stderr.read().decode())

        # ssh.close()

        sftp = ssh.open_sftp()
        sftp.put(new_path, os.getenv("REMOTE_PATH"))

        sftp.close()

        return True
    except Exception as e:
        return False

class TestInstaller(unittest.TestCase):
    def test_install_linux(self):
        # test para la instalacion en linux
        instance = 'i-0d5a011436478a2fc'
        result = install_linux()
        self.assertTrue(result, f"Instalando CloudWatch Agent en la instancia Linux {instance}")

    # def test_install_windows(self):
    #     # Test para la instalacion en windows
    #     result = install_windows("i-1234567890abcdef0")
    #     self.assertEqual(result, "Instalando CloudWatch Agent en la instancia Windows i-1234567890abcdef0")
    #     self.assertTrue(result, "Fallo instalacion de CloudWatch Agent en la instancia Windows i-1234567890abcdef0")


if __name__ == "__main__":
    unittest.main()
