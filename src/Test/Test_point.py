
from Point import *

# Пример 1: Обычная точка
uniform_point1 = np.array([100, 200, 1])
p1 = Point.from_uniform(uniform_point1)
print(f"Из {uniform_point1} -> {p1}")
# Вывод: Из [100 200   1] -> Point(100, 200)

# Пример 2: Та же точка с другим W
uniform_point2 = np.array([200, 400, 2])
p2 = Point.from_uniform(uniform_point2)
print(f"Из {uniform_point2} -> {p2}")
# Вывод: Из [200 400   2] -> Point(100, 200)

# Пример 3: Направленный вектор (или точка на бесконечности)
uniform_vector = np.array([50, 75, 0])
p_vec = Point.from_uniform(uniform_vector)
print(f"Из {uniform_vector} -> {p_vec}")
# Вывод: Из [50 75  0] -> Point(50, 75)
# Здесь деления на 0 не происходит, так как это особая обработка.

# Пример 4: Входная матрица 1x3
uniform_matrix_row = np.array([[300, 600, 3]])
p_matrix_row = Point.from_uniform(uniform_matrix_row)
print(f"Из {uniform_matrix_row} -> {p_matrix_row}")
# Вывод: Из [[300 600   3]] -> Point(100, 200)