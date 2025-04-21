import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
import math


class FontEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Редактор шрифтов")

        # Настройка главного окна
        self.root.geometry("1200x800")

        # Переменные для хранения данных
        self.image_path = None
        self.original_image = None
        self.display_image = None
        self.image_tk = None
        self.current_curve = []  # Текущая кривая: [(x, y, radius), ...]
        self.all_curves = []  # Все кривые
        self.selected_point = None
        self.zoom_level = 1.0
        self.preview_zoom = 1.0
        self.preview_offset = [0, 0]
        self.drag_start = None

        # Переменные для перемещения изображения
        self.image_offset = [0, 0]
        self.image_drag_start = None

        # Режимы работы
        self.mode = "draw"  # 'draw' - рисование, 'pan' - перемещение
        self.point_operation = "add"  # 'add' - добавление, 'resize' - изменение размера
        self.connect_mode = False  # Режим соединения кривых
        self.connect_start_point = None  # Начальная точка для соединения

        # Цвета и параметры
        self.min_radius = 1  # Минимальный размер круга 1 пиксель
        self.max_radius = 20
        self.default_radius = 5
        self.point_color = (255, 0, 0, 128)  # Полупрозрачный красный (RGBA)
        self.curve_color = (0, 0, 255, 128)  # Полупрозрачный синий
        self.preview_color = "black"
        self.connect_color = (255, 165, 0, 200)  # Оранжевый для линий соединения

        # Создание интерфейса
        self.create_widgets()

        # Привязка событий
        self.bind_events()

    def create_widgets(self):
        # Основные фреймы
        self.left_frame = tk.Frame(self.root, width=600, height=800, bg="lightgray")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self.root, width=600, height=800, bg="white")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Левая панель (изображение)
        self.image_canvas = tk.Canvas(self.left_frame, bg="gray", cursor="cross")
        self.image_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Панель инструментов левой панели
        self.left_toolbar = tk.Frame(self.left_frame, height=40, bg="lightgray")
        self.left_toolbar.pack(fill=tk.X, padx=5, pady=2)

        self.load_btn = tk.Button(self.left_toolbar, text="Загрузить изображение", command=self.load_image)
        self.load_btn.pack(side=tk.LEFT, padx=5)

        self.zoom_in_btn = tk.Button(self.left_toolbar, text="+", command=lambda: self.adjust_zoom(1.2))
        self.zoom_in_btn.pack(side=tk.LEFT, padx=5)

        self.zoom_out_btn = tk.Button(self.left_toolbar, text="-", command=lambda: self.adjust_zoom(0.8))
        self.zoom_out_btn.pack(side=tk.LEFT, padx=5)

        self.reset_zoom_btn = tk.Button(self.left_toolbar, text="Сброс масштаба", command=self.reset_zoom)
        self.reset_zoom_btn.pack(side=tk.LEFT, padx=5)

        self.reset_offset_btn = tk.Button(self.left_toolbar, text="Сброс позиции", command=self.reset_image_offset)
        self.reset_offset_btn.pack(side=tk.LEFT, padx=5)

        self.draw_mode_btn = tk.Button(self.left_toolbar, text="Режим рисования (D)",
                                       command=lambda: self.set_mode("draw"))
        self.draw_mode_btn.pack(side=tk.LEFT, padx=5)

        self.pan_mode_btn = tk.Button(self.left_toolbar, text="Режим перемещения (P)",
                                      command=lambda: self.set_mode("pan"))
        self.pan_mode_btn.pack(side=tk.LEFT, padx=5)

        self.resize_btn = tk.Button(self.left_toolbar, text="Режим изменения размера (R)",
                                    command=self.toggle_resize_mode)
        self.resize_btn.pack(side=tk.LEFT, padx=5)

        self.connect_btn = tk.Button(self.left_toolbar, text="Соединить кривые (C)",
                                     command=self.toggle_connect_mode)
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        # Правая панель (предпросмотр)
        self.preview_canvas = tk.Canvas(self.right_frame, bg="white", cursor="hand2")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Панель инструментов правой панели
        self.right_toolbar = tk.Frame(self.right_frame, height=40, bg="white")
        self.right_toolbar.pack(fill=tk.X, padx=5, pady=2)

        self.clear_btn = tk.Button(self.right_toolbar, text="Очистить", command=self.clear_curves)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        self.undo_btn = tk.Button(self.right_toolbar, text="Отменить", command=self.undo_last_point)
        self.undo_btn.pack(side=tk.LEFT, padx=5)

        self.finish_curve_btn = tk.Button(self.right_toolbar, text="Завершить кривую",
                                          command=self.finish_current_curve)
        self.finish_curve_btn.pack(side=tk.LEFT, padx=5)

        self.preview_zoom_in = tk.Button(self.right_toolbar, text="+", command=lambda: self.adjust_preview_zoom(1.2))
        self.preview_zoom_in.pack(side=tk.LEFT, padx=5)

        self.preview_zoom_out = tk.Button(self.right_toolbar, text="-", command=lambda: self.adjust_preview_zoom(0.8))
        self.preview_zoom_out.pack(side=tk.LEFT, padx=5)

    def bind_events(self):
        # События левой панели
        self.image_canvas.bind("<Button-1>", self.on_image_click)
        self.image_canvas.bind("<B1-Motion>", self.on_image_drag)
        self.image_canvas.bind("<ButtonRelease-1>", self.on_image_release)
        self.image_canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Изменение размера круга

        # Горячие клавиши
        self.root.bind("<d>", lambda e: self.set_mode("draw"))
        self.root.bind("<p>", lambda e: self.set_mode("pan"))
        self.root.bind("<r>", lambda e: self.toggle_resize_mode())
        self.root.bind("<c>", lambda e: self.toggle_connect_mode())

        # События правой панели
        self.preview_canvas.bind("<Button-1>", self.start_pan)
        self.preview_canvas.bind("<B1-Motion>", self.pan_preview)
        self.preview_canvas.bind("<ButtonRelease-1>", self.stop_pan)

    def set_mode(self, mode):
        self.mode = mode
        if mode == "draw":
            self.image_canvas.config(cursor="cross")
        else:
            self.image_canvas.config(cursor="hand1")

        # Выходим из режима соединения при смене режима
        if mode != "draw":
            self.connect_mode = False
            self.connect_start_point = None
            self.connect_btn.config(relief=tk.RAISED)
            self.update_image_display()

    def toggle_resize_mode(self):
        self.point_operation = "resize" if self.point_operation == "add" else "add"
        self.resize_btn.config(
            text=f"Режим {'добавления' if self.point_operation == 'add' else 'изменения размера'} (R)"
        )

    def toggle_connect_mode(self):
        self.connect_mode = not self.connect_mode
        if self.connect_mode:
            self.set_mode("draw")  # Переключаемся в режим рисования
            self.connect_btn.config(relief=tk.SUNKEN)
        else:
            self.connect_start_point = None
            self.connect_btn.config(relief=tk.RAISED)

        self.update_image_display()

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Изображения", "*.png;*.jpg;*.jpeg;*.bmp;*.tif"), ("Все файлы", "*.*")])
        if file_path:
            try:
                self.image_path = file_path
                self.original_image = Image.open(file_path)
                self.display_image = self.original_image.copy()
                self.image_offset = [0, 0]
                self.update_image_display()
                self.zoom_level = 1.0
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {str(e)}")

    def on_image_click(self, event):
        if not self.original_image:
            return

        if self.mode == "draw":
            x = (event.x - self.image_offset[0]) / self.zoom_level
            y = (event.y - self.image_offset[1]) / self.zoom_level

            # Проверка на клик по точке
            for curve_idx, curve in enumerate(self.all_curves + [self.current_curve]):
                for point_idx, (px, py, radius) in enumerate(curve):
                    canvas_px = (px * self.zoom_level) + self.image_offset[0]
                    canvas_py = (py * self.zoom_level) + self.image_offset[1]
                    distance = math.sqrt((event.x - canvas_px) ** 2 + (event.y - canvas_py) ** 2)

                    if distance <= radius * self.zoom_level:
                        if self.connect_mode:
                            if self.connect_start_point is None:
                                # Выбираем первую точку для соединения
                                self.connect_start_point = (curve_idx, point_idx)
                            else:
                                # Соединяем точки
                                start_curve, start_point = self.connect_start_point
                                end_curve, end_point = (curve_idx, point_idx)

                                # Проверяем, что точки из разных кривых
                                if start_curve != end_curve:
                                    # Получаем координаты точек
                                    if start_curve < len(self.all_curves):
                                        x1, y1, r1 = self.all_curves[start_curve][start_point]
                                    else:
                                        x1, y1, r1 = self.current_curve[start_point]

                                    if end_curve < len(self.all_curves):
                                        x2, y2, r2 = self.all_curves[end_curve][end_point]
                                    else:
                                        x2, y2, r2 = self.current_curve[end_point]

                                    # Создаем новую кривую-соединение
                                    avg_radius = (r1 + r2) / 2
                                    connection_curve = [
                                        (x1, y1, r1),
                                        ((x1 + x2) / 2, (y1 + y2) / 2, avg_radius),
                                        (x2, y2, r2)
                                    ]
                                    self.all_curves.append(connection_curve)

                                # Сбрасываем режим соединения
                                self.connect_start_point = None
                                self.connect_mode = False
                                self.connect_btn.config(relief=tk.RAISED)
                        else:
                            self.selected_point = (curve_idx, point_idx)
                        self.update_image_display()
                        return

            # Добавление новой точки
            if not self.connect_mode and self.point_operation == "add" and len(
                    self.current_curve) < 6:  # До 6 точек для 5-й степени
                self.current_curve.append((x, y, self.default_radius))
                self.update_image_display()
                self.update_preview()

        elif self.mode == "pan":
            self.image_drag_start = (event.x, event.y)

    def on_image_drag(self, event):
        if self.mode == "draw" and self.selected_point is not None:
            x = (event.x - self.image_offset[0]) / self.zoom_level
            y = (event.y - self.image_offset[1]) / self.zoom_level

            curve_idx, point_idx = self.selected_point
            if curve_idx < len(self.all_curves):
                old_x, old_y, radius = self.all_curves[curve_idx][point_idx]
                self.all_curves[curve_idx][point_idx] = (x, y, radius)
            else:
                old_x, old_y, radius = self.current_curve[point_idx]
                self.current_curve[point_idx] = (x, y, radius)

            self.update_image_display()
            self.update_preview()

        elif self.mode == "pan" and self.image_drag_start:
            dx = event.x - self.image_drag_start[0]
            dy = event.y - self.image_drag_start[1]
            self.image_drag_start = (event.x, event.y)

            self.image_offset[0] += dx
            self.image_offset[1] += dy
            self.update_image_display()

    def on_mouse_wheel(self, event):
        if self.mode == "draw" and self.selected_point is not None:
            # Изменение размера выбранной точки
            delta = 1 if event.delta > 0 else -1
            curve_idx, point_idx = self.selected_point

            if curve_idx < len(self.all_curves):
                x, y, radius = self.all_curves[curve_idx][point_idx]
                new_radius = max(self.min_radius, min(radius + delta, self.max_radius))
                self.all_curves[curve_idx][point_idx] = (x, y, new_radius)
            else:
                x, y, radius = self.current_curve[point_idx]
                new_radius = max(self.min_radius, min(radius + delta, self.max_radius))
                self.current_curve[point_idx] = (x, y, new_radius)

            self.update_image_display()
            self.update_preview()

    def on_image_release(self, event):
        self.selected_point = None
        self.image_drag_start = None

    def bezier_point(self, points, t):
        """Вычисляет точку на кривой Безье для заданного t (0-1)"""
        n = len(points) - 1
        x, y = 0.0, 0.0
        for i, (px, py) in enumerate(points):
            # Биномиальный коэффициент
            coeff = math.comb(n, i) * (1 - t) ** (n - i) * t ** i
            x += px * coeff
            y += py * coeff
        return x, y

    def bezier_radius(self, radii, t):
        """Вычисляет радиус на кривой Безье для заданного t (0-1)"""
        n = len(radii) - 1
        r = 0.0
        for i, radius in enumerate(radii):
            # Биномиальный коэффициент
            coeff = math.comb(n, i) * (1 - t) ** (n - i) * t ** i
            r += radius * coeff
        return r

    def update_image_display(self):
        if self.display_image:
            width, height = self.display_image.size
            new_width = int(width * self.zoom_level)
            new_height = int(height * self.zoom_level)

            resized_image = self.display_image.resize((new_width, new_height), Image.LANCZOS)

            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            offset_image = Image.new("RGBA", (canvas_width, canvas_height), (128, 128, 128, 0))
            offset_image.paste(resized_image, (int(self.image_offset[0]), int(self.image_offset[1])))

            draw = ImageDraw.Draw(offset_image)

            # Отрисовка кривых Безье с переменной шириной
            for curve in self.all_curves + [self.current_curve if len(self.current_curve) >= 2 else []]:
                if len(curve) < 2:
                    continue

                # Создаем список точек для кривой Безье
                points = [(p[0], p[1]) for p in curve]
                radii = [p[2] for p in curve]

                # Рисуем кривую Безье с переменной шириной
                steps = 20
                for i in range(steps):
                    t1 = i / steps
                    t2 = (i + 1) / steps

                    # Вычисляем точки на кривой Безье
                    x1, y1 = self.bezier_point(points, t1)
                    x2, y2 = self.bezier_point(points, t2)
                    r1 = self.bezier_radius(radii, t1)
                    r2 = self.bezier_radius(radii, t2)

                    # Преобразуем координаты с учетом масштаба и смещения
                    canvas_x1 = (x1 * self.zoom_level) + self.image_offset[0]
                    canvas_y1 = (y1 * self.zoom_level) + self.image_offset[1]
                    canvas_x2 = (x2 * self.zoom_level) + self.image_offset[0]
                    canvas_y2 = (y2 * self.zoom_level) + self.image_offset[1]
                    canvas_r1 = max(1, r1 * self.zoom_level)  # Не меньше 1 пикселя
                    canvas_r2 = max(1, r2 * self.zoom_level)

                    # Рисуем сегмент кривой с плавным изменением ширины
                    segment_steps = max(3, int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)))
                    for j in range(segment_steps):
                        t = j / (segment_steps - 1)
                        x = x1 + (x2 - x1) * t
                        y = y1 + (y2 - y1) * t
                        radius = r1 + (r2 - r1) * t

                        cx = (x * self.zoom_level) + self.image_offset[0]
                        cy = (y * self.zoom_level) + self.image_offset[1]
                        cr = max(1, radius * self.zoom_level)  # Не меньше 1 пикселя

                        draw.ellipse(
                            [cx - cr, cy - cr, cx + cr, cy + cr],
                            fill=self.curve_color,
                            outline=self.curve_color
                        )

            # Отрисовка контрольных точек (только в левом окне)
            for curve in self.all_curves + [self.current_curve]:
                for x, y, radius in curve:
                    cx = (x * self.zoom_level) + self.image_offset[0]
                    cy = (y * self.zoom_level) + self.image_offset[1]
                    cr = max(1, radius * self.zoom_level)  # Не меньше 1 пикселя

                    draw.ellipse(
                        [cx - cr, cy - cr, cx + cr, cy + cr],
                        fill=self.point_color,
                        outline=(0, 0, 0, 255)  # Черная граница для видимости
                    )

            # Отрисовка линии соединения в режиме соединения
            if self.connect_mode and self.connect_start_point is not None:
                curve_idx, point_idx = self.connect_start_point
                if curve_idx < len(self.all_curves):
                    x1, y1, r1 = self.all_curves[curve_idx][point_idx]
                else:
                    x1, y1, r1 = self.current_curve[point_idx]

                # Получаем текущую позицию мыши
                mouse_x = (self.root.winfo_pointerx() - self.root.winfo_rootx() -
                           self.image_canvas.winfo_x() - self.image_offset[0]) / self.zoom_level
                mouse_y = (self.root.winfo_pointery() - self.root.winfo_rooty() -
                           self.image_canvas.winfo_y() - self.image_offset[1]) / self.zoom_level

                # Рисуем временную линию соединения
                canvas_x1 = (x1 * self.zoom_level) + self.image_offset[0]
                canvas_y1 = (y1 * self.zoom_level) + self.image_offset[1]
                canvas_x2 = (mouse_x * self.zoom_level) + self.image_offset[0]
                canvas_y2 = (mouse_y * self.zoom_level) + self.image_offset[1]

                # Рисуем линию с плавным изменением ширины
                steps = 20
                for i in range(steps):
                    t = i / (steps - 1)
                    x = canvas_x1 + (canvas_x2 - canvas_x1) * t
                    y = canvas_y1 + (canvas_y2 - canvas_y1) * t
                    radius = max(1, (r1 * self.zoom_level) * (1 - t * 0.5))  # Плавное уменьшение радиуса

                    draw.ellipse(
                        [x - radius, y - radius, x + radius, y + radius],
                        fill=self.connect_color,
                        outline=self.connect_color
                    )

            self.image_tk = ImageTk.PhotoImage(offset_image)
            self.image_canvas.delete("all")
            self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)

    def reset_image_offset(self):
        self.image_offset = [0, 0]
        self.update_image_display()

    def finish_current_curve(self):
        if len(self.current_curve) >= 2:
            self.all_curves.append(self.current_curve.copy())
            self.current_curve = []
            self.update_image_display()
            self.update_preview()

    def undo_last_point(self):
        if self.current_curve:
            self.current_curve.pop()
            self.update_image_display()
            self.update_preview()
        elif self.all_curves:
            self.current_curve = self.all_curves.pop()
            self.undo_last_point()

    def clear_curves(self):
        self.all_curves = []
        self.current_curve = []
        self.update_image_display()
        self.update_preview()

    def adjust_zoom(self, factor):
        self.zoom_level *= factor
        self.zoom_level = max(0.1, min(self.zoom_level, 10.0))
        self.update_image_display()

    def reset_zoom(self):
        self.zoom_level = 1.0
        self.update_image_display()

    def update_preview(self, *args):
        self.preview_canvas.delete("all")

        for curve in self.all_curves + [self.current_curve if len(self.current_curve) >= 2 else []]:
            if len(curve) < 2:
                continue

            # Создаем список точек для кривой Безье
            points = [(p[0], p[1]) for p in curve]
            radii = [p[2] for p in curve]

            # Рисуем кривую Безье с переменной шириной (без точек в правом окне)
            steps = 20
            for i in range(steps):
                t1 = i / steps
                t2 = (i + 1) / steps

                # Вычисляем точки на кривой Безье
                x1, y1 = self.bezier_point(points, t1)
                x2, y2 = self.bezier_point(points, t2)
                r1 = self.bezier_radius(radii, t1)
                r2 = self.bezier_radius(radii, t2)

                # Преобразуем координаты для предпросмотра
                px1 = (x1 * self.preview_zoom) + self.preview_offset[0]
                py1 = (y1 * self.preview_zoom) + self.preview_offset[1]
                px2 = (x2 * self.preview_zoom) + self.preview_offset[0]
                py2 = (y2 * self.preview_zoom) + self.preview_offset[1]
                pr1 = max(1, r1 * self.preview_zoom)  # Не меньше 1 пикселя
                pr2 = max(1, r2 * self.preview_zoom)

                # Рисуем сегмент кривой с плавным изменением ширины
                segment_steps = max(3, int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)))
                for j in range(segment_steps):
                    t = j / (segment_steps - 1)
                    x = px1 + (px2 - px1) * t
                    y = py1 + (py2 - py1) * t
                    radius = pr1 + (pr2 - pr1) * t

                    self.preview_canvas.create_oval(
                        x - radius, y - radius, x + radius, y + radius,
                        fill=self.preview_color, outline=""
                    )

    def adjust_preview_zoom(self, factor):
        self.preview_zoom *= factor
        self.preview_zoom = max(0.1, min(self.preview_zoom, 10.0))
        self.update_preview()

    def start_pan(self, event):
        self.drag_start = (event.x, event.y)

    def pan_preview(self, event):
        if self.drag_start:
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            self.drag_start = (event.x, event.y)

            self.preview_offset[0] += dx
            self.preview_offset[1] += dy
            self.update_preview()

    def stop_pan(self, event):
        self.drag_start = None


if __name__ == "__main__":
    root = tk.Tk()
    app = FontEditor(root)
    root.mainloop()