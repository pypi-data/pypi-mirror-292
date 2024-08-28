###
# This example compares the HI maps and power spectra obtained using the 
# photon-conserving (PC) and excursion-set (ES) methods.
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
default_simulation_data = script.default_simulation_data(gadget_snap, outpath, sigma_8=0.829, ns=0.961, omega_b=0.0482)

## Number of grid cells in each direction used for generating the maps.
ngrid = 64
## Class object containing the fields smoothed to the desired resolution.
matter_fields = script.matter_fields(default_simulation_data, ngrid, outpath, overwrite_files=False)

## Initialize power spectrum plans and set the k-bins.
matter_fields.initialize_powspec()
k_edges, k_bins = matter_fields.set_k_edges(log_bins=False)

## Two different class objects, one for PC and another for ES
ionization_map_PC = script.ionization_map(matter_fields, method='PC')
ionization_map_ES = script.ionization_map(matter_fields, method='ES', ES_filter='sharp-k')

## The values of Mmin and zeta for HI maps.
log10Mmin = 9.0
zeta = 15

fcoll_arr = matter_fields.get_fcoll_for_Mmin(log10Mmin)
fcoll_mean = np.mean(fcoll_arr * (1 + matter_fields.densitycontr_arr))
print ( 'zeta times fcoll = ' +  '{:.2f}'.format(zeta * fcoll_mean) )

## The ionization maps obtained using the two methods.
qi_PC_arr = ionization_map_PC.get_qi(zeta * fcoll_arr)
qi_ES_arr = ionization_map_ES.get_qi(zeta * fcoll_arr)

qi_PC_mean = np.mean(qi_PC_arr * (1 + matter_fields.densitycontr_arr))
qi_ES_mean = np.mean(qi_ES_arr * (1 + matter_fields.densitycontr_arr))
print ( 'mass averaged ionized fraction (PC) = ' + '{:.2f}'.format(qi_PC_mean) )
print ( 'mass averaged ionized fraction (ES) = ' + '{:.2f}'.format(qi_ES_mean) )

## Another PC run with ionized mass fraction same as ES.
zeta_2 = qi_ES_mean / fcoll_mean
qi_PC_2_arr = ionization_map_PC.get_qi(zeta_2 * fcoll_arr)
qi_PC_2_mean = np.mean(qi_PC_2_arr * (1 + matter_fields.densitycontr_arr))
print ( 'zeta_2 times fcoll = ' +  '{:.2f}'.format(zeta_2 * fcoll_mean) )
print ( 'mass averaged ionized fraction (PC_2) = ' + '{:.2f}'.format(qi_PC_2_mean) )

## The HI density fields for the three cases.
Delta_HI_PC_arr = (1 - qi_PC_arr) * (1 + matter_fields.densitycontr_arr)
Delta_HI_ES_arr = (1 - qi_ES_arr) * (1 + matter_fields.densitycontr_arr)
Delta_HI_PC_2_arr = (1 - qi_PC_2_arr) * (1 + matter_fields.densitycontr_arr)

## The power spectra.
powspec_HI_PC_binned, kount = ionization_map_PC.get_binned_powspec(Delta_HI_PC_arr, k_edges, units='mK')
powspec_HI_ES_binned, kount = ionization_map_ES.get_binned_powspec(Delta_HI_ES_arr, k_edges, units='mK')
powspec_HI_PC_2_binned, kount = ionization_map_PC.get_binned_powspec(Delta_HI_PC_2_arr, k_edges, units='mK')


#####################################
## PLOTTING STARTS
####################################

fig = plt.figure(figsize=(15.2, 8))

ax_PC = fig.add_subplot(231)
ax_ES = fig.add_subplot(232)
ax_PC_2 = fig.add_subplot(233)

box = default_simulation_data.box
centre = 0.33 ## the position of the slice in units of box size

ngrid = matter_fields.ngrid
dx = box / ngrid
ygrid = int(ngrid * centre)

###

vmin = min( np.min(Delta_HI_PC_arr[:,ygrid,:]), np.min(Delta_HI_ES_arr[:,ygrid,:]), np.min(Delta_HI_PC_2_arr[:,ygrid,:]) )
vmax = max( np.max(Delta_HI_PC_arr[:,ygrid,:]), np.max(Delta_HI_ES_arr[:,ygrid,:]), np.max(Delta_HI_PC_2_arr[:,ygrid,:]) )

###

