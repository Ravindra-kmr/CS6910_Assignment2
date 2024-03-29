# CS6910 Assignment 2 : Part A : Train from scratch
---
[preprocess.py](https://github.com/PranjalChitale/CS6910_Assignment2/blob/main/part_a/preprocess.py) contains the code to preprocess the dataset.  
Tasks performed :- 
1. Split the train data to (train, val) - (90:10) split.  
2. Peform data augmentation if required.  
3. Generate batches of the train data and test data according to the batch_size passed.  

[cnn.py](https://github.com/PranjalChitale/CS6910_Assignment2/blob/main/part_a/cnn.py)
Contains the code to define the class for the CNN model.
Has methods to add specific layers to the CNN model including Conv-pool blocks, OutputLayer, BatchNorm, Dropout.
Has a train function to train the CNN model on the train set data and a test function to evaluate on the test set data, based on the parameters passed to the function.

[main.py](https://github.com/PranjalChitale/CS6910_Assignment2/blob/main/part_a/main.py)
Contains the code to create the network, train and evaluate the model on the test data.
It parses command-line arguments to create and train the network.


### How to pass the hyperparameters configuration as command-line arguments to main.py  ?
```
--augmentation # Add if you need data augmentation.
--train_path #Path of the train data directory
--test_path' #Path of the test data directory
--batch_size #Batch size
--learning_rate #Learning rate
--image_size # Image size -> height, width
--num_conv_layers #Number of Convolution-Pool Blocks
--num_epochs #Number of Epochs to train for.
--num_filters #'Number of Filters in Convolution Layer, space separated.
--filter_size #Filter size in each convolution layer, comma seperated
--pool_size' #Pool size in each MaxPool layer
--dense_neurons #Neurons in Dense Layer after all Convolution Layers.
--batch_norm #Add if you need batch norm layer.
--dropout #Dropout Rate, 0 indicates no dropout.

Example :-
python main.py --augmentation --batch_norm --image_size 224 224 --num_conv_layers 5 \
--num_filters 32 64 128 256 512  --filter_size 11,11 7,7 5,5 3,3 2,2 \
--pool_size 2,2 2,2 2,2 2,2 2,2 --dense_neurons 256 --dropout 0.2 \
--learning_rate 0.00001 --batch_size 64
```

### Train a CNN on train data
```
from preprocess import generate_batch_train_val
from preprocess import generate_batch_test
from cnn import *
import tensorflow as tf 

cnn = CNN(tuple(input_shape))
cnn.build_model(num_conv_layers, num_filters, filter_size, pool_size, activation_fn = "relu", batch_norm = batch_norm, dropout = dropout, dense_neurons = dense_neurons, num_classes = 10)
cnn.train(train_data, val_data, optimizer = "Adam", learning_rate = learning_rate, loss_fn = 'categorical_crossentropy', num_epochs = num_epochs, batch_size = batch_size)
```

### Load a pretrained model and evaluate performance on test data

```
#Load the model weights from the path
cnn.model = keras.models.load_model(best_model_path)

#Displays the Model summary.
print(cnn.model.summary())

#Evaluates the performance of the model on the test set.
cnn.test(test_data)
```

### Filter Visualization 

```
#Arguments
--test_path' #Path of the test data directory
--batch_size #Batch size
--image_size # Image size -> height, width
--num_conv_layers #Number of Convolution-Pool Blocks
--best_model_path  #Path to best model, default : Fetch best model from Wandb (requires Wandb Setting)
```

Run [filter_visualization.py](https://github.com/PranjalChitale/CS6910_Assignment2/blob/main/part_a/filter_visualization.py)

- Creates a 10x3 grid to display the sample image from train data its true label at the bottom of image and predicted label on the left of the image.
- Visualizes featuremaps generated by the Filters of the first layer of the CNN model for the best configuration generated by the Wandb Sweep.
- We do this by using the first image from a randomly picked test batch of the test data generator and view the feature maps for that image.
- We view these filters in grids of predefined size.


### Use WANDB sweep

```
# In wandb_sweep.py

#First Set your project name and username
wandb.init(project=project_name, entity=entity)

#To add a new agent to an existing sweep, comment next line and directly put sweep_id in wandb.agent
sweep_id = wandb.sweep(sweep_config, project=project_name, entity=entity)
wandb.agent(sweep_id, project=project_name, function=train_wandb)

#Change the config_sweep as per the need, to sweep using different strategy.
```
