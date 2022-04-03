# -*- coding: utf-8 -*-
"""Assignment2_A_GBP.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WIkG0ZbzyGIPytww_oVqNiq5QIBjvM8C
"""

# Importing the required packages
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import keras
import cv2

#Define the Command Line Arguments
parser = argparse.ArgumentParser(description='Set the directory paths, hyperparameters of the model.')
parser.add_argument('--image_path', type=str, default='./inaturalist_12K/train/Arachnida/0a1b1f40a024ef9e472f73341b9edabb.jpg', help='Path of the test data directory')
parser.add_argument('--num_neurons', type=int, default=10, help='Number of neurons to fix')
parser.add_argument('--featuremap_number', type=int, default=356, help='Feature map number whose neurons you want to fix.')
parser.add_argument('--conv_layer_name', type=str, default='conv2d_4', help='Convolution layer name whose neuron to fix.')
parser.add_argument('--best_model_path', type=str, default="wandb", help='Path to best model, default:get from wandb sweep')


#Parse the arguments
args = parser.parse_args()
image_path = args.image_path
num_neurons = args.num_neurons
featuremap_number = args.featuremap_num
conv_layer_name = args.conv_layer_name
best_model_path = args.best_model_path

# Importing the wandb to get the best model configuration
!pip install wandb --upgrade
import wandb
api = wandb.Api()

# Downloading the inaturalist dataset.
dataset_url = "https://storage.googleapis.com/wandb_datasets/nature_12K.zip"
dataset_dir = tf.keras.utils.get_file("nature_12K",origin=dataset_url,cache_dir='.',extract=True)
trainset_dir = './datasets/inaturalist_12K/train/'
testset_dir = './datasets/inaturalist_12K/val/'

# Importing the best model configuration and weights.
# sweep = api.sweep("cs6910_a2/CS6910_A2/dn3iw4rd")
# runs = sorted(sweep.runs, key=lambda run: run.summary.get("val_accuracy", 0), reverse=True)
# runs[0].file("model-best.h5").download(replace=True)
# print("Best model saved to model-best.h5")
if best_model_path == 'wandb':
    sweep = api.sweep("") #Add sweep url here : Entity_name/Project_name/sweep_id
    #Sort the runs is descending order of val_accuracy
    runs = sorted(sweep.runs, key=lambda run: run.summary.get("val_accuracy", 0), reverse=True)
    #Pick the top ranked run.
    runs[0].file("model-best.h5").download(replace=True)
    best_model_path = 'model-best.h5'
image_size = [224,224]
input_shape= image_size
input_shape.append(3)
model = keras.models.load_model(best_model_path)
model.summary()

# # Setting up to log into wandb the gdb images obtained.
# project_name = 'CS6910_A2' #Add project name here
# entity = 'cs6910_a2 ' #Add username here
# wandb.init(project=project_name, entity=entity)

# Defining the custom activation funciton (same as relu) and its gradient as defined in guided back propagation.
@tf.custom_gradient
def guidedRelu(x):
  def grad(dy):
    return tf.cast(dy>0,"float32") * tf.cast(x>0, "float32") * dy
  return tf.nn.relu(x), grad

# Takes as input: model, layer name, image path, num of neurons to test with and feature map number on which we want to search for the set neuron.
def Guided_backpropagation(model, layer,image_path, num_neurons=1,featuremap_num = 0):
  model = tf.keras.models.Model(inputs = [model.inputs],outputs = [model.get_layer(layer).output])
  activaton_layer_dict = [l for l in model.layers[1:] if hasattr(l,'activation')]

#   Changing the activation function with new activaiton function
  for activaton_layer in activaton_layer_dict:
    activaton_layer.activation = guidedRelu

# Reading and resizing the image.
  image=cv2.imread(image_path)
  resized_image=cv2.resize(image,(224,224))
  flattened_image = np.expand_dims(resized_image, axis=0)
  plt.imshow(resized_image)
  plt.title(image_path)
#   images = wandb.Image(plt, caption="Actual Image:"+image_path)
#   wandb.log({"Question-A5_image": images})
  plt.show()
  fig = plt.figure(figsize=(50,50))

  rows,columns = 10,1
  neuron_count = 1
  while neuron_count <= num_neurons:
    with tf.GradientTape() as tape: # Record operations for automatic differentiation.
      inputs = tf.cast(flattened_image, tf.float32)
      tape.watch(inputs)
      outputs = model(inputs)[0]
      neuron_position = np.random.randint(outputs.shape[0],size=2)

      if outputs[neuron_position[0],neuron_position[1],featuremap_num] != 0:    # if the neuron is set than only its gradient will backpropagate therefore checking if the neuron is set.
        feature_map = outputs[neuron_position[0],neuron_position[1],featuremap_num]
        grads = tape.gradient(feature_map,inputs)[0]    # Finding the gradient dy(y,x)
        gbp_grads =grads
        gbp_visualisation = np.dstack((gbp_grads[:,:,0],gbp_grads[:,:,1],gbp_grads[:,:,2]))       
        gbp_visualisation -= np.min(gbp_visualisation)
        gbp_visualisation /= gbp_visualisation.max()    # normalizing the visualisation.

        # Plotting the visualization
        ax = fig.add_subplot(rows,columns,neuron_count)
        ax.imshow(gbp_visualisation)
        ax.title.set_text("Fixed neuron position in "+str(layer)+' layer: ('+str(neuron_position[0])+','+str(neuron_position[1])+','+str(featuremap_num)+')')
        neuron_count+=1
  plt.show()
#   wandb.log({"Question_5A_gbp_images": plt})  


# image_path='./datasets/inaturalist_12K/train/Arachnida/0a1b1f40a024ef9e472f73341b9edabb.jpg'
Guided_backpropagation(model,conv_layer_name,image_path,num_neurons,featuremap_number)