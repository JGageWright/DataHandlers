import pandas as pd
import numpy as np
from scipy.constants import physical_constants

import matplotlib.pyplot as plt
plt.style.use('..\JGW.mplstyle')

from DataHandlers.ASTM_E698_2011 import PeakTempCorrection, iter_refine, get_Z, get_k
from DataHandlers.LinReg import PolyReg

# ----------------------------------------------------------------------------------------------------------------------
# USER DEFINED PARAMETERS
beta_choose = 7
# There is typically also raw csv file, mass, and Thermal Resistance
# However, this data is in an atypical shape because the correction has already been applied.
tolerance_frac = 0.005
T_Arrhenius = 370
# -----------------------------------------------------------------------------------------------------------------------
df = pd.read_csv('ExampleData_ASTME698.csv')
df.columns = ['Heat Rate', 'Corr. Peak Temp (K)']
df['log10(Heat Rate)'] = np.log10(df.iloc[:, 0])

# Calculate the Activation Energy
R = physical_constants['molar gas constant'][0]
logHeatRate_vs_Tinv = PolyReg(1/df['Corr. Peak Temp (K)'], df['log10(Heat Rate)'], 1)
Ea = -2.19 * R * logHeatRate_vs_Tinv.coef[0]

# Refine Ea
# T_chosen is the Corr. Peak Temp (K) at beta_choose
T_chosen = df.loc[df['Heat Rate'] == beta_choose, 'Corr. Peak Temp (K)']
ref_Ea = iter_refine(Ea,
                     logHeatRate_vs_Tinv.coef[0],
                     T_chosen,
                     tolerance_frac)
Z = get_Z(ref_Ea, T_chosen, beta_choose)
k = get_k(ref_Ea, Z, T_Arrhenius)

report = pd.Series({'Ea':ref_Ea, 'Z':Z, 'k':k})
print(report)

# FWO plot
x, y = 1/df['Corr. Peak Temp (K)'], df['log10(Heat Rate)']
fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(x, y)
ax.set_ylabel(r'log$_{10}$(β)')
ax.set_xlabel('1/T$_{m}$ (K$^{-1}$)')
ax.set_title(r"Example Data (Table X2.1)")
ax.annotate('R$^2$ = '+ str(round(logHeatRate_vs_Tinv.r_squared,4)), (.75, .85),
            xycoords=ax.transAxes,
            size=20)
ax3 = plt.plot(x, logHeatRate_vs_Tinv.coef[0]*x + logHeatRate_vs_Tinv.coef[1], color='red')
plt.grid()


# y, x = df['Corr. Peak Temp (K)'], df['Heat Rate']
# fig2 = plt.figure(figsize=(16,9))
# ax2 = fig2.add_subplot(111)
# ax2.scatter(x, y)
# ax2.set_ylabel('Peak Temperature (K)')
# ax2.set_xlabel('β (K/min)')
# ax2.set_title(r"Example Data")
#
# T_v_beta = PolyReg(x, y, 1)

# Peak Temperature vs. Heating Rate
beta, temp = df['Heat Rate'], df['Corr. Peak Temp (K)']
fig2 = plt.figure()
ax2 = fig2.add_subplot(111)
ax2.scatter(beta, temp)
ax2.set_ylabel('T$_{m}$ (K)')
ax2.set_xlabel('β (K/min)')
ax2.set_title(r"Example Data (Table X2.1)")
plt.grid()
# T_v_beta = PolyReg(beta, temp, 1)
# ax3 = plt.plot(beta, T_v_beta.coef[0]*beta + T_v_beta.coef[1], color='r')

# Kissinger
df['ln(Heat Rate/Tm2)'] = np.log(df['Heat Rate'] / df['Corr. Peak Temp (K)']**2)
x2, y2 = 1/df['Corr. Peak Temp (K)'], df['ln(Heat Rate/Tm2)']
K_fit = PolyReg(x2, y2, 1)

k_fig = plt.figure()
k_ax = k_fig.add_subplot()
k_ax.scatter(x2, y2)
k_ax.set_ylabel('ln(β/T$_{m}^{2}$)')
k_ax.set_xlabel('1/T$_{m}$ (K$^{-1}$)')
k_ax.set_title(r"Example Data (Table X2.1)")

k_ax2 = plt.plot(x2, K_fit.coef[0]*x + K_fit.coef[1], color='red')
k_ax.annotate('R$^2$ = '+ str("%.4f" % K_fit.r_squared), (.75, .85),
            xycoords=ax.transAxes,
            size=20)

plt.grid()
plt.show()