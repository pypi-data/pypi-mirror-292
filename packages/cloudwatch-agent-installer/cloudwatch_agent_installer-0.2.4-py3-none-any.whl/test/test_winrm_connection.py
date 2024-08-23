import winrm
import unittest
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print(os.getenv("WINDOWS_PASSWORD"))

class TestWinrmConnection(unittest.TestCase):

    def setUp(self):
        # Configura los detalles de la conexión SSH
        self.hostname = "3.140.248.36"
        self.username = os.getenv("WINDOWS_USER")
        self.user_password = os.getenv("WINDOWS_PASSWORD")

    def test_connection_windows(self):
        try:
            print(f"Conectando a {self.hostname} con usuario {self.username} y contraseña {self.user_password}")
            session = winrm.Session(f'http://{self.hostname}:5985/wsman', auth=(self.username, self.user_password), transport='ntlm')
            result = session.run_ps('ipconfig')
            print(result.status_code)
            print(result.std_out.decode())
            print(result.std_err.decode())
            self.assertTrue(True)
        except Exception as e:
            print(f"Error al establecer conexión WinRM: {e}")
            self.fail("La conexión WinRM falló " + self.user_password)

if __name__ == "__main__":
    unittest.main()
