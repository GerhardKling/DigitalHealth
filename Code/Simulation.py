"""
Simulation
@author: GK
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Import coefficient matrix
#Variables: 0 is y, 1 is c, 2 is k, 3 is l, 4 is h
df = pd.read_excel('Matrix.xlsx', header = None)

#Step-by-step forecasts
def forecast(step: int, df, imp: int, res: int):
    #Variables to forecast: 0 to 4
    predict = np.zeros(step)
    
    #Deep copy of DataFrame
    matrix = df.copy()
    predict[0] = matrix.iloc[res, imp]
    for idx in range(1, step):
        matrix = np.matmul(matrix,df)
        predict[idx] = matrix.iloc[res, imp] + predict[idx-1]
    return predict

#Forecasting
res_y_imp_h = forecast(step = 10, df = df, imp = 4, res = 0)
res_c_imp_h = forecast(step = 10, df = df, imp = 4, res = 1)
res_k_imp_h = forecast(step = 10, df = df, imp = 4, res = 2)
res_l_imp_h = forecast(step = 10, df = df, imp = 4, res = 3)

#Plotting
plt.rcParams['font.size'] = 8
fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
ax1.plot(res_y_imp_h, 'r')
ax1.set_title('Impact on GDP', size=12)
ax2.plot(res_c_imp_h, 'b') 
ax2.set_title('Impact on ICT', size=12)
ax3.plot(res_k_imp_h, 'k') 
ax3.set_title('Impact on non_ICT', size=12)
# set the spacing between subplots
plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=0.8, 
                    wspace=0.5, 
                    hspace=0.5)
plt.show()
fig.savefig('Impulse.png')

