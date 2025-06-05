import numpy as np
from Point import Point # Убедитесь, что Point.py находится в той же директории или доступен в PYTHONPATH


# Базовый класс для всех графических фигур
class GraphicObject:
    def __init__(self, color="#000000", fill_color="#0003AEFF"):
        self.points = [] # Список вершин/ключевых точек фигуры (декартовы координаты)
        self.color = color # Цвет контура
        self.fill_color = fill_color # Цвет заливки
        self.id = None
        self.center = Point(0, 0) # Центр фигуры (вычисляется из points)
        self.calculate_center() # Вычислить центр при создании

    def draw(self, editor_instance, pixel_buffer=None):
        raise NotImplementedError # Должен быть переопределен для отрисовки конкретной фигуры

    def apply_transform(self, transform_matrix):
        # Применение матрицы преобразования к каждой точке объекта
        new_points_homogeneous = []
        for p in self.points:
            # 1. Точка в однородные: [x, y, 1]
            hom_coords = p.to_uniform()
            # 2. Умножение на матрицу преобразования: [X', Y', W'] = [x, y, 1] . M
            transformed_hom_coords = np.dot(hom_coords, transform_matrix)
            # 3. Обратно в декартовы: Point(X'/W', Y'/W')
            new_points_homogeneous.append(Point.from_uniform(transformed_hom_coords))
        self.points = new_points_homogeneous # Обновить точки фигуры
        self.calculate_center() # Пересчитать центр

    def calculate_center(self):
        # Вычисление среднего арифметического координат всех точек объекта
        if not self.points:
            self.center = Point(0, 0)
            return

        # Среднее по X: sum(x_i) / N
        sum_x = sum(p.x for p in self.points)
        meanX = sum_x / len(self.points)
        # Среднее по Y: sum(y_i) / N
        sum_y = sum(p.y for p in self.points)
        meanY = sum_y / len(self.points)
        # print(f'Result:{len(self.points)}') # Отладочный вывод
        self.center = Point(meanX, meanY) # Установить центр

# Класс для рисования линии (отрезка)
class Line(GraphicObject):
    def __init__(self, p1, p2, color="#000000"):
        super().__init__(color=color)
        self.points = [p1, p2] # Две конечные точки линии: P1=(x1,y1), P2=(x2,y2)
        self.calculate_center()

    def draw(self, editor_instance, pixel_buffer=None):
        # Отрисовка линии: передача начальной и конечной точки для отрисовки
        editor_instance.bresenham_line(self.points[0], self.points[1], self.color, pixel_buffer=pixel_buffer)

# Класс для рисования креста (Kr)
class Cross(GraphicObject):
    def __init__(self, center_x, center_y, size, color="#000000", fill_color="#FFFFFFFF"):
        super().__init__(color=color, fill_color=fill_color)
        half_size = size / 2
        quarter_size = size / 4
        # Определение 12 вершин многоугольника (x,y) для формы креста
        self.points = [
            Point(center_x - quarter_size, center_y - half_size), # Верхняя левая часть верхней перекладины
            Point(center_x + quarter_size, center_y - half_size), # Верхняя правая часть верхней перекладины
            Point(center_x + quarter_size, center_y - quarter_size), # Правый верхний угол центра
            Point(center_x + half_size, center_y - quarter_size), # Правая верхняя часть правой перекладины
            Point(center_x + half_size, center_y + quarter_size), # Правая нижняя часть правой перекладины
            Point(center_x + quarter_size, center_y + quarter_size), # Правый нижний угол центра
            Point(center_x + quarter_size, center_y + half_size), # Нижняя правая часть нижней перекладины
            Point(center_x - quarter_size, center_y + half_size), # Нижняя левая часть нижней перекладины
            Point(center_x - quarter_size, center_y + quarter_size), # Левый нижний угол центра
            Point(center_x - half_size, center_y + quarter_size), # Левая нижняя часть левой перекладины
            Point(center_x - half_size, center_y - quarter_size), # Левая верхняя часть левой перекладины
            Point(center_x - quarter_size, center_y - quarter_size)  # Левый верхний угол центра
        ]
        self.calculate_center()

    def draw(self, editor_instance, pixel_buffer=None):
        # Заливка и отрисовка контура по всем 12 точкам
        editor_instance.scanline_fill(self.points, self.color, self.fill_color, pixel_buffer=pixel_buffer)

# Класс для рисования флага (Flag)
class Flag(GraphicObject):
    def __init__(self, base_x, base_y, width, height, color="#000000", fill_color="#FFFFFFFF"):
        super().__init__(color=color, fill_color=fill_color)
        # Определение 5 вершин многоугольника (x,y) для формы флага
        self.points = [
            Point(base_x, base_y),                 # Нижний левый угол
            Point(base_x, base_y - height),        # Верхний левый угол
            Point(base_x + width, base_y - height),# Верхний правый угол
            Point(base_x + width, base_y),         # Нижний правый угол
            Point(base_x + width/2, base_y - height/2) # Точка среза (треугольный "хвост" флага)
        ]
        self.calculate_center()

    def draw(self, editor_instance, pixel_buffer=None):
        # Заливка и отрисовка контура по 5 точкам
        editor_instance.scanline_fill(self.points, self.color, self.fill_color, pixel_buffer=pixel_buffer)

