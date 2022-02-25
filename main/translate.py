__author__ = "paraii"
__version__ = "v2.3"
# import traceback

from configparser import ConfigParser
from hashlib import md5
from multiprocessing import Process
from random import randint
from threading import Thread, Event
from time import sleep
from tkinter import (
    Canvas,
    Label,
    Tk,
    Menu,
    Toplevel,
    Checkbutton,
    colorchooser,
    Button,
    Entry,
    ttk,
)
from webbrowser import open as webopen
from aip import AipOcr
from mss import mss  # https://python-mss.readthedocs.io/examples.html
from mss.tools import to_png
from requests import post, get
from gui_utils.screenshoot import ScreenShoot
from gui_utils.link_label import LinkLabel
import re
import json


class Config:
    from os import path
    from sys import argv

    MATH_PATH = path.dirname(path.realpath(argv[0])).split("\\")
    MATH_PATH = "\\".join(MATH_PATH[0:-1])
    debug = True
    if re.search("[\u4e00-\u9fa5]", MATH_PATH) != None:
        input(f"文件路径不能含有中文！当前路径为{MATH_PATH}\n按任意键退出...")
    config = ConfigParser()
    config.read(MATH_PATH + r"\config.ini", encoding="utf-8-sig")

    ####################参数####################
    FONT = config.get("Other", "font")
    FONTCOLOR = config.get("Other", "font_color")
    is_local = config.get("Other", "is_localOCR")
    is_show_bg = config.get("Other", "is_show_bg")
    show_text_dely = config.get("Other", "show_text_dely")
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

    @staticmethod
    def read_config():
        Config.config.read(Config.MATH_PATH + r"\config.ini", encoding="utf-8-sig")
        ####################参数####################
        Config.FONT = Config.config.get("Other", "font")
        Config.FONTCOLOR = Config.config.get("Other", "font_color")
        Config.is_local = Config.config.get("Other", "is_localOCR")
        Config.is_show_bg = Config.config.get("Other", "is_show_bg")
        Config.show_text_dely = Config.config.get("Other", "show_text_dely")
        Config.select_area_key = Config.config.get("Other", "select_area_key")
        Config.translate_key = Config.config.get("Other", "translate_key")

        ##百度智能云 文字识别##
        Config.APP_ID = Config.config.get("BaiduOCR", "appid")
        Config.API_KEY = Config.config.get("BaiduOCR", "appkey")
        Config.SECRET_KEY = Config.config.get("BaiduOCR", "secretkey")
        Config.client = AipOcr(Config.APP_ID, Config.API_KEY, Config.SECRET_KEY)

        ##百度翻译开放平台##
        Config.appid = Config.config.get("BaiduTranslate", "appid")
        Config.appkey = Config.config.get("BaiduTranslate", "appkey")
        # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
        Config.from_lang = Config.config.get("BaiduTranslate", "from_lang")
        Config.to_lang = Config.config.get("BaiduTranslate", "to_lang")
        Config.trans_url = "https://api.fanyi.baidu.com/api/trans/vip/translate"
        ####################参数####################

    @staticmethod
    def save_config():
        Config.config.set("Other", "font", Config.FONT)
        Config.config.set("Other", "font_color", Config.FONTCOLOR)
        Config.config.set("Other", "is_localOCR", Config.is_local)
        Config.config.set("Other", "is_show_bg", Config.is_show_bg)
        Config.config.set("Other", "show_text_dely", Config.show_text_dely)
        Config.config.set("Other", "select_area_key", Config.select_area_key)
        Config.config.set("Other", "translate_key", Config.translate_key)

        ##百度智能云 文字识别##
        Config.config.set("BaiduOCR", "appid", Config.APP_ID)
        Config.config.set("BaiduOCR", "appkey", Config.API_KEY)
        Config.config.set("BaiduOCR", "secretkey", Config.SECRET_KEY)

        ##百度翻译开放平台##
        Config.config.set("BaiduTranslate", "appid", Config.appid)
        Config.config.set("BaiduTranslate", "appkey", Config.appkey)
        with open(Config.MATH_PATH + r"\config.ini", "w", encoding="utf-8-sig") as f:
            Config.config.write(f)

    @staticmethod
    def set_show_bg(is_show):
        Config.is_show_bg = str(is_show)

    @staticmethod
    def set_text_dely(time):
        Config.show_text_dely = str(time)

    @staticmethod
    def set_key_fy(key):
        Config.translate_key = str(key)

    @staticmethod
    def set_key_grab(key):
        Config.select_area_key = str(key)

    @staticmethod
    def set_font_color(color):
        Config.FONTCOLOR = str(color)

    @staticmethod
    def set_font_size(size):
        fontsetting = Config.FONT.split(" ")
        fontsetting[1] = str(size)
        Config.FONT = " ".join(fontsetting)

    @staticmethod
    def set_local_ocr(is_local):
        Config.is_local = str(is_local)

    @staticmethod
    def set_baidu_ocr(APP_ID, API_KEY, SECRET_KEY):
        Config.APP_ID = APP_ID
        Config.API_KEY = API_KEY
        Config.SECRET_KEY = SECRET_KEY
        Config.client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    @staticmethod
    def set_baidu_translate(appid, appkey):
        Config.appid = appid
        Config.appkey = appkey


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
        # from lib.paddleocr.paddleocr import PaddleOCR

        from paddleocr import PaddleOCR

        self.que = que
        self.result = result
        self.box_area = box_area
        self.accurate = True
        self._temp_path = r"\inference_model\_temp.png"

        self._paddle = PaddleOCR(  # paddleocr --help
            use_angle_cls=False,
            lang="japan",
            det_model_dir=f"{Config.MATH_PATH}/inference_model/ch_ppocr_server_v2.0_det_infer/",
            rec_model_dir=f"{Config.MATH_PATH}/inference_model/japan_mobile_v2.0_rec_infer",
            rec_char_dict_path=f"{Config.MATH_PATH}/inference_model/japan_dict.txt",
            use_gpu=False,
            use_tensorrt=True,
            use_space_char=True,
            det_db_unclip_ratio=2.5,
            det_db_thresh=0.9,
            max_text_length=256,
            show_log=True,
        )

    def baidu_api_ocr(self, img_bytes):
        # ocr
        options = {}
        options["language_type"] = "JAP"

        if self.accurate:
            res = Config.client.basicAccurate(img_bytes, options)
            if "error_code" in res and res["error_code"] == 18:
                return "ocr error_code 18 超出每秒翻译限制"
            elif "error_code" in res and res["error_code"] == 17:
                self.accurate = False
                return ""
            else:
                res = res["words_result"]
                debug_print("OCR:高精度")
        else:
            res = Config.client.basicGeneral(img_bytes, options)
            if "error_code" in res and res["error_code"] == 18:
                return "ocr error_code 18 超出每秒翻译限制"
            elif "error_code" in res and res["error_code"] == 17:
                self.result = "※今日OCR额度已用完"
                return ""
            else:
                res = res["words_result"]
                debug_print("OCR:标准精度")

        words = []
        # print("error_code" in res)
        # print(res["error_code"])
        # print(res["error_code"] == 17)
        for wrd in res:
            words.append(wrd["words"])
        query = "".join(words)
        return str(query)

    def paddle_ocr(self):
        boxes = self._paddle.ocr(Config.MATH_PATH + self._temp_path, cls=False)
        result = []
        for box in boxes:
            result.append(box[1][0])
        debug_print("OCR:Paddle")
        return "".join(result)

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
        if "error_code" in res.keys():
            debug_print(res)
            self.result = f"百度翻译错误：{res}"
        else:
            self.result = res["trans_result"][0]["dst"]
            debug_print(f"translate result: {self.result}")

    def baidu_api_run(self, img_bytes):
        is_text_exist = True
        if Config.is_local == "1":
            query = self.paddle_ocr()
        else:
            query = self.baidu_api_ocr(img_bytes)
        debug_print(f"ocr result: {query}")

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
            if Config.is_local == "1":
                to_png(img.rgb, img.size, output=Config.MATH_PATH + self._temp_path)
                # img.save(Config.MATH_PATH + self._temp_path, format="PNG")
            if img is not None:
                # img_bytes = BytesIO()
                # img.save(img_bytes, format="PNG")
                img_bytes = to_png(img.rgb, img.size)
                is_text_exist = self.baidu_api_run(img_bytes)
                if not is_text_exist:
                    sleep(0.5)
                    time += 1
                    if time > 10:
                        print("Timeout: cannnot find text")
                        break
        self.que.put(self.result)  # 发送翻译结果

    def captureImage(self):
        with mss() as sct:
            sct.compression_level = 0
            bbox = [int(x) for x in self.box_area]
            img = sct.grab(tuple(bbox))
        return img


