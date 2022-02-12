from webbrowser import open as webopen
from tkinter import Label


class LinkLabel(Label):
    # LinkLabel可以显示超链接
    def __init__(self, master, link, text, font=("宋体", 13, "underline"), bg="#f0f0f0"):
        super().__init__(master, text=text, font=font, fg="blue", bg=bg)
        self.link = link
        self.bind("<Enter>", self._changecolor)
        self.bind("<Leave>", self._changecurcor)
        self.bind("<Button-1>", self._golink)
        self.isclick = False

    def _changecolor(self, event):
        self["fg"] = "#D52BC4"
        self["cursor"] = "hand2"

    def _changecurcor(self, event):
        if self.isclick == False:
            self["fg"] = "blue"
        self["cursor"] = "xterm"

    def _golink(self, event):
        self.isclick = True
        webopen(self.link)
