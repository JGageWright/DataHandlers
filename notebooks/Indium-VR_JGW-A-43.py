import pandas as pd
import numpy as np
from scipy.constants import physical_constants
import matplotlib.pyplot as plt
plt.style.use('..\JGW.mplstyle')

# Notebook version only
# import os
# os.chdir(r'C:\Users\Administrator\Documents\GitHub\DataHandlers')
# End Notebook version only

from ASTM_E698_2011 import PeakTempCorrection, iter_refine, get_Z, get_k
from LinReg import PolyReg

# --------------------------------------------------------------------------------------------
# USER DEFINED PARAMETERS
raw = pd.read_csv(r'Indium-VR_JGW-A-43.csv')
mass = 5.491 #in mg
Therm_Resist = 0.49441 #in K/mW
beta_choose = 50
# --------------------------------------------------------------------------------------------


#Import and fit
df = PeakTempCorrection(raw, Therm_Resist, mass)
Rate_Corr = PolyReg(df['Heat Rate'], df['Lag Corr. ΔT'], 1)
# Rate_Corr.report()

R = physical_constants['molar gas constant'][0]
logHeatRate_vs_Tinv = PolyReg(1/df['Lag Corr. Temp (K)'], df['log10(Heat Rate)'], 1)
Ea = -2.19 * R * logHeatRate_vs_Tinv.coef[0]
print(Ea)
# Refine Ea
# T_chosen is the Corr. Peak Temp (K) at beta_choose
T_chosen = df.loc[df['Heat Rate'] == beta_choose, 'Lag Corr. Temp (K)']
ref_Ea = iter_refine(Ea,
                     logHeatRate_vs_Tinv.coef[0],
                     T_chosen,
                     0.005)
Z = get_Z(ref_Ea, T_chosen, beta_choose)
k = get_k(ref_Ea, Z, 200)

report = pd.Series({'Ea':ref_Ea, 'Z':Z, 'k':k})
print(report)

fig = plt.figure(figsize=(16,9))
ax = fig.add_subplot(111)
ax.scatter(1/df['Lag Corr. Temp (K)'], df['log10(Heat Rate)'])
ax.set_ylabel(r'log$_{10}$(β)')
ax.set_xlabel('1/T (K$^{-1}$)')
ax.set_title(r"Indium Melt")
ax.annotate('R$^2$ = '+ str(round(logHeatRate_vs_Tinv.r_squared,4)), (.73, .85),
            xycoords=ax.transAxes,
            size=20)

ax1 = plt.plot(1/df['Lag Corr. Temp (K)'],
               logHeatRate_vs_Tinv.coef[0]*(1/df['Lag Corr. Temp (K)']) +
               logHeatRate_vs_Tinv.coef[1],
               color='red')

plt.grid()
plt.show()

# Depreciated Heat Rate correction Plotting
# fig, ax1 = plt.subplots()
# ax1.scatter(df['Heat Rate'], df['Lag Corr. ΔT'], c='black', zorder=0.1)
# ax1.set_ylabel('Lag Corrected ΔT (K)')
# ax1.set_xlabel('Heating Rate (K/min)')
# ax2 = plt.plot(df['Heat Rate'], df['Heat Rate'] * Rate_Corr.coef[0] + Rate_Corr.coef[1])
#
# # # Does the Lag Correction affect linearity?
# # x_unc, y_unc = df['Heat Rate'], df['Peak Temp (C)'] - df.loc[df['Heat Rate']==10, 'Peak Temp (C)'].array
# # ax3 = ax1.twiny()
# # ax3 = plt.scatter(x_unc, y_unc, c='red', zorder=1)
#
# # Try Kissinger Equation
# df['ln(Heat Rate/Tm2)'] = np.log(df['Heat Rate'] / df['Lag Corr. Temp (K)']**2)
# k_fig, k_ax = plt.subplots()
# k_ax.scatter(1/df['Lag Corr. Temp (K)'], df['ln(Heat Rate/Tm2)'], c='black')
# k_ax.set_ylabel('ln(Heat Rate/Tm2)')
# k_ax.set_xlabel('1/T')
