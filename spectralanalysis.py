#!/usr/bin/env python

"""
pitchlabeltrack.py
--
Christopher Kuech
cjkuech@gmail.com
--
Requires:
    Python 2.7
Instructions:
    python pitchlabelspectrogram.py [wav-file-name]
"""

from math import log
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.colors import Normalize, LogNorm
import matplotlib.mlab as mlab
import numpy as np
import sys
import Tkinter as tk
import wavelab




(WIDTH, HEIGHT) = (800, 500)
FNAME = './Bach.wav' if len(sys.argv) != 2 else sys.argv[1]
font = ('Helvetica', 14, 'bold')
HOURGLASSEMOJI = u"\u231b"





class SquareNorm(Normalize):
	def __call__(self, *args):
		v = Normalize.__call__(self, *args)
		return v*v

class NegLogNorm(LogNorm):
	def __call__(self, *args):
		v = LogNorm.__call__(self, *args)
		return 1.0 - v






@wavelab.callback
def update():
	"""the function run on the graphics thread"""

	waiting.set(HOURGLASSEMOJI)

	p = ptype.get()
	w = wsize.get()
	wty = wtype.get()

	pnorm = {
		"square": SquareNorm(),
		"linear": Normalize(),
		"dB": LogNorm(),
		"-dB": NegLogNorm(),
	}
	windowing = {
		"rectangle": mlab.window_none,
		"hamming": np.hamming,
		"hanning": mlab.window_hanning
	}

	axes.cla()
	axes.specgram(wav, Fs=44100, NFFT=w, norm=pnorm[p], window=windowing[wty])
	axes.set_xlabel("Time (sec)")
	axes.set_ylabel("Frequency (Hz)")

	canvas.show()
	waiting.set("")

	




# read wave file
(framerate, wav) = wavelab.readwav(FNAME)
frame = 0

# create a GUI instance (do before any use of Tkinter)
root = tk.Tk()
root.wm_title("Frequency Spectrogram")

# these objects hold the variables from the widgets
wsize = tk.IntVar() # window size (in frames)
wsize.set(2205)
wtype = tk.StringVar() # type of windowing to use
wtype.set("rectangle")
ptype = tk.StringVar() # type of power to use
ptype.set("square")
waiting = tk.StringVar() # the current pitch
waiting.set("")



# create the wrappers for embedding matplots in Tkinter
canvasframe = tk.Frame(root, width=WIDTH, height=HEIGHT)
canvasframe.grid(row=0, column=0, columnspan=4)
figure = Figure()
axes = figure.add_axes( (0.15, 0.15, 0.7, 0.7), frameon=True,
						xlabel="Time (sec)", ylabel="Frequency (Hz)")
canvas = FigureCanvasTkAgg(figure, canvasframe)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
canvas.show()

widgetps = lambda n, v: {'variable': v, 'text': n, 'value': n, 'command': update}
	# returns the dict of kwargs that initialize a widget

# create the wtype controller and add it to the GUI
tk.Label(root, font=font, text="Windowing").grid(row=1, column=0, pady=10)
wframe = tk.Frame(root)
wframe.grid(row=2, column=0, pady=10, sticky="n")
tk.Radiobutton(wframe, **widgetps("rectangle", wtype)).grid(sticky="w", row=0)
tk.Radiobutton(wframe, **widgetps("hamming"  , wtype)).grid(sticky="w", row=1)
tk.Radiobutton(wframe, **widgetps("hanning"  , wtype)).grid(sticky="w", row=2)

# create the wsize controller and add it to the GUI
tk.Label(root, font=font, text="Window Size").grid(row=1, column=1, pady=10)
tk.Scale(root, variable=wsize, orient=tk.HORIZONTAL, from_=10, to=4410, command=update).grid(row=2, column=1, sticky="wen")

# create the ptype controller and add it to the GUI
tk.Label(root, font=font, text="Power").grid(row=1, column=2, pady=10)
pframe = tk.Frame(root)
pframe.grid(row=2, column=2, pady=10, sticky="n")
tk.Radiobutton(pframe, **widgetps("square", ptype)).grid(sticky="w", row=0)
tk.Radiobutton(pframe, **widgetps("dB",     ptype)).grid(sticky="w", row=1)
tk.Radiobutton(pframe, **widgetps("-dB",    ptype)).grid(sticky="w", row=2)
tk.Radiobutton(pframe, **widgetps("linear", ptype)).grid(sticky="w", row=3)

# shows if the script is calculating or not
tk.Label(root, font=font, text="Activity").grid(row=1, column=3, pady=10)
(fontfamily, fontsize, fontweight) = font
waitingfont = (fontfamily, 34, fontweight)
tk.Label(root, font=waitingfont, textvariable=waiting, width=5).grid(row=2, column=3)





# draw the canvas
update()

# start the main update loop for the GUI (and block)
tk.mainloop()






