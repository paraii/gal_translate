__author__ = "paraii"

from configparser import ConfigParser
from hashlib import md5
from io import BytesIO
from multiprocessing import Process, Queue, freeze_support, set_start_method
from os import path
from random import randint
from sys import argv
from threading import Thread, Event
from time import sleep
from tkinter import Canvas, Tk
from aip import AipOcr
from PIL import ImageGrab
from PyHook3 import HookManager
from pythoncom import PumpMessages
from requests import post
from screenshoot import ScreenShoot


class Config:
    MATH_PATH = path.dirname(path.realpath(argv[0]))
    debug = True

    config = ConfigParser()
    config.read(MATH_PATH + r"\config.ini", encoding="utf-8-sig")

    ####################参数####################
    FONT = config.get("Other", "font")
    FONTCOLOR = config.get("Other", "font_color")
    show_text_dely = float(config.get("Other", "show_text_dely"))
    select_area_key = config.get("Other", "select_area_key")
    translate_key = config.get("Other", "translate_key")
    ##百度智能云 文字识别##
    APP_ID = config.get("BaiduOCR", "appid")
    API_KEY = config.get("BaiduOCR", "appkey")
    SECRET_KEY = config.get("BaiduOCR", "secretkey")
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    ##百度翻译开放平台##
    appid = config.get("BaiduTranslate", "appid")
    appkey = config.get("BaiduTranslate", "appkey")
    # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
    from_lang = config.get("BaiduTranslate", "from_lang")
    to_lang = config.get("BaiduTranslate", "to_lang")
    trans_url = "https://api.fanyi.baidu.com/api/trans/vip/translate"
    ####################参数####################
    def __init__(self):
        pass


def cal_bgcolor():
    bgcolor = "white"
    fontcolor = int(Config.FONTCOLOR[1:], 16)
    if (fontcolor + 1) & 0x0000FF == 0x0:
        bgcolor = fontcolor - 1
    else:
        bgcolor = fontcolor + 1
    bgcolor = hex(bgcolor).replace("0x", "#")
    return bgcolor


def debug_print(s, *args):
    if Config.debug:
        print(s, *args)


