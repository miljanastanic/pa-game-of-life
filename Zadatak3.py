from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from IPython.display import HTML
import numpy as np
import multiprocessing
from multiprocessing import Queue, Value, Manager, Array, Condition
import copy

n = 10
manager = Manager()
steps = manager.list()
steps.append((np.random.rand(n ** 2).reshape(n, n) > 0.5).astype(np.int8))

queue = [ Queue() for i in range(n * n) ]
doneThreads = Value('i', 0)
condition = multiprocessing.Condition()
addqueue = multiprocessing.Queue()

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

def igraj(x, y, i, value):

  neighbours = 0
  cordinates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

  for i,j in cordinates:
        row = getRow(x, i)
        column = getColumn(y, j)
        queue[n*row+column].put(value)
 
  for i in range(8):
        q = queue[n*x+y].get()
        neighbours += q

  value = isCellAlive(value, neighbours)
  addqueue.put((x, y, i, value))

  condition.acquire()
  doneThreads.value+=1

  if doneThreads.value == n ** 2:
    doneThreads.value = 0

    temp = steps[-1]
    temp [x][y] = value 
    steps[-1] = temp

    steps.append(temp)
    condition.notify_all()
    condition.release()
  else:
    temp = steps[-1]
    temp [x][y] = value 
    steps[-1] = temp
    
    condition.wait()
    condition.release()

processes = []
for k in range(10):
  for i in range(n):
      for j in range(n):
        p = multiprocessing.Process(target=igraj, kwargs={"x": i, "y": j,"i": k, "value": steps[k][i][j]})
        p.start()
        processes.append(p)

  for p in processes:
      p.join()

anim = animate(steps);
HTML(anim.to_html5_video())
