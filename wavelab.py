

import array
from colorsys import hsv_to_rgb as hsvtorgb
import contextlib
import json
import numpy as np
import threading
import wave






def frequencies(X, fps=44100):
	"""Detects the frequencies in a song clip
	   X: an iterable of samples
	   return: a dict mapping frequencies (Hz) to power"""

	fps = float(fps)
	w = len(X)
	wfs = (2.0 * abs(x) / w for x in np.fft.rfft(X))
	return {i*fps/w: power for (i, power) in enumerate(wfs)}







def readwav(fname):
	"""fname: the file name of the wave file
	   return: a tuple (framerate, numpy array of samples)"""

	with contextlib.closing(wave.open(fname, 'rb')) as wr:
		(_, _, framerate, nframes, _, _) = wr.getparams()
		frames = wr.readframes(nframes)
	return (framerate, np.array(list(array.array("h", frames))))








def thread(fn):
	"""spawns a thread that executes fn to remove need to
	   expose threading module outside wavelab"""

	t = threading.Thread(target=fn)
	t.setDaemon(True) # exit if main thread exits
	t.start()








_handlers = {} # avoid multiple threads for same callback

def callback(fn):
	"""wraps fn so it doesn't block the calling thread"""

	def worker():
		while True:
			event.wait()
			fn()

	def handle(*args):
		"""tkinter for some reason passes in a str(variable),
		   so we just ignore"""

		event.set()
		event.clear()

	if fn not in _handlers:
		event = threading.Event()
		_handlers[fn] = handle
		thread(worker)
	return _handlers[fn]








def closest(l, n):
	"""finds the closest number in sorted list l to n"""

	mid = int(len(l) / 2)
	if len(l) < 7:
		return min(l, key=lambda e: abs(n - e))
	elif n > l[mid]:
		return closest(l[mid:], n)
	else:
		return closest(l[:mid+1], n)






with open('pitches.json', 'r') as jsonfile:
	_ptof = json.load(jsonfile)
	_ftop = {_ptof[p]: p for p in _ptof}
	_fs   = sorted(_ftop.keys())


def pitch(freq):
	"""finds the closest pitch to the frequency freq"""

	return _ftop[closest(_fs, freq)]





















