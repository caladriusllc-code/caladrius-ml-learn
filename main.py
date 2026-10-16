import numpy as np
import pandas as pd
from numpy.linalg import det

A = np.array([[1, -1, 2], [0, 1, 1], [0, 1, 0]])

determinant = det(A)
print("Determinant:", determinant)

data = pd.read_csv("./mldl/1_regression_lineaire.csv")
print(data.describe())
