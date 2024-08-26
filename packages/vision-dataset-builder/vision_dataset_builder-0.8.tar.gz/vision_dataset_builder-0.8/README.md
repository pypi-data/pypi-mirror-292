# Vision Dataset Builder

**Vision Dataset Builder** is a Python library that simplifies managing image datasets for computer vision projects. It offers a CLI and API for building image banks, splitting datasets, and more.

## Features

- **Build Image Bank**: Organize images and labels into a structured image bank.
- **Dataset Splitting**: Split datasets into training, validation, and test sets.
- **Customizable**: Modify configurations via `config.yaml` or programmatically.

## Installation

```bash
pip install vision-dataset-builder
```

After running the above command, you will see output indicating that the package and its dependencies have been successfully installed.

## Usage

### Command-Line Interface (CLI)

- **Rebuild Image Bank**:
  ```bash
  vision-dataset-builder rebuild-image-bank
  ```

- **Clean Image Bank**:
  ```bash
  vision-dataset-builder clean-image-bank
  ```

- **Split Image Bank**:
  ```bash
  vision-dataset-builder split-image-bank
  ```

- **Clean Dataset**:
  ```bash
  vision-dataset-builder clean-dataset
  ```

### Programmatic API

```python
from vision_dataset_builder import load_config, split_image_bank

# Override config values
config = load_config(overrides={
    'train_ratio': 0.7,
    'validation_ratio': 0.2,
    'test_ratio': 0.1
})

# Split the image bank
split_image_bank(config=config)
```

### Configuration

Edit `config.yaml` to set paths and ratios for your datasets:

```yaml
# config.yaml

# Folder paths
raw_data_folder: "raw_data"
image_bank_folder: "image_bank"
image_folder: "images"
label_folder: "labels"
dataset_folder: "dataset"

# Split ratios
train_ratio: 0.8
validation_ratio: 0.1
test_ratio: 0.1
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License.
```