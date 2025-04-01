import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class FontDesignerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Редактор")
        self.root.geometry("1000x600")

        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.image = None
        self.image_tk = None
        self.scale_factor = 1.0


        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.BOTTOM, pady=10)

        self.load_button = tk.Button(button_frame, text="Загрузить изображение", command=self.load_image,
                                     width=20, height=2, relief=tk.RAISED)
        self.load_button.pack(side=tk.LEFT, padx=5)


        self.undo_button = tk.Button(button_frame, text="Назад", command=self.undo_last_action,
                                     width=20, height=2, relief=tk.RAISED)
        self.undo_button.pack(side=tk.LEFT, padx=5)


        self.zoom_in_button = tk.Button(button_frame, text="+", command=self.zoom_in,
                                         width=5, height=2, relief=tk.RAISED)
        self.zoom_in_button.pack(side=tk.LEFT, padx=5)


        self.zoom_out_button = tk.Button(button_frame, text="-", command=self.zoom_out,
                                          width=5, height=2, relief=tk.RAISED)
        self.zoom_out_button.pack(side=tk.LEFT, padx=5)


        self.circles = []
        self.selected_circle = None
        self.start_x = None
        self.start_y = None


        self.default_radius = 30


        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Configure>", self.on_resize)

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = Image.open(file_path)
            self.scale_factor = 1.0
            self.update_image()

    def undo_last_action(self):
        if self.circles:
            last_circle = self.circles.pop()
            self.canvas.delete(last_circle['id'])

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

            if hasattr(self, 'image_id'):
                self.canvas.delete(self.image_id)

            self.image_id = self.canvas.create_image(x, y, anchor=tk.NW, image=self.image_tk)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def on_resize(self, event):
        if self.image_tk:
            new_size = (int(self.image.width * self.scale_factor), int(self.image.height * self.scale_factor))
            self.center_image(new_size)

    def zoom_in(self):
        if self.image:
            self.scale_factor *= 1.1
            self.update_image()

    def zoom_out(self):
        if self.image:
            self.scale_factor /= 1.1
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
                                                outline="red", width=2)


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
