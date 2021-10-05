import numpy as np
import matplotlib.pyplot as plt
plt.style.use('JGW.mplstyle')

x = np.linspace(0, 10, 100)

fig = plt.figure()
ax0 = fig.add_subplot(111)

ax0.plot(x, np.sin(x + 0 * np.pi/6))
# ax1 = plt.plot(x, np.sin(x + 1 * np.pi/6))
ax2 = plt.scatter(x, np.sin(x + 2 * np.pi/6))
# ax3 = plt.plot(x, np.sin(x + 3 * np.pi/6))
ax4 = plt.plot(x, np.sin(x + 4 * np.pi/6))
# ax5 = plt.plot(x, np.sin(x + 5 * np.pi/6))
ax6 = plt.plot(x, np.sin(x + 6 * np.pi/6))
# ax7 = plt.plot(x, np.sin(x + 7 * np.pi/6))
ax8 = plt.plot(x, np.sin(x + 8 * np.pi/6))
# ax9 = plt.plot(x, np.sin(x + 9 * np.pi/6))
ax10 = plt.plot(x, np.sin(x + 10 * np.pi/6))
# ax11 = plt.plot(x, np.sin(x + 11 * np.pi/6))

ax0.set_title('Title')

plt.show()