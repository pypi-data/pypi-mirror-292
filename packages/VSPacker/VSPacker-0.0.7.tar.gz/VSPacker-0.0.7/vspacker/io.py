import fnmatch
import os
import pathlib
import shutil
import zipfile
from typing import List, Tuple, Union


def zip_files(dir_path, zip_path, exclude_patterns, include_files, overwrite, internal_folder=None):
    files_to_zip = {}

    # Collect files from the directory
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, dir_path)
            if not any(fnmatch.fnmatch(relative_path, pattern) for pattern in exclude_patterns):
                if overwrite or relative_path not in files_to_zip:
                    # If internal_folder is specified, prepend it to the relative path
                    if internal_folder:
                        relative_path = os.path.join(internal_folder, relative_path)
                    files_to_zip[relative_path] = file_path

    # Collect additional files specified in include_files
    for entry in include_files:
        if isinstance(entry, tuple):
            src_file, dest_path = entry
        else:
            src_file = entry
            dest_path = os.path.basename(src_file)

        if not any(
            fnmatch.fnmatch(src_file, pattern) for pattern in exclude_patterns
        ) and os.path.isfile(src_file):
            if overwrite or dest_path not in files_to_zip:
                files_to_zip[dest_path] = src_file

    # Write files to the zip archive
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for filename, file_path in files_to_zip.items():
            zipf.write(file_path, filename)


def pack_to_folder(
    dir_paths: Union[List[str], str],
    output_folder: str,
    exclude_patterns: Union[List[str], str],
    include_files: Union[List[Union[str, Tuple[str, str]]], Union[str, Tuple[str, str]]],
    overwrite: bool,
):
    """Copy files from multiple directories to a single output folder."""
    
    if isinstance(dir_paths, str):
        dir_paths = [dir_paths]
    if isinstance(exclude_patterns, str):
        exclude_patterns = [exclude_patterns]
    if isinstance(include_files, (str, tuple)):
        include_files = [include_files]

    # Copy files from specified directories
    for dir_path in dir_paths:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, dir_path)
                if not any(fnmatch.fnmatch(relative_path, pattern) for pattern in exclude_patterns):
                    output_path = os.path.join(output_folder, relative_path)
                    if overwrite or not os.path.exists(output_path):
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        shutil.copy(file_path, output_path)

    # Include additional files specified in include_files
    for entry in include_files:
        if isinstance(entry, tuple):
            src_file, dest_path = entry
        else:
            src_file = entry
            dest_path = os.path.basename(src_file)

        output_path = os.path.join(output_folder, dest_path)
        if not any(fnmatch.fnmatch(src_file, pattern) for pattern in exclude_patterns) and (
            overwrite or not os.path.exists(output_path)
        ):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            shutil.copy(src_file, output_path)


def unzip(zip_path, out_path):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(out_path)


def pack_example(
    example_file_path: str | List[str],
    version: str,
    output_folder: str,
):
    if isinstance(example_file_path, str):
        example_file_path = [example_file_path]
    for path in example_file_path:
        filename = os.path.basename(path)
        filename_without_extension = pathlib.Path(filename).stem
        file_extension = pathlib.Path(filename).suffix
        new_filename = f"{filename_without_extension}_v{version}{file_extension}"
        example_file_release_path = os.path.join(output_folder, new_filename)
        shutil.copy(path, example_file_release_path)
        return example_file_release_path
