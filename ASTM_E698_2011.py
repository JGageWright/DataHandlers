import pandas as pd
import numpy as np
import sympy as sp
from scipy.constants import physical_constants

def PeakTempCorrection(df, R0=0.49441, m=1):
    '''
    df must have Heat Rate, Peak Temp, Peak Height (W/g) as first three columns.

    ASTM E698-2011
    df is a dataframe of raw data, which has Heat Rate, Peak Temp (C), and Peak Height (W/g) columns
    R0 is the thermal resistance in K/mW
    m is the mass of the sample in mg
    '''

    df.columns = ['Heat Rate', 'Peak Temp (C)', 'Peak Height (W/g)']
    df['log10(Heat Rate)'] = np.log10(df.iloc[:, 0])
    df['Height (mW)'] = df.iloc[:, 2] * m / 1000
    df['Lag Corr. Temp (C)'] = df.iloc[:, 1] - (df['Height (mW)'] * R0)
    df['Lag Corr. Temp (K)'] = df['Lag Corr. Temp (C)'] + 273.15
    df['Lag Corr. ΔT'] = df['Lag Corr. Temp (C)'] - df.loc[df.iloc[:, 0] == 10, 'Lag Corr. Temp (C)'].array
    return df

def get_D(X):
    '''
    Calculates the value of D from the function given in table X2.2
    '''
    D, x, R = sp.symbols('D x R')
    R = physical_constants['molar gas constant'][0]
    rho = sp.log((x+2)**-1 * x**-1 * sp.exp(-x))
    eq = sp.Eq(D, -sp.diff(rho, x))
    return sp.solve(eq.subs(x, X), D)[0]

def get_Z(Ea, T_chosen, beta_choose):
    '''
    Calculates the value of the Arrhenus Prexponential factor
    '''
    Z, beta, E, R, T = sp.symbols('Z beta E R T')
    R = physical_constants['molar gas constant'][0]
    T = T_chosen
    beta = beta_choose
    E = Ea
    Z = beta * E / R / T**2 * sp.exp(E / (R * T))
    return Z

def get_k(Ea, Z, T):
    R = physical_constants['molar gas constant'][0]
    return Z * sp.exp(-Ea / (R * T))


def Refine_Ea(Ea, slope, T_chosen):
    '''
    Choose a peak temperature with a moderate heating rate for T_chosen
    This is the peak temperature at beta_choose
    '''
    R = physical_constants['molar gas constant'][0]
    X = Ea / (R * T_chosen)
    D = get_D(X)
    Ea_new = -(1/np.log10(np.exp(1))) * R * slope / D
    return Ea_new

def iter_refine(Ea, slope, T_chosen, tolerance_frac):
    '''
    Refines Ea until sucessive values agree within the tolerance_frac
    '''
    Ea_list = [Ea]
    Ea_list.append(Refine_Ea(Ea, slope, T_chosen))
    while abs((Ea_list[-1] - Ea_list[-2])/ Ea_list[-2]) > tolerance_frac:
        Ea_list.append(Refine_Ea(Ea_list[-1], slope, T_chosen))

    report = pd.Series(Ea_list, name='Ea (J/mol)')
    print(report)
    return Ea_list[-1]