class HotKey(Process):  # 键盘热键监听
    def __init__(self, que, que_setting, array):
        super().__init__()
        self.que = que
        self.que_setting = que_setting
        self.array = array
        self.keylist = []
        self.ss = None
        self.translate_key = Config.translate_key
        self.select_area_key = Config.select_area_key

    def grab(self):
        self.ss = ScreenShoot()
        if self.ss.box_area != None:
            self.que.put(f"box_area${self.ss.box_area}$new")  # 发送box_area

    def reset_key(self, key1, key2):
        self.translate_key = key1
        self.select_area_key = key2

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
        if not self.que_setting.empty():
            setting = self.que_setting.get().split("$")
            self.reset_key(setting[0], setting[1])

        if event.Key == self.select_area_key:
            self.grab()
        elif event.Key == self.translate_key:
            self.translate()
        elif event.Key == "Return":
            sleep(float(Config.show_text_dely))
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

    def OnMouseMove(self, event):
        self.array[0] = int(event.Position[0])
        self.array[1] = int(event.Position[1])
        return True

    def run(self):
        from PyHook3 import HookManager
        from pythoncom import PumpMessages

        hm = HookManager()
        hm.KeyDown = self.OnKeyboardEvent
        hm.MouseMove = self.OnMouseMove
        hm.HookKeyboard()
        hm.HookMouse()
        PumpMessages()


