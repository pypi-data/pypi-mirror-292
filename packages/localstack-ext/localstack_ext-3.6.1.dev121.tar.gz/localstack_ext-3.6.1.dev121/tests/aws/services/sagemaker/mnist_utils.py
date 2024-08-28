import gzip
import os

import numpy as np
from localstack.utils.files import new_tmp_file
from localstack.utils.http import download

dirname = os.path.dirname(os.path.abspath(__file__))


def get_mnist_data(train=True):
    """Download MNIST dataset and convert it to numpy array

    Args:
        train (bool): download training set

    Returns:
        tuple of images and labels as numpy arrays
    """

    if train:
        images_file = "train-images-idx3-ubyte.gz"
        labels_file = "train-labels-idx1-ubyte.gz"
    else:
        images_file = "t10k-images-idx3-ubyte.gz"
        labels_file = "t10k-labels-idx1-ubyte.gz"

    # download objects
    bucket = "sagemaker-sample-files"
    tmp_files = {}
    for dl_file in [images_file, labels_file]:
        key = os.path.join("datasets/image/MNIST", dl_file)
        tmp_files[dl_file] = new_tmp_file()
        download(f"https://{bucket}.s3.amazonaws.com/{key}", tmp_files[dl_file])

    return _convert_to_numpy(tmp_files[images_file], tmp_files[labels_file])


def _convert_to_numpy(images_file, labels_file):
    """Byte string to numpy arrays"""
    with gzip.open(images_file, "rb") as f:
        images = np.frombuffer(f.read(), np.uint8, offset=16).reshape(-1, 28, 28)

    with gzip.open(labels_file, "rb") as f:
        labels = np.frombuffer(f.read(), np.uint8, offset=8)

    return images, labels


def normalize(x, axis):
    eps = np.finfo(float).eps

    mean = np.mean(x, axis=axis, keepdims=True)
    # avoid division by zero
    std = np.std(x, axis=axis, keepdims=True) + eps
    return (x - mean) / std
