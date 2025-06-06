import tkinter as tk
from tkinter import colorchooser, simpledialog, messagebox
import numpy as np
import math
from PIL import Image, ImageTk
from Point import Point
from GraphicObject import GraphicObject,Cross,Flag,Line,BezierCurve
from Transformations import Transformations
from TMO import SetOperations




class GraphicEditor:
    def __init__(self, master):
        self.master = master # Главное окно Tkinter
        master.title("Графический редактор (Вариант 70)") # Установка заголовка окна

        self.current_color = "#000000" # Текущий цвет обводки (по умолчанию черный)
        self.current_fill_color = "#0003AEFF" 
        self.objects = [] # Список всех графических объектов на холсте
        self.selected_object = None # Выбранный в данный момент объект
        self.drawing_primitive = None # Текущий режим рисования (например, "line", "cross")
        self.temp_points = [] # Временные точки для интерактивного рисования
        self.temp_line_id = None # ID временной линии (для трансформаций)
        self.transform_center_marker_id = None # ID маркера центра трансформации
        self.current_transformation_mode = None # Текущий режим трансформации (например, "translation", "rotation_around_point")

        self.canvas_width = 1400 # Ширина холста
        self.canvas_height = 600 # Высота холста
        # Создание холста Tkinter для рисования
        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height, bg="white", borderwidth=2, relief="groove")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Инициализация массива пикселей для ручной отрисовки (по умолчанию белый фон)
        self.pixels = np.full((self.canvas_height, self.canvas_width, 3), 255, dtype=np.uint8)
        # Создание объекта PhotoImage из массива пикселей для отображения на холсте
        self.photo_image = ImageTk.PhotoImage(Image.fromarray(self.pixels))
        self.image_item = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image) # Размещение изображения на холсте


        self.create_menu() # Вызов метода для создания меню
        self.create_toolbar() # Вызов метода для создания панели инструментов

        # Привязка событий мыши к методам-обработчикам
        self.canvas.bind("<Button-1>", self.on_canvas_click) # Левая кнопка мыши
        self.canvas.bind("<Button-3>", self.on_canvas_right_click) # Правая кнопка мыши
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.dragging_object = False # Флаг, указывающий, происходит ли перетаскивание объекта

        self.tmo_selected_objects = [] # Список для хранения двух выбранных объектов для ТМО

    def create_menu(self):
        # Создание главного меню приложения
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Выход", command=self.master.quit) # Пункт "Выход" для завершения работы приложения

        # Меню "Редактировать"
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Редактировать", menu=edit_menu)
        edit_menu.add_command(label="Выбрать объект", command=self.select_object_mode) # Переключение в режим выбора объекта
        edit_menu.add_command(label="Удалить выбранный", command=self.delete_selected_object) # Удаление выбранного объекта
        edit_menu.add_command(label="Очистить всё", command=self.clear_all_objects) # Очистка всего холста

        # Меню "Примитивы"
        primitives_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Примитивы", menu=primitives_menu)
        primitives_menu.add_command(label="Отрезок", command=lambda: self.start_drawing("line")) # Начать рисование отрезка
        primitives_menu.add_command(label="Крест (Kr)", command=lambda: self.start_drawing("cross")) # Начать рисование креста
        primitives_menu.add_command(label="Флаг (Flag)", command=lambda: self.start_drawing("flag")) # Начать рисование флага
        primitives_menu.add_command(label="Кривая Безье", command=lambda: self.start_drawing("bezier")) # Начать рисование кривой Безье

        # Меню "ТМО" (Теоретико-множественные операции)
        tmo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ТМО", menu=tmo_menu)
        tmo_menu.add_command(label="Выбрать объекты для ТМО", command=self.select_tmo_objects_mode) # Выбор двух объектов для ТМО
        tmo_menu.add_command(label="Пересечение (A ∩ B)", command=self.perform_intersection) # Выполнить операцию пересечения
        tmo_menu.add_command(label="Разность (A \ B)", command=self.perform_difference) # Выполнить операцию разности
        tmo_menu.add_command(label="Объединение (A ∪ B)", command=self.perform_union) # Выполнить операцию объединения


        # Меню "Преобразования"
        transform_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Преобразования", menu=transform_menu)
        transform_menu.add_command(label="Перемещение", command=self.start_translation) # Начать перемещение объекта
        transform_menu.add_command(label="Поворот (Rc)", command=self.start_rotation_around_point) # Начать поворот вокруг произвольной точки
        transform_menu.add_command(label="Зеркальное отражение относительно центра фигуры (Mf)", command=self.mirror_around_figure_center) # Отразить относительно центра фигуры
        transform_menu.add_command(label="Зеркальное отражение относительно вертикальной прямой (MV)", command=self.start_mirror_vertical_line) # Отразить относительно вертикальной прямой

        # Меню "Цвет"
        color_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Цвет", menu=color_menu)
        color_menu.add_command(label="Цвет обводки", command=self.choose_outline_color) # Выбрать цвет обводки
        color_menu.add_command(label="Цвет заливки", command=self.choose_fill_color) # Выбрать цвет заливки

        # Меню "Помощь"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about) # Показать информацию о программе

    def create_toolbar(self):
        # Создание панели инструментов в нижней части окна
        toolbar = tk.Frame(self.master, bd=2, relief=tk.RAISED)
        toolbar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        # Добавление кнопок на панель инструментов для быстрого доступа к функциям
        tk.Button(toolbar, text="Отрезок", command=lambda: self.start_drawing("line")).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Крест", command=lambda: self.start_drawing("cross")).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Флаг", command=lambda: self.start_drawing("flag")).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Безье", command=lambda: self.start_drawing("bezier")).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Выбрать", command=self.select_object_mode).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Удалить", command=self.delete_selected_object).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Очистить все", command=self.clear_all_objects).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Перемещение", command=self.start_translation).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Поворот Rc", command=self.start_rotation_around_point).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Отражение Mf", command=self.mirror_around_figure_center).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Отражение MV", command=self.start_mirror_vertical_line).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Цвет обводки", command=self.choose_outline_color).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Цвет заливки", command=self.choose_fill_color).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="ТМО", command=self.select_tmo_objects_mode).pack(side=tk.LEFT, padx=2, pady=2)

    def hex_to_rgb(self, hex_color):
        # Преобразование шестнадцатеричного строкового представления цвета в кортеж RGB
        hex_color = hex_color.lstrip('#') # Удаление символа '#'
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) # Разбор строки на компоненты R, G, B и преобразование в целые числа

    def choose_outline_color(self):
        # Открытие диалога выбора цвета для обводки
        color_info = colorchooser.askcolor(title="Выбрать цвет обводки")
        if color_info[1]: # Если цвет был выбран (не отменено)
            self.current_color = color_info[1] # Обновление текущего цвета обводки
            if self.selected_object: # Если есть выбранный объект
                self.selected_object.color = self.current_color # Обновление цвета обводки выбранного объекта
                self.redraw_all_objects() # Перерисовка всех объектов для применения изменений

    def choose_fill_color(self):
        # Открытие диалога выбора цвета для заливки
        color_info = colorchooser.askcolor(title="Выбрать цвет заливки")
        if color_info[1]: # Если цвет был выбран
            self.current_fill_color = color_info[1] # Обновление текущего цвета заливки
            if self.selected_object and hasattr(self.selected_object, 'fill_color'): # Если есть выбранный объект и он поддерживает заливку
                self.selected_object.fill_color = self.current_fill_color # Обновление цвета заливки выбранного объекта
                self.redraw_all_objects() # Перерисовка всех объектов

    def show_about(self):
        # Отображение информационного окна "О программе"
        messagebox.showinfo("О программе", "Графический редактор. Вариант 70.\nРазработано в рамках курсовой работы по дисциплине \"Графические системы компьютеров\".")

    def start_drawing(self, primitive_type):
        # Переключение редактора в режим рисования определенного примитива
        self.drawing_primitive = primitive_type # Установка типа примитива для рисования
        self.temp_points = [] # Сброс временных точек
        self.selected_object = None # Снятие выделения с текущего объекта
        self.tmo_selected_objects = [] # Сброс выбранных объектов для ТМО
        self.canvas.config(cursor="cross") # Изменение курсора на "крестик"
        self.clear_transform_marker() # Удаление маркера трансформации
        self.clear_temp_line() # Удаление временной линии
        self.current_transformation_mode = None # Сброс режима трансформации
        self.redraw_all_objects() # Перерисовка всех объектов
        if primitive_type == "bezier":
            messagebox.showinfo("Кривая Безье", "Кликните левой кнопкой мыши до 20 раз для задания контрольных точек. Правая кнопка мыши для завершения.") # Инструкции для Безье


    def select_object_mode(self):
        # Переключение редактора в режим выбора объекта
        self.drawing_primitive = None # Сброс режима рисования
        self.canvas.config(cursor="arrow") # Изменение курсора на "стрелку"
        self.clear_transform_marker() # Удаление маркера трансформации
        self.clear_temp_line() # Удаление временной линии
        self.current_transformation_mode = None # Сброс режима трансформации
        self.tmo_selected_objects = [] # Сброс выбранных объектов для ТМО
        self.redraw_all_objects() # Перерисовка всех объектов

    def clear_all_objects(self):
        # Очистка всех объектов на холсте
        if messagebox.askyesno("Очистить всё", "Вы уверены, что хотите удалить все объекты с холста?"):
            self.objects = [] # Очистка списка объектов
            self.selected_object = None # Сброс выбранного объекта
            self.tmo_selected_objects = [] # Сброс выбранных объектов для ТМО
            self.clear_transform_marker()
            self.clear_temp_line()
            self.redraw_all_objects() # Перерисовка (очистка)

    def delete_selected_object(self):
        # Удаление выбранного объекта с холста
        if self.selected_object: # Если есть выбранный объект
            self.objects.remove(self.selected_object) # Удаление объекта из списка
            self.selected_object = None # Сброс выбранного объекта
            self.clear_transform_marker() # Удаление маркера трансформации
            self.tmo_selected_objects = [] # Сброс выбранных объектов для ТМО, если они были удалены
            self.redraw_all_objects() # Перерисовка всех объектов

    def on_canvas_click(self, event):
        # Обработчик события клика левой кнопкой мыши по холсту
        if self.drawing_primitive: # Если активен режим рисования примитива
            if self.drawing_primitive == "bezier":
                # Для кривой Безье добавляем контрольные точки
                if len(self.temp_points) < 20: # Ограничение до 20 точек
                    self.temp_points.append(Point(event.x, event.y))
                    self.redraw_all_objects() # Перерисовать для отображения временных маркеров
                    if len(self.temp_points) >= 2: # Временная кривая при 2+ точках
                        temp_bezier = BezierCurve(self.temp_points, "#AAAAAA")
                        temp_bezier.draw(self)
                        self.update_canvas_image()
                else:
                    messagebox.showwarning("Кривая Безье", "Достигнуто максимальное количество контрольных точек (20).")
                    # Автоматическое завершение, если достигнуто 20 точек
                    self.on_canvas_right_click(event) # Имитируем правый клик для завершения
            else: # Для других примитивов (линия, крест, флаг)
                self.temp_points.append(Point(event.x, event.y)) # Добавление текущей точки клика во временный список
                if self.drawing_primitive == "line":
                    if len(self.temp_points) == 2: # Если собрано две точки для линии
                        line = Line(self.temp_points[0], self.temp_points[1], self.current_color) # Создание объекта Line
                        self.objects.append(line) # Добавление линии в список объектов
                        self.drawing_primitive = None # Сброс режима рисования
                        self.canvas.config(cursor="arrow") # Изменение курсора на "стрелку"
                        self.selected_object = line # Выбор только что созданной линии
                        self.redraw_all_objects() # Перерисовка всех объектов
                elif self.drawing_primitive == "cross":
                    if len(self.temp_points) == 2: # Если собраны две точки для креста (центр и точка для определения размера)
                        center_x, center_y = self.temp_points[0].x, self.temp_points[0].y # Первая точка - центр
                        size = math.sqrt((event.x - center_x)**2 + (event.y - center_y)**2) * 2 # Размер определяется расстоянием до второй точки
                        cross = Cross(center_x, center_y, size, self.current_color, self.current_fill_color) # Создание объекта Cross
                        self.objects.append(cross) # Добавление креста в список объектов
                        self.drawing_primitive = None # Сброс режима рисования
                        self.canvas.config(cursor="arrow") # Изменение курсора
                        self.selected_object = cross # Выбор только что созданного креста
                        self.redraw_all_objects() # Перерисовка
                elif self.drawing_primitive == "flag":
                    if len(self.temp_points) == 2: # Если собраны две точки для флага (левый нижний угол и точка для определения размеров)
                        x1, y1 = self.temp_points[0].x, self.temp_points[0].y
                        x2, y2 = self.temp_points[1].x, self.temp_points[1].y
                        width = abs(x2 - x1) # Ширина флага
                        height = abs(y2 - y1) # Высота флага
                        flag = Flag(min(x1, x2), max(y1, y2), width, height, self.current_color, self.current_fill_color) # Создание объекта Flag
                        self.objects.append(flag) # Добавление флага в список объектов
                        self.drawing_primitive = None # Сброс режима рисования
                        self.canvas.config(cursor="arrow") # Изменение курсора
                        self.selected_object = flag # Выбор только что созданного флага
                        self.redraw_all_objects() # Перерисов

        elif self.current_transformation_mode == "rotation_around_point":
            # Установка центра вращения и запрос угла поворота
            self.transform_center = Point(event.x, event.y) # Центр поворота - точка клика
            self.draw_transform_marker_on_canvas(self.transform_center.x, self.transform_center.y, "#FF0000") # Отрисовка маркера центра
            
            if self.selected_object: # Если объект выбран, запрашиваем угол
                angle = simpledialog.askfloat("Поворот", "Введите угол поворота (градусы):") # Запрос угла у пользователя
                if angle is not None:
                    Transformations.rotate_around_point(self.selected_object, angle, self.transform_center.x, self.transform_center.y) # Выполнение поворота
                    self.redraw_all_objects() # Перерисовка всех объектов
            self.current_transformation_mode = None # Сброс режима трансформации
            self.clear_transform_marker() # Удаление маркера центра
            self.canvas.config(cursor="arrow") # Изменение курсора
        elif self.current_transformation_mode == "mirror_vertical_line":
            # Установка линии отражения для зеркального отображения по вертикали
            self.mirror_line_x = event.x # X-координата вертикальной линии
            self.draw_temp_vertical_line(self.mirror_line_x) # Отрисовка временной вертикальной линии

            if self.selected_object: # Если объект выбран
                Transformations.mirror_vertical_line(self.selected_object, self.mirror_line_x) # Выполнение отражения
                self.redraw_all_objects() # Перерисовка
            self.current_transformation_mode = None # Сброс режима трансформации
            self.clear_temp_line() # Удаление временной линии
            self.canvas.config(cursor="arrow") # Изменение курсора
        elif self.current_transformation_mode == "translation" and self.selected_object:
            # Начало перетаскивания объекта для перемещения
            self.start_drag_x = event.x # Запоминание начальной X-координаты
            self.start_drag_y = event.y # Запоминание начальной Y-координаты
            self.dragging_object = True # Установка флага перетаскивания
        elif self.current_transformation_mode == "select_tmo_objects":
            # В режиме выбора объектов для ТМО
            clicked_obj = self.get_object_at_click(event.x, event.y)
            if clicked_obj:
                if clicked_obj not in self.tmo_selected_objects:
                    self.tmo_selected_objects.append(clicked_obj)
                    self.selected_object = clicked_obj # Выделяем последний выбранный для визуализации
                    self.redraw_all_objects()
                    if len(self.tmo_selected_objects) == 2:
                        messagebox.showinfo("ТМО", "Два объекта выбраны. Теперь выберите операцию ТМО (Пересечение, Разность, Объединение).")
                        self.current_transformation_mode = None # Выходим из режима выбора для ТМО
                        self.canvas.config(cursor="arrow")
                    else:
                        messagebox.showinfo("ТМО", "Выберите второй объект для операции ТМО.")
                else:
                    messagebox.showwarning("ТМО", "Этот объект уже выбран. Выберите другой.")
            else:
                messagebox.showwarning("ТМО", "Кликните по существующему объекту для выбора.")
        else:
            # Режим выбора объекта: попытка выбрать объект по клику
            self.select_object_at_click(event.x, event.y)

    def wu_line(self, p0, p1, color, pixel_buffer=None):
        """Алгоритм Ву для сглаженных линий"""
        x0, y0 = p0.x, p0.y
        x1, y1 = p1.x, p1.y
        
        def plot(x, y, brightness):
            """Вспомогательная функция для отрисовки пикселя с прозрачностью"""
            r, g, b = self.hex_to_rgb(color)
            if 0 <= y < self.canvas_height and 0 <= x < self.canvas_width:
                if pixel_buffer is not None:
                    buffer = pixel_buffer
                else:
                    buffer = self.pixels
                
                # Смешивание цветов с учетом прозрачности
                new_r = int(buffer[y, x][0] * (1 - brightness) + r * brightness)
                new_g = int(buffer[y, x][1] * (1 - brightness) + g * brightness)
                new_b = int(buffer[y, x][2] * (1 - brightness) + b * brightness)
                
                buffer[y, x] = [new_r, new_g, new_b]

        # Определяем, является ли линия более вертикальной или горизонтальной
        steep = abs(y1 - y0) > abs(x1 - x0)
        
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        
        dx = x1 - x0
        dy = y1 - y0
        gradient = dy / dx if dx != 0 else 1
        
        # Первая конечная точка
        xend = round(x0)
        yend = y0 + gradient * (xend - x0)
        xgap = 1 - (x0 + 0.5) % 1
        xpxl1 = xend
        ypxl1 = int(yend)
        
        if steep:
            plot(ypxl1, xpxl1, (1 - (yend % 1)) * xgap)
            plot(ypxl1 + 1, xpxl1, (yend % 1) * xgap)
        else:
            plot(xpxl1, ypxl1, (1 - (yend % 1)) * xgap)
            plot(xpxl1, ypxl1 + 1, (yend % 1) * xgap)
        
        intery = yend + gradient
        
        # Вторая конечная точка
        xend = round(x1)
        yend = y1 + gradient * (xend - x1)
        xgap = (x1 + 0.5) % 1
        xpxl2 = xend
        ypxl2 = int(yend)
        
        if steep:
            plot(ypxl2, xpxl2, (1 - (yend % 1)) * xgap)
            plot(ypxl2 + 1, xpxl2, (yend % 1) * xgap)
        else:
            plot(xpxl2, ypxl2, (1 - (yend % 1)) * xgap)
            plot(xpxl2, ypxl2 + 1, (yend % 1) * xgap)
        
        # Основной цикл
        for x in range(xpxl1 + 1, xpxl2):
            if steep:
                plot(int(intery), x, 1 - (intery % 1))
                plot(int(intery) + 1, x, intery % 1)
            else:
                plot(x, int(intery), 1 - (intery % 1))
                plot(x, int(intery) + 1, intery % 1)
            intery += gradient

    def on_canvas_right_click(self, event):
        # Обработчик события клика правой кнопкой мыши
        if self.drawing_primitive == "bezier":
            if len(self.temp_points) >= 2: # Необходимо минимум 2 контрольные точки для кривой
                bezier_curve = BezierCurve(self.temp_points, self.current_color)
                self.objects.append(bezier_curve)
                self.selected_object = bezier_curve
            else:
                messagebox.showwarning("Кривая Безье", "Недостаточно контрольных точек для построения кривой Безье (минимум 2).")
            
            self.drawing_primitive = None # Сброс режима рисования
            self.temp_points = [] # Очистка временных точек
            self.canvas.config(cursor="arrow") # Изменение курсора
            self.redraw_all_objects() # Перерисовка
        else:
            # Для других режимов правый клик может сбрасывать текущее действие или выбор
            self.drawing_primitive = None
            self.temp_points = []
            self.selected_object = None
            self.current_transformation_mode = None
            self.clear_transform_marker()
            self.clear_temp_line()
            self.tmo_selected_objects = []
            self.canvas.config(cursor="arrow")
            self.redraw_all_objects()


    def on_canvas_drag(self, event):
        # Обработчик события перетаскивания мыши
        if self.dragging_object and self.selected_object and self.current_transformation_mode == "translation":
            # Если объект перетаскивается в режиме перемещения
            dx = event.x - self.start_drag_x # Вычисление смещения по X
            dy = event.y - self.start_drag_y # Вычисление смещения по Y
            Transformations.translate(self.selected_object, dx, dy) # Применение перемещения к выбранному объекту
            self.start_drag_x = event.x # Обновление начальной X-координаты
            self.start_drag_y = event.y # Обновление начальной Y-координаты
            self.redraw_all_objects() # Перерисовка всех объектов
        elif self.drawing_primitive == "bezier" and len(self.temp_points) > 0:
            # Временная отрисовка линии при добавлении контрольных точек Безье
            self.redraw_all_objects() # Очистка и перерисовка для обновления
            temp_bezier_points = list(self.temp_points) + [Point(event.x, event.y)] # Добавление текущего положения курсора как временной контрольной точки
            
            if len(temp_bezier_points) >= 2: # Только если есть хотя бы 2 точки (первая и текущее положение)
                temp_bezier = BezierCurve(temp_bezier_points, "#AAAAAA") # Создание временной кривой Безье
                temp_bezier.draw(self) # Отрисовка временной кривой
            
            # Также рисуем временную линию от последней контрольной точки до курсора
            if len(self.temp_points) > 0:
                self.bresenham_line(self.temp_points[-1], Point(event.x, event.y), "#FFA500", width=1) # Оранжевая линия
            
            self.update_canvas_image() # Обновление изображения на холсте


    def on_canvas_release(self, event):
        # Обработчик события отпускания кнопки мыши
        self.dragging_object = False # Сброс флага перетаскивания
        if self.current_transformation_mode == "translation":
            self.canvas.config(cursor="arrow") # Изменение курсора обратно на "стрелку"
            self.current_transformation_mode = None # Сброс режима трансформации

    def get_object_at_click(self, x, y):
        # Метод для получения объекта по координатам клика, возвращает первый найденный объект
        for obj in reversed(self.objects): # Итерация в обратном порядке (сверху вниз)
            if isinstance(obj, (Cross, Flag)):
                if self.is_point_in_polygon(Point(x, y), obj.points):
                    return obj
            elif isinstance(obj, BezierCurve):
                # Проверка контрольных точек
                for cp in obj.control_points:
                    if math.sqrt((x - cp.x)**2 + (y - cp.y)**2) < 10: # Область вокруг контрольной точки
                        return obj
                # Проверка самой кривой
                for i in range(len(obj.points) - 1):
                    p1 = obj.points[i]
                    p2 = obj.points[i+1]
                    dist = self.point_line_distance(Point(x, y), p1, p2)
                    if dist < 5: # Если точка близко к сегменту кривой
                        return obj
            elif isinstance(obj, Line):
                p1 = obj.points[0]
                p2 = obj.points[1]
                dist = self.point_line_distance(Point(x, y), p1, p2)
                if dist < 5:
                    return obj
        return None


    def select_object_at_click(self, x, y):
        # Метод для выбора объекта по координатам клика
        selected_obj = self.get_object_at_click(x,y)
        if selected_obj:
            self.selected_object = selected_obj # Установка выбранного объекта
        else:
            self.selected_object = None # Сброс выбранного объекта

        self.redraw_all_objects() # Перерисовка всех объектов для отображения выделения

    def point_line_distance(self, pt, p1, p2):
        # 1. Вычисляем вектор направления линии (p1 -> p2)
        dx = p2.x - p1.x  # Разница по X между точками линии
        dy = p2.y - p1.y  # Разница по Y между точками линии

        # 2. Квадрат длины вектора (dx, dy)
        length_sq = dx*dx + dy*dy  # dx² + dy² (используется вместо sqrt для оптимизации)

        # 3. Если линия вырождена в точку (p1 == p2)
        if length_sq == 0:
            # Возвращаем обычное расстояние между pt и p1
            return math.hypot(pt.x - p1.x, pt.y - p1.y)  # √((pt.x-p1.x)² + (pt.y-p1.y)²)

        # 4. Вычисляем параметр t проекции точки pt на линию (p1, p2)
        # Формула скалярного произведения: (pt - p1) · (p2 - p1) / length_sq
        t = ((pt.x - p1.x) * dx + (pt.y - p1.y) * dy) / length_sq
        
        # 5. Ограничиваем t отрезком [0, 1] (проекция должна лежать НА отрезке)
        t = max(0, min(1, t))

        # 6. Находим координаты проекции точки на линию
        proj_x = p1.x + t * dx  # p1.x + t*(p2.x - p1.x)
        proj_y = p1.y + t * dy  # p1.y + t*(p2.y - p1.y)

        # 7. Возвращаем расстояние между pt и её проекцией
        return math.hypot(pt.x - proj_x, pt.y - proj_y)  # √((pt.x-proj_x)² + (pt.y-proj_y)²)

    def is_point_in_polygon(self, pt, poly_points):
        # Проверка, находится ли точка внутри многоугольника (алгоритм "луч")
        x, y = pt.x, pt.y
        n = len(poly_points) # Количество вершин многоугольника
        inside = False # Флаг, указывающий, находится ли точка внутри

        if n < 3: # Если менее 3 точек, это не многоугольник
            return False

        p1x, p1y = poly_points[0].x, poly_points[0].y # Первая вершина многоугольника
        for i in range(n + 1): # Итерация по всем ребрам, включая замыкающее
            p2x, p2y = poly_points[i % n].x, poly_points[i % n].y # Текущая вторая вершина ребра
            # Проверка, находится ли луч справа от точки и пересекает ли ребро
            if y > min(p1y, p2y) and y <= max(p1y, p2y) and x <= max(p1x, p2x):
                if p1y != p2y:
                    xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x # X-координата пересечения луча с ребром
                if p1x == p2x or x <= xinters: # Если луч пересекает ребро
                    inside = not inside # Инвертируем флаг (пересечение четное/нечетное количество раз)
            p1x, p1y = p2x, p2y # Переход к следующему ребру
        return inside # Возвращаем результат


    def redraw_all_objects(self):
        # Полная перерисовка всего холста
        self.pixels.fill(255) # Очистка буфера пикселей (заполнение белым цветом)

        # Отрисовка всех объектов из списка
        for obj in self.objects:
            obj.draw(self)

        # Дополнительная отрисовка выделения для выбранного объекта
        if self.selected_object:
            if isinstance(self.selected_object, Line):
                self.bresenham_line(self.selected_object.points[0], self.selected_object.points[1], "#FF0000", width=3) # Выделение линии красным цветом и толщиной
            elif isinstance(self.selected_object, (Cross, Flag)):
                points = self.selected_object.points
                n = len(points)
                for i in range(n):
                    p1 = points[i] # Первая точка ребра
                    p2 = points[(i + 1) % n] # Вторая точка ребра (замыкание)
                    self.bresenham_line(p1, p2, "#FF0000", width=3) # Выделение контура многоугольника красным
            elif isinstance(self.selected_object, BezierCurve):
                # Выделение для кривой Безье: отрисовка контрольных точек и соединяющих их линий
                for cp in self.selected_object.control_points:
                    self.put_pixel(cp.x, cp.y, "#FF0000", width=5) # Отрисовка контрольных точек красным цветом

                # Отрисовка "многоугольника" из контрольных точек (визуализация управляющего полигона)
                for i in range(len(self.selected_object.control_points) - 1):
                    p1 = self.selected_object.control_points[i] # Первая контрольная точка
                    p2 = self.selected_object.control_points[i+1] # Следующая контрольная точка
                    self.bresenham_line(p1, p2, "#FF8C00", width=1) # Отрисовка оранжевых линий
            # Отрисовка временных контрольных точек для Безье, если режим активен
            if self.drawing_primitive == "bezier":
                for cp in self.temp_points:
                    self.put_pixel(cp.x, cp.y, "#00FF00", width=5) # Временные контрольные точки зеленым

        # Выделение объектов для ТМО
        if len(self.tmo_selected_objects) > 0:
            for i, obj in enumerate(self.tmo_selected_objects):
                highlight_color = "#0000FF" if i == 0 else "#00FFFF" # Синий для первого, голубой для второго
                if isinstance(obj, Line):
                    self.bresenham_line(obj.points[0], obj.points[1], highlight_color, width=3)
                elif isinstance(obj, (Cross, Flag)):
                    points = obj.points
                    n = len(points)
                    for j in range(n):
                        p1 = points[j]
                        p2 = points[(j + 1) % n]
                        self.bresenham_line(p1, p2, highlight_color, width=3)
                elif isinstance(obj, BezierCurve):
                    for cp in obj.control_points:
                        self.put_pixel(cp.x, cp.y, highlight_color, width=5)
                    for j in range(len(obj.control_points) - 1):
                        p1 = obj.control_points[j]
                        p2 = obj.control_points[j+1]
                        self.bresenham_line(p1, p2, highlight_color, width=1)


        self.update_canvas_image() # Обновление изображения на Canvas из пиксельного буфера

        # Рисование интерактивных маркеров поверх пикселей
        self.clear_transform_marker() # Очистка предыдущего маркера трансформации
        if self.current_transformation_mode == "rotation_around_point" and hasattr(self, 'transform_center'):
            self.draw_transform_marker_on_canvas(self.transform_center.x, self.transform_center.y, "#FF0000") # Отрисовка маркера центра вращения
        
        self.clear_temp_line() # Очистка предыдущей временной линии
        if self.current_transformation_mode == "mirror_vertical_line" and hasattr(self, 'mirror_line_x'):
            self.draw_temp_vertical_line(self.mirror_line_x) # Отрисовка временной вертикальной линии отражения

        # Если объект выбран, рисуем его центр
        if self.selected_object and self.selected_object.center and self.current_transformation_mode != "select_tmo_objects":
            # Не рисуем центр для Bezier, если мы в режиме рисования Bezier
            if not (isinstance(self.selected_object, BezierCurve) and self.drawing_primitive == "bezier"):
                self.draw_transform_marker_on_canvas(self.selected_object.center.x, self.selected_object.center.y, "#00FF00") # Отрисовка центра выбранного объекта зеленым

    def put_pixel(self, x, y, color_hex, width=1, pixel_buffer=None):
        # Установка пикселя в буфер с заданным цветом и учетом толщины
        r, g, b = self.hex_to_rgb(color_hex) # Преобразование HEX цвета в RGB
        x = int(round(x)) # Округление X-координаты до целого
        y = int(round(y)) # Округление Y-координаты до целого

        target_buffer = pixel_buffer if pixel_buffer is not None else self.pixels # Выбор буфера

        # Отрисовка квадрата пикселей для имитации толщины
        for dy_offset in range(-width // 2, width - width // 2):
            for dx_offset in range(-width // 2, width - width // 2):
                px, py = x + dx_offset, y + dy_offset # Смещенные координаты пикселя
                if 0 <= py < self.canvas_height and 0 <= px < self.canvas_width: # Проверка, что пиксель находится в пределах холста
                    target_buffer[py, px] = [r, g, b] # Установка цвета пикселя в буфер


    def update_canvas_image(self):
        # Обновление изображения на холсте Tkinter из пиксельного буфера
        self.photo_image = ImageTk.PhotoImage(image=Image.fromarray(self.pixels)) # Создание PhotoImage из текущего массива пикселей
        self.canvas.itemconfig(self.image_item, image=self.photo_image) # Обновление изображения на холсте


    # Алгоритм Брезенхэма для отрисовки линии
    def bresenham_line(self, p1, p2, color, width=1, pixel_buffer=None):
        # Алгоритм Брезенхэма для отрисовки линии.
        # Зачем: Это эффективный алгоритм для отрисовки прямых линий на растровых дисплеях,
        # использующий только целочисленные операции, что ускоряет процесс
        # и избегает ошибок округления, присущих операциям с плавающей запятой.

        # Инициализация буфера пикселей, если не передан
        if pixel_buffer is None:
            pixel_buffer = self.pixels

        # Получаем целочисленные координаты начальной (p1) и конечной (p2) точек.
        x1, y1 = int(p1.x), int(p1.y)
        x2, y2 = int(p2.x), int(p2.y)

        # Вычисляем абсолютные изменения координат по X и Y.
        # Математически: |x2 - x1| и |y2 - y1|.
        # Зачем: Нужны для определения основного направления линии и расчета ошибки.
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        # Определяем направление шага по X и Y (1 или -1).
        # Зачем: Указывает, нужно ли двигаться вправо/влево или вверх/вниз.
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1

        # Инициализируем начальное значение ошибки (err).
        # Математически: err = dx - dy.
        # Зачем: Эта переменная помогает решить, какой пиксель выбрать на следующем шаге:
        # сместиться ли по X, по Y, или по обоим, чтобы оставаться максимально близко к идеальной линии.
        # Если dy больше dx, то линия ближе к вертикали, и наоборот.
        err = dx - dy

        # Главный цикл отрисовки линии. Продолжается до тех пор, пока не достигнет конечной точки.
        while True:
            # Установка текущего пикселя (x1, y1) заданным цветом.
            # Если width > 1, рисуется квадрат пикселей.
            self.put_pixel(x1, y1, color, width, pixel_buffer)

            # Проверка условия выхода из цикла: если текущий пиксель совпадает с конечной точкой.
            if x1 == x2 and y1 == y2:
                break

            # Удвоенное значение ошибки.
            # Математически: 2 * err.
            # Зачем: Используется для принятия решения о следующем шаге без дробных чисел.
            e2 = 2 * err

            # Если ошибка `e2` больше `-dy`, это означает, что линия "ушла" слишком далеко от идеальной по оси Y.
            # Корректируем ошибку, уменьшая `err` на `dy`, и делаем шаг по X.
            # Математически: err = err - dy, x1 = x1 + sx.
            # Зачем: Приближает линию к идеальной, двигаясь по горизонтали.
            if e2 > -dy:
                err -= dy
                x1 += sx

            # Если ошибка `e2` меньше `dx`, это означает, что линия "ушла" слишком далеко от идеальной по оси X.
            # Корректируем ошибку, увеличивая `err` на `dx`, и делаем шаг по Y.
            # Математически: err = err + dx, y1 = y1 + sy.
            # Зачем: Приближает линию к идеальной, двигаясь по вертикали.
            if e2 < dx:
                err += dx
                y1 += sy

    # Алгоритм Scanline для закрашивания полигона (ЗАКРАШИВАНИЕ) (PAINT)
    def scanline_fill(self, points, outline_color, fill_color, pixel_buffer=None):
        # Проверка на пустой список точек.
        # Если точек нет, полигон не существует, поэтому ничего не рисуем и выходим.
        if not points:
            return

        # Находим минимальную и максимальную Y-координаты среди всех вершин полигона.
        # Это определяет диапазон строк (сканлайнов), которые нужно обработать.
        # Зачем: Оптимизация, чтобы итерировать только по тем строкам, которые фактически пересекают полигон.
        min_y = min(p.y for p in points)
        max_y = max(p.y for p in points)

        edges = [] # Список для хранения информации о ребрах полигона.
        n = len(points) # Общее количество вершин полигона.
        
        # Обход всех ребер полигона
        for i in range(n):
            p1 = points[i]
            p2 = points[(i + 1) % n] # Следующая точка (замыкание полигона: последняя точка с первой).

            # Пропускаем горизонтальные ребра.
            # Зачем: Горизонтальные ребра не пересекают сканлайны (горизонтальные линии) в отдельных точках,
            # и их обработка требует особого подхода или может быть проигнорирована, если они не влияют на заливку.
            if p1.y == p2.y:
                continue

            # Упорядочиваем точки ребра так, чтобы p1 была ниже (имела меньшую Y-координату), чем p2.
            # Зачем: Это упрощает вычисления и обеспечивает, что ребро всегда "идет вверх" при сканировании.
            if p1.y > p2.y:
                p1, p2 = p2, p1

            # Добавляем ребро в список `edges`.
            # Формат: [ymin, ymax, x_на_ymin, 1/m (dx/dy)]
            # ymin: Y-координата нижней точки ребра.
            # ymax: Y-координата верхней точки ребра.
            # x_на_ymin: X-координата точки, соответствующей ymin.
            # inv_slope (1/m или dx/dy): Обратный наклон ребра.
            # Зачем: Позволяет эффективно вычислять X-координату пересечения сканлайна с ребром:
            # x_текущее = x_на_ymin + inv_slope * (y_текущее - ymin).
            edges.append([p1.y, p2.y, p1.x, (p2.x - p1.x) / (p2.y - p1.y)])

        # Итерация по каждой строке развертки (сканлайну) от минимальной до максимальной Y-координаты полигона.
        # Зачем: Каждая Y-координата представляет собой горизонтальную линию, которую мы "сканируем" для заливки.
        for y in range(min_y, max_y + 1):
            intersections = [] # Список для хранения X-координат пересечений текущего сканлайна с ребрами.
            
            # Для каждого ребра в списке `edges`.
            for edge in edges:
                ymin, ymax, x_curr, inv_slope = edge
                # Проверяем, пересекает ли текущий сканлайн (`y`) данное ребро.
                # `ymin <= y < ymax` гарантирует, что сканлайн находится между нижней и верхней точкой ребра
                # (исключая верхнюю точку, чтобы избежать двойного учета на стыках ребер).
                if ymin <= y < ymax:
                    # Вычисляем X-координату пересечения текущего сканлайна с ребром.
                    # Это уравнение прямой: x = x_0 + (dx/dy) * (y - y_0).
                    current_x = x_curr + inv_slope * (y - ymin)
                    intersections.append(current_x) # Добавляем X-координату пересечения.

            # Сортируем найденные X-координаты пересечений по возрастанию.
            # Зачем: Это необходимо для правильной попарной заливки.
            # Например, если пересечения [10, 50, 70, 90], мы заливаем между 10-50 и 70-90.
            intersections.sort()

            # Заливаем пиксели попарно между точками пересечения.
            # Шаг `2` означает, что мы берем пары (intersections[i], intersections[i+1]).
            # Зачем: Внутри полигона сканлайн пересекает его контур четное количество раз.
            # Между каждой такой парой находится внутренняя часть полигона.
            for i in range(0, len(intersections), 2):
                # Убеждаемся, что есть вторая точка для пары.
                if i + 1 < len(intersections):
                    # Округляем X-координаты до целых чисел для пикселей.
                    x_start = int(round(intersections[i])) # Начальная X-координата для заливки.
                    x_end = int(round(intersections[i+1])) # Конечная X-координата для заливки.
                    
                    # Итерируем по пикселям от x_start до x_end (включительно) на текущем сканлайне `y`.
                    # Зачем: Закрашиваем все пиксели, находящиеся внутри полигона на данной строке.
                    for x in range(x_start, x_end + 1):
                        # Устанавливаем пиксель в буфере `pixel_buffer` заданным цветом заливки.
                        self.put_pixel(x, y, fill_color, pixel_buffer=pixel_buffer)

        # Рисуем контур (обводку) полигона поверх заливки.
        # Зачем: Обеспечивает четкие границы полигона, которые могут быть "размыты" или неточны
        # из-за дискретизации при заливке, а также позволяет иметь контур другого цвета.
        for i in range(n):
            p1 = points[i]
            p2 = points[(i + 1) % n]
            # Используем алгоритм Брезенхэма для точной отрисовки линий контура.
            self.bresenham_line(p1, p2, outline_color, pixel_buffer=pixel_buffer)


    def clear_transform_marker(self):
        # Удаление маркера центра трансформации с холста Tkinter
        if self.transform_center_marker_id: # Если маркер существует
            # Если transform_center_marker_id является списком (несколько элементов для маркера)
            if isinstance(self.transform_center_marker_id, list):
                for item_id in self.transform_center_marker_id:
                    self.canvas.delete(item_id)
            else: # Если это одиночный ID
                self.canvas.delete(self.transform_center_marker_id) # Удаление объекта Canvas по его ID
            self.transform_center_marker_id = None # Сброс ID

    def draw_transform_marker_on_canvas(self, x, y, color_hex):
        # Рисование маркера центра трансформации (сочетание крестика и круга) на Tkinter Canvas
        self.clear_transform_marker() # Очищаем предыдущий маркер
        marker_size = 5 # Размер маркера
        
        # Рисуем круг
        oval_id = self.canvas.create_oval(x - marker_size, y - marker_size, x + marker_size, y + marker_size,
                                           outline=color_hex, width=2)
        
        # Рисуем крест
        line1_id = self.canvas.create_line(x - marker_size * 2, y, x + marker_size * 2, y, fill=color_hex, width=2)
        line2_id = self.canvas.create_line(x, y - marker_size * 2, x, y + marker_size * 2, fill=color_hex, width=2)
        
        # Сохраняем ID всех элементов маркера для последующего удаления
        self.transform_center_marker_id = [oval_id, line1_id, line2_id]


    # Методы для ТМО
    def select_tmo_objects_mode(self):
        # Переключение в режим выбора двух объектов для ТМО
        self.current_transformation_mode = "select_tmo_objects"
        self.tmo_selected_objects = [] # Очищаем список выбранных для ТМО
        self.selected_object = None # Снимаем обычное выделение
        self.canvas.config(cursor="hand2")
        messagebox.showinfo("Выбор объектов для ТМО", "Кликните на два объекта (Крест или Флаг) для выполнения ТМО.")
        self.redraw_all_objects()


    def check_tmo_selection(self):
        # Проверяет, выбраны ли два объекта для ТМО и являются ли они поддерживаемыми типами
        if len(self.tmo_selected_objects) != 2:
            messagebox.showwarning("Ошибка ТМО", "Для выполнения операции ТМО необходимо выбрать ровно два объекта.")
            return False
        # Проверка типов объектов
        for obj in self.tmo_selected_objects:
            if not isinstance(obj, (Cross, Flag)):
                messagebox.showwarning("Ошибка ТМО", "Пиксельные ТМО поддерживаются только для примитивов 'Крест' и 'Флаг'.")
                self.tmo_selected_objects = [] # Сбрасываем выбор
                self.redraw_all_objects()
                return False
        return True

    def perform_intersection(self):
        # Выполнить операцию пересечения
        if self.check_tmo_selection():
            obj1, obj2 = self.tmo_selected_objects[0], self.tmo_selected_objects[1]
            SetOperations.intersection(self, obj1, obj2)
            self.tmo_selected_objects = [] # Сбрасываем выбор после операции
            self.selected_object = None
            self.redraw_all_objects() # Возвращаем основной вид

    def perform_difference(self):
        # Выполнить операцию разности (A \ B)
        if self.check_tmo_selection():
            obj1, obj2 = self.tmo_selected_objects[0], self.tmo_selected_objects[1]
            # Предлагаем пользователю выбрать порядок
            choice = messagebox.askyesno("Разность", "Выполнить A - B? (Нет для B - A)")
            if choice: # A - B
                SetOperations.difference(self, obj1, obj2)
            else: # B - A
                SetOperations.difference(self, obj2, obj1)
            self.tmo_selected_objects = []
            self.selected_object = None
            self.redraw_all_objects()

    def perform_union(self):
        # Выполнить операцию объединения
        if self.check_tmo_selection():
            obj1, obj2 = self.tmo_selected_objects[0], self.tmo_selected_objects[1]
            SetOperations.union(self, obj1, obj2)
            self.tmo_selected_objects = []
            self.selected_object = None
            self.redraw_all_objects()

    # Геометрические преобразования
    def start_translation(self):
        # Инициализация режима перемещения объекта
        if not self.selected_object: # Если объект не выбран
            messagebox.showwarning("Ошибка", "Сначала выберите объект для перемещения.") # Предупреждение
            return
        self.current_transformation_mode = "translation" # Установка режима трансформации
        messagebox.showinfo("Перемещение", "Переместите объект, перетаскивая его мышью.") # Инструкция
        self.canvas.config(cursor="fleur") # Изменение курсора на "перемещение"
        self.tmo_selected_objects = [] # Сброс ТМО-выбора

    def start_rotation_around_point(self):
        # Инициализация режима поворота объекта вокруг произвольной точки
        if not self.selected_object: # Если объект не выбран
            messagebox.showwarning("Ошибка", "Сначала выберите объект для поворота.") # Предупреждение
            return
        self.current_transformation_mode = "rotation_around_point" # Установка режима трансформации
        messagebox.showinfo("Поворот (Rc)", "Кликните левой кнопкой мыши на холсте, чтобы задать центр поворота.") # Инструкция
        self.canvas.config(cursor="dotbox") # Изменение курсора
        self.tmo_selected_objects = [] # Сброс ТМО-выбора

    def mirror_around_figure_center(self):
        # Выполнение зеркального отражения объекта относительно его собственного центра
        if not self.selected_object: # Если объект не выбран
            messagebox.showwarning("Ошибка", "Сначала выберите объект для отражения.") # Предупреждение
            return
        Transformations.mirror_around_figure_center(self.selected_object) # Вызов статического метода трансформации
        self.redraw_all_objects() # Перерисовка
        self.tmo_selected_objects = [] # Сброс ТМО-выбора

    def start_mirror_vertical_line(self):
        # Инициализация режима зеркального отражения объекта относительно вертикальной линии
        if not self.selected_object: # Если объект не выбран
            messagebox.showwarning("Ошибка", "Сначала выберите объект для отражения.") # Предупреждение
            return
        self.current_transformation_mode = "mirror_vertical_line" # Установка режима трансформации
        messagebox.showinfo("Зеркальное отражение (MV)", "Кликните левой кнопкой мыши на холсте, чтобы задать вертикальную линию отражения.") # Инструкция
        self.canvas.config(cursor="sb_v_double_arrow") # Изменение курсора
        self.tmo_selected_objects = [] # Сброс ТМО-выбора

    def draw_temp_vertical_line(self, x):
        # Рисование временной вертикальной линии на холсте Tkinter
        self.clear_temp_line() # Очистка предыдущей временной линии
        # Создание линии на Canvas, запоминание ее ID
        self.temp_line_id = self.canvas.create_line(x, 0, x, self.canvas_height, fill="red", dash=(4, 4), width=2)

    def clear_temp_line(self):
        # Удаление временной линии с холста Tkinter
        if self.temp_line_id: # Если временная линия существует
            self.canvas.delete(self.temp_line_id) # Удаление по ID
            self.temp_line_id = None # Сброс ID


if __name__ == "__main__":
    try:
        root = tk.Tk() # Создание главного окна Tkinter
        app = GraphicEditor(root) # Создание экземпляра графического редактора
        root.mainloop() # Запуск главного цикла Tkinter
    except KeyboardInterrupt as e: print(f'Stopped by user......') # Остновка ctrl=+c
    except Exception as e: print(f'Error: {e}') # Общая обработка ошибок