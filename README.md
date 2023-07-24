# Refresh 1.2.4c
Refresh by Surce v1.2.4c is a Python script that streamlines Docker container management by updating container images in specified directories.

The script scans folders for 'docker-compose.yaml' files, pulls the latest image if outdated, and restarts the container with updated images. It also allows an option to delete old images after updates.

# Features:

Automatic Image Update: Automatically updates Docker container images based on the latest available versions.

'docker-compose.yaml' Scanning: Scans specified directories for 'docker-compose.yaml' files to determine container configurations.

Container Cleanup: Optionally deletes old container images after updates to free up disk space.

Detailed Output: Provides informative output about the current status and actions taken for each container.

User Configuration: Configurable options through 'refresh.conf' file, including image cleanup preference and base directory setting.

Experience hassle-free Docker container updates and efficient management with Refresh by Surce v1.2.4c.

# FAQ
The base_directory in the script acts as the starting point from which the script will search for Docker-related files, specifically the 'docker-compose.yaml' files. The purpose of this variable is to define the top-level directory where all your Docker project folders are located.

When you run the script, it will look for 'docker-compose.yaml' files in all subdirectories of the base_directory. By organizing your Docker projects in separate folders, each containing its own 'docker-compose.yaml' file, you can manage multiple containers independently.

For example, let's say you have multiple Docker projects, and their folder structure is as follows:

/home/pi/composefiles/
    ├── project1/
    │   ├── docker-compose.yaml
    │   └── ...
    ├── project2/
    │   ├── docker-compose.yaml
    │   └── ...
    ├── project3/
    │   ├── docker-compose.yaml
    │   └── ...
    └── ...

Then /home/pi/composefiles should be the base_directory on the refresh.conf file
