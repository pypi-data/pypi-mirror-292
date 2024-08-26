import os
import pathlib
from xml.etree import ElementTree as ET


def construct_output_folder(project_dir, version):
    release_folder = os.path.join(project_dir, "bin", "release", "versions", version)
    pathlib.Path(release_folder).mkdir(parents=True, exist_ok=True)
    return release_folder


def get_info(project_file_path):
    tree = ET.parse(project_file_path)
    root = tree.getroot()
    project_name = root.find(".//Title")
    version = root.find(".//Version")
    return project_name.text if project_name is not None else "Project", (
        version.text if version is not None else "1.0.0"
    )  # (Project, 1.0.0)
