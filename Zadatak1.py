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
semaphores = [[threading.Semaphore(0)] * n for i in range(n * n)]
listcounters = [[0] * n for _ in range(n)]
semaphore = threading.Semaphore(1)
key = threading.Lock()

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

def igraj(x, y):
  global n
  global steps
  global currentState
  global doneThreads
  global condition
  global semaphores
  global listcounters
  global semaphore
  global key

  neighbours = 0
  cordinates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

  for i,j in cordinates:
   
    row = getRow(x, i)
    column = getColumn(y, j)
    
    neighbours += currentState[row][column]
    semaphore.acquire() #sinh suseda koji menjaju vr brojaca
    listcounters[row][column]+=1

    if listcounters[row][column] == 8:

     listcounters[row][column]=0
     semaphores[row][column].release() #poslednji sused budi semaforom
   
    semaphore.release() 


  semaphores[x][y].acquire() #kad je semafor pustio moze da upise novu vrednost
  currentState[x][y] = isCellAlive(currentState[x][y], neighbours)

  condition.acquire() #conditionom zasticen i brojac celija
  doneThreads+=1

  if doneThreads == n ** 2:
    steps.append(copyState(currentState))
    doneThreads = 0;
    condition.notifyAll()
    condition.release()
  else:
    condition.wait()
    condition.release()

threads=[]

for k in range(50):
  for i in range(n):
    for j in range(n):
      t = threading.Thread(target=igraj, args=(i,j))
      t.start()
      threads.append(t)

for t in threads:
  t.join()

anim = animate(steps)
HTML(anim.to_html5_video())

