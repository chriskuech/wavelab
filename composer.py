#!/usr/bin/env python

"""
composer.py
--
Christopher Kuech
cjkuech@gmail.com
--
Requires:
    Python 2.7, PyAudio
Instructions:
    python composer.py [number-of-controllers]
"""



from array import array
from math import sin, pi
from pyaudio import PyAudio
import sys
from threading import Thread, Lock
import Tkinter as tk







class App(tk.Frame):

    def __init__(self, root, n):
        # init view with scrollbar
        tk.Frame.__init__(self, root)
        self.canvas = tk.Canvas(root, borderwidth=0, background="#ffffff")
        self.frame = tk.Frame(self.canvas, background="#ffffff")
        self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw", tags="self.frame")
        self.frame.bind("<Configure>", self.onconfigure)
        self.canvas["width"] = 810
        self.canvas["height"] = 130 * (n + 1)

        # init controllers
        self.controllers = [Controller(self, self.frame, i) for i in xrange(n)]

        # make combined wave view
        self.disp = DisplayView(self.frame)
        self.disp.grid(row=n, column=0)
        self.disp["bg"] = "#555"

        self.sound = Sound()
        self.update()
        self.sound.play()
           

    def update(self):
        # create composite drawing
        imgdata = []
        for x in xrange(DisplayView.WIDTH):
            y = sum(c.disp.imgdata[x] for c in self.controllers) / len(self.controllers)
            imgdata.append(y)
        self.disp.setimgdata(imgdata)

        # create composite sound
        wavdata = []
        for t in xrange(int(Sound.FPS / Sound.F0)):
            samp = sum(c.sound.wavdata[t] for c in self.controllers) / len(self.controllers)
            wavdata.append(samp)
        self.sound.setwavdata(wavdata)


    def onconfigure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))







class Controller:

    def __init__(self, parent, wrapper, i):
        self.parent = parent

        self.disp = DisplayView(wrapper)
        self.disp.grid(row=i, column=0)

        self.ctrl = ControlView(wrapper)
        self.ctrl.grid(row=i, column=1)

        self.sound = Sound()

        self.f = tk.IntVar()
        self.a = tk.DoubleVar()
        self.p = tk.DoubleVar()

        self.f.set(0)
        self.a.set(1)
        self.p.set(0)

        self.ctrl.bind(self)

        self.disp.plot(self.f.get() + 1, self.a.get(), self.p.get())
        self.sound.update(self.f.get() + 1, self.a.get(), self.p.get())


    def onupdate(self):
        self.disp.plot(self.f.get() + 1, self.a.get(), self.p.get())
        self.sound.update(self.f.get() + 1, self.a.get(), self.p.get())
        self.parent.update()












class ControlView(tk.Frame):
    
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        kwargs0 = {
            "activebackground": "#f99",
            "fg": "#333",
            "font": ("Helvetica-Neue Helvetica sans-serif", "18"),
            "bd": 1, # 3D border width
            "highlightthickness": 1, # focus thickness
            "length": 100, # currently default already
            "orient": tk.VERTICAL,
            "sliderrelief": tk.FLAT,
            "troughcolor": "#ddd",
        }

        self.fslide = tk.Scale(self, label="f", from_=0,   to=8,    resolution=1,       **kwargs0)
        self.aslide = tk.Scale(self, label="a", from_=0.0, to=1,    resolution=0.1,     **kwargs0)
        self.pslide = tk.Scale(self, label="p", from_=0.0, to=2*pi, resolution=2*pi/24, **kwargs0)

        self.fslide.grid(row=0, column=0)
        self.aslide.grid(row=0, column=1)
        self.pslide.grid(row=0, column=2)


    def bind(self, ctrl):
        for (w, v) in ((self.fslide, ctrl.f), (self.aslide, ctrl.a), (self.pslide, ctrl.p)):
            w["variable"] = v
            w["command"] = lambda _: ctrl.onupdate()












class DisplayView(tk.Canvas):

    WIDTH = 600
    HEIGHT = 120

    def __init__(self, parent):
        tk.Canvas.__init__(self, parent, width=DisplayView.WIDTH, height=DisplayView.HEIGHT, bg="#333")
        self.imgdata = [0 for x in xrange(DisplayView.WIDTH)]


    def clear(self):
        self.img = tk.PhotoImage(width=DisplayView.WIDTH, height=DisplayView.HEIGHT)


    def drawaxis(self):
        for x in xrange(DisplayView.WIDTH):
            self.img.put("#999", (x, DisplayView.HEIGHT // 2))


    def show(self):
        self.create_image((round(DisplayView.WIDTH / 2), round(DisplayView.HEIGHT / 2)), image=self.img)


    def plot(self, f, a, p):
        self.clear()
        self.drawaxis()
        (f, a, p) = (float(f) / DisplayView.WIDTH, a * DisplayView.HEIGHT / 2 * 0.95, p)
        for x in xrange(DisplayView.WIDTH):
            y = a * sin(2 * pi * x * f - p)
            self.setpx(x, y)
        self.show()


    def setimgdata(self, data):
        self.clear()
        self.drawaxis()
        for (x, y) in enumerate(data):
            self.setpx(x, y)
        self.show()


    def setpx(self, x, y):
        mid = round(DisplayView.HEIGHT / 2)
        (i, j) = (min(max(mid - y + 2, 0), DisplayView.HEIGHT), min(max(x + 5, 0), DisplayView.WIDTH))
        self.imgdata[x] = y
        self.img.put("#F00", (int(j), int(i)))










class Sound:

    # F0 = 16.35   # C0
    F0 = 110.0   # A2
    FPS = 44100


    def __init__(self):
        self.wavdata = array('h', [0 for i in xrange(int(Sound.FPS / Sound.F0))])
        self.lock = Lock()


    def play(self):
        def worker():
            p = PyAudio()
            stream = p.open(format=p.get_format_from_width(2),
                            channels=1, rate=44100, output=True)
            while True:
                self.lock.acquire()
                stream.write(self.wavdata.tostring())
                self.lock.release()
        t = Thread(target=worker)
        t.setDaemon(True)
        t.start()


    def update(self, f, a, p):
        f = Sound.F0 * 2**f / Sound.FPS
        a = (2**15 - 1) * a
        for t in xrange(int(Sound.FPS / Sound.F0)):
            samp = a * sin(2 * pi * t * f - p)
            self.wavdata[t] = Sound.truncate(samp)


    def setwavdata(self, wavdata):
        self.lock.acquire()
        for (i, samp) in enumerate(wavdata):
            self.wavdata[i] = Sound.truncate(samp)
        self.lock.release()


    @staticmethod
    def truncate(samp):
        return int(max(min(samp, 2**15 - 1), -2**15))















if __name__ == "__main__":
    n = int(sys.argv[1] if len(sys.argv) == 2 else 3)
    root = tk.Tk()
    root.wm_title("Additive Synthesizer")
    App(root, n).pack(side="top", fill="both", expand=True)
    root.mainloop()



#eof
