from tensorflow.python.keras.datasets import mnist
import numpy as np
from math import exp
import sys


# Relu activation function
def relu(x, derivative=False):
    if x > 0:
        if derivative:
            return 1
        return x
    return 0


def softmax(arr):
    total = np.sum(arr)
    for idx in range(len(arr)):
        arr[idx] /= total
    return arr


if __name__ == '__main__':
    # x contains the images, y contains the corresponding number
    (train_x, train_y), (test_x, test_y) = mnist.load_data()

    # Set the number of neurons in each of the layers
    n_in, n_h1, n_h2, n_out = 784, 16, 16, 10

    # Randomize the seed
    np.random.seed(seed=None)
    # Initialize weights from a uniform distribution between -0.25 and 0.25
    weights = [np.random.uniform(-0.25, 0.25, (n_in, n_h1)),
               np.random.uniform(-0.25, 0.25, (n_h1, n_h2)),
               np.random.uniform(-0.25, 0.25, (n_h2, n_out))]
    # Initialize the matrix for the activation values
    activations = [np.zeros(n_in),
                   np.zeros(n_h1),
                   np.zeros(n_h2),
                   np.zeros(n_out)]
    # Initialize biases from a uniform distribution between -0.25 an 0.25
    biases = [np.random.uniform(-0.25, 0.25, n_h1),
              np.random.uniform(-0.25, 0.25, n_h2),
              np.random.uniform(-0.25, 0.25, n_out)]
    # Initialize the error matrix, called delta
    delta = [np.zeros(n_h1),
             np.zeros(n_h2),
             np.zeros(n_out)]

    # Change the type to float so as to make sure we get decimal values when normalizing
    train_x, test_x = train_x.astype('float32'), test_x.astype('float32')
    # Normalizing by dividing by the max RGB value
    train_x, test_x = train_x/255, test_x/255
    # Transpose the arrays so they can be input to the input nodes
    train_x, test_x = train_x.transpose(0, 1, 2).reshape(-1, 784), test_x.transpose(0, 1, 2).reshape(-1, 784)

    # Determine number of epochs
    epochs = 1
    learning_rate = 0.05
    batch_size = 20
    # epochs = int(input("Number of epochs: "))
    # learning_rate = float(input("Learning rate: "))
    cost, cost_sum = 0.0, 0.0

    # Iterate through the epochs
    for epoch in range(epochs):
        print("Epoch {}/{}:".format(epoch + 1, epochs))
        # Iterate through all training images
        for train_index in range(60000):
            sys.stdout.write("\rTraining {}/60000\t Cost: {:.4f}".format(train_index + 1, cost))
            # FORWARD PROPAGATION
            # Add the input
            activations[0] = train_x[train_index]
            # Calculate the activations through the layers
            for l in range(len(activations) - 1):
                # To calculate the activations of the neurons in layer l+1 we take the following dot product and add the
                # respective bias
                activations[l + 1] = activations[l].dot(weights[l]) + biases[l]
                # Apply the sigmoid to get the final activation, except for the last layer
                for i in range(len(activations[l + 1])):
                    if l + 1 != len(activations):
                        activations[l + 1][i] = relu(activations[l + 1][i])

            # For the last layer we use softmax
            activations[3] = softmax(activations[3])

            # Create an expected output vector
            y = np.zeros(n_out)
            for i in range(n_out):
                if i == train_y[train_index]:
                    y[i] = 1.0
                else:
                    y[i] = 0.0

            # BACK PROPAGATION
            # NOTE: generally the weights are indicated with the receiving neuron (in this case j) first, though in this
            #       case the matrices are defined like this for the matrix multiplications
            # NOTE: since the matrices have different dimensions the layer l refers to different parts of the network in
            #       different matrices (e.g. delta[0] refers to the errors in h1, whereas activations[0] refers to the
            #       activations in the input layer)

            for i in range(n_out):
                cost_sum += (activations[3][i] - y[i]) ** 2
            # Calculate the average cost every 10 iterations
            if train_index % 10 == 0:
                cost = cost_sum / 20
                cost_sum = 0

            # Calculate the error in the output layer
            for i in range(n_out):
                delta[2][i] = 2 * (activations[3][i] - y[i])
            # Propagate the error backwards
            for l in reversed(range(2)):
                for k in range(len(weights[l + 1])):
                    error_sum = 0
                    for j in range(len(weights[l + 1][k])):
                        error_sum += weights[l + 1][k][j] * delta[l + 1][j] * relu(activations[l + 1][k], True)
                    delta[l][k] = error_sum
            # Update the weights and biases
            for l in reversed(range(len(weights))):
                # biases[l] -= delta[l]
                for k in range(len(weights[l])):
                    for j in range(len(weights[l][k])):
                        # As noted before, the index l represents a different layer in each of the matrices
                        weights[l][k][j] -= learning_rate * (activations[l][k] * delta[l][j])

            sys.stdout.flush()

        print("\n")

    # TESTING
    correct = 0
    for testIndex in range(10000):
        sys.stdout.write("\rTesting {}/10000".format(testIndex + 1))
        # Add the input
        activations[0] = test_x[testIndex]
        # Calculate the activations through the layers
        for l in range(len(activations) - 1):
            # To calculate the activations of the neurons in layer l+1 we take the following dot product and add the
            # respective bias
            activations[l + 1] = activations[l].dot(weights[l]) + biases[l]
            # Apply the sigmoid to get the final activation
            for i in range(len(activations[l + 1])):
                activations[l + 1][i] = relu(activations[l + 1][i])

        guess = np.argmax(activations[3])

        if guess == test_y[testIndex]:
            correct += 1

        sys.stdout.flush()

    accuracy = correct / 10000
    print("\nAccuracy: {}".format(accuracy))

    # Save the weights to files
    np.save('weights/weights_layer1.npy', weights[0])
    np.save('weights/weights_layer2.npy', weights[1])
    np.save('weights/weights_layer3.npy', weights[2])
