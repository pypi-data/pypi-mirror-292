import xarray as xr

@xr.register_dataarray_accessor("xwp")


class xwp(object):
    '''
    This is a classe to work on pressure file
    '''
    
    def __init__(self, xarray_obj):
        '''
        Constructor for xwp.
        
        :param xarray_obj: pressure DataArray
        :type xarray_obj: xr.DataArray
        '''
        self._obj = xarray_obj 
    pass

#------------------functions----------------------