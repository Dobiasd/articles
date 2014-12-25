#!/usr/bin/env python
# -*- coding: ascii -*-
"""programming language learning curves
"""
__author__ = 'Tobias Hermann'
__version__ = '1.0.0'

from matplotlib import pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
import matplotlib

prop = fm.FontProperties(fname='Humor-Sans.ttf', size=18)

def annotate(text, pos, to):
  plt.annotate(text, xy=to, arrowprops=dict(arrowstyle='->'), xytext=pos,
    fontproperties=prop)

def defaults1():
  plt.xkcd()

  fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  ax.spines['right'].set_color('none')
  ax.spines['top'].set_color('none')
  plt.xticks([])
  plt.yticks([])

  ax.set_ylim([0,100])
  ax.set_xlim([0,100])

def defaults2(title, loc='upper right', filename=None):
  plt.legend(prop=prop, loc=loc)
  plt.title(title, fontproperties=prop)
  plt.xlabel('time', fontproperties=prop)
  if not filename:
    filename = title.lower()
  plt.savefig(filename.lower() + '.png', dpi=75)
  plt.clf()

def javascript():
  defaults1()

  annotate('callbacks', (5, 38), (30, 60))
  annotate('callbacks', (5, 38), (30, 20))

  x = [0, 30, 40, 100]
  y = [ [60, 60, 20, 20], [20, 20, 60, 60] ]
  labels = ['productivity', 'self-assessment']

  for y_arr, label in zip(y, labels):
    plt.plot(x, y_arr, label=label)

  defaults2('Javascript')

def python():
  defaults1()

  annotate('unit tests', (40, 20), (30, 42))
  annotate('decorators', (40, 70), (60, 55))

  x1 = [ 0, 30, 35, 100]
  y1 = [40, 42, 50,  55]
  x2 = [ 0, 60, 65, 100]
  y2 = [50, 55, 60,  62]

  plt.plot(x1, y1, label='productivity')
  plt.plot(x2, y2, label='self-assessment')

  defaults2('Python')

def lisp():
  defaults1()

  annotate('macros', (30, 50), (50, 35))
  annotate('macros', (30, 50), (50, 25))

  x1 = [ 0, 50, 100]
  y1 = [10, 35,  80]
  x2 = [ 0, 50, 100]
  y2 = [ 5, 25, 70]

  plt.plot(x1, y1, label='productivity')
  plt.plot(x2, y2, label='self-assessment')

  defaults2('Lisp', 'upper left')

def php():
  defaults1()

  x1 = [ 0, 100]
  y1 = [10, 10]
  x2 = [ 0, 100]
  y2 = [90, 90]

  plt.plot(x1, y1, label='productivity')
  plt.plot(x2, y2, label='self-assessment')

  defaults2('php', 'center')

def java():
  defaults1()

  annotate('design patterns', (25, 20), (30, 30))
  annotate('design patterns', (25, 20), (30, 35))

  x1 = [ 0, 30, 100]
  y1 = [20, 30,  30]
  x2 = [ 0, 30, 100]
  y2 = [30, 35,  65]

  plt.plot(x1, y1, label='productivity')
  plt.plot(x2, y2, label='self-assessment')

  defaults2('Java')

def cpp():
  defaults1()

  annotate('templates', (25, 35), (50, 60))

  x1 = [ 0, 100]
  y1 = [20, 30]
  x2 = [ 0, 50, 52, 100]
  y2 = [30, 60, 30, 90]

  plt.plot(x1, y1, label='productivity')
  plt.plot(x2, y2, label='self-assessment')

  defaults2('C++', 'upper left', 'cpp')

def haskell():
  defaults1()

  annotate('My brain hurts!', (1, 20), (2, 8))
  annotate('My brain hurts!', (1, 20), (6, 8))
  annotate('My brain hurts!', (1, 20), (10, 8))
  annotate('My brain hurts!', (1, 20), (14, 8))
  annotate('My brain hurts!', (1, 20), (18, 8))
  annotate('My brain hurts!', (1, 20), (22, 8))
  annotate('My brain hurts!', (1, 20), (26, 8))

  annotate('Monads', (25, 40), (40, 20))
  annotate('Monads', (25, 40), (40, 30))

  x1 = [ 0,  5, 28, 40, 50, 100]
  y1 = [ 1, 1, 1, 30, 25, 100]
  x2 = [0, 2, 4, 6, 8,10,12,14,16,18,20,22,24,26,28, 40,42,44,46,48,50, 100]
  y2 = [3, 8, 3, 8, 3, 8, 3, 8, 3, 8, 3, 8, 3, 8, 3, 20, 3, 8, 3, 8, 3, 40]

  plt.plot(x1, y1, label='productivity')
  plt.plot(x2, y2, label='self-assessment')

  defaults2('Haskell', 'upper left')

def main():
  python()
  javascript()
  lisp()
  php()
  java()
  cpp()
  haskell()

if __name__ == "__main__":
  main()