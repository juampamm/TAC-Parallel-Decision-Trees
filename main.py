
from random import seed
from random import randrange
from csv import reader
import time
import multiprocessing
import random

PARALLEL = False
PARALLEL2 = False

NUM_ATRIBUTES = 8
SAMPLES = 1500
N_FOLDS = 5

MAX_DEPTH = 5


# Load a CSV file
def load_csv(filename):
    file = open(filename, "rt")
    lines = reader(file, delimiter=';')
    dataset = list(lines)

    return dataset


# Convert string column to float
def str_column_to_float(dataset, column):
    for row in dataset:
        row[column] = float(row[column].strip())


# Split a dataset into k folds
def cross_validation_split(dataset, n_folds):
    dataset_split = list()
    dataset_copy = list(dataset)
    fold_size = int(len(dataset) / n_folds)
    for i in range(n_folds):
        fold = list()
        while len(fold) < fold_size:
            index = randrange(len(dataset_copy))
            fold.append(dataset_copy.pop(index))
        dataset_split.append(fold)
    return dataset_split


# Calculate accuracy percentage
def accuracy_metric(actual, predicted):
    correct = 0
    for i in range(len(actual)):
        if actual[i] == predicted[i]:
            correct += 1
    return correct / float(len(actual)) * 100.0

def eval_parallel(valores):
    train_set = list(valores[0])
    train_set.remove(valores[1])
    train_set = sum(train_set, [])
    test_set = list()
    for row in valores[1]:
        row_copy = list(row)
        test_set.append(row_copy)
        row_copy[-1] = None
    predicted = valores[2](train_set, test_set, valores[3][0], valores[3][1])
    actual = [row[-1] for row in valores[1]]
    accuracy = accuracy_metric(actual, predicted)
    return accuracy

# Evaluate an algorithm using a cross validation split
def evaluate_algorithm(dataset, algorithm, n_folds, *args):
    folds = cross_validation_split(dataset, n_folds)
    scores = list()
    if PARALLEL2 == True:
        valores = []
        for ii in range(n_folds):
            aux = []
            aux.append(folds)
            aux.append(folds[ii])
            aux.append(algorithm)
            aux.append(args)
            valores.append(aux)
        #valores = [[folds, folds[0], algorithm, args], [folds, folds[1], algorithm, args], [folds, folds[2], algorithm, args], [folds, folds[3], algorithm, args], [folds, folds[4], algorithm, args]]
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        scores = pool.map(eval_parallel, valores)
    else:
        for fold in folds:
            train_set = list(folds)
            train_set.remove(fold)
            train_set = sum(train_set, [])
            test_set = list()
            for row in fold:
                row_copy = list(row)
                test_set.append(row_copy)
                row_copy[-1] = None
            predicted = algorithm(train_set, test_set, *args)
            actual = [row[-1] for row in fold]
            accuracy = accuracy_metric(actual, predicted)
            scores.append(accuracy)
    return scores


# Split a dataset based on an attribute and an attribute value
def test_split(index, value, dataset):
    left, right = list(), list()
    for row in dataset:
        if row[index] < value:
            left.append(row)
        else:
            right.append(row)
    return left, right


# def prueba(valores):


# Calculate the Gini index for a split dataset
def gini_index(groups, classes):
    # count all samples at split point
    n_instances = float(sum([len(group) for group in groups]))
    # sum weighted Gini index for each group
    gini = 0.0
    for group in groups:
        size = float(len(group))
        # avoid divide by zero
        if size == 0:
            continue
        score = 0.0
        # score the group based on the score for each class
        for class_val in classes:
            p = [row[-1] for row in group].count(class_val) / size
            score += p * p
        # weight the group score by its relative size
        gini += (1.0 - score) * (size / n_instances)
    return gini


