# molecular_orbitals/utils/math_utils.py

import numpy as np

def calculate_distance(coord1: tuple, coord2: tuple) -> float:
    """
    Вычисляет Евклидово расстояние между двумя точками в 3D пространстве.
    """
    return np.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(coord1, coord2)))

def normalize_vector(vector: np.ndarray) -> np.ndarray:
    """
    Нормализует вектор, приводя его длину к 1.
    """
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm
