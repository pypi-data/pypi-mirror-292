import os
import shutil
import splitfolders
from .helper import (
    get_dirs_inside_data_folder,
    check_duplicate_file_names,
    find_duplicate_file_names,
)
from .config import config


def clean_image_bank():
    if os.path.exists(config["image_bank_folder"]):
        shutil.rmtree(config["image_bank_folder"])
        print("Image bank has been cleaned.")
    else:
        print("Image bank does not exist.")


def create_image_bank_folders():
    os.makedirs(
        os.path.join(config["image_bank_folder"], config["image_folder"]), exist_ok=True
    )
    os.makedirs(
        os.path.join(config["image_bank_folder"], config["label_folder"]), exist_ok=True
    )


def copy_all_images():
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


def copy_all_labels():
    for directory in get_dirs_inside_data_folder():
        source_dir = os.path.join(
            config["raw_data_folder"], directory, config["label_folder"]
        )
        destination_dir = os.path.join(
            config["image_bank_folder"], config["label_folder"]
        )
        shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
    print("All labels have been successfully copied to the image bank.")


def clean_dataset():
    if os.path.exists(config["dataset_folder"]):
        shutil.rmtree(config["dataset_folder"])
        print("Dataset has been cleaned.")
    else:
        print("Dataset does not exist.")


def create_dataset_folders():
    os.makedirs(os.path.join(config["dataset_folder"], "train"), exist_ok=True)
    os.makedirs(os.path.join(config["dataset_folder"], "validation"), exist_ok=True)
    os.makedirs(os.path.join(config["dataset_folder"], "test"), exist_ok=True)


def split_image_bank():
    """
    Split the image bank into train, validation, and test sets.
    """
    if not os.path.exists(config["image_bank_folder"]):
        print("Image bank does not exist.")
        return

    # Clean any existing dataset folder
    clean_dataset()

    # Create dataset folders
    if not os.path.exists(config["dataset_folder"]):
        create_dataset_folders()

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
    
def copy_all():
    """
    Copy all images and labels from raw_data to image_bank
    """
    clean_image_bank()
    create_image_bank_folders()
    copy_all_images()
    copy_all_labels()