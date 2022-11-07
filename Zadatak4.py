from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from IPython.display import HTML
import random
import numpy as np
import multiprocessing
import queue

n = 8
aliveOrDead = [1, 0]
step = np.random.choice(aliveOrDead, n * n).reshape(n, n)
pool = multiprocessing.Pool(multiprocessing.cpu_count())

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

def igraj(task, step):
    result = []

    cordinatesX = [-1, -1, -1, 0, 0, 1, 1, 1]
    cordinatesY = [-1, 0, 1, -1, 1, -1, 0, 1]

    for x, y in task:
        brojac = 0
        for sused in range(8):
          if (x + cordinatesX[sused]) < 0:
            currX = n - 1
          else:
            currX = (x + cordinatesX[sused]) % n
          if (y + cordinatesY[sused]) < 0:
            currY = n - 1
          else:
            currY = (y + cordinatesY[sused]) % n
          brojac += step[currX, currY]

        z = isCellAlive(step[x, y], brojac)
        result.append((x, y, z))
        
    return result


steps = []
steps.append(step.copy())



tasks = []
results = []

for i in range(n):
    queue = []
    for j in range(n):
        queue.append((i, j))
    tasks.append(queue)


for k in range(20):
    for task in tasks:
        results.append(pool.apply_async(igraj, args = (task, step)))

    for result in results:
        for tupl in result.get():
            step[tupl[0], tupl[1]] = tupl[2]

    steps.append(step.copy())

pool.close()
pool.join()


anim = animate(steps)
HTML(anim.to_html5_video())