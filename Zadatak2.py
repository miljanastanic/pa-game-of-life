from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from IPython.display import HTML
import numpy as np
from queue import Queue, Empty
import threading

def copyState(s):
  states = []
  states = s.copy()
  return states

n = 10
steps = [(np.random.rand(n ** 2).reshape(n, n) > 0.5).astype(np.int8)]
currentState = copyState(steps[0])

doneThreads = 0
condition = threading.Condition()
queue = [ Queue() for i in range(n * n) ]

def animate(steps):
  def init():
    im.set_data(steps[0])
    return [im]
  
  
  def animate(i):
    im.set_data(steps[i])
    return [im]

  im = plt.matshow(steps[0], interpolation='None', animated=True);
  
  anim = FuncAnimation(im.get_figure(), animate, init_func=init,
                  frames=len(steps), interval=500, blit=True, repeat=False);
  return anim

def isCellAlive(value, aliveNeighbours):
    if (aliveNeighbours < 2) or (aliveNeighbours > 3): 
      return 0 
    elif value  == 1 and (aliveNeighbours == 2 or aliveNeighbours == 3):
      return 1 
    elif value == 0 and aliveNeighbours == 3: 
      return 1
    return value

def getRow(x, i):
   row = (x + i) % n
   return row

def getColumn(y, j):
   column = (y + j) % n
   return column

cordinates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
def neighbours(n):
  for x in range(n):
    for y in range(n):
      for i,j in cordinates:
        row = getRow(x, i)
        column = getColumn(y, j)
        queue[n*row+column].put(currentState[x][y])  

def igraj(x, y):
  global currentState
  global doneThreads

  neighbours = 0
  for i in range(8):
    q = queue[n*x+y].get()
    neighbours+=q
  currentState[x][y] = isCellAlive(currentState[x][y], neighbours)
  doneThreads+=1

  condition.acquire()
  if doneThreads == n ** 2:
    steps.append(copyState(currentState))
    doneThreads = 0
    condition.notifyAll()
    condition.release()
  else:
    condition.wait()
    condition.release()

threads=[]
neighbours(n)
for k in range(50):
  for i in range(n):
    for j in range(n):
        t = threading.Thread(target=igraj, args=(i,j))
        t.start()
        threads.append(t)
  neighbours(n)

  for t in threads:
    t.join()

anim = animate(steps)
HTML(anim.to_html5_video())   



