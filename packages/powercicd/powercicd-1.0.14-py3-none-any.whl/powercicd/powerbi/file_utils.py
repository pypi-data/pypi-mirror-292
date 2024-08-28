import os


def find_parent_dir_where_exists_file(start_path: str, file: str) -> str:
    start_path = os.path.normpath(start_path)
    folder = start_path
    while True:
        project_config_path = os.path.join(folder, file)
        if os.path.exists(project_config_path):
            return folder
        prev_folder = folder
        folder = os.path.dirname(folder)
        if folder == prev_folder or folder == "/" or folder == "" or folder is None:
            raise Exception(f"{file} not found in any parent directory")

