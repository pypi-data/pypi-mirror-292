import fnmatch
import os
import pathlib
import shutil
import zipfile
from typing import List

# def zip_files(
#     zip_filename,
#     project_dir,
#     file_patterns,
#     exclude_patterns,
#     include_files,
#     overwrite,
#     project_name,
#     output_folder,
# ):
#     zip_path = os.path.join(output_folder, zip_filename)
#     project_folder_in_zip = f"{project_name}/"
#     files_to_zip = {}
#     target_dir = os.path.join(project_dir, "bin", "release", "net48")
#     for filename in os.listdir(target_dir):
#         file_path = os.path.join(target_dir, filename)
#         if os.path.isfile(file_path):
#             if not any(fnmatch.fnmatch(filename, pattern) for pattern in exclude_patterns) and any(
#                 fnmatch.fnmatch(filename, pattern) for pattern in file_patterns
#             ):
#                 if overwrite or filename not in files_to_zip:
#                     files_to_zip[filename] = file_path
#     for file in include_files:
#         if (
#             not any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns)
#             and any(fnmatch.fnmatch(file, pattern) for pattern in file_patterns)
#             and os.path.isfile(file)
#         ):
#             basename = os.path.basename(file)
#             if overwrite or basename not in files_to_zip:
#                 files_to_zip[basename] = file
#     with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
#         for filename, file_path in files_to_zip.items():
#             zipf.write(file_path, project_folder_in_zip + filename)
#     return zip_path


def zip_files(dir_path, zip_path, exclude_patterns, include_files, overwrite):
    files_to_zip = {}
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, dir_path)
            if not any(fnmatch.fnmatch(relative_path, pattern) for pattern in exclude_patterns):
                if overwrite or relative_path not in files_to_zip:
                    files_to_zip[relative_path] = file_path
    for file in include_files:
        if not any(
            fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns
        ) and os.path.isfile(file):
            basename = os.path.basename(file)
            if overwrite or basename not in files_to_zip:
                files_to_zip[basename] = file
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for filename, file_path in files_to_zip.items():
            zipf.write(file_path, filename)


def pack_to_folder(
    dir_paths: List[str] | str,
    output_folder: str,
    exclude_patterns: List[str] | str,
    include_files: List[str] | str,
    overwrite: bool,
):
    """Copy files from multiple directories to a single output folder.

    Args:
        dir_paths (List[str] | str): directories to copy files from
        output_folder (str): destination folder
        exclude_patterns (List[str]): patterns to exclude files from being copied
        include_files (List[str]): external files to include in the output folder
        overwrite (bool): overwrite existing files
    """
    if isinstance(dir_paths, str):
        dir_paths = [dir_paths]
    if isinstance(exclude_patterns, str):
        exclude_patterns = [exclude_patterns]
    if isinstance(include_files, str):
        include_files = [include_files]
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

    for file in include_files:
        output_path = os.path.join(output_folder, os.path.basename(file))
        if not any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns) and (
            overwrite or not os.path.exists(output_path)
        ):
            shutil.copy(file, output_path)


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
