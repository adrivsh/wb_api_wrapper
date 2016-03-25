import pandas as pd
#from pandas.io import wb
from pandas_datareader import wb
# import numpy as np
from datetime import date
import pandas as pd

start_year = 1900
today_year = date.today().year

#use str.contains("a|b") next time)
def search_wb_local(wbbdd,query,col="name"):
    return wbbdd.ix[[query.lower() in c.lower() for c in wbbdd[col]],["id","name","source"]]

def search_wb(query):
    return wb.search(query)[["id","name","source"]]

def get_wb(wb_name):
    """return unstacked dataframe (countries, year) with WB data"""
    return wb.download(indicator=wb_name,start=start_year,end=today_year,country="all").unstack("year")[wb_name].dropna(how="all").dropna(how="all",axis=1)

def get_wb_df(wb_name,colname):
    """gets a dataframe from wb data with all years and all countries, and a lot of nans"""    
    #return all values
    wb_raw  =(wb.download(indicator=wb_name,start=start_year,end=today_year,country="all"))
    #sensible name for the column
    # wb_raw.rename(columns={wb_raw.columns[0]: colname},inplace=True)
    return wb_raw.rename(columns={wb_raw.columns[0]: colname})
    
def get_wb_series(wb_name,colname='value'):
    """"gets a pandas SERIES (instead of dataframe, for convinience) from wb data with all years and all countries, and a lotof nans""" 
    return get_wb_df(wb_name,colname)[colname]
    

def get_wb_mrv(wb_name,colname):
    """most recent value from WB API"""
    return mrv(get_wb_df(wb_name,colname))
    
def get_wb_lrv(wb_name,colname):
    """most recent value from WB API"""
    return lrv(get_wb_df(wb_name,colname))


def mlrv_gp(x,least_or_most,include_year=False):
    """this function gets the MOST or LEAST recent value from a wb-pulled dataframe grouped by country"""
   
    if least_or_most=="least":
        the_years =x["year"].min()
    elif least_or_most=="most":
        the_years =x["year"].max()
    else:
        raise ValueError('least_or_most was not in ["least","most"]')
   
    out= x.ix[(x["year"])==the_years,2]
    if include_year:
        return float(out),the_years
    else:
        return out

    
def mrv(data,include_year=False):    
    """most recent values from a dataframe. assumes one column is called 'year'"""    
    return lrv_or_mrv(data,"most",include_year)

def lrv(data,include_year=False):    
    """most recent values from a dataframe. assumes one column is called 'year'"""    
    return lrv_or_mrv(data,"least",include_year)
    
def lrv_or_mrv(data,least_or_most,include_year=False):    
    """LEAST recent values from a dataframe. assumes one column is called 'year'"""    
    try:
        if data.shape[1]>1:
            data = data.unstack()
    except IndexError :
        pass #data is already a series;
        
    #removes nans, and takes the least or most recent value. hop has a horrible shape
    hop=data.reset_index().dropna().groupby("country").apply(mlrv_gp,least_or_most,include_year)
    
    if include_year:
        return pd.DataFrame(hop.tolist(), columns=['value',"year"], index=hop.index)
    else:    
        return hop.reset_index().set_index("country")[0]
    
def mr_year(data):    
    """year of most recent values from a dataframe. assumes one column is called 'year'
    superesed by lrv(data, include_year=True)"""
    try:
        if data.shape[1]>1:
            data = data.unstack()
    except IndexError :
        pass #data is already a series;
    
    #removes nans, and takes the most revent value
    return data.reset_index().dropna().groupby("country")["year"].max()
    
def avg_gp(x):
    """this function gets the average over the last 10 years of a wb-pulled dataframe grouped by country"""
    last_year = float(x["year"].max())
    lyten = last_year - 10;
    where = x["year"].astype(float)>lyten
    out= x.ix[where,2].mean()
    return out    
    
def avg_val(data):    
    """10 year average from a dataframe. assumes one column is called 'year'"""    
    #removes nans, and takes the most revent value. hop has a horrible shape
    hop=data.reset_index().dropna().groupby("country").apply(avg_gp)
    #reshapes hop as simple dataframe indexed by country
    hop= hop.reset_index().drop("level_1",axis=1).set_index("country")
    return hop

def get_wb_avg(wb_name,colname):
    """most recent value from WB API"""
    return avg_val(get_wb_df(wb_name,colname))
    