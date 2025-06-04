import numpy as np


# Класс для точки (пиксельные координаты)
class Point:
    def __init__(self, x, y):
        self.x = int(round(x)) # Координата X, округленная до целого
        self.y = int(round(y)) # Координата Y, округленная до целого

    def to_uniform(self):
        # Преобразование точки в однородные координаты для выполнения матричных операций
        return np.array([self.x, self.y, 1])

    @staticmethod
    def from_uniform(matrix: np.array):
        # Преобразование из однородных координат обратно в обычные пиксельные координаты
        if matrix.shape == (3,): # Если входная матрица представляет собой вектор (1D массив)
            if matrix[2] != 0: # Проверка на нулевой третий элемент для деления
                return Point(matrix[0] / matrix[2], matrix[1] / matrix[2])
            else:
                return Point(matrix[0], matrix[1]) # Если третий элемент равен нулю, возвращаем точку без деления (для направленных векторов)
        elif matrix.shape == (1, 3): # Если входная матрица представляет собой строку матрицы (2D массив 1x3)
            if matrix[0, 2] != 0: # Проверка на нулевой третий элемент
                return Point(matrix[0, 0] / matrix[0, 2], matrix[0, 1] / matrix[0, 2])
            else:
                return Point(matrix[0, 0], matrix[0, 1]) # Если третий элемент равен нулю
        else:
            raise ValueError("Неожиданная форма матрицы для преобразования") # Выброс исключения при неожиданной форме матрицы

