# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 10:13:37 2021

@author: Nash Skipper
"""

import cartopy.crs as ccrs
from netCDF4 import Dataset
import numpy as np

#> Note: only tested with Lambert Conformal Conic projection.
class cmaqfile(object):
    
    def __init__(self, path):
        self.f = Dataset(path)
    
    
    def getXY(self):

        """
        Get X and Y grid cell centers (in m) from CMAQ file metadata.

        Returns
        -------
        X : ndarry of float
            X direction grid cell centers in m
        Y : ndarry of float
            X direction grid cell centers in m
    
        """
        
        if self.f.GDTYP==1:
            print('ERROR: Cannot use getXY with lat-lon projection.')
            return
        
        xcell = self.f.XCELL
        xstart = self.f.XORIG
        xend = xstart + xcell*self.f.NCOLS
        ycell = self.f.YCELL
        ystart = self.f.YORIG
        yend = ystart + ycell*self.f.NROWS
        
        #> grid cell centers
        X = np.arange(xstart+xcell/2., xend, xcell)
        Y = np.arange(ystart+ycell/2., yend, ycell)
        
        return X, Y
    
    
    def getXYbnds(self):

        """
        Get X and Y grid cell corners (in m) from CMAQ file metadata.

        Returns
        -------
        Xbnds : ndarry of float
            X direction grid cell edges in m
        Ybnds : ndarry of float
            X direction grid cell edges in m
    
        """
        
        if self.f.GDTYP==1:
            print('ERROR: Cannot use getXYbnds with lat-lon projection.')
            return
        
        xcell = self.f.XCELL
        xstart = self.f.XORIG
        xend = xstart + xcell*self.f.NCOLS
        ycell = self.f.YCELL
        ystart = self.f.YORIG
        yend = ystart + ycell*self.f.NROWS
        
        #> grid cell corners
        X = np.arange(xstart, xend+xcell, xcell)
        Y = np.arange(ystart, yend+ycell, ycell)
        Xbnds, Ybnds = np.meshgrid(X, Y)
        
        return Xbnds, Ybnds
    
    
    def getCMAQproj(self, radius=6370000.):

        """
        Generate cartopy map projection from CMAQ file metadata.
        Note: Only Lambert Conformal Conic projection implemented.
              Will add others as needed.
        
        Parameters
        ----------
        radius : float, optional
            Assumed radius of the earth. The default is 6370000.
        
        Returns
        -------
        projection : cartopy crs
            Cartopy coordinate reference system generated from CMAQ projection
            information.
    
        """
        
        #> Lambert conformal
        if self.f.GDTYP==2:
            centlon = self.f.XCENT
            centlat = self.f.YCENT
            stdpar = (self.f.P_ALP, self.f.P_BET)
            cmaqglobe = ccrs.Globe(ellipse=None,
                                   semimajor_axis=radius,
                                   semiminor_axis=radius)
            projection = ccrs.LambertConformal(central_longitude=centlon,
                                               central_latitude=centlat,
                                               standard_parallels=stdpar,
                                               globe=cmaqglobe)
        
        return projection
    
    
    def getvar(self, var):

        """
        Get the values for a variable in the cmaq file.

        Parameters
        ----------
        var : str
            Variable name.

        Returns
        -------
        ndarray
            Array containing data for specified variable.

        """
        return self.f.variables[var][:].squeeze()
    
    
    def ll2xy(self, lons, lats):

        """
        Get the X and Y coordinates of (longitude, latitude) points.
        Inspired by Barron Henderson PseudoNetCDF package.

        Parameters
        ----------
        lons : float OR iterable of float
            Longitudes to be transformed.
        lats : float OR iterable of float
            Latitudes to be transformed.

        Returns
        -------
        xpts : list of float
            Coordinates of west-east dimension (X).
        xpts : list of float
            Coordinates of south-north dimension (Y).

        """
        
        if self.f.GDTYP==1:
            print('ERROR: Cannot use ll2xy with lat-lon projection.')
            return
        
        lons = np.asarray(lons)
        lats = np.asarray(lats)
        if lons.size != lats.size:
            print('ERROR: Number longitude and latitude points must be equal.')
            return
        
        cmaqproj = self.getCMAQproj()
        xpts, ypts, _ = cmaqproj.transform_points(ccrs.PlateCarree(), lons, lats).T
        
        return xpts, ypts
    
    
    def xy2ll(self, X, Y):
        
        """
        Get the longitude and latitude coordinates of X, Y points.
        Inspired by Barron Henderson PseudoNetCDF package.

        Parameters
        ----------
        X : float OR iterable of float
            Longitudes to be transformed.
        Y : float OR iterable of float
            Latitudes to be transformed.

        Returns
        -------
        lonpts : list of float
            Longitude coordinates.
        latpts : list of float
            Latitude coordinates.

        """
        
        if self.f.GDTYP==1:
            print('ERROR: Cannot use ll2xy with lat-lon projection.')
            return
        
        X = np.asarray(X)
        Y = np.asarray(Y)
        if X.size != Y.size:
            print('ERROR: Number X and Y points must be equal.')
            return
        
        cmaqproj = self.getCMAQproj()
        lonpts, latpts, _ = ccrs.PlateCarree().transform_points(cmaqproj, X, Y).T
        
        return lonpts, latpts
    
    
    def ll2ij(self, lons, lats):

        """
        Get the indices of (longitude, latitude) points.
        Inspired by Barron Henderson PseudoNetCDF package.

        Parameters
        ----------
        lons : float OR iterable of float
            Longitudes to be transformed.
        lats : float OR iterable of float
            Latitudes to be transformed.

        Returns
        -------
        i : list of int
            Indices of west-east dimension. NaN if outside the domain.
        j : list of int
            Indices of south-north dimension. NaN if outside the domain.

        """
        
        if self.f.GDTYP==1:
            print('ERROR: Cannot use ll2ij with lat-lon projection.')
            return
        
        lons = np.asarray(lons)
        lats = np.asarray(lats)
        if lons.size != lats.size:
            print('ERROR: Number longitude and latitude points must be equal.')
            return
        
        X, Y = self.getXY()
        Xbnds, Ybnds = self.getXYbnds()
        xpts, ypts = self.ll2xy(lons, lats)
        
        i=[]; j=[]
        for x, y in zip(xpts, ypts):
            if x < Xbnds.min() or x > Xbnds.max(): #> outside the domain
                i.append(np.nan)
                j.append(np.nan)
            elif y < Ybnds.min() or y > Ybnds.max(): #> outside the domain
                i.append(np.nan)
                j.append(np.nan)
            else:
                i.append(np.argmin(np.abs(X-x)))
                j.append(np.argmin(np.abs(Y-y)))
        return i, j
    
    
if __name__ == '__main__':
    
    #> cmaq file for testing
    #cmaqpath = '../POST_LA4/hr2day_ACONC_LA4_2018_20180901-20181130.nc'
    #file = cmaqfile(cmaqpath)
    
    #> metcro2d for eric from hires files
    cmaqpath = "C:/Users/emei3/Downloads/HIRES/METCRO2D_forecast4_20210426"
    file = cmaqfile(cmaqpath)
    #in order of STER, MGE, SSG, FTY, COV, CVC, SDK
    lons = (-84.46837, -84.50322, -84.58422, -84.52058, 
            -83.83925, -83.83684, -84.29018)
    lats = (33.83169, 33.91965, 33.72607, 33.77784,
            33.60807, 33.62966, 33.68808)
    I, J = file.ll2ij(lons, lats) #need lat lon +1
    
    #> check lat/lon conversion methods
    '''
    lons = (-119., -118., -117., -116., -114.8)
    lats = (33., 33.5, 34., 34.5, 37.5)
    x, y = file.ll2xy(lons, lats)
    i, j = file.ll2ij(lons, lats)
    #O3 = file.getvar('O3_8HRMAX').mean(axis=0)
    #O3_subset = O3[j, i]
    cmaqproj = file.getCMAQproj()
    checklon, checklat, z = ccrs.PlateCarree().transform_points(cmaqproj, x, y).T
    lonmesh, latmesh = np.meshgrid(lons, lats)
    xmesh, ymesh = np.meshgrid(x, y)
    check_result = ccrs.PlateCarree().transform_points(cmaqproj, xmesh, ymesh)
    loncheck, latcheck, zcheck = ccrs.PlateCarree().transform_points(cmaqproj, xmesh, ymesh).T
    loncheck2, latcheck2 = file.xy2ll(x, y)
    '''
    
    #> X, Y grid cell centers
    X, Y = file.getXY()
    Xmesh, Ymesh = np.meshgrid(X, Y)
    #> X, Y grid cell corners
    Xbnds, Ybnds = file.getXYbnds()
    
    
    