from tkinter import messagebox
import numpy as np
from GraphicObject import Cross,Flag



class SetOperations:
    @staticmethod
    def get_pixel_buffer(width, height):
        # Возвращает пустой пиксельный буфер (белый фон)
        return np.full((height, width, 3), 255, dtype=np.uint8)

    @staticmethod
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return np.array([int(hex_color[i:i+2], 16) for i in (0, 2, 4)], dtype=np.uint8)

    @staticmethod
    def rgb_to_hex(rgb_color):
        return '#%02x%02x%02x' % tuple(rgb_color)

    @staticmethod
    def intersection(editor_instance, obj1, obj2):
        # Выполнение операции пересечения на пиксельном уровне
        if not (isinstance(obj1, (Cross, Flag)) and isinstance(obj2, (Cross, Flag))):
            messagebox.showwarning("ТМО: Пересечение", "Пиксельное пересечение поддерживается только для Креста и Флага. Выберите два таких объекта.")
            return

        # Создаем два временных буфера
        buffer1 = SetOperations.get_pixel_buffer(editor_instance.canvas_width, editor_instance.canvas_height)
        buffer2 = SetOperations.get_pixel_buffer(editor_instance.canvas_width, editor_instance.canvas_height)

        # Рисуем первый объект в первый буфер
        # Используем непрозрачный цвет заливки для ТМО
        original_fill_color1 = obj1.fill_color
        obj1.fill_color = "#FF0000" # Красный для obj1
        obj1.draw(editor_instance, pixel_buffer=buffer1)
        obj1.fill_color = original_fill_color1 # Восстанавливаем оригинальный цвет

        # Рисуем второй объект во второй буфер
        original_fill_color2 = obj2.fill_color
        obj2.fill_color = "#0000FF" # Синий для obj2
        obj2.draw(editor_instance, pixel_buffer=buffer2)
        obj2.fill_color = original_fill_color2 # Восстанавливаем оригинальный цвет

        # Создаем буфер для результата
        result_buffer = SetOperations.get_pixel_buffer(editor_instance.canvas_width, editor_instance.canvas_height)
        intersection_color = SetOperations.hex_to_rgb("#00FF00") # Зеленый для пересечения

        # Проходим по всем пикселям и применяем логику пересечения
        # Если пиксель окрашен в обоих буферах (не белый), то это пересечение
        white = np.array([255, 255, 255], dtype=np.uint8)
        for y in range(editor_instance.canvas_height):
            for x in range(editor_instance.canvas_width):
                pixel1_is_colored = not np.array_equal(buffer1[y, x], white)
                pixel2_is_colored = not np.array_equal(buffer2[y, x], white)

                if pixel1_is_colored and pixel2_is_colored:
                    result_buffer[y, x] = intersection_color
                else:
                    result_buffer[y, x] = white # Остальное белое

        # Отображаем результат на Canvas
        editor_instance.pixels = result_buffer
        editor_instance.update_canvas_image()
        messagebox.showinfo("ТМО: Пересечение", "Результат пересечения отображен на холсте.")

    @staticmethod
    def difference(editor_instance, obj1, obj2):
        # Выполнение операции разности (obj1 - obj2) на пиксельном уровне
        if not (isinstance(obj1, (Cross, Flag)) and isinstance(obj2, (Cross, Flag))):
            messagebox.showwarning("ТМО: Разность", "Пиксельная разность поддерживается только для Креста и Флага. Выберите два таких объекта.")
            return

        # Создаем два временных буфера
        buffer1 = SetOperations.get_pixel_buffer(editor_instance.canvas_width, editor_instance.canvas_height)
        buffer2 = SetOperations.get_pixel_buffer(editor_instance.canvas_width, editor_instance.canvas_height)

        # Рисуем первый объект в первый буфер
        original_fill_color1 = obj1.fill_color
        obj1.fill_color = "#FF0000" # Красный для obj1
        obj1.draw(editor_instance, pixel_buffer=buffer1)
        obj1.fill_color = original_fill_color1

        # Рисуем второй объект во второй буфер
        original_fill_color2 = obj2.fill_color
        obj2.fill_color = "#0000FF" # Синий для obj2
        obj2.draw(editor_instance, pixel_buffer=buffer2)
        obj2.fill_color = original_fill_color2

        # Создаем буфер для результата
        result_buffer = SetOperations.get_pixel_buffer(editor_instance.canvas_width, editor_instance.canvas_height)
        difference_color = SetOperations.hex_to_rgb("#FFA500") # Оранжевый для разности

        # Проходим по всем пикселям и применяем логику разности (A - B)
        # Если пиксель окрашен в буфере 1, но не окрашен в буфере 2
        white = np.array([255, 255, 255], dtype=np.uint8)
        for y in range(editor_instance.canvas_height):
            for x in range(editor_instance.canvas_width):
                pixel1_is_colored = not np.array_equal(buffer1[y, x], white)
                pixel2_is_colored = not np.array_equal(buffer2[y, x], white)

                if pixel1_is_colored and not pixel2_is_colored:
                    result_buffer[y, x] = difference_color
                else:
                    result_buffer[y, x] = white

        # Отображаем результат на Canvas
        editor_instance.pixels = result_buffer
        editor_instance.update_canvas_image()
        messagebox.showinfo("ТМО: Разность", "Результат разности (A - B) отображен на холсте.")

    @staticmethod
    def union(editor_instance, obj1, obj2):
        # Выполнение операции объединения на пиксельном уровне
        if not (isinstance(obj1, (Cross, Flag)) and isinstance(obj2, (Cross, Flag))):
            messagebox.showwarning("ТМО: Объединение", "Пиксельное объединение поддерживается только для Креста и Флага. Выберите два таких объекта.")
            return

        # Создаем два временных буфера
        buffer1 = SetOperations.get_pixel_buffer(editor_instance.canvas_width, editor_instance.canvas_height)
        buffer2 = SetOperations.get_pixel_buffer(editor_instance.canvas_width, editor_instance.canvas_height)

        # Рисуем первый объект в первый буфер
        original_fill_color1 = obj1.fill_color
        obj1.fill_color = "#FF0000" # Красный для obj1
        obj1.draw(editor_instance, pixel_buffer=buffer1)
        obj1.fill_color = original_fill_color1

        # Рисуем второй объект во второй буфер
        original_fill_color2 = obj2.fill_color
        obj2.fill_color = "#0000FF" # Синий для obj2
        obj2.draw(editor_instance, pixel_buffer=buffer2)
        obj2.fill_color = original_fill_color2

        # Создаем буфер для результата
        result_buffer = SetOperations.get_pixel_buffer(editor_instance.canvas_width, editor_instance.canvas_height)
        union_color = SetOperations.hex_to_rgb("#800080") # Пурпурный для объединения

        # Проходим по всем пикселям и применяем логику объединения
        # Если пиксель окрашен хотя бы в одном из буферов
        white = np.array([255, 255, 255], dtype=np.uint8)
        for y in range(editor_instance.canvas_height):
            for x in range(editor_instance.canvas_width):
                pixel1_is_colored = not np.array_equal(buffer1[y, x], white)
                pixel2_is_colored = not np.array_equal(buffer2[y, x], white)

                if pixel1_is_colored or pixel2_is_colored:
                    result_buffer[y, x] = union_color
                else:
                    result_buffer[y, x] = white

        # Отображаем результат на Canvas
        editor_instance.pixels = result_buffer
        editor_instance.update_canvas_image()
        messagebox.showinfo("ТМО: Объединение", "Результат объединения отображен на холсте.")
