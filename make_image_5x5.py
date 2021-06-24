#
#  Add a 1x1 deg image within a 5x5 deg image. Different methods to do this.
#
# Created by Ivan Valtchanov, 23 June 2021
#
import os
import numpy as np

from astropy.io import fits
from astropy import wcs

home = os.path.expanduser('~')
#
wdir = f'{home}/Desktop/XXL_Euclid'
#
ndim = 7200
field_size = 5.0 # degrees
pix_size = field_size/7200.0
#
fill_value = 1.0e-20
xim = np.full((ndim,ndim),fill_value,dtype=np.float32)
#
w = wcs.WCS(naxis=2)
w.wcs.crpix = [ndim/2.0, ndim/2.0]
w.wcs.cdelt = np.array([pix_size, pix_size])
# ~arbitrary location
w.wcs.crval = [30.0,-5.0]
w.wcs.ctype = ["RA---TAN", "DEC--TAN"]
#
header = w.to_header()
#
# now read the 1x1 deg image
#
with fits.open(f'{wdir}/stacked_final.fits') as hdu:
    image = hdu[0].data
#
# keep the shape
xs = image.shape
# number of tiles in one direction, total number is tiles*tiles
tiles = int(ndim/xs[0])
#
# choose the method
#
method = 'center'
#method = 'random'
#method = 'fill' # simple tiling
#method = 'fill_random' # tile but with rotation/swap, each subsequent one will be rotated by 90 deg and then swapped
#
# centred 
#
if (method == 'center'):
    x0 = int(ndim/2.0) - int(xs[0]/2.0)
    y0 = int(ndim/2.0) - int(xs[1]/2.0)
    xim[x0:x0+xs[0],y0:y0+xs[1]] = image
elif (method == 'random'):
    # random position within the 5x5 image
    # pick a random point with the 5x5 image where the 1x1 image will fit in
    #
    xmin = int(xs[0]/2.0)
    ymin = int(xs[1]/2.0)
    xmax = ndim - int(xs[0]/2.0)
    ymax = ndim - int(xs[1]/2.0)
    x0 = np.random.randint(xmin,high=xmax)
    y0 = np.random.randint(ymin,high=ymax)
    xim[x0:x0+xs[0],y0:y0+xs[1]] = image
elif (method == 'fill'):
    # fill the large image by the smaller one via tiling
    xim = np.tile(image,(tiles,tiles)).astype(np.float32)
elif (method == 'fill_random'):
    # like tiling but now each tile will be rotated by 90 deg with respect to previous tile
    k = 1
    for i in np.arange(tiles):
        for j in np.arange(tiles):
            x0 = i*xs[0]
            y0 = j*xs[1]
            x1 = x0 + xs[0]
            y1 = y0 + xs[1]
            rim = np.rot90(image,k=k)
            xim[x0:x1,y0:y1] = rim
            k += 1
        #
    #
#
#
# add the result in a FITS HDU
#
hdu = fits.PrimaryHDU(xim,header=header)
hdul = fits.HDUList([hdu])
#
# save as FITS file
hdul.writeto(f'{wdir}/test_image_5x5_{method}.fits',overwrite=True)
#