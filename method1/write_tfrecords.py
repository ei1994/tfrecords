from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os.path
import sys

from PIL import Image

import numpy as np
import tensorflow as tf
from tensorflow.python.platform import gfile
import config
import glob

IMAGE_HEIGHT = 299
IMAGE_WIDTH = 299
CLASSES_NUM = 30

# for train
RECORD_DIR = 'pig_body'
TRAIN_FILE = 'train.tfrecords'
#TRAIN_FILE = 'D:\pig_recognize\record\train.tfrecords'
VALID_FILE = 'valid.tfrecords'

FLAGS = None

def _int64_feature(values):
  if not isinstance(values, (tuple, list)):
    values = [values]
  return tf.train.Feature(int64_list=tf.train.Int64List(value=[values]))

def _bytes_feature(values):
  return tf.train.Feature(bytes_list=tf.train.BytesList(value=[values]))

def _float_feature(values):
  if not isinstance(values, (tuple, list)):
    values = [values]
  return tf.train.Feature(float_list=tf.train.FloatList(value=values))

def label_to_one_hot(label):
  one_hot_label = np.zeros([CLASSES_NUM])
  one_hot_label[label] = 1.0
  return one_hot_label.astype(np.uint8)  #(4,10)


def image_to_tfexample(image_raw, label_raw, height, width):
  return tf.train.Example(features=tf.train.Features(feature={
        'height': _int64_feature(height),
        'width': _int64_feature(width),
        'label_raw': _bytes_feature(label_raw),
        'image_raw': _bytes_feature(image_raw)}))


def conver_to_tfrecords(data_set, name):
  """Converts a dataset to tfrecords."""
  if not os.path.exists(RECORD_DIR):
      os.makedirs(RECORD_DIR)
  filename = os.path.join(RECORD_DIR, name)
  print('>> Writing', filename)
  writer = tf.python_io.TFRecordWriter(filename)
  data_set_list=list(data_set)
  num_examples = len(data_set_list)
  count = 0
  for index in range(num_examples):
    count += 1
    image = data_set_list[index][0]
    height = image.shape[0]
    width = image.shape[1]
    # 以二进制的形式保存
    image_raw = image.tostring()
    label = data_set_list[index][1]
    label_raw = label_to_one_hot(label).tostring()
    
    example = image_to_tfexample(image_raw, label_raw, height, width)
    writer.write(example.SerializeToString())
    if count %500 == 0:
	    print('processed {}/{}'.format(count,num_examples))
  writer.close()
  print('>> Writing Done!')


def create_data_list(image_dir):
  if not gfile.Exists(image_dir):
    print("Image director '" + image_dir + "' not found.")
    return None
  extensions = [ '*.jpg']
  print("Looking for images in '" + image_dir + "'")
  
#  file_list = []
#  for extension in extensions:
#    file_glob = os.path.join(image_dir, extension)
#    file_list.extend(gfile.Glob(file_glob))

  file_list = glob.glob('D:/pig_recognize/pig_recognize_body/pig_body/train_data1/*.jpg')   
  
  if not file_list:
    print("No files found in '" + image_dir + "'")
    return None
  images = []
  labels = []
  all_list = len(file_list)
  count = 0
  for file_name in file_list:
    count += 1
    image = Image.open(file_name)
    image_resize = image.resize(size=(IMAGE_WIDTH,IMAGE_HEIGHT))
    input_img = np.array(image_resize, dtype='uint8')
    image.close()
    label_name = int(os.path.basename(file_name).split('_')[0]) - 1   #start at 0
    images.append(input_img)
    labels.append(label_name)
    if count % 500 == 0:
	    print('processed :{}/{}'.format(count,all_list))
  return zip(images, labels)


def main(_):
  training_data = create_data_list(FLAGS.train_dir)
  conver_to_tfrecords(training_data, TRAIN_FILE)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--train_dir',
      type=str,
      default='pig_body/train_data1',
      help='Directory training to get captcha data files and write the converted result.'
  )
  parser.add_argument(
      '--valid_dir',
      type=str,
      default='pig_body/valid_data',
      help='Directory validation to get captcha data files and write the converted result.'
  )
  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)




