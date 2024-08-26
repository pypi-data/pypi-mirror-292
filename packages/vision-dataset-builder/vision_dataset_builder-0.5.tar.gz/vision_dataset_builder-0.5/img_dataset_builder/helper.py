import os
from .config import config


def get_dirs_inside_data_folder():
    return [
        directory
        for directory in os.listdir(config["raw_data_folder"])
        if os.path.isdir(os.path.join(config["raw_data_folder"], directory))
    ]


def find_duplicate_file_names():
    file_names = set()
    duplicate_file_names = set()
    for directory in get_dirs_inside_data_folder():
        dir_path = os.path.join(
            config["raw_data_folder"], directory, config["image_folder"]
        )
        for _, _, files in os.walk(dir_path):
            for file in files:
                if file in file_names:
                    duplicate_file_names.add(os.path.join(dir_path, file))
                else:
                    file_names.add(file)
    return list(duplicate_file_names)


def check_duplicate_file_names():
    return len(find_duplicate_file_names()) > 0
