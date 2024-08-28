from __future__ import print_function
import numpy as np
import sys, os
import configparser

def run_music(music_exec, ### full path to the MUSIC executable
              box, ### Mpc/h
              zlist, ### numpy array
              seed,
              outpath, ### output directory
              outroot = 'snap',
              dx = 1.0, ### Mpc/h
              omega_m = 0.308,
              omega_l = 0.692,
              omega_b = 0.0482,
              h = 0.678,
              sigma_8 = 0.829,
              ns = 0.961,
):
    """
    Higher level routine to run the 2LPT code using MUSIC.

    Parameters
    ----------
    music_exec: string
        The full path to the MUSIC executable.
    box: float
        The comoving box length in units of Mpc/h.
    zlist: array
        An array containing the redshifts where outputs are requested.
    seed: int
        The random seed
    outpath: str
        The output directory where the output snapshots would be stored.
    outroot: str, optional
        The root of the output snapshots. Default is ``snap``. The output files will be names as
        `snap_000`, `snap_001`, ...
    dx: float, optional
        The mean inter-particle distance. By default this is also the grid size. Units are Mpc/h.
        If `int(box / dx)` is NOT a power of 2, the `dx` will be adjusted accordingly.
    omega_m: float, optional
        :math:`\Omega_{m}`, the matter density in units of the critical density at z = 0 (includes all
        non-relativistic matter, i.e., dark matter and baryons).
    omega_l: float, optional
        :math:`\Omega_{\Lambda}`, the cosmological constant density in units of the critical density at z = 0.
    h: float, optional
        The Hubble parameter, defined as 100 h km/s/Mpc.
    omega_b: float, optional
        :math:`\Omega_{b}`, the baryon density in units of the critical density at z = 0.
    sigma_8: float, optional
        The normalization of the power spectrum, i.e., the variance when the field is filtered with a top hat
        filter of radius 8 Mpc/h.
    ns: float, optional
        The power-law index of the primordial power spectrum.

    """
    if (not os.path.exists(music_exec)):
        sys.exit("MUSIC executable not found. Terminating.")

    ngrid, nlevel = get_nlevel(box, dx)
    
    zlist = np.sort(zlist)
    zlist = zlist[::-1]

    run_music_commandline(box, zlist, outpath, seed, outroot, nlevel, omega_m, omega_l, omega_b, h, sigma_8, ns, music_exec)

def get_nlevel(box, dx):
    ngrid = round(box / dx)
    if (ngrid & (ngrid - 1) != 0): ##ngrid is NOT a power of two
        ngrid_req = ngrid
        nlevel = round(np.log2(ngrid_req))
        ngrid = int(2 ** nlevel)

        dx_req = dx
        dx = box / ngrid

        print ("requested dx = ",  dx_req, ", using dx = ", dx)

    print ("number of particles = ", ngrid, "^ 3")

    nlevel = int(np.log2(ngrid))
    return ngrid, nlevel

def run_music_commandline(box, zlist, outpath, seed, outroot, nlevel, omega_m, omega_l, omega_b, h, sigma_8, ns, music_exec):

    for loop, z in enumerate(zlist):

        config = configparser.ConfigParser()
        config.optionxform = lambda option: option  ### preserve cases of the keys

        snap_str = '{:03d}'.format(loop)
        info_file = "./music_" + snap_str + ".info"
        log_file = info_file + ".log"
        outfile = outpath + "/" + outroot + "_" + snap_str

        if (nlevel <= 9):
            num_files = 1
        else:
            num_files = int(np.ceil(2.0 ** (3 * (nlevel - 9))))

        print ("running MUSIC for z = ", z, ", output snapshot: ", outfile)
        
        ################

        config['setup'] = {
            "boxlength": box,
            "zstart": z,
            "levelmin": nlevel,
            "levelmax": nlevel,
            "baryons": "no",
            "use_2LPT": "yes",
            "use_LLA": "no",
            "periodic_TF": "yes",
        }


        config['cosmology'] = {
            "Omega_m": omega_m,
            "Omega_L": omega_l,
            "w0": -1.0,
            "wa": 0.0,
            "Omega_b": omega_b,
            "H0": h * 100,
            "sigma_8": sigma_8,
            "nspec": ns,
            "transfer": "eisenstein",
        }

        # if (loop == 0):
        #     random_out = int(seed)
        # else:
        #     random_out = "./wnoise_" + '{:04d}'.format(nlevel) + ".bin"
        random_out = int(seed)
        config['random'] = {
            "seed[" + str(nlevel) + "]": random_out,
        }

        config['output'] = {
            "format": "gadget2",
            "filename": outfile,
            "gadget_lunit": "kpc",
            "gadget_num_files": num_files
        }

        config['poisson'] = {
            "fft_fine": "yes",
            "accuracy": 1e-5,
            "pre_smooth": 3,
            "post_smooth": 3,
            "smoother": "gs",
            "laplace_order": 6,
            "grad_order": 6,
        }

        with open(info_file, 'w') as configfile:
            config.write(configfile)
        

        os.system('stdbuf -o0 ' + music_exec + ' ' + info_file + ' > ' + log_file + ' 2>&1')
        os.system('stdbuf -o0 mv ' + info_file + ' ' + log_file + ' ' + info_file + '_log.txt ' + outpath)

    os.system('stdbuf -o0 mv wnoise_' + '{:04d}'.format(nlevel) + '.bin ' + outpath)
    os.system('stdbuf -o0 mv input_powerspec.txt ' + outpath)
