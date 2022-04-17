import numpy as np
from numpy.linalg import lstsq
import pandas as pd

class PolyReg:
    """
    No parameters can be fixed
    Object to hold all information associated with a polynomial model.
    Polynomial coefficients in order of decreasing degree are in coef[i].
    Note that ss_yy is commonly named ss_tot in other implementations.
    coef = ndarray of fitting parameters in order of decreasing degree
    ss_res = sum of squares of residuals.
    std_err = ndarray of standard errors of the fitting parameters in order of decreasing degree.
    These are calculated as the square root of diagonal elements in the covariance matrix
    """
    def __init__(self, xdata, ydata, degree: int):
        """
        :param xdata: Array of xdata
        :param ydata: Array of ydata
        :param degree: Degree of polynomial fit
        """
        self.xdata = xdata
        self.ydata = ydata
        self.degree = degree
        self.coef, self.cov = np.polyfit(xdata, ydata, degree, cov=True)
        self.residuals = ydata - np.polyval(self.coef, xdata)
        self.ss_res = np.sum(self.residuals**2)
        self.ss_yy = np.sum((ydata - np.mean(ydata)) ** 2)
        self.ss_xx = np.sum((xdata - np.mean(xdata)) ** 2)
        self.ss_xy = np.sum((xdata - np.mean(xdata))*(ydata - np.mean(ydata)))
        self.r_squared = 1 - (self.ss_res / self.ss_yy)
        self.std_err = np.sqrt(np.diag(self.cov))
        self.s_y = np.sqrt(self.ss_res / (len(ydata) - 1 - self.degree))
        self.roots = np.roots(self.coef)
        
    def report(self):
        '''
        Returns some quantities of interest
        '''
        params = {}
        for i in range(len(self.coef)):
            params['coef_deg' + str(len(self.coef) - i -1)] = self.coef[i]
            params['std_err_deg' + str(len(self.coef) - i -1)] = self.std_err[i]
            
        params['r_squared'] = self.r_squared
        params['s_y'] = self.s_y
        series = pd.Series(params)
        return series
    
    def eval(self, x):
        return np.polyval(self.coef, x)
    
    
class LinFixB:
    def __init__(self, xdata, ydata) -> None:
        self.xdata = xdata
        self.ydata = ydata
        
        x_col = xdata[:, np.newaxis] # x must be a column vector for np.lstsq
        y_col = ydata[:, np.newaxis] # y must have same shape as x
        
        self.coef, ss_res, rank, s = lstsq(x_col, y_col, rcond=False)
        b = np.zeros([1]) # insert intercept manually
        self.coef = np.append(self.coef, b)
        
        self.cov = np.cov(xdata, ydata)
        self.residuals = ydata - np.polyval(self.coef, xdata)
        self.ss_res = np.sum(self.residuals**2)
        self.ss_yy = np.sum((ydata) ** 2)
        self.r_squared = 1 - (self.ss_res / self.ss_yy)
        self.std_err = np.sqrt(np.diag(self.cov)) # Not sure if this is correct
        self.s_y = np.sqrt(self.ss_res / (len(ydata) - 2)) # len(ydata) - 1 - degree of fit
        self.roots = np.roots(self.coef)
        
    def report(self):
        '''
        Returns some quantities of interest
        '''
        params = {}
        for i in range(len(self.coef)):
            params['coef_deg' + str(len(self.coef) - i -1)] = self.coef[i]
            params['std_err_deg' + str(len(self.coef) - i -1)] = self.std_err[i]
            
        params['r_squared'] = self.r_squared
        params['s_y'] = self.s_y
        series = pd.Series(params)
        return series
    
    def eval(self, x):
        return np.polyval(self.coef, x)