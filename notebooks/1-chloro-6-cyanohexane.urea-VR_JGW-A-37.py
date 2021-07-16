import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('..\JGW.mplstyle')

# Notebook version only
# import os
# os.chdir(r'C:\Users\Administrator\Documents\GitHub')
# End Notebook version only

from DataHandlers.LinReg import PolyReg
from DataHandlers.ASTM_E698_2011 import PeakTempCorrection

# USER DEFINED PARAMETERS
# raw = pd.read_csv(r'C:\Users\Administrator\Documents\GitHub\DataHandlers\notebooks\1-chloro-6-cyanohexane.urea-VR_JGW-A-37.csv')
raw = pd.read_csv(r'1-chloro-6-cyanohexane.urea-VR_JGW-A-37.csv')
mass = 9.620 #in mg
Therm_Resist = 0.49441 #in K/mW

#Import and fit
df = PeakTempCorrection(raw, Therm_Resist, mass)
Rate_Corr = PolyReg(df['Heat Rate'], df['Lag Corr. ΔT'], 1)
# Rate_Corr.report()

#Plotting
fig, ax1 = plt.subplots()
ax1.scatter(df['Heat Rate'], df['Lag Corr. ΔT'], c='black', zorder=0.1)
ax1.set_ylabel('Lag Corrected ΔT (K)')
ax1.set_xlabel('Heating Rate (K/min)')
ax2 = plt.plot(df['Heat Rate'], df['Heat Rate'] * Rate_Corr.coef[0] + Rate_Corr.coef[1])

# # Does the Lag Correction affect linearity?
# x_unc, y_unc = df['Heat Rate'], df['Peak Temp (C)'] - df.loc[df['Heat Rate']==10, 'Peak Temp (C)'].array
# ax3 = ax1.twiny()
# ax3 = plt.scatter(x_unc, y_unc, c='red', zorder=1)

# Try Kissinger Equation
df['ln(Heat Rate/Tm2)'] = np.log(df['Heat Rate'] / df['Lag Corr. Temp (K)']**2)
k_fig, k_ax = plt.subplots()
k_ax.scatter(1/df['Lag Corr. Temp (K)'], df['ln(Heat Rate/Tm2)'], c='black')
k_ax.set_ylabel('ln(Heat Rate/Tm2)')
k_ax.set_xlabel('1/T')


plt.show()