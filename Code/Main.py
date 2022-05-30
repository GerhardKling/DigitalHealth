"""
Main file
@author: GK
"""
import Data_merge

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

"""
Descriptive analysis
"""

df = pd.read_pickle('Merged_data.pkl')

#No data for Brunei, Lao
list_asean = [
    ('KHM', 'Cambodia'),
    ('IDN', 'Indonesia'),
    ('MYS', 'Malaysia'),
    ('MMR', 'Myanmar'),
    ('PHL', 'Philippines'),
    ('SGP', 'Singapore'),
    ('THA', 'Thailand'),
    ('VNM', 'Vietnam'),
    ]

#Obtain list of ISOs
list_iso = []
for country in list_asean:
    list_iso.append(country[0])
    
#Create dummy for ASEAN countries
df['ASEAN'] = df['iso'].apply(lambda x: 1 if x in list_iso else 0)

"""
A: Convergence of ASEAN countries
"""
#Long-term growth: ASEAN versus other countries
#Adjust type for groupby operation
#Convert column names into list
variable_list = list(df)
float_list = variable_list[4 : -1] #for floats
inter_list = []
inter_list.append(variable_list[3])
inter_list.append(variable_list[-1])

#Adjust types
for var in float_list:
    df[var] = pd.to_numeric(df[var], downcast='float')

for var in inter_list:
    df[var] = pd.to_numeric(df[var], downcast='integer')
    

#Plot grouped time series
fig1, ax1 = plt.subplots(figsize = (7,7))

#Removes the box around figure
ax1.spines["right"].set_visible(False)
ax1.spines["top"].set_visible(False)

#Title
ax1.set_title('Long-term income per capita')

#Axes labels
ax1.set_ylabel('Income per capita')
ax1.set_xlabel('Year')

#Use unstack()
df.groupby(['year','ASEAN']).mean()['inc_pc'].unstack().plot(ax = ax1)
fig1.savefig('Inc_pc.png')


"""
B: Share of ICT capital tends to be higher in ASEAN countries
"""

#Plot grouped time series
fig2, ax2 = plt.subplots(figsize = (7,7))

#Removes the box around figure
ax2.spines["right"].set_visible(False)
ax2.spines["top"].set_visible(False)

#Title
ax2.set_title('Share of ICT capital')

#Axes labels
ax2.set_ylabel('ICT capital share')
ax2.set_xlabel('Year')

#Use unstack()
df.groupby(['year','ASEAN']).mean()['ict_share'].unstack().plot(ax = ax2)
fig2.savefig('Ict_share.png')


"""
C: Descriptive analysis
"""
#Descriptive data for whole sample
table = df.describe(exclude = [object])

#Transpose for table export
out_table = table.T.round(3)
out_table.drop(labels = ['year', 'ASEAN'], axis = 0, inplace = True)
out_table.drop(labels = ['min', 'max'], axis = 1, inplace = True)

#Export to Excel
out_table.to_excel('Table1.xlsx')



"""
D: Growth decomposition
"""

def growth_rates(var: str, df, iso: str):
    """
    Determines log returns added to DataFrame denoted df
    The group variable is iso
    """
    new_var = var + '_g'
    df[new_var] = np.log(df[var]).diff()
    mask = df[iso] != df[iso].shift(1)
    df[new_var][mask] = np.nan

growth_list = ['l_quant', 'c_ict', 'c_non_ict']

for var in growth_list:
    growth_rates(var = var, df = df, iso = 'iso')

#Select independent variables
#Note: include dependent variable to check for listwise deletion
X = df[['gdp_g', 'l_quant_g', 'c_ict_g', 'c_non_ict_g', 'ASEAN']].dropna(how = 'any')

#Select dependent variable
y = X['gdp_g']
X = X[['l_quant_g', 'c_ict_g', 'c_non_ict_g', 'ASEAN']]

#Estimate OLS model
model = sm.OLS(y, sm.add_constant(X)).fit()

#Show model summary
model.summary()

coef = model.params
pvalues = model.pvalues

"""
Convert into Stata dta file
"""
df.to_stata("ASEAN.dta")



