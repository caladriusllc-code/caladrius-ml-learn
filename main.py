import numpy as np
from numpy.linalg import det

A = np.array([[1,-1, 2], [0, 1, 1], [0,1,0]])

x = det(A)

print(x)

