from win32.lib.win32con import DESKTOPHORZRES, DESKTOPVERTRES
from win32.win32api import GetSystemMetrics
from win32.win32gui import GetDC
from win32.win32print import GetDeviceCaps
from tkinter import Canvas, Tk

# 框选按 Space 确认, Esc 退出
class Box:
    def __init__(self):
        self.start_x = -1
        self.start_y = -1
        self.end_x = -1
        self.end_y = -1

    def is_none(self):
        return self.start_x == -1 or self.end_x == -1

    def set_start(self, x, y):
        self.start_x = x
        self.start_y = y

    def set_end(self, x, y):
        self.end_x = x
        self.end_y = y

    def box(self):
        lt_x = min(self.start_x, self.end_x)
        lt_y = min(self.start_y, self.end_y)
        rb_x = max(self.start_x, self.end_x)
        rb_y = max(self.start_y, self.end_y)
        return lt_x, lt_y, rb_x, rb_y

    def center(self):
        center_x = (self.start_x + self.end_x) / 2
        center_y = (self.start_y + self.end_y) / 2
        return center_x, center_y


class SelectionArea:
    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.area_box = Box()

    def empty(self):
        return self.area_box.is_none()

    def set_start_point(self, x, y):
        self.canvas.delete("area", "lt_txt", "rb_txt")
        self.area_box.set_start(x, y)
        # 开始坐标文字
        self.canvas.create_text(x, y - 10, text=f"({x}, {y})", fill="red", tag="lt_txt")

    def update_end_point(self, x, y):
        self.area_box.set_end(x, y)
        self.canvas.delete("area", "rb_txt")
        box_area = self.area_box.box()
        # 选择区域
        self.canvas.create_rectangle(
            *box_area, fill="black", outline="red", width=2, tags="area"
        )
        self.canvas.create_text(x, y + 10, text=f"({x}, {y})", fill="red", tag="rb_txt")


class ScreenShoot:
    def __init__(self):
        self.win = Tk()
        self.screen_scale_rate = 1

        self.width = self.win.winfo_screenwidth()
        self.height = self.win.winfo_screenheight()

        self.win.overrideredirect(True)
        self.win.attributes("-alpha", 0.25)

        self.is_selecting = False

        self.win.attributes("-topmost", 1)

        # 绑定按 Space 确认, Esc 退出
        self.win.bind("<KeyPress-Escape>", self.exit)
        self.win.bind("<KeyPress-space>", self.confirm_select_box)
        self.win.bind("<Button-1>", self.select_start)
        self.win.bind("<ButtonRelease-1>", self.select_done)
        self.win.bind("<Motion>", self.change_selection_area)

        self.canvas = Canvas(self.win, width=self.width, height=self.height)
        self.canvas.pack()
        self.area = SelectionArea(self.canvas)
        self.win.mainloop()

    def exit(self, event):
        self.box_area = None
        self.win.destroy()

    def clear(self):
        self.canvas.delete("area", "lt_txt", "rb_txt")
        self.win.attributes("-alpha", 0)

    def get_real_resolution(self):
        # 获取真实的分辨率
        hDC = GetDC(0)
        # 横向分辨率
        w = GetDeviceCaps(hDC, DESKTOPHORZRES)
        # 纵向分辨率
        h = GetDeviceCaps(hDC, DESKTOPVERTRES)
        return w, h

    def get_screen_size(self):
        # 获取DPI缩放后的分辨率
        w = GetSystemMetrics(0)
        h = GetSystemMetrics(1)
        return w, h

    def select_box(self):
        real_resolution = self.get_real_resolution()
        screen_size = self.get_screen_size()
        self.screen_scale_rate = round(real_resolution[0] / screen_size[0], 2)  # DPI缩放
        if self.area.empty():
            return None
        else:
            self.box_area = [x for x in self.area.area_box.box()]
            self.clear()

    def confirm_select_box(self, event):
        self.select_box()
        self.win.destroy()

    def select_start(self, event):
        self.is_selecting = True
        self.area.set_start_point(event.x, event.y)

    def change_selection_area(self, event):
        if self.is_selecting:
            self.area.update_end_point(event.x, event.y)

    def select_done(self, event):
        self.is_selecting = False