im_PC = ax_PC.imshow(Delta_HI_PC_arr[:,ygrid,:].T, origin='lower', extent=[0, box, 0, box], vmin=vmin, vmax=vmax, interpolation='bicubic', cmap=plt.get_cmap('hot'))
ax_PC.set_xlabel(r'$x (h^{-1} \, \mathrm{cMpc})$')
ax_PC.set_ylabel(r'$z (h^{-1} \, \mathrm{cMpc})$')
ax_PC.set_title(r'PC: $\zeta f_{\mathrm{coll}} = ' + '{:.2f}'.format(zeta * fcoll_mean) + ', Q_{\mathrm{HII}}^{M} = ' + '{:.2f}'.format(qi_PC_mean) + '$')

cbar_PC = fig.colorbar(im_PC, ax=ax_PC)
cbar_PC.set_label(r'$\Delta_{\mathrm{HI}}$')

###

im_ES = ax_ES.imshow(Delta_HI_ES_arr[:,ygrid,:].T, origin='lower', extent=[0, box, 0, box], vmin=vmin, vmax=vmax, interpolation='bicubic', cmap=plt.get_cmap('hot'))
ax_ES.set_xlabel(r'$x (h^{-1} \, \mathrm{cMpc})$')
ax_ES.set_ylabel(r'$z (h^{-1} \, \mathrm{cMpc})$')
ax_ES.set_title(r'ES: $\zeta f_{\mathrm{coll}} = ' + '{:.2f}'.format(zeta * fcoll_mean) + ', Q_{\mathrm{HII}}^{M} = ' + '{:.2f}'.format(qi_ES_mean) + '$')

cbar_ES = fig.colorbar(im_ES, ax=ax_ES)
cbar_ES.set_label(r'$\Delta_{\mathrm{HI}}$')

###

im_PC_2 = ax_PC_2.imshow(Delta_HI_PC_2_arr[:,ygrid,:].T, origin='lower', extent=[0, box, 0, box], vmin=vmin, vmax=vmax, interpolation='bicubic', cmap=plt.get_cmap('hot'))
ax_PC_2.set_xlabel(r'$x (h^{-1} \, \mathrm{cMpc})$')
ax_PC_2.set_ylabel(r'$z (h^{-1} \, \mathrm{cMpc})$')
ax_PC_2.set_title(r'PC: $\zeta f_{\mathrm{coll}} = ' + '{:.2f}'.format(zeta_2 * fcoll_mean) + ', Q_{\mathrm{HII}}^{M} = ' + '{:.2f}'.format(qi_PC_2_mean) + '$')

cbar_PC_2 = fig.colorbar(im_PC_2, ax=ax_PC_2)
cbar_PC_2.set_label(r'$\Delta_{\mathrm{HI}}$')

###




##################################

ax_pk = fig.add_subplot(212)

ax_pk.plot( k_bins[kount > 0], k_bins[kount > 0] ** 3 * powspec_HI_PC_binned[kount > 0] / (2 * np.pi ** 2), 'b-',
            label=r'PC: $\zeta f_{\mathrm{coll}} = ' + '{:.2f}'.format(zeta * fcoll_mean) + ', Q_{\mathrm{HII}}^{M} = ' + '{:.2f}'.format(qi_PC_mean) + '$' )
ax_pk.plot( k_bins[kount > 0], k_bins[kount > 0] ** 3 * powspec_HI_ES_binned[kount > 0] / (2 * np.pi ** 2), 'r:',
            label=r'ES: $\zeta f_{\mathrm{coll}} = ' + '{:.2f}'.format(zeta * fcoll_mean) + ', Q_{\mathrm{HII}}^{M} = ' + '{:.2f}'.format(qi_ES_mean) + '$' )
ax_pk.plot( k_bins[kount > 0], k_bins[kount > 0] ** 3 * powspec_HI_PC_2_binned[kount > 0] / (2 * np.pi ** 2), 'b--',
            label=r'PC: $\zeta f_{\mathrm{coll}} = ' + '{:.2f}'.format(zeta_2 * fcoll_mean) + ', Q_{\mathrm{HII}}^{M} = ' + '{:.2f}'.format(qi_PC_2_mean) + '$' )

ax_pk.legend(loc='best')
ax_pk.set_xscale('log')
ax_pk.set_yscale('log')
ax_pk.set_xlabel(r'$k (h / \mathrm{cMpc})$')
ax_pk.set_ylabel(r'$\Delta^2_{21}(k) (\mathrm{mK}^2)$')


fig.tight_layout()
plt.show()
