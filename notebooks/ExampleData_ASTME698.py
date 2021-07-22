import pandas as pd
import numpy as np
from scipy.constants import physical_constants

import matplotlib.pyplot as plt
plt.style.use('..\JGW.mplstyle')

from ASTM_E698_2011 import PeakTempCorrection, iter_refine, get_Z, get_k
from LinReg import PolyReg

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

# x, y = 1/df['Corr. Peak Temp (K)'], df['log10(Heat Rate)']
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.scatter(x, y)
# ax.set_ylabel(r'log$_{10}$(β)')
# ax.set_xlabel('1/T (K$^{-1}$)')
# ax.set_title(r"Example Data")
# ax.annotate('R$^2$ = '+ str(round(logHeatRate_vs_Tinv.r_squared,4)), (.73, .85),
#             xycoords=ax.transAxes,
#             size=20)
# ax3 = plt.plot(x, logHeatRate_vs_Tinv.coef[0]*x + logHeatRate_vs_Tinv.coef[1], color='red')

y, x = df['Corr. Peak Temp (K)'], df['Heat Rate']
fig2 = plt.figure(figsize=(16,9))
ax2 = fig2.add_subplot(111)
ax2.scatter(x, y)
ax2.set_ylabel('Peak Temperature (K)')
ax2.set_xlabel('β (K/min)')
ax2.set_title(r"Example Data")

T_v_beta = PolyReg(x, y, 1)


plt.grid()
plt.show()