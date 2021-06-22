import numba as nb
import numpy as np

vec1 = np.array([1, 1])
vec2 = np.array([0, 0])
print(vec1@vec2 / np.linalg.norm(vec2))
