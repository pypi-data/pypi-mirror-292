# CloudWatch Agent Installer

Este proyecto proporciona una solución para instalar el Amazon CloudWatch Agent en instancias EC2 de Linux y Windows. El programa automatiza la configuración y la instalación del agente en instancias EC2 utilizando Python.

## Características

- **Automatización de Instalación**: Instala CloudWatch Agent en instancias EC2 de Linux y Windows.
- **Compatibilidad con SSH y WinRM**: Utiliza conexiones SSH para Linux y WinRM para Windows.
- **Configuración Flexible**: Configura parámetros de instalación y credenciales mediante el archivo `config.py`.

## Requisitos

- **Python 3.x**: Asegúrate de tener Python 3.x instalado en tu máquina.
- **AWS Credentials**: Necesitas tener configuradas tus credenciales de AWS (clave de acceso y secreto).
- **Permisos**: Debes tener permisos para gestionar instancias EC2 en tu cuenta de AWS.
- **Dependencias**: Las dependencias están listadas en `requirements.txt`.

## Instalación

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/JoseDavidN/CloudWatch_Agent_Installer.git
   cd CloudWatch_Agent_Installer
2. **Crea y activa un entorno virtual** (opcional, pero recomendado)
   ```bash
   python3 -m venv venv #En Windows: python -m venv venv
   source venv/bin/activate #En Windows:  source venv/Scripts/activate
3. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
4. **Copiar el archivo de variables de entorno**
   ```bash
   cp .env.example .env
5. **Configura las variables de entorno**  
   - Asegurate de que las variables de entorno estan correctamente configuradas
   - Alternativamente, puedes editar el archivo `config.py` para configurar tus credenciales (No recomendado por razones de seguridad)

## Uso

Para ejecutar el programa simplemente ejecute el archivo `main.py`:
   ```bash
   python3 main.py #En windows: python main.py
   ```

## Estructura del proyecto
- `CloudWatch_Agent_Install/config.py`: Archivo de configuracion para parametros del proyecto
- `CloudWatch_Agent_Install/installer.py`: Contiene las funciones para instalar el CloudWatch Agent en linux y windows
- `CloudWatch_Agent_Install/main.py`: Punto de entrada principal del programa que coordina la instalacion
- `requirements.txt`: Lista de dependencias del proyecto
- `README.md`: Documentacion del proyecto

## Contribuciones

Las contribuciones son bienvenidas. Por favor hable un issue o un pull request si deseas contribuir al proyecto. Para detalles sobre el proceso de contribucion consulta el archivo [CONTRIBUTING.md](CONTRIBUTING.md) si esta disponible.

## Licencia

Este proyecto esta licenciado bajo la Licencia MIT. Consulte el archivo `LICENCE` para mas detalles.

## Contacto
Para preguntas o soporte adicional por favor contacta a [gomezjosedavid997@gmail.com](mailto:gomezjosedavid997@gmail.com).