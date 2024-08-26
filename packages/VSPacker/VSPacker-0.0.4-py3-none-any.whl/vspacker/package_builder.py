import os
import shutil

from vspacker.io import pack_example, pack_to_folder, zip_files
from vspacker.vs_project import construct_output_folder, get_info


class AssemblyBuilder:
    def __init__(self, project_file):
        self.project_file = project_file
        self.project_dir = os.path.dirname(project_file)
        self.project_name, self.version = get_info(self.project_file)
        self.output_folder = construct_output_folder(self.project_dir, self.version)
        self.validate_paths()

    def validate_paths(self):
        if not os.path.exists(self.project_dir):
            raise FileNotFoundError(f"Project directory not found: {self.project_dir}")
        if not os.path.exists(self.project_file):
            raise FileNotFoundError(f"Project file not found: {self.project_file}")
        if not self.project_file.endswith(".csproj"):
            raise ValueError(f"Invalid project file: {self.project_file}")

    def build_zip(self, input_dir, zip_filename, exclude_patterns, include_files, internal_folder=None):
        zip_path = os.path.join(self.output_folder, zip_filename)
        zip_files(
            input_dir,
            zip_path,
            exclude_patterns,
            include_files,
            overwrite=True,
        )
        print(f"Plugin built and zipped successfully: {zip_path}")
        return zip_path

    def build_folder(self, dir_paths, folder_name, exclude_patterns, include_files):
        output_folder = os.path.join(self.output_folder, folder_name)
        pack_to_folder(
            dir_paths,
            output_folder,
            exclude_patterns,
            include_files,
            overwrite=True,
        )
        print(f"Plugin built and copied to: {output_folder}")
        return output_folder

    def copy_file(self, src_file, dest_path, rename=None):
        if not os.path.exists(src_file):
            raise FileNotFoundError(f"Source file not found: {src_file}")
        if not os.path.exists(dest_path):
            raise FileNotFoundError(f"Destination path not found: {dest_path}")
        if rename is not None:
            dest_file = os.path.join(dest_path, rename)
        else:
            dest_file = os.path.join(dest_path, os.path.basename(src_file))
        shutil.copy(src_file, dest_file)
        print(f"File copied successfully: {dest_file}")
        return dest_file

    def package_example(self, example_file):
        if not os.path.exists(example_file):
            raise FileNotFoundError(f"Example file not found: {example_file}")
        example_path = pack_example(
            example_file,
            self.version,
            self.output_folder,
        )
        print(f"Example file packaged successfully: {example_path}")
        return example_path
