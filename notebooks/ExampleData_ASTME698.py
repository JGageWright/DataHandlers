import pandas as pd
import numpy as np

import sympy as sp
from sympy.interactive import printing
printing.init_printing(use_latex=True)
from sympy.parsing.latex import parse_latex
from scipy.constants import physical_constants

import matplotlib.pyplot as plt
plt.style.use('JGW.mplstyle')

from ASTM_E698_2011 import PeakTempCorrection, iter_refine, get_Z, get_k
from LinReg import PolyReg

# USER DEFINED PARAMETERS
beta_choose = 7
# Typically also raw csv file, mass, and Thermal Resistance
# This data is in an atypical shape because the correction has already been applied.
df = pd.read_csv('notebooks\ExampleData_ASTME698.csv')
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
                     0.005)
Z = get_Z(ref_Ea, T_chosen, beta_choose)
k = get_k(ref_Ea, Z, 370)

report = pd.Series({'Ea':ref_Ea, 'Z':Z, 'k':k})
print(report)


