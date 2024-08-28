###
# This example shows how to plot two-dimensional slices of the HI density fields 
# for different parameters and resolutions.
###

from __future__ import print_function

import numpy as np
import pylab as plt

import script


## Full path to the GADGET-2 snapshot file. The file `examples/snap_008` is included with the 
## `script` distribution. You can also use your own GADGET-2 snapshot if you have one.
gadget_snap = './snap_008'

## The output directory.
outpath = './script_files'

## Class object for reading GADGET-2 snapshot file and setting up CIC density and velocity fields.
## Make sure you mention sigma_8, ns and omega_b as these variables are not stored in the 
## GADGET-2 snapshot. 
gadget_data = script.default_simulation_data(gadget_snap, outpath, sigma_8=0.829, ns=0.961, omega_b=0.0482)

## The number of grid cells used for making the maps. We will make maps for three different resolutions.
ngrid_arr = np.array([64, 32, 16])
## For each resolution, we will make maps for two values of Mmin.
log10Mmin_arr = np.array([8.0, 10.0])
## All the maps will have the same mass-averaged ionized fraction.
QHII_mean = 0.5

## Set up the plots.
fig = plt.figure(figsize=(15, 8))
box = gadget_data.box
centre = 0.33 ## the position of the slice in units of box size
num_ngrid = len(ngrid_arr)
num_Mmin = len(log10Mmin_arr)

for ngridloop, ngrid in enumerate(ngrid_arr):
    ## loop over resolution
    
    ## Class object containing the fields smoothed to the desired resolution.
    dens_fields = script.matter_fields(gadget_data, ngrid, outpath, overwrite_files=False)
    ## Class object for ionization maps.
    ionmap = script.ionization_map(dens_fields)

    for Mminloop, log10Mmin in enumerate(log10Mmin_arr):
        ## loop over Mmin
        
        ## collapsed fraction.
        fcoll_arr = dens_fields.get_fcoll_for_Mmin(log10Mmin)
        fcoll_mean = np.mean(fcoll_arr * (1 + dens_fields.densitycontr_arr))
        ## given the mass averaged ionized fraction, find the value of zeta.
        zeta = QHII_mean / fcoll_mean
        ## ionization field
        qi_arr = ionmap.get_qi(zeta * fcoll_arr)

        QHII_mean_map = np.mean(qi_arr * (1 + dens_fields.densitycontr_arr))
        #print ( 'grid size = ', ngrid, ': mass averaged ionized fraction from the map = ' + '{:.2f}'.format(QHII_mean_map) )



        ax = fig.add_subplot(num_Mmin, num_ngrid, Mminloop * num_ngrid + ngridloop + 1)



        dx = box / ngrid
        zgrid = int(ngrid * centre)
        im = ax.imshow(qi_arr[:,:,zgrid].T, origin='lower', extent=[0, box, 0, box], interpolation='bicubic', vmin=0.0, vmax=1.0)
        ax.set_xlabel(r'$x (h^{-1} \, \mathrm{cMpc})$')
        ax.set_ylabel(r'$y (h^{-1} \, \mathrm{cMpc})$')
        ax.set_title(r'$\log \, M_{\mathrm{min}} / M_{\odot} = ' + '{:.2f}'.format(log10Mmin) + ', \Delta x = ' + '{:.2f}'.format(dx) + ' \, h^{-1}$ cMpc')

        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label(r'$x_{\mathrm{HII}}$')

fig.tight_layout()
plt.show()

