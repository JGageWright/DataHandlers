import pandas as pd
import numpy as np
from scipy import fftpack
import matplotlib.pyplot as plt
plt.style.use('JGW')

# filename = r"C:\Users\jgage\Desktop\7972_201208EAscan11D22113A.csv"
# data = pd.read_csv(filename, names=['Potential / V', 'Current / A', 'idk'])


noise = 0.1 # rel. magnitude of noise
samp_rate = 2000 # sample rate in Hz, BEWARE OF ALIASING
tstep = 1 / samp_rate # time between samples in s
periods = 10
t = np.arange(0, periods, tstep)
f = fftpack.fftfreq(t.size, d=tstep)

# The signal is a 3 sin, 2 cos, and some noise
sig_freq = np.array([1, 2, 4])
sig = noise*np.random.randn(t.size)
sig = sig + np.cos(2*np.pi*t * 200) + np.cos(2*np.pi*t * 4)
for i in sig_freq:
    sig = sig + np.sin(2*np.pi*t * i)

'''
Fourier Transform
Recall that sin and cos are complex functions of two frequencies, ω and -ω.
Therefore, this particular FT is symmetric about f=0.
You can use rfft() to eliminate this
'''
sig_fft = fftpack.fft(sig) # fft() returns an array of complex numbers in "Standard Order"
# Notice that pure sin signals are not visible -- They have no real component (Euler's formula)

'''
Taking the amplitude will show all complex signals onto the real axis
The FT amplitide is proportional to the square root of the sum of oscillation amplitudes at a given frequency
The FT power is proportional to the number of signals
'''
amplitude = np.abs(sig_fft) # Modulus = sqrt(real^2 + imag^2)
real = np.real(sig_fft) # just for plotting, mpl throws a warning if you give it a complex number
power = amplitude**2 # Power = real^2 + imag^2
angle = np.angle(sig_fft) # Argument

fig, ax = plt.subplots(4, 1)
ax[0].plot(t, sig)
ax[1].plot(f, real)
ax[2].plot(f, amplitude)
ax[3].plot(f, power)
# ax[1].set_xlim(-5,5)
# ax[2].set_xlim(-5,5)
# ax[3].set_xlim(-5,5)
plt.show()