class MainCanvas(Canvas):  # 大小随窗口缩放的Canvas
    def __init__(self, parent, que=None, que_setting=None, array=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.root = parent
        self.que = que
        self.que_setting = que_setting
        self.array = array
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
        self._on_setting = False
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
        else:
            self.rect_bg = self.create_rectangle(
                0, 0, 0, 0, fill=self._bgcolor, tags="rect_bg"
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

        self.rect_menu_id = self.create_rectangle(
            0,
            0,
            0,
            0,
            activeoutline="red",
            activefill="blue",
            fill=self._bgcolor,
            tags="rect_menu",
        )  # 用于触发鼠标事件的矩形

        if not self._is_area:
            self.popup_menu = Menu(self, tearoff=0)
            self.popup_menu.add_command(label="清空", command=self.menu_clear)
            self.popup_menu.add_command(label="设置", command=self.menu_setting)
            self.popup_menu.add_command(label="更新", command=self.open_github)
            self.popup_menu.add_command(label="退出", command=self.menu_close)
            self.tag_bind("rect_menu", "<Button-1>", self.on_mouse_down_menu)
            self.check_mouse = True
            Thread(target=self.check_mouse_position).start()
        else:
            self.tag_bind("rect_menu", "<Button-1>", self.menu_close)

        self.tag_bind("rect_size", "<Button-1>", self.on_mouse_down_size)
        self.tag_bind("rect_move", "<Button-1>", self.on_mouse_down_move)
        self.tag_bind("rect_size", "<Motion>", self.on_mouse_motion_size)
        self.tag_bind("rect_move", "<Motion>", self.on_mouse_motion_move)
        self.bind("<ButtonRelease-1>", self.on_mouse_release)

    def open_github(self):
        tags = get(
            "https://api.github.com/repos/paraii/gal_translate/tags"
        )  # https://api.github.com/repos/paraii/gal_translate
        tags = json.loads(tags.text)
        v = tags[0]["name"]
        if v != __version__:
            webopen(f"https://github.com/paraii/gal_translate/releases/tag/{v}")
        else:
            self.que.put("已是最新版本")

    def check_mouse_position(self):
        x, y = 0, 0
        while self.check_mouse:
            if Config.is_show_bg == "1" and self.itemcget(self.text_id, "text") != "":
                rect = self.get_root_rect()
                x = self.array[0]
                y = self.array[1]
                if (
                    x > rect[0] and x < rect[2] and y > rect[1] and y < rect[3]
                ) and not (
                    x > rect[2] - 3 * self._rect_width - 2 * self._rect_gap
                    and x < rect[2]
                    and y > rect[3] - self._rect_width
                    and y < rect[3]
                ):
                    self.itemconfig(self.rect_bg, fill=self._bgcolor)
                else:
                    self.itemconfig(self.rect_bg, fill="#505050")
            elif self.itemcget(self.rect_bg, "fill") == "#505050":
                self.itemconfig(self.rect_bg, fill=self._bgcolor)
            sleep(0.1)

    def menu_clear(self):
        self.que.put("")

    def menu_setting(self):
        if self._on_setting:
            return
        self._on_setting = True
        top = Toplevel(self.root)
        top.overrideredirect(True)
        top.attributes("-topmost", 1)

        def set_pos():
            sleep(0.1)
            size = top.geometry(None).split("+")[0]
            if size != "1x1":
                sizeint = size.split("x")
                top.geometry(
                    f"{size}+{(self.root.winfo_screenwidth()- int(sizeint[0]))//2}+{(self.root.winfo_screenheight()- int(sizeint[1]))//2}"
                )

        def choose_color():
            choose = colorchooser.askcolor()
            Config.set_font_color(choose[1])
            b1.config(bg=choose[1])
            bgcolor = cal_bgcolor()
            self._bgcolor = bgcolor
            self.root.attributes("-transparentcolor", bgcolor)
            self.config(bg=bgcolor)
            self.itemconfig(self.rect_menu_id, fill=bgcolor)
            self.itemconfig(self.rect_move_id, fill=bgcolor)
            self.itemconfig(self.rect_id, fill=bgcolor)

        def choose_font(value):
            Config.set_font_size(t1.get())
            self.itemconfig(self.text_id, font=Config.FONT)

        def choose_local_ocr():
            if Config.is_local == "1":
                Config.set_local_ocr("0")
            else:
                Config.set_local_ocr("1")

        def choose_show_bg():
            if Config.is_show_bg == "1":
                Config.set_show_bg("0")
            else:
                Config.set_show_bg("1")

        def confirm_setting():
            Config.set_baidu_ocr(t_ocr1.get(), t_ocr2.get(), t_ocr3.get())
            Config.set_baidu_translate(t_fy1.get(), t_fy2.get())
            Config.set_text_dely(t_dely.get())
            Config.set_key_fy(t_key1.get())
            Config.set_key_grab(t_key2.get())
            Config.save_config()
            while not self.que_setting.empty():
                self.que_setting.get()
            self.que_setting.put(f"{Config.translate_key}${Config.select_area_key}")
            self._on_setting = False
            top.destroy()

        def get_key_values():
            keys = []
            for i in range(ord("A"), ord("Z") + 1):
                keys.append(chr(i))
            for i in range(1, 13):
                keys.append(f"F{i}")
            return tuple(keys)

        b1 = Button(top, text="字体颜色", bg=Config.FONTCOLOR, command=choose_color)
        b1.grid(row=0, column=0)
        l1 = Label(top, text="字体大小")
        l1.grid(row=0, column=1, sticky="e")
        t1 = ttk.Combobox(top, width=5)
        t1.insert(0, Config.FONT.split(" ")[1])
        t1["values"] = (10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40)
        t1["state"] = "readonly"
        t1.grid(row=0, column=2, sticky="w")
        t1.bind("<<ComboboxSelected>>", choose_font)
        b_bg = Checkbutton(top, text="开启衬色", command=choose_show_bg)
        if Config.is_show_bg == "1":
            b_bg.select()
        b_bg.grid(row=2, column=3)

        l_key1 = Label(top, text="翻译键")
        l_key1.grid(row=1, column=0, sticky="e")
        t_key1 = ttk.Combobox(top, width=5)
        t_key1.insert(0, Config.translate_key)
        t_key1["values"] = get_key_values()
        t_key1["state"] = "readonly"
        t_key1.grid(row=1, column=1, sticky="w")

        l_key2 = Label(top, text="选择键")
        l_key2.grid(row=1, column=2, sticky="e")
        t_key2 = ttk.Combobox(top, width=5)
        t_key2.insert(0, Config.select_area_key)
        t_key2["values"] = get_key_values()
        t_key2["state"] = "readonly"
        t_key2.grid(row=1, column=3, sticky="w")

        b2 = Checkbutton(top, text="开启本地OCR", command=choose_local_ocr)
        if Config.is_local == "1":
            b2.select()
        b2.grid(row=2, column=0)
        l_dely = Label(top, text="文字显示延迟(秒)")
        l_dely.grid(row=2, column=1, sticky="e")
        t_dely = Entry(top, width=5)
        t_dely.insert(0, Config.show_text_dely)
        t_dely.grid(row=2, column=2, sticky="w")

        l_ocr0 = LinkLabel(
            top, link="https://cloud.baidu.com/product/ocr_general", text="百度OCR"
        )
        l_ocr0.grid(row=3, column=0)
        l_ocr1 = Label(top, text="APP_ID")
        l_ocr1.grid(row=4, column=0)
        l_ocr2 = Label(top, text="API_KEY")
        l_ocr2.grid(row=5, column=0)
        l_ocr3 = Label(top, text="SECRET_KEY")
        l_ocr3.grid(row=6, column=0)

        t_ocr1 = Entry(top, width=30)
        t_ocr1.grid(row=4, column=1, columnspan=3, sticky="w")
        t_ocr2 = Entry(top, width=30)
        t_ocr2.grid(row=5, column=1, columnspan=3, sticky="w")
        t_ocr3 = Entry(top, width=30)
        t_ocr3.grid(row=6, column=1, columnspan=3, sticky="w")

        t_ocr1.insert(0, Config.APP_ID)
        t_ocr2.insert(0, Config.API_KEY)
        t_ocr3.insert(0, Config.SECRET_KEY)

        l_fy0 = LinkLabel(top, link="https://api.fanyi.baidu.com", text="百度翻译")
        l_fy0.grid(row=7, column=0)
        l_fy1 = Label(top, text="APP_ID")
        l_fy1.grid(row=8, column=0)
        l_fy1 = Label(top, text="API_KEY")
        l_fy1.grid(row=9, column=0)

        t_fy1 = Entry(top, width=30)
        t_fy1.grid(row=8, column=1, columnspan=3, sticky="w")
        t_fy2 = Entry(top, width=30)
        t_fy2.grid(row=9, column=1, columnspan=3, sticky="w")

        t_fy1.insert(0, Config.appid)
        t_fy2.insert(0, Config.appkey)

        b_end = Button(top, text="ok", command=confirm_setting)
        b_end.grid(row=10, column=1)
        Thread(target=set_pos).start()

    def menu_close(self, event=None):
        self.delete(self.rect_id)
        self.delete(self.rect_move_id)
        self.delete(self.rect_menu_id)
        if self._is_area:
            self.delete(self.rect_border_id)
        else:
            self.check_mouse = False
        self.root.quit()

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

    def on_mouse_down_menu(self, event):
        self.popup_menu.tk_popup(
            event.x_root + self._rect_width, event.y_root + self._rect_height, 0
        )

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
        else:
            self.coords(
                self.rect_bg,
                0,
                0,
                self.width,
                self.height,
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
            self.rect_menu_id,
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
        box_canvas = MainCanvas(
            self.area_root,
            que=self.que,
            width=x2 - x1,
            height=y2 - y1,
            bg=bgcolor,
        )
        box_canvas.pack()
        self.area_root.mainloop()


class Tkwin(Thread):
    def __init__(self, que, que_setting, array):
        super().__init__()
        self.que = que
        self.que_setting = que_setting
        self.array = array
        self.transimg = TranslateImage(self.que)
        self.rect_id = -1

    def change_rect_color(self):
        self.canvas.itemconfig(self.canvas.rect_id, activefill="green")
        sleep(0.1)
        self.canvas.itemconfig(self.canvas.rect_id, activefill="gray")

    def on_mouse_wheel(self, event):  # 鼠标滚轮事件
        Thread(target=self.change_rect_color).start()
        debug_print("on_mouse_wheel")
        sleep(float(Config.show_text_dely))
        self.que.put("translate")

    def run(self):
        bgcolor = cal_bgcolor()

        self.root = Tk()
        self.root.geometry(
            f"700x60+{(self.root.winfo_screenwidth()- 700)//2}+{(self.root.winfo_screenheight() - 60)//2}"
        )
        self.root.attributes("-transparentcolor", bgcolor)
        self.root.attributes("-alpha", 0.8)
        self.root.attributes("-topmost", 1)
        # self.root.attributes("-toolwindow", 1)
        self.root.overrideredirect(True)
        self.canvas = MainCanvas(
            self.root,
            que=self.que,
            que_setting=self.que_setting,
            array=self.array,
            bg=bgcolor,
        )
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
    from multiprocessing import Queue, Array, freeze_support, set_start_method

    freeze_support()  # Windows使用Pyinstaller对多进程打包必须 https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing
    set_start_method("spawn")
    debug_print("debug:", Config.debug)

    que = Queue()  # 通信队列
    que_setting = Queue()
    array = Array("i", [0, 0])
    p1 = Tkwin(que, que_setting, array)  # GUI
    p1.start()
    p2_hotkey = HotKey(que, que_setting, array)  # 键盘热键监听（功能入口）
    p2_hotkey.start()

    tags = get(
        "https://api.github.com/repos/paraii/gal_translate/tags"
    )  # https://api.github.com/repos/paraii/gal_translate
    tags = json.loads(tags.text)
    if tags[0]["name"] != __version__:
        que.put("有新版本，可打开菜单更新")

    p1.join()
    p2_hotkey.terminate()
