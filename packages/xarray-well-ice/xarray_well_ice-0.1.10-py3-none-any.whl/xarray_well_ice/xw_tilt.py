import xarray as xr
import matplotlib.pyplot as plt

@xr.register_dataset_accessor("xwt")


class xwt(object):
    '''
    This is a classe to work on tilt file from borehole logging
    '''
    
    def __init__(self, xarray_obj):
        '''
        Constructor for xwp.
        
        :param xarray_obj: Xarray Data Set
        :type xarray_obj: xr.Dataset
        '''
        self._obj = xarray_obj 
    pass

#------------------functions----------------------

    def plot_raw(self,opt='SCL',**kwargs):
        '''
        Plot raw data for a given captor.

        :param opt: Name of the captor
        :type opt: string
        '''

        for i in range(15):
            self._obj['tilt_'+opt+'('+str(i+1)+')'].plot(label=opt+str(i+1),**kwargs)

        return