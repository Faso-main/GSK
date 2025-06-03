import numpy as np
from Point import Point


# Базовый класс для всех графических фигур
class GraphicObject:
    def __init__(self, color="#000000", fill_color="#0003AEFF"):
        self.points = [] # Список точек, определяющих фигуру
        self.color = color # Цвет контура фигуры (по умолчанию черный)
        self.fill_color = fill_color # Цвет заливки фигуры (по умолчанию полупрозрачный зеленый)
        self.id = None
        self.center = Point(0, 0) # Центр фигуры (инициализируется в (0,0))
        self.calculate_center() # Вычисление центра фигуры при создании

    def draw(self, editor_instance, pixel_buffer=None):
        # Метод для отрисовки объекта, должен быть переопределен в дочерних классах
        # Добавлен параметр pixel_buffer для рисования во временные буферы
        raise NotImplementedError

    def apply_transform(self, transform_matrix):
        # Применение матрицы преобразования ко всем точкам объекта
        new_points_homogeneous = []
        for p in self.points:
            hom_coords = p.to_uniform() # Преобразование текущей точки в однородные координаты
            transformed_hom_coords = np.dot(hom_coords, transform_matrix) # Умножение на матрицу преобразования
            new_points_homogeneous.append(Point.from_uniform(transformed_hom_coords)) # Преобразование обратно из однородных координат
        self.points = new_points_homogeneous # Обновление списка точек объекта
        self.calculate_center() # Пересчет центра фигуры после преобразования

    def calculate_center(self):
        # Вычисление центра объекта путем усреднения координат всех его точек
        if not self.points: # Если у объекта нет точек, центр остается (0,0)
            self.center = Point(0, 0)
            return

        sum_x = sum(p.x for p in self.points) # Сумма всех X-координат
        #print(f'Result X:{sum_x}')
        sum_y = sum(p.y for p in self.points) # Сумма всех Y-координат
        #print(f'Result X:{sum_y}')
        meanX=sum_x / len(self.points)
        meanY=sum_y / len(self.points)
        print(f'Reslut:{len(self.points)}')
        self.center = Point(meanX, meanY) # Вычисление среднего арифметического для X и Y


# Класс для рисования линии (отрезка)
class Line(GraphicObject):
    def __init__(self, p1, p2, color="#000000"):
        super().__init__(color=color) # Вызов конструктора базового класса с заданным цветом
        self.points = [p1, p2] # Линия определяется двумя точками
        self.calculate_center() # Вычисление центра линии

    def draw(self, editor_instance, pixel_buffer=None):
        # Отрисовка линии с использованием алгоритма Брезенхэма
        editor_instance.bresenham_line(self.points[0], self.points[1], self.color, pixel_buffer=pixel_buffer) # Вызов метода отрисовки линии редактора


# Класс для рисования креста (Kr)
class Cross(GraphicObject):
    def __init__(self, center_x, center_y, size, color="#000000", fill_color="#FFFFFFFF"):
        super().__init__(color=color, fill_color=fill_color) # Вызов конструктора базового класса
        half_size = size / 2 # Половина размера креста
        quarter_size = size / 4 # Четверть размера креста
        # Определение точек, образующих многоугольник в форме креста
        self.points = [
            Point(center_x - quarter_size, center_y - half_size),
            Point(center_x + quarter_size, center_y - half_size),
            Point(center_x + quarter_size, center_y - quarter_size),
            Point(center_x + half_size, center_y - quarter_size),
            Point(center_x + half_size, center_y + quarter_size),
            Point(center_x + quarter_size, center_y + quarter_size),
            Point(center_x + quarter_size, center_y + half_size),
            Point(center_x - quarter_size, center_y + half_size),
            Point(center_x - quarter_size, center_y + quarter_size),
            Point(center_x - half_size, center_y + quarter_size),
            Point(center_x - half_size, center_y - quarter_size),
            Point(center_x - quarter_size, center_y - quarter_size)
        ]
        self.calculate_center() # Вычисление центра креста

    def draw(self, editor_instance, pixel_buffer=None):
        # Заливка и отрисовка контура креста с использованием Scanline алгоритма
        editor_instance.scanline_fill(self.points, self.color, self.fill_color, pixel_buffer=pixel_buffer) # Вызов метода заливки и отрисовки контура


