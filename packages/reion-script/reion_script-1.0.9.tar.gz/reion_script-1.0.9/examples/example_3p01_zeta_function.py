###
# This example shows how to use a arbitrary mass-dependent zeta
# to make the HI maps
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

## Let us first make a map for constant zeta.

## The values of Mmin and zeta for HI maps.
log10Mmin = 9.0
zeta = 15

## The collapsed fraction followed by the ionization field
zeta_fcoll_arr = matter_fields.get_zeta_fcoll(zeta, log10Mmin=log10Mmin)
qi_arr = ionization_map.get_qi(zeta_fcoll_arr)

## Some outputs to check how we have done so far.
qi_mean = np.mean(qi_arr * (1 + matter_fields.densitycontr_arr))
print ( 'constant zeta: mass averaged ionized fraction = ' + '{:.6f}'.format(qi_mean) )
print ( 'constant zeta: zeta times fcoll = ' +  '{:.6f}'.format(np.mean(zeta_fcoll_arr * (1 + matter_fields.densitycontr_arr))) )

#print (np.min(zeta_fcoll_arr), np.max(zeta_fcoll_arr))

######################################

## define the zeta(M) function

def zetafunc(M):
    #return zeta * np.exp( - 0.66 * 10 ** log10Mmin / M)
    return 9.3 * (M / 1.e10) ** (-0.5)

zeta_fcoll_2_arr = matter_fields.get_zeta_fcoll(zetafunc, log10Mmin=log10Mmin)
qi_2_arr = ionization_map.get_qi(zeta_fcoll_2_arr)

## Some outputs to check how we have done so far.
qi_2_mean = np.mean(qi_2_arr * (1 + matter_fields.densitycontr_arr))
print ( 'mass-dependent zeta: mass averaged ionized fraction = ' + '{:.6f}'.format(qi_2_mean) )
print ( 'mass-dependent zeta: zeta times fcoll = ' +  '{:.6f}'.format(np.mean(zeta_fcoll_2_arr * (1 + matter_fields.densitycontr_arr))) )

#print (np.min(zeta_fcoll_2_arr), np.max(zeta_fcoll_2_arr))
#print (np.min(zeta_fcoll_arr - zeta_fcoll_2_arr), np.max(zeta_fcoll_arr - zeta_fcoll_2_arr))
#print (np.min(zeta_fcoll_arr / zeta_fcoll_2_arr), np.max(zeta_fcoll_arr / zeta_fcoll_2_arr))

## The HI density field.
Delta_HI_arr = (1 - qi_arr) * (1 + matter_fields.densitycontr_arr)
Delta_HI_2_arr = (1 - qi_2_arr) * (1 + matter_fields.densitycontr_arr)


## Initialize power spectrum plans and set the k-bins.
matter_fields.initialize_powspec()
k_edges, k_bins = matter_fields.set_k_edges(nbins=15, log_bins=True)

## The binned power spectra. Set the units to `mK`.
powspec_21cm_binned, kount = ionization_map.get_binned_powspec(Delta_HI_arr, k_edges, units='mK')
powspec_21cm_2_binned, kount = ionization_map.get_binned_powspec(Delta_HI_2_arr, k_edges, units='mK')

#####################################
## PLOTTING STARTS
####################################

fig = plt.figure(figsize=(11, 8))

ax_1 = fig.add_subplot(221)
ax_2 = fig.add_subplot(222)

box = default_simulation_data.box
centre = 0.54 ## the position of the slice in units of box size

ngrid = matter_fields.ngrid
dx = box / ngrid
ygrid = int(ngrid * centre)

### HI density

vmin = min( np.min(Delta_HI_arr[:,ygrid,:]), np.min(Delta_HI_2_arr[:,ygrid,:]) )
vmax = max( np.max(Delta_HI_arr[:,ygrid,:]), np.max(Delta_HI_2_arr[:,ygrid,:]) )

im_1 = ax_1.imshow(Delta_HI_arr[:,ygrid,:].T, origin='lower', extent=[0, box, 0, box], interpolation='bicubic', vmin=vmin, vmax=vmax)
ax_1.set_xlabel(r'$x (h^{-1} \, \mathrm{cMpc})$')
ax_1.set_ylabel(r'$z (h^{-1} \, \mathrm{cMpc})$')
ax_1.set_title(r'$\zeta = ' + '{:.2f}'.format(zeta) + '$')

cbar_1 = fig.colorbar(im_1, ax=ax_1)
cbar_1.set_label(r'$\Delta_{\mathrm{HI}}$')

### 

im_2 = ax_2.imshow(Delta_HI_2_arr[:,ygrid,:].T, origin='lower', extent=[0, box, 0, box], interpolation='bicubic', vmin=vmin, vmax=vmax)
ax_2.set_xlabel(r'$x (h^{-1} \, \mathrm{cMpc})$')
ax_2.set_ylabel(r'$z (h^{-1} \, \mathrm{cMpc})$')
ax_2.set_title(r'varying $\zeta$')


cbar_2 = fig.colorbar(im_2, ax=ax_2)
cbar_2.set_label(r'$\Delta_{\mathrm{HI}}$')

##################################

## The HI power spectra
ax_pk = fig.add_subplot(212)

ax_pk.plot( k_bins[kount > 0], k_bins[kount > 0] ** 3 * powspec_21cm_binned[kount > 0] / (2 * np.pi ** 2), label=r'$\zeta = ' + '{:.2f}'.format(zeta) + '$' )
ax_pk.plot( k_bins[kount > 0], k_bins[kount > 0] ** 3 * powspec_21cm_2_binned[kount > 0] / (2 * np.pi ** 2), label=r'varying $\zeta$')
ax_pk.legend(loc='best')
ax_pk.set_xscale('log')
ax_pk.set_yscale('log')
ax_pk.set_xlabel(r'$k (h / \mathrm{cMpc})$')
ax_pk.set_ylabel(r'$\Delta^2_{21}(k) (\mathrm{mK}^2)$')


fig.tight_layout()
plt.show()
