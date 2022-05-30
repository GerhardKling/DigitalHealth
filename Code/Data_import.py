"""
Importing data from Conference Board
Excel files: TED1.xlsx, TED1.xlsx
Export to pickle: pkl file with same name
@author: GK
"""
import pandas as pd


def convert_data(file: str, sheet: str, header_num: int, list_variables: list):
    #Specify sheet name and the row where header starts
    file_name = file + '.xlsx' #Add file extension
    df = pd.read_excel(file_name, sheet_name = sheet, header = header_num)
    
    #Transpose DataFrame
    df = df.T
    
    #Total number of variables
    #Avoid hard coded values
    num_var = len(list_variables)
    
    #Number of columns
    #Adding 1 as max in range is exclusive 
    #Adjust for number of variables
    max_col = df.shape[1] + 1 - num_var
    
    #Modify using list_variables
    #After all dfs with the same variable have been vertically stacked  
    
    list_dfs_hor = [] #List for horizontal stack
    
    for adx, name in enumerate(list_variables): 
        #Start with empty list for each variable
        list_dfs_vert = [] #List for vertical stack   
         
        for idx in range(0 + adx, max_col + adx, num_var):
            df_temp = df[idx][5 : ].to_frame()
            df_temp.columns = [name]    
            
            if adx == 0: #Only for first variable
                df_temp['region'] = df[idx].values[0]
                df_temp['iso'] = df[idx].values[1]
                df_temp['country'] = df[idx].values[2]         
           
            #Add to list for vertical stack  
            list_dfs_vert.append(df_temp)
       
        #Stack DataFrames vertically
        df_merged_vert = pd.concat(list_dfs_vert, axis = 0)
        
        #Add to list for horizontal stack
        list_dfs_hor.append(df_merged_vert) 
     
    #Stack DataFrames horizontally
    df_merged = pd.concat(list_dfs_hor, axis = 1)
    
    #Convert index to column
    df_merged['year'] = df_merged.index
    
    #Change order of columns
    add_variables = ['year', 'iso', 'country', 'region']
    
    #Add to front of list
    for var in add_variables:
        list_variables.insert(0, var)
    
    df_merged = df_merged.reindex(columns = list_variables)
    
    #Save the merged data
    file_name = file + ".pkl"
    df_merged.to_pickle(file_name)
    
    #Return a Pandas DataFrame
    return df_merged

