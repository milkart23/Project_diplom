# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class FontDesignerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Font Designer")
        self.root.geometry("800x600")  # Устанавливаем размер окна

        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.image = None
        self.image_tk = None
        self.scale_factor = 1.0  # Начальный масштаб

        # Создаем фрейм для кнопок
        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.BOTTOM, pady=10)  # Добавляем отступы по вертикали

        # Кнопка загрузки изображения
        self.load_button = tk.Button(button_frame, text="Загрузить изображение", command=self.load_image,
                                     width=20, height=2, relief=tk.RAISED)
        self.load_button.pack(side=tk.LEFT, padx=5)  # Добавляем отступы по горизонтали

        # Кнопка удаления изображения
        self.delete_button = tk.Button(button_frame, text="Удалить фото", command=self.delete_image,
                                       width=20, height=2, relief=tk.RAISED)
        self.delete_button.pack(side=tk.LEFT, padx=5)  # Добавляем отступы по горизонтали

        # Кнопка увеличения изображения
        self.zoom_in_button = tk.Button(button_frame, text="+", command=self.zoom_in,
                                         width=5, height=2, relief=tk.RAISED)
        self.zoom_in_button.pack(side=tk.LEFT, padx=5)

        # Кнопка уменьшения изображения
        self.zoom_out_button = tk.Button(button_frame, text="-", command=self.zoom_out,
                                          width=5, height=2, relief=tk.RAISED)
        self.zoom_out_button.pack(side=tk.LEFT, padx=5)

        # Переменные для хранения кругов и их свойств
        self.circles = []  # Список для хранения кругов
        self.selected_circle = None  # Выбранный круг для изменения размера
        self.start_x = None
        self.start_y = None

        # Начальный радиус круга
        self.default_radius = 30

        # Обработчики событий
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)  # Движение мыши с зажатой кнопкой
        self.canvas.bind("<ButtonRelease-1>", self.on_release)  # Отпускание кнопки мыши
        self.root.bind("<Configure>", self.on_resize)  # Обработка изменения размера окна

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = Image.open(file_path)
            self.scale_factor = 1.0  # Сбрасываем масштаб при загрузке нового изображения
            self.update_image()

    def delete_image(self):
        # Очищаем холст и сбрасываем переменные
        self.canvas.delete("all")  # Удаляем все объекты на холсте
        self.image = None
        self.image_tk = None
        self.circles.clear()  # Очищаем список кругов

    def update_image(self):
        if self.image:
            new_size = (int(self.image.width * self.scale_factor), int(self.image.height * self.scale_factor))
            self.image_tk = ImageTk.PhotoImage(self.image.resize(new_size, Image.LANCZOS))
            self.center_image(new_size)

    def center_image(self, new_size):
        if self.image_tk:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            x = (canvas_width - new_size[0]) // 2
            y = (canvas_height - new_size[1]) // 2

            # Создаем или обновляем изображение на холсте
            if hasattr(self, 'image_id'):
                self.canvas.delete(self.image_id)

            self.image_id = self.canvas.create_image(x, y, anchor=tk.NW, image=self.image_tk)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))  # Обновляем область прокрутки

    def on_resize(self, event):
        if self.image_tk:
            new_size = (int(self.image.width * self.scale_factor), int(self.image.height * self.scale_factor))
            self.center_image(new_size)

    def zoom_in(self):
        if self.image:
            self.scale_factor *= 1.1  # Увеличиваем масштаб на 10%
            self.update_image()

    def zoom_out(self):
        if self.image:
            self.scale_factor /= 1.1  # Уменьшаем масштаб на 10%
            self.update_image()

    def on_click(self, event):
        for circle in self.circles:
            x1, y1, x2, y2 = circle['coords']
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.selected_circle = circle
                return

        new_circle_id = self.canvas.create_oval(event.x - self.default_radius,
                                                event.y - self.default_radius,
                                                event.x + self.default_radius,
                                                event.y + self.default_radius,
                                                outline="green", width=2)

        self.circles.append({'id': new_circle_id,
                             'coords': (event.x - self.default_radius,
                                        event.y - self.default_radius,
                                        event.x + self.default_radius,
                                        event.y + self.default_radius)})

    def on_drag(self, event):
        if self.selected_circle:
            circle = self.selected_circle
            x1, y1, x2, y2 = circle['coords']

            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            radius = int(((event.x - center_x) ** 2 + (event.y - center_y) ** 2) ** 0.5)

            if radius > 5:
                circle['coords'] = (center_x - radius, center_y - radius,
                                    center_x + radius, center_y + radius)

                self.canvas.delete(circle['id'])
                circle['id'] = self.canvas.create_oval(circle['coords'],
                                                       outline="red", width=1)

    def on_release(self, event):
        self.selected_circle = None


if __name__ == "__main__":
    root = tk.Tk()
    app = FontDesignerApp(root)
    root.mainloop()
