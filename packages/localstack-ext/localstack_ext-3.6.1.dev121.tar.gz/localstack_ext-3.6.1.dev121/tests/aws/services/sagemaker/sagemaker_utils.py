# Taken from https://github.com/awslabs/amazon-sagemaker-examples/blob/master/
#    sagemaker-python-sdk/tensorflow_distributed_mnist/utils.py

import os


def _int64_feature(value):
    # keep imports here to avoid ModuleNotFoundError running nosetests
    import tensorflow as tf

    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def _bytes_feature(value):
    import tensorflow as tf

    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def convert_to(data_set, name, directory):
    import tensorflow as tf

    """Converts a dataset to tfrecords."""
    images = data_set.images
    labels = data_set.labels
    num_examples = data_set.num_examples

    if images.shape[0] != num_examples:
        raise ValueError(
            "Images size %d does not match label size %d." % (images.shape[0], num_examples)
        )
    rows = images.shape[1]
    cols = images.shape[2]
    depth = images.shape[3]

    filename = os.path.join(directory, name + ".tfrecords")
    writer = tf.python_io.TFRecordWriter(filename)
    for index in range(num_examples):
        image_raw = images[index].tostring()
        example = tf.train.Example(
            features=tf.train.Features(
                feature={
                    "height": _int64_feature(rows),
                    "width": _int64_feature(cols),
                    "depth": _int64_feature(depth),
                    "label": _int64_feature(int(labels[index])),
                    "image_raw": _bytes_feature(image_raw),
                }
            )
        )
        writer.write(example.SerializeToString())
    writer.close()
