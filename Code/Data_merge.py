"""
Merging TED1 and TED2
@author: GK
Returns: pickled data: Merged_data.pkl
"""

import pandas as pd

from Data_import import convert_data 

"""
Convert TED1 file
"""
#Call the function
file = "TED1"
sheet = 'DATA'
header_num = 4

#List of variables
list_variables = [
    'r_gdp',
    'n_gdp',
    'emp',
    'hours',
    't_hours',
    'pop',
    'out_p',
    'out_h',
    'inc_pc',
    'gdp_g',
    'emp_g',
    't_hours_g',
    'pop_g',
    'out_p_g',
    'out_h_g',
    'inc-pc_g'
    ]

df_TED1 = convert_data(file, sheet, header_num, list_variables)


"""
Convert TED2 file
"""
#Call the function
#NOTE: remove additional column NR
file = "TED2"
sheet = 'DATA'
header_num = 4

#List of variables
list_variables = [
    'gdp',
    'l_quant',
    'l_qual',
    'c_total',
    'c_ict',
    'c_non_ict',
    'l_quant_c',
    'l_qual_c',
    'c_total_c',
    'c_ict_c',
    'c_non_ict_c',
    'tfp',
    'l_share',
    'c_share',
    'ict_share',
    'non_ict_share'
    ]

df_TED2 = convert_data(file, sheet, header_num, list_variables)


"""
Merge DataFrames
"""
#Remove region and country from TED2 before merger
del df_TED2['region']
del df_TED2['country']

#Looking at ICT limits the data to the period 1990 to 2021
df_merged = pd.merge(df_TED1, df_TED2, on = ['iso', 'year'], how = 'left')

"""
WARNING: As we created a DataFrame using external data (data import), 
numeric variables might be represented as data type objects (not int or float). 
This affects numeric operations (e.g., groupby)
Check type: type(df_merged['year'][8]) or df_merged.info() - NumPy objects
Use: df['year'] = pd.to_numeric(df['year'], downcast='integer')
"""

#Rescale variables: e.g., GDP in billion
rescale_list = [
    'r_gdp',
    'n_gdp',
    'emp',
    'pop'
    ]

for var in rescale_list:
    df_merged[var] = df_merged[var]/1000


#Save the merged data
df_merged.to_pickle('Merged_data.pkl')