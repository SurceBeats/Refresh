import os
import time
import subprocess
import yaml
import docker
import configparser
import sys

current_directory = os.path.dirname(os.path.abspath(__file__))

def uprint(texto, informacion=None, informacion2=None):
    erase_line = '\x1b[2K'  # Código de escape para borrar la línea actual
    carriage_return = '\r'  # Retorno de carro para el inicio de la línea

    if informacion is not None and informacion2 is not None:
        sys.stdout.write(f"{erase_line}{carriage_return}" + texto + str(informacion) + str(informacion2))
    if informacion is not None:
        sys.stdout.write(f"{erase_line}{carriage_return}" + texto + str(informacion))
    else:
        sys.stdout.write(f"{erase_line}{carriage_return}" + texto)
    sys.stdout.flush()

def check_and_generate_config():
    config_file = os.path.join(current_directory, 'refresh.conf')

    if not os.path.exists(config_file):
        # Si el archivo no existe, lo generamos y añadimos las líneas requeridas
        config = configparser.ConfigParser()
        config['OPTIONS'] = {
            'delete_old_images_after_update': 'no',
            'base_directory': '/home/pi/composefiles'
        }

        with open(config_file, 'w') as configfile:
            config.write(configfile)

def read_config():
    check_and_generate_config()

    config = configparser.ConfigParser()
    config.read(os.path.join(current_directory, 'refresh.conf'))
    delete_old_images_after_update = config.get('OPTIONS', 'delete_old_images_after_update', fallback='no')
    base_directory = config.get('OPTIONS', 'base_directory', fallback='/home/pi/composefiles')
    return delete_old_images_after_update.lower(), base_directory

delete_old_images_after_update, base_directory = read_config()

print()
print("Refresh by Surce v1.2.4c")
print()
print("!! Running from:", current_directory)
if delete_old_images_after_update.lower() == 'yes':
    print("!! Option 'delete_old_images_after_update' is enabled")
else:
    print("!! Option 'delete_old_images_after_update' is disabled")
if base_directory.lower():
    print("!! Base Directory is:", base_directory)

print()
uprint("<> Folder Structure: Scanning folders in", base_directory)
time.sleep(0.1)

def delete_unused_images(container_name):
    client = docker.from_env()

    try:
        container = client.containers.get(container_name)
        images = container.image.history()
        image_ids = {image['Id'] for image in images}
        unused_images = client.images.prune(filters={'dangling': False})
        for image in unused_images.get('ImagesDeleted', []):
            if image.get('Deleted') and image['Deleted'] not in image_ids:
                uprint(f"<> Deleted unused image: {image['Deleted']}")
                time.sleep(0.1)
    except docker.errors.NotFound:
        uprint(f"<> Container '{container_name}' not found.")
        time.sleep(0.1)
def find_docker_compose_files(directory):
    docker_compose_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file == "docker-compose.yml":
                docker_compose_files.append(os.path.join(root, file))
    return docker_compose_files

def update_containers():
    docker_compose_files = find_docker_compose_files(base_directory)

    if not docker_compose_files:
        uprint("<> Image Status: No 'docker-compose.yml' files found in", base_directory)
        time.sleep(0.1)
        return

    for file_path in docker_compose_files:
        folder = os.path.dirname(file_path)
        uprint(f"<> Processing folder: {folder}")
        time.sleep(0.1)
        os.chdir(folder)

        with open("docker-compose.yml", "r") as compose_file:
            try:
                compose_data = yaml.safe_load(compose_file)
            except yaml.YAMLError as exc:
                uprint("<> Image Status: Unable to parse docker-compose.yml file in", folder)
                time.sleep(0.1)
                uprint(exc)
                time.sleep(0.1)
                continue

        services = compose_data.get("services")
        if not services:
            uprint("<> Image Status: No 'services' section found in docker-compose.yml... Skipping Update")
            time.sleep(0.1)
            continue

        service_name = next(iter(services))
        service_data = services[service_name]

        docker_image = service_data.get("image")
        docker_hostname = service_data.get("container_name")

        if not docker_image or not docker_hostname:
            uprint("<> Image Status: Unable to find 'image' or 'container_name' in docker-compose.yml file... Skipping Update")
            time.sleep(0.1)
            continue

        uprint("<> Current image for container is: ", docker_image)
        time.sleep(0.1)
        uprint("<> Current hostname for container is: ", docker_hostname)
        time.sleep(0.1)

        try:
            # Use subprocess to run docker pull and check the output with grep
            pull_process = subprocess.run(["sudo", "docker", "pull", docker_image], capture_output=True, text=True)
            if "Image is up to date" in pull_process.stdout:
                uprint("")
                print("\033[1;32;40m<>\033[0m Up to date:", docker_hostname)
                time.sleep(0.1)
            else:
                uprint("")
                print("\033[1;31;40m<>\033[0m Outdated:  ", docker_hostname)
                time.sleep(0.1)
                subprocess.run(["sudo", "docker-compose", "stop", docker_hostname])
                subprocess.run(["sudo", "docker-compose", "rm", "-f", docker_hostname])
                subprocess.run(["sudo", "docker-compose", "pull", docker_hostname])
                subprocess.run(["sudo", "docker-compose", "up", "-d", docker_hostname])
                if delete_old_images_after_update == 'yes':
                    delete_unused_images(docker_hostname)

        except Exception as e:
            uprint(f"<> Error occurred while updating container: {e}", "")
            time.sleep(0.1)

delete_old_images_after_update, _ = read_config()  # Solo necesitamos el primer valor de la configuración
update_containers()
print()
uprint("\033[1;32;40m<>\033[0m Finished!")
print()
print()
