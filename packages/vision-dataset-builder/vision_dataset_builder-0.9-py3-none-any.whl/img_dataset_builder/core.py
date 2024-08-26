import os
import shutil
import splitfolders
from .helper import (
    get_dirs_inside_data_folder,
    check_duplicate_file_names,
    find_duplicate_file_names,
)
from .config import load_config

def clean_image_bank(config=None):
    if config is None:
        config = load_config()

    if os.path.exists(config["image_bank_folder"]):
        shutil.rmtree(config["image_bank_folder"])
        print("Image bank has been cleaned.")
    else:
        print("Image bank does not exist.")

def create_image_bank_folders(config=None):
    if config is None:
        config = load_config()

    os.makedirs(
        os.path.join(config["image_bank_folder"], config["image_folder"]), exist_ok=True
    )
    os.makedirs(
        os.path.join(config["image_bank_folder"], config["label_folder"]), exist_ok=True
    )

def copy_all_images(config=None):
    if config is None:
        config = load_config()

    if check_duplicate_file_names():
        print("Duplicate file names exist. Cannot merge images.")
        for file in find_duplicate_file_names():
            print(file)
    else:
        for directory in get_dirs_inside_data_folder():
            source_dir = os.path.join(
                config["raw_data_folder"], directory, config["image_folder"]
            )
            destination_dir = os.path.join(
                config["image_bank_folder"], config["image_folder"]
            )
            shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
        print("All images have been successfully copied to the image bank.")

def copy_all_labels(config=None):
    if config is None:
        config = load_config()

    for directory in get_dirs_inside_data_folder():
        source_dir = os.path.join(
            config["raw_data_folder"], directory, config["label_folder"]
        )
        destination_dir = os.path.join(
            config["image_bank_folder"], config["label_folder"]
        )
        shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
    print("All labels have been successfully copied to the image bank.")

def clean_dataset(config=None):
    if config is None:
        config = load_config()

    if os.path.exists(config["dataset_folder"]):
        shutil.rmtree(config["dataset_folder"])
        print("Dataset has been cleaned.")
    else:
        print("Dataset does not exist.")

def create_dataset_folders(config=None):
    if config is None:
        config = load_config()

    os.makedirs(os.path.join(config["dataset_folder"], "train"), exist_ok=True)
    os.makedirs(os.path.join(config["dataset_folder"], "validation"), exist_ok=True)
    os.makedirs(os.path.join(config["dataset_folder"], "test"), exist_ok=True)

def split_image_bank(config=None):
    """
    Split the image bank into train, validation, and test sets.
    """
    if config is None:
        config = load_config()

    if not os.path.exists(config["image_bank_folder"]):
        print("Image bank does not exist.")
        return

    # Clean any existing dataset folder
    clean_dataset(config)

    # Create dataset folders
    if not os.path.exists(config["dataset_folder"]):
        create_dataset_folders(config)

    # Split the image bank into train, validation, and test sets
    splitfolders.ratio(
        config["image_bank_folder"],
        output=config["dataset_folder"],
        seed=config.get("seed", 42),
        ratio=(config["train_ratio"], config["validation_ratio"], config["test_ratio"]),
    )

    print(
        "Image bank has been successfully split into train, validation, and test sets."
    )

def copy_all(config=None):
    """
    Copy all images and labels from raw_data to image_bank.
    """
    if config is None:
        config = load_config()

    clean_image_bank(config)
    create_image_bank_folders(config)
    copy_all_images(config)
    copy_all_labels(config)