class TranslateImage:
    def __init__(self, que, result="", box_area=""):
        self.que = que
        self.result = result
        self.box_area = box_area
        self.accurate = True

    def baidu_api_ocr(self, img_bytes):
        # ocr
        options = {}
        options["language_type"] = "JAP"
        if self.accurate:
            res = Config.client.basicAccurate(img_bytes.getvalue(), options)
            if "error_code" in res and res["error_code"] == 18:
                return False
            elif "error_code" in res and res["error_code"] == 17:
                self.accurate = False
            else:
                res = res["words_result"]
                debug_print("OCR高精度")
        if not self.accurate:
            res = Config.client.basicGeneral(img_bytes.getvalue(), options)
            if "error_code" in res and res["error_code"] == 18:
                return False
            elif "error_code" in res and res["error_code"] == 17:
                self.result = "※今日OCR额度已用完"
                return True
            else:
                res = res["words_result"]
                debug_print("OCR标准精度")

        words = []
        for wrd in res:
            words.append(wrd["words"])
        query = "".join(words)
        debug_print(f"ocr result: {query}")
        return query

    def baidu_api_translate(self, query):
        salt = randint(32768, 65536)
        sign = md5(
            (Config.appid + query + str(salt) + Config.appkey).encode("utf-8")
        ).hexdigest()
        # Build request
        payload = {
            "appid": Config.appid,
            "q": query,
            "from": Config.from_lang,
            "to": Config.to_lang,
            "salt": salt,
            "sign": sign,
        }
        # Send request
        r = post(
            Config.trans_url,
            params=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        res = r.json()

        self.result = res["trans_result"][0]["dst"]
        debug_print(f"translate result: {self.result}")

    def baidu_api_run(self, img_bytes):
        is_text_exist = True
        query = self.baidu_api_ocr(img_bytes)
        if query != "":
            self.baidu_api_translate(query)
        else:
            is_text_exist = False
        return is_text_exist

    def translate_image(self):
        is_text_exist = False
        time = 0
        while not is_text_exist:
            img = self.captureImage()
            if img is not None:
                img_bytes = BytesIO()
                img.save(img_bytes, format="PNG")
                is_text_exist = self.baidu_api_run(img_bytes)
                if not is_text_exist:
                    sleep(0.5)
                    time += 1
                    if time > 10:
                        print("Timeout: cannnot find text")
                        break
        self.que.put(self.result)  # 发送翻译结果

    def captureImage(self):
        return ImageGrab.grab(self.box_area)


class HotKey(Process):  # 键盘热键监听
    def __init__(self, que):
        super().__init__()
        self.que = que
        self.keylist = []
        self.ss = None

    def grab(self):
        self.ss = ScreenShoot()
        if self.ss.box_area != None:
            self.que.put(f"box_area${self.ss.box_area}$new")  # 发送box_area

    def translate(self):
        self.que.put("translate")

    def OnKeyboardEvent(self, event):
        # print('MessageName:', event.MessageName)  # 同上，共同属性不再赘述
        # print('Message:', event.Message)
        # print('Time:', event.Time)
        # print('Window:', event.Window)
        # print('WindowName:', event.WindowName)
        # print('Ascii:', event.Ascii, chr(event.Ascii))  # 按键的ASCII码
        # print("Key:", event.Key)  # 按键的名称
        # print('KeyID:', event.KeyID)  # 按键的虚拟键值
        # print('ScanCode:', event.ScanCode)  # 按键扫描码
        # print('Extended:', event.Extended)  # 判断是否为增强键盘的扩展键
        # print('Injected:', event.Injected)
        # print('Alt', event.Alt)  # 是某同时按下Alt

        # print('Transition', event.Transition)  # 判断转换状态
        # print('---')

        if event.Key == Config.select_area_key:
            self.grab()
        elif event.Key == Config.translate_key:
            self.translate()
        elif event.Key == "Return":
            self.translate()
        else:
            self.keylist.append(event.Key)

        # 三键组合
        if len(self.keylist) > 0 and self.keylist[0] != "Lcontrol":
            self.keylist.clear()
        if len(self.keylist) > 2:
            if (
                self.keylist[0] == "Lcontrol"
                and self.keylist[1] == "Lmenu"
                and self.keylist[2] == "Z"
            ):
                self.translate()
            self.keylist.clear()
        return True

    def run(self):
        hm = HookManager()
        hm.KeyDown = self.OnKeyboardEvent
        hm.HookKeyboard()
        PumpMessages()


class ResizingCanvas(Canvas):  # 大小随窗口缩放的Canvas
    def __init__(self, parent, que=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.root = parent
        self.que = que
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.text_id = -1

        self._mouse_x = -1
        self._mouse_y = -1
        self._resizing = False
        self._moving = False

        self._rect_width = 30
        self._rect_height = 30
        self._rect_gap = 2
        self._bgcolor = cal_bgcolor()
        if self.root.attributes("-alpha") < 0.5:
            self._is_area = True
        else:
            self._is_area = False
        if self._is_area:
            self.rect_border_id = self.create_rectangle(
                0,
                0,
                0,
                0,
                outline="red",
                dash=(5, 1),
                fill=self._bgcolor,
            )

        self.rect_id = self.create_rectangle(
            0,
            0,
            0,
            0,
            activeoutline="red",
            activefill="gray",
            fill=self._bgcolor,
            tags="rect_size",
        )  # 用于触发鼠标事件的矩形

        self.rect_move_id = self.create_rectangle(
            0,
            0,
            0,
            0,
            activeoutline="red",
            activefill="yellow",
            fill=self._bgcolor,
            tags="rect_move",
        )  # 用于触发鼠标事件的矩形

        self.rect_close_id = self.create_rectangle(
            0,
            0,
            0,
            0,
            activeoutline="red",
            activefill="blue",
            fill=self._bgcolor,
            tags="rect_close",
        )  # 用于触发鼠标事件的矩形

        self.tag_bind("rect_size", "<Button-1>", self.on_mouse_down_size)
        self.tag_bind("rect_move", "<Button-1>", self.on_mouse_down_move)
        self.tag_bind("rect_size", "<Motion>", self.on_mouse_motion_size)
        self.tag_bind("rect_move", "<Motion>", self.on_mouse_motion_move)
        self.tag_bind("rect_close", "<Button-1>", self.on_mouse_down_close)
        self.bind("<ButtonRelease-1>", self.on_mouse_release)

    def get_root_rect(self):
        geo = self.root.geometry(None)
        geo = geo.split("+")
        g0 = geo[0].split("x")
        g1 = int(g0[0])
        g2 = int(g0[1])
        g3 = int(geo[1])
        g4 = int(geo[2])
        return [g3, g4, g3 + g1, g4 + g2]

    def on_mouse_down_size(self, event):
        self._resizing = True

    def on_mouse_down_move(self, event):
        self._moving = True

    def on_mouse_down_close(self, event):
        self.delete(self.rect_id)
        self.delete(self.rect_move_id)
        self.delete(self.rect_close_id)
        if self._is_area:
            self.delete(self.rect_border_id)
        self.root.quit()

    def on_mouse_motion_size(self, event):
        if self._resizing:
            geo = self.root.geometry(None)
            geo = geo.split("+")
            if event.x < 30:
                event.x = 30
            if event.y < 10:
                event.y = 10
            geo[0] = f"{event.x}x{event.y}"
            self.root.geometry("+".join(geo))

    def on_mouse_motion_move(self, event):
        if self._moving:
            if self._mouse_x == -1 and self._mouse_y == -1:
                self._mouse_x = event.x_root
                self._mouse_y = event.y_root
            else:
                delta_x = event.x_root - self._mouse_x
                delta_y = event.y_root - self._mouse_y
                self._mouse_x = event.x_root
                self._mouse_y = event.y_root
                geo = self.root.geometry(None)
                geo = geo.split("+")
                geo[1] = str(int(geo[1]) + delta_x)
                geo[2] = str(int(geo[2]) + delta_y)
                self.root.geometry("+".join(geo))

    def on_mouse_release(self, event):
        self._mouse_x = -1
        self._mouse_y = -1
        self._resizing = False
        self._moving = False
        if self._is_area:
            self.que.put(f"box_area${self.get_root_rect()}$")  # 发送box_area

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height

        self.width = event.width
        self.height = event.height

        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the 'resizable' tag
        self.scale("resizable", 0, 0, wscale, hscale)

        self.coords(self.text_id, (self.width / 2, self.height / 2))
        self.itemconfig(
            self.text_id,
            width=self.width - 2 * self._rect_width,
        )

        if self._is_area:
            self.coords(
                self.rect_border_id,
                5,
                5,
                self.width - 5,
                self.height - 5,
            )

        self.coords(
            self.rect_id,
            self.width - self._rect_width,
            self.height - self._rect_height,
            self.width,
            self.height,
        )

        self.coords(
            self.rect_move_id,
            self.width - 2 * self._rect_width - self._rect_gap,
            self.height - self._rect_height,
            self.width - self._rect_width - self._rect_gap,
            self.height,
        )

        self.coords(
            self.rect_close_id,
            self.width - 3 * self._rect_width - 2 * self._rect_gap,
            self.height - self._rect_height,
            self.width - 2 * self._rect_width - 2 * self._rect_gap,
            self.height,
        )


class PickMsg(Thread):  # 消息循环
    def __init__(self, que, canvas, transimg):
        super().__init__()
        self._running = True
        self._event = Event()
        self.que = que
        self.area = None
        self.canvas = canvas
        self.transimg = transimg

    def translate(self):
        debug_print("begin translate")
        if self.transimg.box_area != "":
            Thread(target=self.transimg.translate_image).start()
        else:
            print("Box is None")

    def terminate(self):
        self._running = False
        if self.area != None:
            self.area.terminate()

    def create_area(self):
        if self.area != None:
            self.area.terminate()
        self.area = Areawin(self.que, self.transimg.box_area)
        self.area.start()

    def run(self):
        while self._running:
            if not self.que.empty():
                msg = self.que.get()
                if msg != None:
                    msg_arg = msg.split("$")
                    if msg_arg[0] == "box_area":  # 接收box_area

                        self.transimg.box_area = [
                            float(x) for x in msg_arg[1][1:-1].split(",")
                        ]
                        debug_print(f"msg area: {self.transimg.box_area}")

                        if msg_arg[2] == "new":
                            self.create_area()

                    elif msg == "translate":
                        self.translate()
                    else:  # 接收翻译结果
                        self.canvas.itemconfig(self.canvas.text_id, text=msg)
                        # self.canvas.itemconfig(self.canvas.outline_id, text=msg)
            self._event.wait(0.1)


class Areawin(Process):
    def __init__(self, que, box):
        super().__init__()
        self.que = que
        self.box = box
        self.area_root = None
        self._running = True

    def run(self):
        bgcolor = cal_bgcolor()

        self.area_root = Tk()
        self.area_root.attributes("-transparentcolor", bgcolor)
        self.area_root.attributes("-alpha", 0.3)
        self.area_root.attributes("-topmost", 1)
        x1 = int(self.box[0])
        y1 = int(self.box[1])
        x2 = int(self.box[2])
        y2 = int(self.box[3])
        self.area_root.geometry(f"{x2-x1}x{y2-y1}+{x1}+{y1}")
        self.area_root.overrideredirect(True)
        box_canvas = ResizingCanvas(
            self.area_root,
            que=self.que,
            width=x2 - x1,
            height=y2 - y1,
            bg=bgcolor,
        )
        box_canvas.pack()
        self.area_root.mainloop()


class Tkwin(Thread):
    def __init__(self, que):
        super().__init__()
        self.que = que
        self.transimg = TranslateImage(self.que)
        self.rect_id = -1

    def change_rect_color(self):
        self.canvas.itemconfig(self.canvas.rect_id, activefill="green")
        sleep(0.1)
        self.canvas.itemconfig(self.canvas.rect_id, activefill="gray")

    def on_mouse_wheel(self, event):  # 鼠标滚轮事件
        Thread(target=self.change_rect_color).start()
        debug_print("on_mouse_wheel")
        sleep(Config.show_text_dely)
        self.que.put("translate")

    def run(self):
        bgcolor = cal_bgcolor()

        self.root = Tk()
        self.root.title("日->中")
        self.root.geometry(
            f"700x60+{(self.root.winfo_screenwidth()- 700)//2}+{(self.root.winfo_screenheight() - 60)//2}"
        )
        self.root.attributes("-transparentcolor", bgcolor)
        self.root.attributes("-alpha", 0.8)
        self.root.attributes("-topmost", 1)
        # self.root.attributes("-toolwindow", 1)
        self.root.overrideredirect(True)
        self.canvas = ResizingCanvas(self.root, width=700, height=150, bg=bgcolor)
        self.canvas.addtag_all("resizable")
        self.canvas.pack()

        msgloop = PickMsg(self.que, self.canvas, self.transimg)
        msgloop.start()

        self.canvas.text_id = self.canvas.create_text(
            (self.canvas.width / 2, self.canvas.height / 2),
            text="日->中",
            font=Config.FONT,
            fill="#FFFFFE",
            width=self.canvas.width,
        )
        # self.canvas.outline_id = self.canvas.create_text(
        #     (self.canvas.width/2, self.canvas.height/2), text='日->中', font=FONT+' bold', fill='#FFFFFE', width=self.canvas.width)

        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.root.mainloop()
        msgloop.terminate()


if __name__ == "__main__":
    freeze_support()  # Windows使用Pyinstaller对多进程打包必须 https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing
    set_start_method("spawn")
    debug_print("debug:", Config.debug)
    que = Queue()  # 通信队列
    p1 = Tkwin(que)  # GUI
    p1.start()
    p2 = HotKey(que)  # 键盘热键监听（功能入口）
    p2.start()
    p1.join()
    p2.terminate()
