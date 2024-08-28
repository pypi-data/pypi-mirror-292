###
# This example shows how to make light cone map for a reionization history
# using the outputs from MUSIC
###



from __future__ import print_function

import numpy as np
import os
import configparser

import matplotlib.pyplot as plt
from matplotlib.image import NonUniformImage
import matplotlib

import script as script

## Use the directory where you have stored the MUSIC output files
data_path = '/home/tirth/LARGE_DATA_FILES/GADGET-3-DATA/N128_L128.0_MUSIC_2LPT-r1'
data_root = 'snap'
outpath = data_path + '/script_files'  ## directory where the script-related files were stored


### Set some parameters. log10Mmin and zeta set the reionization history
ngrid = 64
log10Mmin = 15.0
zeta = 9.0

### The y-coordinate of the slice
centre = 0.19 ## in units of box size

z_arr = np.array([])
QHI_mean_arr = np.array([])
Delta_HI_z_arr = np.empty( shape=(0, ngrid, ngrid) )
vlos_z_arr = np.empty( shape=(0, ngrid, ngrid) )
ygrid = int(ngrid * centre)

loop = 0
snap = 0
delta_snap = 1


### looping over all the MUSIC output files in the directory
while(True):
    snap_str = '{:03d}'.format(snap)
    gadget_snap = data_path + "/" + data_root + "_" + snap_str

    if (loop == 0):
        config = configparser.ConfigParser()
        config.read(data_path + '/music_000.info')
        omega_b = float(config['cosmology']['Omega_b'])
        sigma_8 = float(config['cosmology']['sigma_8'])
        ns = float(config['cosmology']['nspec'])
        #print (omega_b, sigma_8, ns)

    if (os.path.exists(gadget_snap)):

        gadget_data = script.default_simulation_data(gadget_snap, outpath, sigma_8=sigma_8, ns=ns, omega_b=omega_b)
        if (loop == 0):
            omega_m = gadget_data.cosmo.omega_m
            omega_l = gadget_data.cosmo.omega_l
            h = gadget_data.cosmo.h
            YHe = gadget_data.cosmo.YHe

        dens_fields = script.matter_fields(gadget_data, ngrid, outpath, overwrite_files=False)
        ionmap = script.ionization_map(dens_fields)

        # if (gadget_data.z >= 14.0):
        #     zeta = 0.0
        # else:
        #     zeta = 1.e5

        fcoll_arr = dens_fields.get_fcoll_for_Mmin(log10Mmin)
        qi_arr = ionmap.get_qi(zeta * fcoll_arr)
        Delta_HI_arr = (1 - qi_arr) * (1 + dens_fields.densitycontr_arr)

        box = gadget_data.box
        Delta_HI_z_arr = np.concatenate((Delta_HI_z_arr, [Delta_HI_arr[:,ygrid,:]]), axis = 0)
        vlos_z_arr = np.concatenate((vlos_z_arr, [dens_fields.velocity_arr[-1,:,ygrid,:]]), axis = 0)

        z_arr = np.append(z_arr, gadget_data.z)
        QHI_mean_arr = np.append(QHI_mean_arr, np.mean(Delta_HI_arr))
        #print (gadget_data.z, np.mean(Delta_HI_arr), np.min(fcoll_arr), np.max(fcoll_arr))



    else: ## when we do not find the next snapshot
        break

    loop += 1
    snap += delta_snap

#print ("k bin values: ", k_bins)

num_maps = loop

### check if the history is sensible! compute CMB optical depth
tau_arr = script.utils.get_tau(z_arr, 1 - QHI_mean_arr, omega_m, omega_l, omega_b, h, YHe)
print ('CMB tau for the reionization hstory: ', tau_arr[0])

### create the light cone map
Delta_HI_los_arr, xcom_los_arr, zlos_arr = script.utils.create_light_cone_map(z_arr, Delta_HI_z_arr, box, ngrid, omega_m, omega_l, vlos_z_arr=vlos_z_arr)
#Delta_HI_los_arr, xcom_los_arr, zlos_arr = script.utils.create_light_cone_map(z_arr, Delta_HI_z_arr, box, ngrid, omega_m, omega_l, vlos_z_arr=None)


### start plotting
fig = plt.figure(figsize=(15, 3))
ax = fig.add_subplot(111)


im = ax.imshow(Delta_HI_los_arr.T, interpolation='bicubic', extent=(xcom_los_arr[0], xcom_los_arr[-1], 0, box), aspect=1.0)

################
## set the ticks along the z-axis. The axis is uniform in comoving distance, but not in redshift.

import math
# ztick_min = math.ceil(np.min(zlos_arr))
# ztick_max = math.floor(np.max(zlos_arr))
# dztick = 1.0
# ztick_min = 5.5
# ztick_max = 14.5
# dztick = 1.5
# ztickmarks = np.arange(ztick_min, ztick_max+dztick/2, dztick)
ztickmarks = [5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 11.0, 12.0, 13.0, 14.0]
ax.xaxis.set_ticks( np.interp(ztickmarks, zlos_arr[::-1], xcom_los_arr[::-1]) )

def functick(x, pos=None):
    val = np.interp(x, xcom_los_arr[::-1], zlos_arr[::-1])
    #print (x, val)
    return '{0:g}'.format(val)

ticks = matplotlib.ticker.FuncFormatter(functick)
ax.xaxis.set_major_formatter(ticks)

###############

ax.set_xlabel(r'$z$')
ax.set_ylabel(r'$x (h^{-1} \, \mathrm{cMpc})$')

fig.tight_layout()
plt.show()
