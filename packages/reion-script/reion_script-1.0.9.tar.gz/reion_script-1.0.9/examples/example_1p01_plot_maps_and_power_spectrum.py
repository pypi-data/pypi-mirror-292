###
# This example shows how to plot two-dimensional slices of the matter and HI density fields 
# and also plot the 21 cm power spectrum.
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

## If the GADGET-2 output distances are stored in kpc/h units, set scaledist = 0.001
scaledist = 1.e-3

## Class object for reading GADGET-2 snapshot file and setting up CIC density and velocity fields.
## Make sure you mention sigma_8, ns and omega_b as these variables are not stored in the 
## GADGET-2 snapshot. 
default_simulation_data = script.default_simulation_data(gadget_snap, outpath, sigma_8=0.829, ns=0.961, omega_b=0.0482, scaledist=scaledist)

## Number of grid cells in each direction used for generating the maps.
ngrid = 64
## Class object containing the fields smoothed to the desired resolution.
matter_fields = script.matter_fields(default_simulation_data, ngrid, outpath, overwrite_files=False)
## Class object for ionization maps.
ionization_map = script.ionization_map(matter_fields)

## The values of Mmin and zeta for HI maps.
log10Mmin = 9.0
zeta = 15

## The collapsed fraction followed by the ionization field
fcoll_arr = matter_fields.get_fcoll_for_Mmin(log10Mmin)
qi_arr = ionization_map.get_qi(zeta * fcoll_arr)

## Some outputs to check how we have done so far.
qi_mean = np.mean(qi_arr * (1 + matter_fields.densitycontr_arr))
print ( 'mass averaged ionized fraction = ' + '{:.2f}'.format(qi_mean) )
print ( 'zeta times fcoll = ' +  '{:.2f}'.format(zeta * np.mean(fcoll_arr * (1 + matter_fields.densitycontr_arr))) )

## The HI density field.
Delta_HI_arr = (1 - qi_arr) * (1 + matter_fields.densitycontr_arr)
## Add RSD effects.
Delta_HI_rsd_arr = ionization_map.add_rsd_box(qi_arr)

## Initialize power spectrum plans and set the k-bins.
matter_fields.initialize_powspec()
k_edges, k_bins = matter_fields.set_k_edges(nbins=15, log_bins=True)

## The binned power spectra with and without RSD. Set the units to `mK`.
powspec_21cm_rsd_binned, kount = ionization_map.get_binned_powspec(Delta_HI_rsd_arr, k_edges, units='mK')
powspec_21cm_binned, kount = ionization_map.get_binned_powspec(Delta_HI_arr, k_edges, units='mK')


#####################################
## PLOTTING STARTS
####################################

fig = plt.figure(figsize=(15.2, 8))

ax_den = fig.add_subplot(231)  ## matter density field
ax_HI = fig.add_subplot(232) ## HI density field (without RSD)
ax_HI_rsd = fig.add_subplot(233) ## HI density field (with RSD)

box = default_simulation_data.box
centre = 0.54 ## the position of the slice in units of box size

ngrid = matter_fields.ngrid
dx = box / ngrid
ygrid = int(ngrid * centre)

### matter density

im_den = ax_den.imshow(np.log10(1 + matter_fields.densitycontr_arr[:,ygrid,:].T), origin='lower', extent=[0, box, 0, box], interpolation='bicubic', cmap=plt.get_cmap('hot'))
ax_den.set_xlabel(r'$x (h^{-1} \, \mathrm{cMpc})$')
ax_den.set_ylabel(r'$z (h^{-1} \, \mathrm{cMpc})$')
ax_den.set_title(r'$z = ' + '{:.2f}'.format(default_simulation_data.z) + '$')

cbar_den = fig.colorbar(im_den, ax=ax_den)
cbar_den.set_label(r'$\log \, \Delta$')

### HI density

vmin = min( np.min(Delta_HI_arr[:,ygrid,:]), np.min(Delta_HI_rsd_arr[:,ygrid,:]) )
vmax = max( np.max(Delta_HI_arr[:,ygrid,:]), np.max(Delta_HI_rsd_arr[:,ygrid,:]) )

im_HI = ax_HI.imshow(Delta_HI_arr[:,ygrid,:].T, origin='lower', extent=[0, box, 0, box], interpolation='bicubic', vmin=vmin, vmax=vmax)
ax_HI.set_xlabel(r'$x (h^{-1} \, \mathrm{cMpc})$')
ax_HI.set_ylabel(r'$z (h^{-1} \, \mathrm{cMpc})$')
ax_HI.set_title(r'$\log \, M_{\mathrm{min}} / M_{\odot} = ' + '{:.2f}'.format(log10Mmin) + ', Q_{\mathrm{HII}}^{M} = ' + '{:.2f}'.format(qi_mean) + '$')

cbar_HI = fig.colorbar(im_HI, ax=ax_HI)
cbar_HI.set_label(r'$\Delta_{\mathrm{HI}}$')

### HI density with RSD

im_HI_rsd = ax_HI_rsd.imshow(Delta_HI_rsd_arr[:,ygrid,:].T, origin='lower', extent=[0, box, 0, box], interpolation='bicubic', vmin=vmin, vmax=vmax)
ax_HI_rsd.set_xlabel(r'$x (h^{-1} \, \mathrm{cMpc})$')
ax_HI_rsd.set_ylabel(r'$z (h^{-1} \, \mathrm{cMpc})$')
ax_HI_rsd.set_title('with RSD')


cbar_HI_rsd = fig.colorbar(im_HI_rsd, ax=ax_HI_rsd)
cbar_HI_rsd.set_label(r'$\Delta_{\mathrm{HI}}^{\mathrm{rsd}}$')

##################################

## The HI power spectra with and without RSD
ax_pk = fig.add_subplot(212)

ax_pk.plot( k_bins[kount > 0], k_bins[kount > 0] ** 3 * powspec_21cm_rsd_binned[kount > 0] / (2 * np.pi ** 2), label='with RSD' )
ax_pk.plot( k_bins[kount > 0], k_bins[kount > 0] ** 3 * powspec_21cm_binned[kount > 0] / (2 * np.pi ** 2), label='w/o RSD' )
ax_pk.legend(loc='best')
ax_pk.set_xscale('log')
ax_pk.set_yscale('log')
ax_pk.set_xlabel(r'$k (h / \mathrm{cMpc})$')
ax_pk.set_ylabel(r'$\Delta^2_{21}(k) (\mathrm{mK}^2)$')


fig.tight_layout()
plt.show()
