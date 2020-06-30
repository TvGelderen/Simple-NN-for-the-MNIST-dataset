from tensorflow.python.keras.datasets import mnist
import numpy as np
import matplotlib.pyplot as plt
from math import exp
import sys


# Sigmoid activation function
def sigmoid(x):
    # In some instances a too high activation can cause an OverflowError
    try:
        return 1 / (1 + exp(-x))
    except OverflowError:
        return 1


# Derivative of the sigmoid
def derivative_sigmoid(arr):
    return arr * (1.0 - arr)


if __name__ == '__main__':
    (trainX, trainY), (testX, testY) = mnist.load_data()
    # X contains the images, Y contains the corresponding number

    # Input layer consists of 784 neurons, one for each item in the matrices
    n_in = 784
    # The two hidden layers both contain 16 neurons
    n_h1 = 16
    n_h2 = 16
    # The output layer contains 10 neurons, one for each possible number
    n_out = 10

    # Randomize the seed
    np.random.seed(seed=None)
    # Initialize weights from a uniform distribution between 0.0 and 0.5
    weights = [np.random.uniform(-1, 1, (n_in, n_h1)), np.random.uniform(-1, 1, (n_h1, n_h2)),
               np.random.uniform(-1, 1, (n_h2, n_out))]
    # Initialize the matrix for the activation values
    activations = [np.zeros(n_in), np.zeros(n_h1), np.zeros(n_h2), np.zeros(n_out)]
    # Initialize biases from a uniform distribution between 0.0 an 1.0
    biases = [np.random.rand(n_h1), np.random.rand(n_h2), np.random.rand(n_out)]
    # Initialize the error matrix, called delta
    delta = [np.zeros(n_h1), np.zeros(n_h2), np.zeros(n_out)]

    # Change the type to float so as to make sure we get decimal values when normalizing
    trainX = trainX.astype('float32')
    testX = testX.astype('float32')
    # Normalizing by dividing by the max RGB value
    trainX /= 255
    testX /= 255
    # Transpose the arrays so they can be input to the input nodes
    trainX = trainX.transpose(0, 1, 2).reshape(-1, 784)
    testX = testX.transpose(0, 1, 2).reshape(-1, 784)

    # Determine number of epochs
    epochs = int(input("Number of epochs: "))
    learningRate = float(input("Learning rate: "))

    # Initialize a function with the cost over time
    cost = np.empty((epochs,60000))

    # Iterate through the epochs
    for epoch in range(epochs):
        print("Epoch {}/{}:".format(epoch + 1, epochs))

        # Iterate through all training images
        for trainIndex in range(60000):
            sys.stdout.write("\rTraining {}/60000".format(trainIndex + 1))
            # FORWARD PROPAGATION
            # Add the input
            for i in range(n_in):
                activations[0][i] = trainX[trainIndex][i]
            # Calculate the activations through the layers
            for l in range(len(activations) - 1):
                # To calculate the activations of the neurons in layer l+1 we take the following dot product and add the
                # respective bias
                activations[l + 1] = activations[l].dot(weights[l]) + biases[l]
                # Apply the sigmoid to get the final activation
                for i in range(len(activations[l + 1])):
                    activations[l + 1][i] = sigmoid(activations[l + 1][i])

            # Create an expected output vector
            y = np.zeros(n_out)
            for i in range(n_out):
                if i == trainY[trainIndex]:
                    y[i] = 1.0
                else:
                    y[i] = 0.0

            # Calculate the cost every ten iterations
            if trainIndex % 10 == 0:
                costSum = 0
                for i in range(n_out):
                    costSum += (y[i] - activations[3][i]) ** 2
                cost[epoch][trainIndex] = costSum / 2

            # BACK PROPAGATION
            # NOTE: generally the weights are indicated with the receiving neuron (in this case j) first, though in this
            #       case the matrices are defined like this for the matrix multiplications
            # NOTE: since the matrices have different dimensions the layer l refers to different parts of the network in
            #       different matrices (e.g. delta[0] refers to the errors in h1, whereas actiations[0] refers to the
            #       activations in the input layer)

            # Calculate the error in the output layer
            for i in range(n_out):
                delta[2][i] = (activations[3][i] - y[i]) * derivative_sigmoid(activations[3][i])
            # Propagate the error backwards
            for l in reversed(range(2)):
                for k in range(len(weights[l + 1])):
                    errorSum = 0
                    for j in range(len(weights[l + 1][k])):
                        errorSum += weights[l + 1][k][j] * delta[l + 1][j] * derivative_sigmoid(activations[l + 1][k])
                    delta[l][k] = errorSum
            # Update the weights and biases
            for l in reversed(range(len(weights))):
                biases[l] -= delta[l]
                for k in range(len(weights[l])):
                    for j in range(len(weights[l][k])):
                        # As noted before, the index l represents a different layer in each of the matrices
                        weights[l][k][j] -= learningRate * activations[l][k] * delta[l][j]

            sys.stdout.flush()
        print("\n")

    # TESTING
    correct = 0
    for testIndex in range(10000):
        sys.stdout.write("\rTesting {}/10000".format(testIndex + 1))
        # Add the input
        for i in range(n_in):
            activations[0][i] = testX[testIndex][i]
        # Calculate the activations through the layers
        for l in range(len(activations) - 1):
            # To calculate the activations of the neurons in layer l+1 we take the following dot product and add the
            # respective bias
            activations[l + 1] = activations[l].dot(weights[l]) + biases[l]
            # Apply the sigmoid to get the final activation
            for i in range(len(activations[l + 1])):
                activations[l + 1][i] = sigmoid(activations[l + 1][i])

        guess = np.argmax(activations[3])

        if guess == testY[testIndex]:
            correct += 1

        sys.stdout.flush()

    accuracy = correct / 10000
    print("\nAccuracy: {}".format(accuracy))

    for i in range(epochs):
        plt.plot(cost[i])
        plt.ylabel("Cost in epoch {}".format(epoch))
        plt.show()

    # Save the weights to files
    np.save('weights/weights_layer1.npy', weights[0])
    np.save('weights/weights_layer2.npy', weights[1])
    np.save('weights/weights_layer3.npy', weights[2])
