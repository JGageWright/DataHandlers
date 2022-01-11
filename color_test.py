import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.pyplot import cm
os.system('cls')
plt.style.use('DataHandlers/JGW-VS.mplstyle')

x = np.linspace(0, 10, 100)

fig = plt.figure()
ax0 = fig.add_subplot(111)

color = iter(cm.seismic(np.linspace(0, 1, 10)))

for i in range(10):
    c=next(color)
    ax0.plot(x, np.sin(x + i * np.pi/5), c=c)
# # ax1 = plt.plot(x, np.sin(x + 1 * np.pi/6))
# ax2 = plt.scatter(x, np.sin(x + 2 * np.pi/6), facecolors='none')
# # ax3 = plt.plot(x, np.sin(x + 3 * np.pi/6))
# ax4 = plt.plot(x, np.sin(x + 4 * np.pi/6))
# # ax5 = plt.plot(x, np.sin(x + 5 * np.pi/6))
# ax6 = plt.plot(x, np.sin(x + 6 * np.pi/6))
# # ax7 = plt.plot(x, np.sin(x + 7 * np.pi/6))
# ax8 = plt.plot(x, np.sin(x + 8 * np.pi/6))
# # ax9 = plt.plot(x, np.sin(x + 9 * np.pi/6))
# ax10 = plt.plot(x, np.sin(x + 10 * np.pi/6))
# # ax11 = plt.plot(x, np.sin(x + 11 * np.pi/6))

# ax0.set_title('Title')

plt.show()
