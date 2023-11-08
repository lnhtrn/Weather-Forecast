import numpy as np

# Build a Neural Net
# Implementation with Neural Net comprises of n layers

class Layer:
    def __init__(self, input_size: int, size: int = 1, bias: bool = False):
        self.weights = np.random.rand(	size, input_size)
        self.bias = bias
        
    def predict(self, input: np.ndarray):
        self.nodes = =

class NeuralNet:
    def __init__(self, input_size: int = 1, output_size: int = 1, 
                 n_hidden_layers: int = 0, bias: bool = True): 
        self.input_size = input_size
        self.output_size = output_size
        self.n_layers = n_layers
        self.layers = []
        
    def add_layer(self, size: int = 1):
        self.layers.append(Layer(size))