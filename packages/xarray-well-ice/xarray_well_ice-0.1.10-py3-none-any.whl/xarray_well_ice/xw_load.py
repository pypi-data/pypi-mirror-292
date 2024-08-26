import xarray as xr
import pandas as pd
import numpy as np
from datetime import datetime

def load_xw_pressure(adr,skiprows=2,header=1,col_name='P',col_date='TIMESTAMP',**kwargs):
    '''
    Load date for pressure file
    '''
    
    data=pd.read_csv(adr,header=header,**kwargs).iloc[skiprows:]

    ds=xr.DataArray(data[col_name].to_numpy().astype(np.float64),dims='time')
    
    ds['time']= [datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S') for date_str in data[col_date]]
    ds.attrs['unit']='bar'

    return ds

def load_xw_tilt(adr,skiprows=2,header=1,col_date='TIMESTAMP',**kwargs):
    '''
    Load date for tilt file
    '''
    
    data=pd.read_csv(adr,header=header,**kwargs).iloc[skiprows:]

    ds=xr.Dataset()
    for var in list(data.columns)[2:]:
        ds[var]=xr.DataArray(data[var].to_numpy().astype(np.float64),dims='time')

    ds['time']= [datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S') for date_str in data[col_date]]
    
    ds.attrs['unit']='degree'

    return ds