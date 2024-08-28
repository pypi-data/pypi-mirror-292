###
# This example is included to plot the luminosity function of galaxies from the
# collapsed fraction used to generate the maps.
###


from __future__ import print_function

import numpy as np
import pylab as plt

import script

## Do you have the 2LPT outputs?
use_2LPT = False

if (not use_2LPT):

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

else:
    #######################################
    ## In case you have the 2LPT snapshots ready, you can use the following:
    import configparser
    
    data_path = '/home/tirth/LARGE_DATA_FILES/GADGET-3-DATA/N256_L256.0_MUSIC_2LPT-r1/'
    gadget_snap = data_path + '/snap_038'
    outpath = data_path + '/script_files'  ## directory where the script-related files were stored

    ### read sigma_8, ns and omega_b from the config files
    config = configparser.ConfigParser()
    config.read(data_path + '/music_000.info')
    omega_b = float(config['cosmology']['Omega_b'])
    sigma_8 = float(config['cosmology']['sigma_8'])
    ns = float(config['cosmology']['nspec'])
    default_simulation_data = script.default_simulation_data(gadget_snap, outpath, sigma_8=sigma_8, ns=ns, omega_b=omega_b)

####################################

## Number of grid cells in each direction used for generating the maps.
ngrid = 64
## Class object containing the fields smoothed to the desired resolution.
matter_fields = script.matter_fields(default_simulation_data, ngrid, outpath, overwrite_files=False)
## Class object for ionization maps.
ionization_map = script.ionization_map(matter_fields)

## The values of Mmin and zeta for HI maps.
log10Mmin = 8.0
zeta = 8.0

def zetafunc(M):
    Mcrit = 3.e9
    return zeta * 2.0 ** (- Mcrit / M)

fesc = 0.1
def fescfunc(M):
    return fesc

## luminosity depends on zeta / fesc

M_UV_edges = np.linspace(-10.0, -24.0, 29)
Mmin_arr = matter_fields.Mmin_arr
fcoll_all_Mmin_arr = matter_fields.fcoll_all_Mmin_arr
coeff_spline_arr =  matter_fields.coeff_spline_arr
densitycontr_arr = matter_fields.densitycontr_arr

t_star = 2.e7  ### time-scale of star formation
alpha = -3.0 ### power-law at frequency > Lyman-limit
L_UV_by_L_912 = 2.0 ### luminosity ratio between wavelengths 1600A (UV) and 921A

z = default_simulation_data.z

# M_UV, Phi_UV, Mhalo_UV = matter_fields.get_luminosity_func(M_UV_edges, zeta, fesc, log10Mmin, np.inf, t_star, alpha, L_UV_by_L_912)
# plt.plot(M_UV, np.log10(Phi_UV))

## compute the luminosity function using the scaling relation
M_UV, Phi_UV, Mhalo_UV = default_simulation_data.get_luminosity_func_analytical(M_UV_edges, zetafunc, fesc, log10Mmin, np.inf, t_star, alpha, L_UV_by_L_912)
plt.plot(M_UV, np.log10(Phi_UV))
#print (M_UV)
#print (Mhalo_UV)


## Some data files from high-z surveys have been included in the directory `examples/data_files'.
def read_data(z):

    print ( 'simulation at z = ', z )
    print ( 'using data at z = ', np.round(z) )

    path = './data_files/'
    z_char = "{:.1f}".format( np.round(z) ) ### convert to the nearest redshift where data is available
    z_char = z_char.replace(".", "p")
    filename = path + "UV_lumfun_z" + z_char + ".txt"

    M_UV_data, N_data, N_data_s1, N_data_s2 = np.loadtxt(filename, skiprows=2, unpack=True)
    N_data *= 1.e-3
    N_data_s1 *= 1.e-3
    N_data_s2 *= 1.e-3
    
    N_data_min = N_data + N_data_s1
    N_data_max = N_data + N_data_s2

    N_data = np.where(N_data == 0.0, N_data_max, N_data)
    N_data_min = np.where(N_data_min <= 0.0, 1.e-16, N_data_min)
    
    return M_UV_data, N_data, N_data_min, N_data_max


M_UV_data, N_data, N_data_min, N_data_max = read_data(z)
plt.errorbar(M_UV_data, np.log10(N_data), [np.log10(N_data) - np.log10(N_data_min), np.log10(N_data_max) - np.log10(N_data)], fmt='.', color='black', label=r'data at $z = '+'{:.2f}'.format(np.round(z)) + '$')

mask = N_data_min > 1.e-15
ymin = np.min(N_data_min[mask]) * 1.e-3
ymax = np.max(N_data_max) * 10.0
#print (np.log10(ymin), np.log10(ymax))
plt.ylim(np.log10(ymin), np.log10(ymax))

plt.xlabel(r'$M_{\mathrm{UV}}$')
plt.ylabel(r'$\log [\Phi / \mathrm{Mpc}^{-3}\,\mathrm{mag}^{-1}]$')
plt.title(r'$z = ' + '{:.2f}'.format(z) + '$')
plt.legend(loc='best')

plt.show()
