###
# This example shows how to run MUSIC to generate 2LPT particle positions
# and velocities that are needed for ionization maps.
###


import numpy as np
from script import two_lpt

## The full path to the MUSIC executable.
music_exec = "../music/MUSIC"
## box size
box = 256.0 ### Mpc/h

## Create an array of redshift values where snapshots will be created.
alist = np.linspace(0.0625, 0.1667, num=51) ## equally spaced list of scale factor values between z = 15 and 5
zlist = 1 / alist - 1
#zlist = np.linspace(5.0, 15.0, num=51)


outpath = '/home/tirth/LARGE_DATA_FILES/GADGET-3-DATA/N256_L256.0_MUSIC_2LPT-r1' ## output directory
outroot = 'snap' ## root of the output snapshots
dx = 1. ## the grid resolution in Mpc/h, is also the mean inter-particle distance

## cosmological parameters
omega_m = 0.308
omega_l = 1 - omega_m
omega_b = 0.0482
h = 0.678
sigma_8 = 0.829
ns = 0.961

## random seed
seed = 181170

two_lpt.run_music(music_exec,
                  box,
                  zlist,
                  seed,
                  outpath,
                  outroot,
                  dx,
                  omega_m,
                  omega_l,
                  omega_b,
                  h,
                  sigma_8,
                  ns,
)
