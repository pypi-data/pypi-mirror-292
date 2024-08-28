###
# This example shows how to make a movie of the HI fields for a reionization history
# using the outputs from MUSIC
# and also simultaneously plot the 21 cm power spectrum.
###



from __future__ import print_function

import numpy as np
import pylab as plt
import os
import configparser

from matplotlib.animation import ArtistAnimation

import script

## Most of the code should be straightforward if you have gone through the 
## previous examples.
data_path = '/home/tirth/LARGE_DATA_FILES/GADGET-3-DATA/N256_L256.0_MUSIC_2LPT-r1'
data_root = 'snap'
outpath = data_path + '/script_files'  ## directory where the script-related files would be stored

ngrid = 32
log10Mmin = 8.0
zeta = 8

centre = 0.19 ## in units of box size

z_arr = np.array([])
QHI_mean_arr = np.array([])
Delta_HI_plot_arr = np.empty( shape=(0, ngrid, ngrid) )
zgrid = int(ngrid * centre)

nbins = 20
powspec_plot_arr = np.empty( shape=(0, nbins) )

loop = 0
snap = 0
delta_snap = 1

while(True):
    snap_str = '{:03d}'.format(snap)
    gadget_snap = data_path + "/" + data_root + "_" + snap_str

    if (loop == 0):
        config = configparser.ConfigParser()
        config.read(data_path + '/music_000.info')
        omega_b = float(config['cosmology']['Omega_b'])
        sigma_8 = float(config['cosmology']['sigma_8'])
        ns = float(config['cosmology']['nspec'])
        print (omega_b, sigma_8, ns)

    if (os.path.exists(gadget_snap)):

        gadget_data = script.default_simulation_data(gadget_snap, outpath, sigma_8=sigma_8, ns=ns, omega_b=omega_b)
        dens_fields = script.matter_fields(gadget_data, ngrid, outpath, overwrite_files=False)
        ionmap = script.ionization_map(dens_fields)

        fcoll_arr = dens_fields.get_fcoll_for_Mmin(log10Mmin)
        qi_arr = ionmap.get_qi(zeta * fcoll_arr)
        Delta_HI_arr = (1 - qi_arr) * (1 + dens_fields.densitycontr_arr)

        box = gadget_data.box
        Delta_HI_plot_arr = np.concatenate((Delta_HI_plot_arr, [Delta_HI_arr[:,:,zgrid].T]), axis = 0)

        z_arr = np.append(z_arr, gadget_data.z)
        QHI_mean_arr = np.append(QHI_mean_arr, np.mean(Delta_HI_arr))

        dens_fields.initialize_powspec()
        if (loop == 0): k_edges, k_bins = dens_fields.set_k_edges(nbins=nbins, log_bins=False)
            

        powspec_21cm_binned_arr, kount_arr = ionmap.get_binned_powspec(Delta_HI_arr, k_edges, units='mK')
        powspec_21cm_binned_arr = k_bins ** 3 * powspec_21cm_binned_arr / (2 * np.pi ** 2)
        powspec_plot_arr =  np.concatenate((powspec_plot_arr, [powspec_21cm_binned_arr]), axis = 0)


    else: ## when we do not find the next snapshot
        break

    loop += 1
    snap += delta_snap

#print ("k bin values: ", k_bins)

num_maps = loop

print ('preparing the movie now...')

fig3 = plt.figure(constrained_layout=True)
gs = fig3.add_gridspec(3, 3)

fig = plt.figure(figsize=(7, 8), constrained_layout=True)
gs = fig.add_gridspec(3, 2)
ax1 = fig.add_subplot(gs[0:2,:])
ax2 = fig.add_subplot(gs[-1,0])
ax3 = fig.add_subplot(gs[-1,1])

vmin = np.min(Delta_HI_plot_arr)
vmax = np.max(Delta_HI_plot_arr)
image = ax1.imshow(Delta_HI_plot_arr[0,:,:], origin='lower', extent=[0, box, 0, box], interpolation='bicubic', vmin=vmin, vmax=vmax, cmap=plt.get_cmap('hot'))
cbar = fig.colorbar(image, ax=ax1)
cbar.set_label(r'$\Delta_{\mathrm{HI}}$')


ax2.set_xlabel(r'$z$')
ax2.set_ylabel(r'$Q_{\mathrm{HI}}$')

ax3.set_xlabel(r'$Q_{\mathrm{HI}}$')
ax3.set_ylabel(r'$\Delta^2_{\mathrm{HI}}(k) \mathrm{mK}^2$')
ax3.set_ylim(np.min(powspec_plot_arr[powspec_plot_arr > 0]), np.max(powspec_plot_arr))
ax3.set_yscale('log')

#fig.tight_layout()



ims = ([])
## The k-value for which the power spectrum will be plotted 
kplot_val = 0.1 ### h/cMpc
kplot_ind = np.argmin(np.abs(k_bins - kplot_val)) ## find the nearest point to the desired k value
for frame in range(num_maps):
    image = ax1.imshow(Delta_HI_plot_arr[frame,:,:], origin='lower', extent=[0, box, 0, box], interpolation='bicubic', vmin=vmin, vmax=vmax, cmap=plt.get_cmap('hot'))
    line_Q, = ax2.plot(z_arr[0:frame], QHI_mean_arr[0:frame], color='red')
    line_P, = ax3.plot(QHI_mean_arr[0:frame][powspec_plot_arr[0:frame, kplot_ind] > 0], powspec_plot_arr[0:frame, kplot_ind][powspec_plot_arr[0:frame, kplot_ind] > 0], color='blue')
    
    title_image = ax1.text(0.6 * box, 0.9 * box, r'$z = ' + '{:04.2f}'.format(z_arr[frame]) + ', Q_{\mathrm{HI}} = ' + '{:04.2f}'.format(QHI_mean_arr[frame]) + '$', bbox=dict(facecolor='white', alpha=0.5))
    text_line_P = ax3.text(0.2, 0.5 * np.max(powspec_plot_arr), r'$z = ' + '{:04.2f}'.format(z_arr[frame]) + ', k = ' + '{:04.2f}'.format(k_bins[kplot_ind]) + 'h / \mathrm{cMpc}$')
    
    ims.append([image, title_image, line_Q, line_P, text_line_P])

frame_rate = 10 ## For a given frame_rate x, the frame-time in ms is 1000/x
animation = ArtistAnimation(fig, ims, interval=1000 / frame_rate)

# Try to set the DPI to the actual number of pixels you are plotting.
# Currently set to a low value.
animation.save("example_2p02_redshift_movie.mp4", dpi=256)