def evaluate_row(valores):
    b_index, b_value, b_score, b_groups = 999, 999, 999, None
    for row in valores[2]:
        groups = test_split(valores[0], row[valores[0]], valores[2])
        gini = gini_index(groups, valores[1])
        if gini < b_score:
            b_index, b_value, b_score, b_groups = valores[0], row[valores[0]], gini, groups
    return [b_index, b_value, b_score, b_groups]


# Select the best split point for a dataset
def get_split(dataset):
    class_values = list(set(row[-1] for row in dataset))
    b_index, b_value, b_score, b_groups = 999, 999, 999, None
    if PARALLEL == True:
        valores = []
        for ii in range(NUM_ATRIBUTES):
            aux = []
            aux.append(ii)
            aux.append(class_values)
            aux.append(dataset)
            valores.append(aux)
        pool = multiprocessing.Pool(1)
        resultados = pool.map(evaluate_row, valores)
        pool.close()

        for ii in range(4):
            if b_score > resultados[ii][2]:
                b_index, b_value, b_score, b_groups = resultados[ii][0], resultados[ii][1], resultados[ii][2], resultados[ii][3]
    else:
        for index in range(len(dataset[0]) - 1):
            for row in dataset:
                groups = test_split(index, row[index], dataset)
                gini = gini_index(groups, class_values)
                if gini < b_score:
                    b_index, b_value, b_score, b_groups = index, row[index], gini, groups


    return {'index': b_index, 'value': b_value, 'groups': b_groups}


# Create a terminal node value
def to_terminal(group):
    outcomes = [row[-1] for row in group]
    return max(set(outcomes), key=outcomes.count)


# Create child splits for a node or make terminal
def split(node, max_depth, min_size, depth):
    left, right = node['groups']
    del (node['groups'])
    # check for a no split
    if not left or not right:
        node['left'] = node['right'] = to_terminal(left + right)
        return
    # check for max depth
    if depth >= max_depth:
        node['left'], node['right'] = to_terminal(left), to_terminal(right)
        return
    # process left child
    if len(left) <= min_size:
        node['left'] = to_terminal(left)
    else:
        node['left'] = get_split(left)
        split(node['left'], max_depth, min_size, depth + 1)
    # process right child
    if len(right) <= min_size:
        node['right'] = to_terminal(right)
    else:
        node['right'] = get_split(right)
        split(node['right'], max_depth, min_size, depth + 1)


# Build a decision tree
def build_tree(train, max_depth, min_size):
    root = get_split(train)
    split(root, max_depth, min_size, 1)
    return root


# Make a prediction with a decision tree
def predict(node, row):
    if row[node['index']] < node['value']:
        if isinstance(node['left'], dict):
            return predict(node['left'], row)
        else:
            return node['left']
    else:
        if isinstance(node['right'], dict):
            return predict(node['right'], row)
        else:
            return node['right']


# Classification and Regression Tree Algorithm
def decision_tree(train, test, max_depth, min_size):
    tree = build_tree(train, max_depth, min_size)
    #print_tree(tree)
    predictions = list()
    for row in test:
        prediction = predict(tree, row)
        predictions.append(prediction)
    return (predictions)

# Print a decision tree
def print_tree(node, depth=0):
    if isinstance(node, dict):
        print('%s[X%d < %.3f]' % ((depth*' ', (node['index']+1), node['value'])))
        print_tree(node['left'], depth+1)
        print_tree(node['right'], depth+1)
    else:
        print('%s[%s]' % ((depth*' ', node)))

if __name__ == '__main__':

    seed(1)

    dataset = []
    for ii in range(SAMPLES):
        atributes = []
        for jj in range(NUM_ATRIBUTES):
            atributes.append(random.randint(0, 100000))
        atributes.append(random.randint(0, 1))
        dataset.append(atributes)

    inicio = time.time()
    min_size = 10
    scores = evaluate_algorithm(dataset, decision_tree, N_FOLDS, MAX_DEPTH, min_size)
    print('Scores: %s' % scores)
    print('Mean Accuracy: %.3f%%' % (sum(scores) / float(len(scores))))

    fin = time.time()
    print('Time: ', fin - inicio)

