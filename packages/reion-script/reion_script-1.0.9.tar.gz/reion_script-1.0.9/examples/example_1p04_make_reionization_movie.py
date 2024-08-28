###
# This example shows how to make a movie of the HI fields by varying the global ionized fraction
# and also simultaneously plot the 21 cm power spectrum. The redshift remains unchanged.
###

from __future__ import print_function

import numpy as np
import pylab as plt
from matplotlib.animation import ArtistAnimation

import script

## Most of the code should be straightforward if you have gone through the 
## previous examples.

gadget_snap = './snap_008'
outpath = './script_files'

gadget_data = script.default_simulation_data(gadget_snap, outpath, sigma_8=0.829, ns=0.961, omega_b=0.0482)


ngrid = 64
log10Mmin = 8.0
## Number of maps to be included in the movie.
num_maps = 50
## The values of ionized mass fractions to be used in the movie.
QHII_mean_arr = np.linspace(0.05, 0.99, num=num_maps)

dens_fields = script.matter_fields(gadget_data, ngrid, outpath, overwrite_files=False)
ionmap = script.ionization_map(dens_fields)

fcoll_arr = dens_fields.get_fcoll_for_Mmin(log10Mmin)
fcoll_mean = np.mean(fcoll_arr * (1 + dens_fields.densitycontr_arr))

nbins = 20
dens_fields.initialize_powspec()
k_edges, k_bins = dens_fields.set_k_edges(nbins=nbins, log_bins=False)

box = gadget_data.box
centre = 0.54 ## the position of the slice in units of box size

zeta_arr = np.zeros_like(QHII_mean_arr)
Delta_HI_plot_arr = np.zeros((num_maps, ngrid,ngrid))
powspec_21cm_binned_arr = np.zeros((num_maps, nbins))
kount_arr = np.zeros((num_maps, nbins))

dx = box / ngrid
zgrid = int(ngrid * centre)

for maploop, QHII_mean in enumerate(QHII_mean_arr):

    zeta = QHII_mean / fcoll_mean ## fix zeta from the value of the mean ionized fraction.
    qi_arr = ionmap.get_qi(zeta * fcoll_arr)
    Delta_HI_arr = (1 - qi_arr) * (1 + dens_fields.densitycontr_arr)

    powspec_21cm_binned_arr[maploop,:], kount_arr[maploop,:] = ionmap.get_binned_powspec(Delta_HI_arr, k_edges, units='mK')
    powspec_21cm_binned_arr[maploop,:] = k_bins ** 3 * powspec_21cm_binned_arr[maploop,:] / (2 * np.pi ** 2)
    zeta_arr[maploop] = zeta
    Delta_HI_plot_arr[maploop,:,:] = Delta_HI_arr[:,:,zgrid].T


    if (np.remainder(maploop + 1, 10) == 0): print('done map frame ', maploop + 1, ' of ', num_maps)

print ('preparing the movie now...')

fig = plt.figure(figsize=(12, 5))
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

vmin = np.min(Delta_HI_plot_arr)
vmax = np.max(Delta_HI_plot_arr)
image = ax1.imshow(Delta_HI_plot_arr[0,:,:], origin='lower', extent=[0, box, 0, box], interpolation='bicubic', vmin=vmin, vmax=vmax, cmap=plt.get_cmap('hot'))
cbar = fig.colorbar(image, ax=ax1)
cbar.set_label(r'$\Delta_{\mathrm{HI}}$')


xmin = np.min(k_bins)
xmax = np.max(k_bins)
ymin = np.min(powspec_21cm_binned_arr[kount_arr > 0])
ymax = np.max(powspec_21cm_binned_arr[kount_arr > 0])
ax2.set_xlim(xmin, xmax)
ax2.set_ylim(ymin, ymax)
ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.set_xlabel(r'$k (h / \mathrm{cMpc})$')
ax2.set_ylabel(r'$\Delta^2_{\mathrm{HI}}(k) \mathrm{mK}^2$')

fig.tight_layout()

movie_objects=([])

for frame in range(num_maps):
    image = ax1.imshow(Delta_HI_plot_arr[frame,:,:], origin='lower', extent=[0, box, 0, box], interpolation='bicubic', vmin=vmin, vmax=vmax, cmap=plt.get_cmap('hot'))
    ## The comma on the lhs is necessary
    line, = ax2.plot(k_bins[kount_arr[frame,:] > 0], powspec_21cm_binned_arr[frame,kount_arr[frame,:] > 0], color='blue')
    title_image = ax1.text(0.6 * box, 0.9 * box, r'$Q_{\mathrm{HI}} = ' + '{:04.2f}'.format(1 - QHII_mean_arr[frame]) + '$', bbox=dict(facecolor='white', alpha=0.5))
    
    movie_objects.append([image, title_image, line])


frame_rate = 10 ## For a given frame_rate x, the frame-time in ms is 1000/x
animation = ArtistAnimation(fig, movie_objects, interval=1000 / frame_rate)

# Try to set the DPI to the actual number of pixels you are plotting.
# Currently set to a low value.
animation.save("example_1p04_reionization_movie.mp4", dpi=256)
