#!/usr/bin/env python

"""
pitchanalysis.py
--
Christopher Kuech
cjkuech@gmail.com
--
Requires:
    Python 2.7
Instructions:
    python pitchanalysis.py [wav-file-name]
"""

import matplotlib
from math import log
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import pyaudio
import sys
from time import time, sleep
import Tkinter as tk
import wavelab




(WIDTH, HEIGHT) = (800, 500)
FNAME = './Bach.wav' if len(sys.argv) != 2 else sys.argv[1]
font = ('Helvetica', 14, 'bold')
CHUNK = 1024




def audioworker():
	"""the function run on the audio thread"""

	global frame
	p = pyaudio.PyAudio()
	stream = p.open(format=p.get_format_from_width(2),
					channels=1, rate=4*44100, output=True)
					# unknown why rate is off by 4x
	while True:
		stream.write(data[frame:frame+CHUNK].tostring())
		frame = (frame + CHUNK) % len(wav)
	stream.stop_stream()
	stream.close()
	p.terminate()




def graphicsworker():
	"""the function run on the graphics thread"""

	while True:
		start = time()

		p = ptype.get()
		w = wsize.get()
		wty = wtype.get()

		# compute frequencies from clip
		clip = data[frame:frame+w]
		if wty == "hanning":
			clip *= np.hanning(w)
		elif wty == "hamming":
			clip *= np.hamming(w)
		freqs = wavelab.frequencies(clip)

		# update plot
		xs = np.sort(freqs.keys())
		ys = np.array(map(freqs.get, xs))
		axes.cla()
		(xmax, ymin, ymax) = (10e4, 0.000001, 10e2)
		# (xlim, ylim) = (_, (ymin, ymax)) = ((0, 1e4), (1e-3, 1e7))
		axes.set_xscale("log")
		axes.set_yscale("linear")	             
		axes.set_xlim((1, xmax))
		if p == "square":
			# axes.set_yscale("linear")
			axes.set_ylim((ymin**2, ymax**2))
			ys = ys * ys
		elif p == "dB":
			# axes.set_yscale("log")
			axes.set_ylim((log(ymin), log(ymax)))
			ys = np.log(ys)
		elif p == "-dB":
			# axes.set_yscale("log")
			axes.set_ylim((-log(ymax), -log(ymin)))
			ys = -np.log(ys)
		elif p == "linear":
			# axes.set_yscale("linear")
			axes.set_ylim((ymin, ymax))
		axes.plot(xs, ys, 'r-')
		canvas.show()

		# pitch tracker
		freq = max(freqs, key=lambda f: freqs[f])
		pitch.set(wavelab.pitch(freq).replace('/','\n'))

		# attempt to achieve 30fps animation (at best)
		dt = time() - start
		sleep(max(0, 1.0/30.0 - dt))
	




# read wave file
(framerate, wav) = wavelab.readwav(FNAME)
data = np.concatenate((wav, wav)) # avoid out of bounds
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
pitch = tk.StringVar() # the current pitch
pitch.set("")

widgetps = lambda n, v: {'variable': v, 'text': n, 'value': n}
	# returns the dict of kwargs that initialize a widget

# create the canvas widget and add it to the GUI
# canvas = tk.Canvas(root, borderwidth=0, width=WIDTH, height=HEIGHT, bg='#000')
# canvas.grid(row=0, column=0, columnspan=4)
# canvas.show()



canvasframe = tk.Frame(root, width=WIDTH, height=HEIGHT)
canvasframe.grid(row=0, column=0, columnspan=4)
figure = Figure()
axes = figure.add_axes( (0.1, 0.1, 0.8, 0.8), frameon=True,
						xlabel="Frequency (Hz)", ylabel="Power")
canvas = FigureCanvasTkAgg(figure, canvasframe)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
canvas.show()








# create the wtype controller and add it to the GUI
tk.Label(root, font=font, text="Windowing").grid(row=1, column=0, pady=10)
wframe = tk.Frame(root)
wframe.grid(row=2, column=0, pady=10, sticky="n")
tk.Radiobutton(wframe, **widgetps("rectangle", wtype)).grid(sticky="w", row=0)
tk.Radiobutton(wframe, **widgetps("hamming"  , wtype)).grid(sticky="w", row=1)
tk.Radiobutton(wframe, **widgetps("hanning"  , wtype)).grid(sticky="w", row=2)

# create the wsize controller and add it to the GUI
tk.Label(root, font=font, text="Window Size").grid(row=1, column=1, pady=10)
tk.Scale(root, variable=wsize, orient=tk.HORIZONTAL, from_=10, to=4410).grid(row=2, column=1, sticky="wen")

# create the ptype controller and add it to the GUI
tk.Label(root, font=font, text="Power").grid(row=1, column=2, pady=10)
pframe = tk.Frame(root)
pframe.grid(row=2, column=2, pady=10, sticky="n")
tk.Radiobutton(pframe, **widgetps("square", ptype)).grid(sticky="w", row=0)
tk.Radiobutton(pframe, **widgetps("dB",     ptype)).grid(sticky="w", row=1)
tk.Radiobutton(pframe, **widgetps("-dB",    ptype)).grid(sticky="w", row=2)
tk.Radiobutton(pframe, **widgetps("linear", ptype)).grid(sticky="w", row=3)

# create the area where the pitchlabel is displayed
tk.Label(root, font=font, text="Pitch").grid(row=1, column=3, pady=10)
(fontfamily, fontsize, fontweight) = font
pitchfont = (fontfamily, 24, fontweight)
pitchlabel = tk.Label(root, font=pitchfont, textvariable=pitch, width=7).grid(row=2, column=3)





# start the other threads
wavelab.thread(audioworker)
wavelab.thread(graphicsworker)

# start the main update loop for the GUI (and block)
tk.mainloop()






