import numpy as np
import math



class Transformations:
    @staticmethod
    def translation_matrix(dx, dy):
        # Создание матрицы для перемещения на (dx, dy)
        return np.array([
            [1, 0, 0],
            [0, 1, 0],
            [dx, dy, 1]
        ])

    @staticmethod
    def rotation_matrix(angle_degrees):
        # Создание матрицы для поворота на заданный угол (в градусах)
        angle_rad = math.radians(angle_degrees) # Перевод угла из градусов в радианы
        cos_a = math.cos(angle_rad) # Косинус угла
        sin_a = math.sin(angle_rad) # Синус угла
        return np.array([
            [cos_a, sin_a, 0],
            [-sin_a, cos_a, 0],
            [0, 0, 1]
        ])

    @staticmethod
    def scale_matrix(sx, sy):
        # Создание матрицы для масштабирования по осям X и Y
        return np.array([
            [sx, 0, 0],
            [0, sy, 0],
            [0, 0, 1]
        ])

    @staticmethod
    def mirror_x_axis_matrix():
        # Создание матрицы для отражения относительно оси X
        return np.array([
            [1, 0, 0],
            [0, -1, 0],
            [0, 0, 1]
        ])

    @staticmethod
    def mirror_y_axis_matrix():
        # Создание матрицы для отражения относительно оси Y
        return np.array([
            [-1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])

    @staticmethod
    def rotate_around_point(obj, angle_degrees, center_x, center_y):
        # Поворот объекта вокруг произвольной точки (center_x, center_y)
        # Последовательность преобразований:
        # 1. Перемещение объекта так, чтобы центр вращения оказался в начале координат
        T1 = Transformations.translation_matrix(-center_x, -center_y)
        # 2. Поворот объекта вокруг начала координат
        R = Transformations.rotation_matrix(angle_degrees)
        # 3. Перемещение объекта обратно в исходное положение
        T2 = Transformations.translation_matrix(center_x, center_y)
        # Комбинирование матриц преобразований: T1 -> R -> T2
        transform_matrix = np.dot(np.dot(T1, R), T2)
        #print(transform_matrix)
        obj.apply_transform(transform_matrix) # Применение полученной матрицы к объекту

    @staticmethod
    def mirror_around_figure_center(obj):
        # Отражение объекта относительно его собственного центра
        if not obj.center: # Если центр объекта не определен, вычисляем его
            obj.calculate_center()
        cx, cy = obj.center.x, obj.center.y # Координаты центра объекта

        # Последовательность преобразований для отражения относительно центра:
        # 1. Перемещение объекта так, чтобы его центр оказался в начале координат
        T1 = Transformations.translation_matrix(-cx, -cy)
        # 2. Масштабирование на -1 по обеим осям (эквивалентно отражению)
        M = Transformations.scale_matrix(-1, -1)
        # 3. Перемещение объекта обратно
        T2 = Transformations.translation_matrix(cx, cy)
        # Комбинирование матриц преобразований: T1 -> M -> T2
        transform_matrix = np.dot(np.dot(T1, M), T2)
        obj.apply_transform(transform_matrix) # Применение преобразования

    @staticmethod
    def mirror_vertical_line(obj, line_x):
        # Отражение объекта относительно вертикальной линии x = line_x
        # Последовательность преобразований:
        # 1. Перемещение объекта так, чтобы линия отражения оказалась на оси Y
        T1 = Transformations.translation_matrix(-line_x, 0)
        # 2. Отражение относительно оси Y
        M_y = Transformations.mirror_y_axis_matrix()
        # 3. Перемещение объекта обратно
        T2 = Transformations.translation_matrix(line_x, 0)
        # Комбинирование матриц преобразований
        transform_matrix = np.dot(np.dot(T1, M_y), T2)
        obj.apply_transform(transform_matrix) # Применение преобразования

    @staticmethod
    def translate(obj, dx, dy):
        # Перемещение объекта на заданные смещения dx и dy
        T = Transformations.translation_matrix(dx, dy) # Создание матрицы перемещения
        obj.apply_transform(T) # Применение матрицы к объекту

