import pandas as pd
import numpy as np
from scipy.constants import physical_constants
import matplotlib.pyplot as plt
plt.style.use('..\JGW.mplstyle')

# Notebook version only
# import os
# os.chdir(r'C:\Users\Administrator\Documents\GitHub\DataHandlers\notebooks')
# End Notebook version only

from DataHandlers.ASTM_E698_2011 import PeakTempCorrection, iter_refine, get_Z, get_k
from DataHandlers.LinReg import PolyReg

# --------------------------------------------------------------------------------------------
# USER DEFINED PARAMETERS
raw = pd.read_csv(r'Indium-VR_JGW-A-43.csv')
mass = 5.491 #in mg
Therm_Resist = 0.49441 #in K/mW

beta_choose = 10
T_Arrhenius = 200
tolerance_frac = 0.005
# --------------------------------------------------------------------------------------------
# low_rates = raw.iloc[0:6, :]
# df = PeakTempCorrection(low_rates, Therm_Resist, mass)

#Import and fit
df = PeakTempCorrection(raw, Therm_Resist, mass)
Rate_Corr = PolyReg(df['Heat Rate'], df['Lag Corr. ΔT'], 1)
# Rate_Corr.report()

R = physical_constants['molar gas constant'][0]
logHeatRate_vs_Tinv = PolyReg(1/df['Lag Corr. Temp (K)'], df['log10(Heat Rate)'], 1)
Ea = -2.19 * R * logHeatRate_vs_Tinv.coef[0]

# Refine Ea
# T_chosen is the Corr. Peak Temp (K) at beta_choose
T_chosen = df.loc[df['Heat Rate'] == beta_choose, 'Lag Corr. Temp (K)']
ref_Ea = iter_refine(Ea,
                     logHeatRate_vs_Tinv.coef[0],
                     T_chosen,
                     tolerance_frac)
Z = get_Z(ref_Ea, T_chosen, beta_choose)
k = get_k(ref_Ea, Z, T_Arrhenius)

report = pd.Series({'Ea': ref_Ea, 'Z': Z, 'k': k})
print(report)

# FWO Plot
fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(1/df['Lag Corr. Temp (K)'], df['log10(Heat Rate)'])
ax.set_ylabel(r'log$_{10}$(β)')
ax.set_xlabel('1/T$_{m}$ (K$^{-1}$)')
ax.set_title(r"Indium Melt")
ax.annotate('R$^2$ = ' + str(round(logHeatRate_vs_Tinv.r_squared,4)), (.75, .85),
            xycoords=ax.transAxes,
            size=20)
ax1 = plt.plot(1/df['Lag Corr. Temp (K)'],
               logHeatRate_vs_Tinv.coef[0]*(1/df['Lag Corr. Temp (K)']) +
               logHeatRate_vs_Tinv.coef[1], color='red')
plt.grid()

# Peak Temperature vs. Heating Rate
beta, temp = df['Heat Rate'], df['Lag Corr. Temp (K)']
fig2 = plt.figure()
ax2 = fig2.add_subplot(111)
ax2.scatter(beta, temp)
ax2.set_ylabel('T$_{m}$ (K)')
ax2.set_xlabel('β (K/min)')
ax2.set_title(r"Indium Melt")
plt.grid()
# T_v_beta = PolyReg(beta, temp, 1)
# ax3 = plt.plot(beta, T_v_beta.coef[0]*beta + T_v_beta.coef[1], color='r')



# Kissinger
df['ln(Heat Rate/Tm2)'] = np.log(df['Heat Rate'] / df['Lag Corr. Temp (K)']**2)
k_fig = plt.figure()
k_ax = k_fig.add_subplot()
k_ax.scatter(1/df['Lag Corr. Temp (K)'], df['ln(Heat Rate/Tm2)'])
k_ax.set_ylabel('ln(β/T$_{m}^{2}$)')
k_ax.set_xlabel('1/T$_{m}$ (K$^{-1}$)')
k_ax.set_title(r"Indium Melt")

plt.grid()
plt.show()

# Heat Rate correction Plotting
fig, ax4 = plt.subplots()
ax4.scatter(df['Heat Rate'], df['Lag Corr. Temp (K)'])
ax4.set_ylabel('T$_{m}$ (K)')
ax4.set_xlabel('β (K/min)')
ax4.set_title(r"Indium Melt")
ax5 = plt.scatter(df['Heat Rate'], df['Peak Temp (C)'] + 273.15, c='r')

ax4.legend(['Lag Corrected T$_{m}$', 'Uncorrected T$_{m}$'])

plt.grid()
plt.show()

# # Does the Lag Correction affect linearity?
# x_unc, y_unc = df['Heat Rate'], df['Peak Temp (C)'] - df.loc[df['Heat Rate']==10, 'Peak Temp (C)'].array
# ax3 = ax1.twiny()
# ax3 = plt.scatter(x_unc, y_unc, c='red', zorder=1)
