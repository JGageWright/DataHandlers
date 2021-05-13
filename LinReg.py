from sklearn.linear_model import LinearRegression

# Linear Regression
def Least_sq(x, y):
    reg_x = x.values.reshape(-1,1)
    reg_y = y.values.reshape(-1,1)
    reg = LinearRegression().fit(reg_x, reg_y)
    return [reg, reg_x, reg_y]

# The set of associated metrics to report, check Skoog textbook for definitions
def get_Sumsq(reg_x):
    x_bar = sum(reg_x) / len(reg_x)
    xi_minus_xbar_sq = []
    for i in range(len(reg_x[:,0])):
        xi_minus_xbar_sq.append((reg_x[i, 0] -  x_bar)**2)
    return sum(xi_minus_xbar_sq)

def get_Sxy(reg_x, reg_y):
    x_bar = sum(reg_x) / len(reg_x)
    xi_minus_xbar = []
    for i in range(len(reg_x[:,0])):
        xi_minus_xbar.append(reg_x[i, 0] -  x_bar)
    
    y_bar = sum(reg_y) / len(reg_y)
    yi_minus_ybar = []
    for i in range(len(reg_y[:,0])):
        yi_minus_ybar.append(reg_y[i, 0] -  y_bar)
        
    products = []
    for i in range(len(xi_minus_xbar)):
        products.append(xi_minus_xbar[i] * yi_minus_ybar[i])
    return sum(products)

def get_sy(reg_x, reg_y):
    n = len(reg_x[:,0])
    reg = LinearRegression().fit(reg_x, reg_y)
    return (((get_Sumsq(reg_y) - ((float(reg.coef_) ** 2) * get_Sumsq(reg_x))) / (n-2))) ** (1/2)

def get_sm(reg_x, reg_y):
    n = len(reg_x[:,0])
    num = (get_sy(reg_x, reg_y) ** 2) * n
    denom = (n * sum(reg_x ** 2)) - sum(reg_x)**2
    return (num / denom) ** (1/2)

def get_sb(reg_x, reg_y):
    n = len(reg_x[:,0])
    num = (get_sy(reg_x, reg_y) ** 2) * sum(reg_x ** 2)
    denom = (n * sum(reg_x ** 2)) - sum(reg_x)**2
    return (num / denom) ** (1/2)

def get_Ext_sx(reg_x, reg_y, unknown_mean, replicants=1):
    n = len(reg_x[:,0])
    reg = LinearRegression().fit(reg_x, reg_y)
    y_bar = sum(reg_y) / len(reg_y)
    num = (unknown_mean - y_bar) ** 2
    denom = (float(reg.coef_)**2) * get_Sumsq(reg_x)
    return (get_sy(reg_x, reg_y) / abs(float(reg.coef_))) * (((1/n) + (1/replicants) + (num/denom)) ** (1/2))

def get_SA_sx(reg_x, reg_y):
    n = len(reg_x[:,0])
    reg = LinearRegression().fit(reg_x, reg_y)
    y_bar = sum(reg_y) / len(reg_y)
    num = y_bar ** 2
    denom = (float(reg.coef_)**2) * get_Sumsq(reg_x)
    return (get_sy(reg_x, reg_y) / abs(float(reg.coef_))) * (((1/n) + (num/denom)) ** (1/2))