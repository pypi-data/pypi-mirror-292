import pandas as pd
import numpy as np
import pickle
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def list_data():
    path1 = os.path.join(BASE_DIR, "data/imbalanced/processed")
    path2 = os.path.join(BASE_DIR, "data/balanced/processed")
    aux = {'balanced': sorted([x[:-4] for x in os.listdir(path2)])}
    aux.update({'imbalanced': sorted([x[:-4] for x in os.listdir(path1)])})
    return aux


def load_data(data, imbalanced=False, raw=False):
    type_data = 'balanced'

    if imbalanced:
        type_data = 'imbalanced'

    try:
        if not raw:
            npz = np.load(os.path.join(BASE_DIR, f"data/{type_data}/processed/{data}.npz"))
            dataset = []
            for fold in range(0, len(npz), 4):
                x_train, y_train, x_test, y_test = npz[npz.files[fold]], npz[npz.files[fold + 1]], npz[
                    npz.files[fold + 2]], \
                    npz[npz.files[fold + 3]]
                dataset.append((x_train, y_train, x_test, y_test))

            return dataset

        else:
            return pd.read_csv(os.path.join(BASE_DIR, f"data/{type_data}/raw/{data}.dat"), header=None)

    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset {data} not found")
