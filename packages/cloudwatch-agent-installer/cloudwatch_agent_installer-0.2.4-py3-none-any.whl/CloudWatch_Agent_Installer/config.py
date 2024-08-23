import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Configuracion de AWS
AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Configuracion de CloudWatch Agent
LINUX_INSTALL_COMMAND = "curl https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb -o amazon-cloudwatch-agent.deb && sudo dpkg -i -E amazon-cloudwatch-agent.deb"
LINUX_PERMISSIONS_COMMAND = "sudo rm amazon-cloudwatch-agent.deb && sudo chmod o+w /opt/aws/amazon-cloudwatch-agent/etc/"
LINUX_INIT_AGENT_COMMAND = "sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s"
WINDOWS_DOWNLOAD_URL = "cd .\Downloads\; curl https://amazoncloudwatch-agent.s3.amazonaws.com/windows/amd64/latest/amazon-cloudwatch-agent.msi -o amazon-cloudwatch-agent.msi"
WINDOWS_INSTALL_COMMAND = "msiexec /i amazon-cloudwatch-agent.msi /qn"
WINDOWS_INIT_AGENT_COMMAND = '& "C:/Program Files/Amazon/AmazonCloudWatchAgent/amazon-cloudwatch-agent-ctl.ps1" -a fetch-config -m ec2 -s -c file:"C:/Program Files/Amazon/AmazonCloudWatchAgent/amazon-cloudwatch-agent.json"'

# Configuracion de SSH
SSH_USER = os.getenv("SSH_USER")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH")

# Configuracion de WinRM
WINDOWS_USER = os.getenv("WINDOWS_USER")
WINDOWS_PASSWORD = os.getenv("WINDOWS_PASSWORD")

# Configuracion de archivos
LOCALE_PATH_LINUX = "assets/agent_config_linux.json"
REMOTE_PATH_LINUX = "/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json"

LOCALE_PATH_WINDOWS = "assets/agent_config_windows.json"
REMOTE_PATH_WINDOWS = "C:/Program Files/Amazon/AmazonCloudWatchAgent/amazon-cloudwatch-agent.json"

# Configuraciones adicionales
LOG_FILE_PATH = "/var/log/cloudwatch-agent/cloudwatch-agent-installer.log"