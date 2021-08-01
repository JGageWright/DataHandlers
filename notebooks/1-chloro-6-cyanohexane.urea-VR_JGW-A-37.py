import pandas as pd
import numpy as np
from scipy.constants import physical_constants
import matplotlib.pyplot as plt
plt.style.use('..\JGW.mplstyle')

from DataHandlers.ASTM_E698_2011 import PeakTempCorrection, iter_refine, get_Z, get_k
from DataHandlers.LinReg import PolyReg

# --------------------------------------------------------------------------------------------
# USER DEFINED PARAMETERS
raw = pd.read_csv(r'1-chloro-6-cyanohexane.urea-VR_JGW-A-37.csv')
mass = 9.620 #in mg
Therm_Resist = 0.49441 #in K/mW

beta_choose = 20
tolerance_frac = 0.005
T_Arrhenius = 200
# --------------------------------------------------------------------------------------------


#Import and fit
df = PeakTempCorrection(raw, Therm_Resist, mass)
Standard = pd.read_excel(r'../data/Indium-Standard_JGW-A-43-15.xlsx')


# Compute Heat Rate Corrected peak temperatures using values from Standard
for beta in df['Heat Rate'].values:
    # .values is necessary because pd will actually test the indicies otherwise.
    # Exceptionally silly behavior if you ask me.
    if beta in Standard['Heat Rate'].values:
        df.loc[df['Heat Rate'] == beta, 'Twice Corr. Temp (K)'] \
            = df.loc[df['Heat Rate'] == beta, 'Lag Corr. Temp (K)'].values \
              - Standard.loc[Standard['Heat Rate'] == beta, 'Heat Rate Corr. ΔT'].values
            # .values is necessary here too, otherwise some perfectly valid calculations return NaN ??

# Drop any values not present in unknown AND standard
nonexistent = df.index[df.isnull().any(axis=1)]
df.drop(nonexistent, inplace=True)
print(df)

R = physical_constants['molar gas constant'][0]
logHeatRate_vs_Tinv = PolyReg(1/df['Twice Corr. Temp (K)'], df['log10(Heat Rate)'], 1)
Ea = -2.19 * R * logHeatRate_vs_Tinv.coef[0]

# Refine Ea
# T_chosen is the Corr. Peak Temp (K) at beta_choose
T_chosen = df.loc[df['Heat Rate'] == beta_choose, 'Twice Corr. Temp (K)']
ref_Ea = iter_refine(Ea,
                     logHeatRate_vs_Tinv.coef[0],
                     T_chosen,
                     tolerance_frac)
Z = get_Z(ref_Ea, T_chosen, beta_choose)
k = get_k(ref_Ea, Z, T_Arrhenius)

report = pd.Series({'Ea': ref_Ea, 'Z': Z, 'k': k})
print(report)

# FWO plot
fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(1/df['Twice Corr. Temp (K)'], df['log10(Heat Rate)'])
ax.set_ylabel(r'log$_{10}$(β)')
ax.set_xlabel('1/T$_{m}$ (K$^{-1}$)')
ax.set_title(r"1-chloro-6-cyanohexane/urea Guest Jump")
# ax.annotate('R$^2$ = '+ str(round(logHeatRate_vs_Tinv.r_squared,4)), (.75, .85),
#             xycoords=ax.transAxes,
#             size=20)
#
# ax1 = plt.plot(1/df['Twice Corr. Temp (K)'],
#                logHeatRate_vs_Tinv.coef[0]*(1/df['Twice Corr. Temp (K)']) +
#                logHeatRate_vs_Tinv.coef[1],
#                color='red')
ax23 = plt.scatter(1/df['Lag Corr. Temp (K)'], df['log10(Heat Rate)']) # HRC
ax.legend(['Heat Rate and Lag Corrected T$_{m}$', 'Lag Corrected T$_{m}$']) # HRC

plt.grid()

# Heat Rate correction Plotting
# fig, ax1 = plt.subplots()
# ax1.scatter(df['Heat Rate'], df['Lag Corr. ΔT'], c='black', zorder=0.1)
# ax1.set_ylabel('Lag Corrected ΔT (K)')
# ax1.set_xlabel('Heating Rate (K/min)')
# ax2 = plt.plot(df['Heat Rate'], df['Heat Rate'] * Rate_Corr.coef[0] + Rate_Corr.coef[1])
#
# # Does the Lag Correction affect linearity?
# x_unc, y_unc = df['Heat Rate'], df['Peak Temp (C)'] - df.loc[df['Heat Rate']==10, 'Peak Temp (C)'].array
# ax3 = ax1.twiny()
# ax3 = plt.scatter(x_unc, y_unc, c='red', zorder=1)

# Peak Temperature vs. Heating Rate
beta, temp = df['Heat Rate'], df['Twice Corr. Temp (K)']
fig2 = plt.figure()
ax2 = fig2.add_subplot(111)
ax2.scatter(beta, temp)
ax2.set_ylabel('T$_{m}$ (K)')
ax2.set_xlabel('β (K/min)')
ax2.set_title(r"1-chloro-6-cyanohexane/urea Guest Jump")
ax22 = plt.scatter(beta, df['Lag Corr. Temp (K)'])
ax2.legend(['Heat Rate and Lag Corrected T$_{m}$', 'Lag Corrected T$_{m}$'])
plt.grid()
# T_v_beta = PolyReg(beta, temp, 1)
# ax3 = plt.plot(beta, T_v_beta.coef[0]*beta + T_v_beta.coef[1], color='r')

# Kissinger
df['ln(Heat Rate/Tm2)'] = np.log(df['Heat Rate'] / df['Twice Corr. Temp (K)']**2)
k_fig = plt.figure()
k_ax = k_fig.add_subplot()
k_ax.scatter(1/df['Twice Corr. Temp (K)'], df['ln(Heat Rate/Tm2)'])
k_ax.set_ylabel('ln(β/T$_{m}^{2}$)')
k_ax.set_xlabel('1/T$_{m}$ (K$^{-1}$)')
k_ax.set_title(r"1-chloro-6-cyanohexane/urea Guest Jump")

plt.grid()
plt.show()