# Класс для рисования флага (Flag)
class Flag(GraphicObject):
    def __init__(self, base_x, base_y, width, height, color="#000000", fill_color="#FFFFFFFF"):
        super().__init__(color=color, fill_color=fill_color)
        # Определение точек флага с вырезанным треугольником с правого края
        self.points = [
            Point(base_x, base_y), 
            Point(base_x, base_y - height), 
            Point(base_x + width, base_y - height), 
            Point(base_x + width, base_y),
            Point(base_x + width/2, base_y - height/2) 
        ]
        self.calculate_center()

    def draw(self, editor_instance, pixel_buffer=None):
        # Заливка и отрисовка контура флага с использованием Scanline алгоритма
        editor_instance.scanline_fill(self.points, self.color, self.fill_color, pixel_buffer=pixel_buffer) # Вызов метода заливки и отрисовки контура

# Класс для рисования кривой Безье
class BezierCurve(GraphicObject):
    def __init__(self, control_points, color="#000000"):
        super().__init__(color=color) # Вызов конструктора базового класса
        self.control_points = control_points # Контрольные точки, используемые для построения кривой
        self.points = [] # Точки, составляющие саму кривую Безье
        self.recalculate_curve_points() # Пересчет точек кривой на основе контрольных точек
        self.calculate_center() # Вычисление центра кривой

    def recalculate_curve_points(self, num_segments=100):
        # Пересчет точек кривой на основе контрольных точек и количества сегментов
        self.points = [] # Очистка списка точек кривой
        if len(self.control_points) < 2: # Не менее двух контрольных точек для кривой
            return
        for i in range(num_segments + 1): # Итерация по количеству сегментов
            t = i / num_segments # Параметр t от 0 до 1
            self.points.append(self._de_casteljau(t)) # Добавление точки, вычисленной по алгоритму Де Кастельжо

    def _de_casteljau(self, t):
        # Реализация алгоритма Де Кастельжо для вычисления точки на кривой Безье
        points = list(self.control_points) # Создание копии списка контрольных точек

        while len(points) > 1: # Пока не останется одна точка
            new_points = []
            for i in range(len(points) - 1): # Итерация по парам точек
                x = (1 - t) * points[i].x + t * points[i+1].x # Интерполяция по X
                y = (1 - t) * points[i].y + t * points[i+1].y # Интерполяция по Y
                new_points.append(Point(x, y)) # Добавление новой интерполированной точки
            points = new_points # Обновление списка точек
        return points[0] # Возвращение конечной точки на кривой

    def apply_transform(self, transform_matrix):
        # Применение преобразования к контрольным точкам, затем пересчет кривой
        new_control_points_homogeneous = []
        for p in self.control_points:
            hom_coords = p.to_uniform() # Преобразование контрольной точки в однородные координаты
            transformed_hom_coords = np.dot(hom_coords, transform_matrix) # Умножение на матрицу преобразования
            new_control_points_homogeneous.append(Point.from_uniform(transformed_hom_coords)) # Преобразование обратно
        self.control_points = new_control_points_homogeneous # Обновление контрольных точек
        self.recalculate_curve_points() # Пересчет точек самой кривой
        self.calculate_center() # Пересчет центра кривой

    def draw(self, editor_instance, pixel_buffer=None):
        # Отрисовка кривой путем соединения ее точек отрезками
        if len(self.points) > 1:
            for i in range(len(self.points) - 1):
                editor_instance.bresenham_line(self.points[i], self.points[i+1], self.color, pixel_buffer=pixel_buffer) # Отрисовка отрезка между соседними точками кривой

        # Опциональная отрисовка контрольных точек
        # Обычно контрольные точки не рисуются в буферы для ТМО
        if pixel_buffer is None: # Рисуем контрольные точки только на основном холсте
            for cp in self.control_points:
                editor_instance.put_pixel(cp.x, cp.y, "#0000FF", width=3) # Отрисовка контрольных точек синим цветом