# Класс для рисования кривой Безье
class BezierCurve(GraphicObject):
    def __init__(self, control_points, color="#000000"):
        super().__init__(color=color)
        self.control_points = control_points # Список контрольных точек: C_j=(cx_j, cy_j)
        self.points = [] # Список вычисленных точек, лежащих на кривой (для отрисовки)
        self.recalculate_curve_points() # Генерируем точки кривой из контрольных
        self.calculate_center() # Центр вычисляется по сгенерированным точкам

    def recalculate_curve_points(self, num_segments=None):
        # Автоматическое определение плотности точек на кривой
        if num_segments is None:
            # num_segments определяет, на сколько отрезков будет разбита кривая.
            # Чем больше сегментов, тем больше точек будет сгенерировано на кривой,
            # и тем более гладкой она будет выглядеть.
            #
            # Формула: 50 + 10 * len(self.control_points)
            #
            # 1. `50`: Это базовое (минимальное) количество сегментов.
            #    Зачем `50`: Обеспечивает достаточную гладкость для простых кривых (например, квадратичных с 3 контрольными точками).
            #    Без этого минимума кривая с малым числом контрольных точек (например, 2) может выглядеть как прямая.
            #
            # 2. `10 * len(self.control_points)`: Это дополнительное количество сегментов,
            #    которое зависит от числа контрольных точек.
            #    Зачем `10 * len(...)`: Кривые Безье с большим количеством контрольных точек обычно более сложные
            #    и имеют больше изгибов. Увеличение числа сегментов пропорционально сложности кривой
            #    помогает сохранить её гладкость и детализацию, не делая её "угловатой".
            #    Например:
            #    - 3 контрольные точки (квадратичная кривая): num_segments = 50 + 10*3 = 80
            #    - 4 контрольные точки (кубическая кривая): num_segments = 50 + 10*4 = 90
            #    - 5 контрольных точек: num_segments = 50 + 10*5 = 100
            #
            # На что влияет `num_segments`:
            # - **Гладкость кривой:** Большее значение `num_segments` приводит к более гладкой и точной отрисовке кривой,
            #   поскольку она аппроксимируется большим количеством коротких отрезков.
            # - **Производительность:** Большее значение `num_segments` означает больше вычислений (цикл по `t`)
            #   и больше точек для отрисовки, что может снизить производительность для очень сложных кривых
            #   или большого количества кривых.
            #
            num_segments = 50 + 10 * len(self.control_points)

        self.points = []
        for i in range(num_segments + 1):
            t = i / num_segments # Параметр t от 0 до 1
            self.points.append(self._de_casteljau(t)) # Вычислить точку на кривой для текущего t

    def _de_casteljau(self, t):
        # Алгоритм Де Кастельжо: итеративная линейная интерполяция
        # P(t) = sum( Binomial(N-1, i) * (1-t)^(N-1-i) * t^i * C_i )
        # Где N - число контрольных точек, C_i - i-я контрольная точка.
        points = list(self.control_points) # Создать копию для избежания изменения оригинала

        while len(points) > 1: # Пока не останется одна точка
            new_points = []
            for i in range(len(points) - 1):
                # Линейная интерполяция между соседними точками: (1-t)*P_i + t*P_{i+1}
                x = (1 - t) * points[i].x + t * points[i+1].x
                y = (1 - t) * points[i].y + t * points[i+1].y
                new_points.append(Point(x, y))
            points = new_points # Обновить список точек для следующей итерации
        return points[0] # Остается одна точка - это точка на кривой Безье для данного t

    def apply_transform(self, transform_matrix):
        # Преобразование применяем к КОНТРОЛЬНЫМ точкам
        new_control_points_homogeneous = []
        for p in self.control_points:
            # Преобразование контрольной точки в однородные: [x, y, 1]
            hom_coords = p.to_uniform()
            # Умножение на матрицу: [X', Y', W'] = [x, y, 1] . M
            transformed_hom_coords = np.dot(hom_coords, transform_matrix)
            # Обратно в декартовы: Point(X'/W', Y'/W')
            new_control_points_homogeneous.append(Point.from_uniform(transformed_hom_coords))
        self.control_points = new_control_points_homogeneous # Обновить контрольные точки
        self.recalculate_curve_points() # Пересчитать точки кривой после изменения контрольных
        self.calculate_center() # Пересчитать центр кривой

    def draw(self, editor_instance, pixel_buffer=None):
        if len(self.points) > 1:
            # Отрисовка кривой как последовательности отрезков (используя точки кривой)
            for i in range(len(self.points) - 1):
                editor_instance.wu_line(self.points[i], self.points[i+1], 
                                        self.color, pixel_buffer)
        
        # Отрисовка контрольных точек (визуальная помощь, только на основном холсте)
        if pixel_buffer is None:
            for cp in self.control_points:
                editor_instance.put_pixel(cp.x, cp.y, "#0000FF", width=3)