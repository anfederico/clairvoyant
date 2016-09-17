# Modified from Sci-Kit Learn Documentation
# http://scikit-learn.org/stable/auto_examples/classification/plot_classifier_comparison.html

import numpy
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

'''
Args:
    1. Ticker(str): Name of stock
    2. gamma(float): Kernel coefficient
        Default = 2
    3. C(float): Penalty parameter of the error term
        Default = 1
    4. h(int): Step size in the mesh
        Default = 0.02

Assumptions:
    Assumes 2 features and 1/0 classification
    File is in sample directory as program
    May need to tweek file name depending on indicators
    Training/testing split is set to 90/10

Returns:
    Nothing
'''

def RBFSVM(Ticker, gamma = 2.0, C = 1.0, h = 0.02):

    # Load Training Data
    infile = open('%s_SSOvSSC_TrainingData.csv' % Ticker, 'r')
    X = []
    y = []
    for line in infile:
        CSVdata = line.split(',')
        X.append([float(CSVdata[0]), float(CSVdata[1])])
        if float(CSVdata[2]) > 0:
            y.append(1)
        else:
            y.append(0)
    infile.close()

    # Process learning data
    X = numpy.vstack(X) # Convert to numpy array
    y = numpy.hstack(y) # Convert to numpy array
    X = StandardScaler().fit_transform(X) # Normalization
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.10) # Split into training/testing data (90/10)
    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5 # X min/max
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5 # y min/max
    xx, yy = numpy.meshgrid(numpy.arange(x_min, x_max, h), numpy.arange(y_min, y_max, h))

    # Radial Basis Function Support Vector Machine
    classifier = SVC(gamma=gamma, C=C)
    figure = plt.figure(figsize=(2, 1))
    cm = plt.cm.RdBu # Red/Blue gradients
    RedBlue = ListedColormap(['#FF312E', '#6E8894']) # Red = 0 (Negative) / Blue = 1 (Positve)

    # Plot the training and testing points
    Axes = plt.subplot(1, 2, 1)
    Axes.scatter(X_train[:, 0], X_train[:, 1], c=y_train, cmap=RedBlue) # Training = dark
    Axes.scatter( X_test[:, 0],  X_test[:, 1], c=y_test,  cmap=RedBlue, alpha=0.25) # Testing = light
    Axes.set_xlim(xx.min(), xx.max()) # Limits X Size
    Axes.set_ylim(yy.min(), yy.max()) # Limits Y Size
    Axes.set_xticks(()) # Remove X Tickers
    Axes.set_yticks(()) # Remove Y Tickers

    # Fitting the data
    Axes = plt.subplot(1, 2, 2)
    classifier.fit(X_train, y_train)
    score = classifier.score(X_test, y_test)

    # Plot the decision boundary
    Z = classifier.decision_function(numpy.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # Put the result into a color plot
    Axes.contourf(xx, yy, Z, cmap=cm, alpha=0.8)

    # Plot also the training and testing points
    Axes.scatter(X_train[:, 0], X_train[:, 1], c=y_train, cmap=RedBlue)
    Axes.scatter( X_test[:, 0], X_test[:, 1],  c=y_test,  cmap=RedBlue)
    Axes.set_xlim(xx.min(), xx.max()) # Limits X Size
    Axes.set_ylim(yy.min(), yy.max()) # Limits Y Size
    
    # Title and Scales
    Axes.set_title(Ticker)
    Axes.text(xx.max() - 0.3, yy.min() + 0.3, ('%.2f' % score).lstrip('0'),size=15 , horizontalalignment='right')
    
    plt.show()
    
'''
Example
RBFSVM('TSLA')
'''
