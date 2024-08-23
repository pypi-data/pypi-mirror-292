import boto3
from installer import install_linux, install_windows
from config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


def get_ec2_instances():
    """
    Obtiene las instancias EC2 de la cuenta de AWS en la region especificada.
    """
    ec2 = boto3.resource("ec2", region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    instances = ec2.instances.filter(Filters=[{"Name": "instance-state-name", "Values": ["running"]}])
    return instances


def main():
    """
    Punto de entrada principal del programa.
    Recorre todas las instancias  y ejecuta la instalacion de CloudWatch Agent segun el sistema operativo.
    """

    instances = get_ec2_instances()

    for instance in instances:
        os_type = instance.platform
        if os_type == "windows":
            print(f"Instalando CloudWatch Agent en la instancia Windows {instance.id}")
            install_windows(instance)
        else:
            print(f"Instalando CloudWatch Agent en la instancia Linux {instance.id}")
            install_linux(instance)


if __name__ == "__main__":
    main()