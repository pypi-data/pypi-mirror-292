import unittest
import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

class TestSSHConnection(unittest.TestCase):

    def setUp(self):
        # Configura los detalles de la conexión SSH
        self.hostname = os.getenv("TEST_HOSTNAME")
        self.username = os.getenv("SSH_USER")
        self.key_path = os.getenv("SSH_KEY_PATH")

    def test_ssh_connection(self):
        # Crear un cliente SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Intentar establecer la conexión SSH
            ssh_client.connect(hostname=self.hostname, username=self.username, key_filename=self.key_path)

            # Si la conexión se establece correctamente, la prueba pasa
            print(f"Conexión SSH a {self.hostname} establecida correctamente.")
            self.assertTrue(True)

        except Exception as e:
            # Si hay un error, la prueba falla
            print(f"Error al establecer conexión SSH: {e}")
            self.fail("La conexión SSH falló")

        finally:
            # Cerrar la conexión SSH si está abierta
            ssh_client.close()

if __name__ == '__main__':
    unittest.main()
