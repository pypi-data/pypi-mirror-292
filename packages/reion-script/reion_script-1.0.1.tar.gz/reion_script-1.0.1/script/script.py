from __future__ import print_function
import numpy as np
import sys, os

import script_fortran_modules

class cosmo:
    """
    Base class for setting the cosmological parameters.

    Parameters
    ----------
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

    def __init__(self, omega_m=0.3, omega_l=0.7, h=0.7, omega_b=0.048, sigma_8=0.8, ns=0.96, YHe=0.24):
        self.omega_m = omega_m
        self.omega_l = omega_l
        self.h = h
        self.omega_b = omega_b
        self.sigma_8 = sigma_8
        self.ns = ns
        self.YHe = YHe

class default_simulation_data:
    """
    Base class for reading GADGET-2 snapshot file and setting up CIC density and velocity fields.

    Parameters
    ----------
    snapshot_file: str
        Full path to the GADGET-2 snapshot file.
    outpath: str, optional
        The directory where the outputs (e.g., the CIC-smoothed density and velocity fields) would be stored.
    default_density_file: str, optional
        The name of the file where the CIC-smoothed density and velocity fields would be written. The file
        will be created in the `outpath` directory.
    default_fcoll_all_Mmin_file: str, optional
        The name of the file where the halo collapsed fraction fields (calculated using the subgrid
        prescription) would be written. The file will be created in the `outpath` directory.
    scaledist: float, optional
        The scaling applied to convert the GADGET-2 box length and particle positions to Mpc/h units.
        Set scaledist = 1 if the GADGET-2 output was written in Mpc/h units. 
        Set scaledist = 0.001 if the GADGET-2 output was written in kpc/h units.
    default_dx: float, optional
        The grid resolution, in units of Mpc/h, for calculating the CIC density and velocity fields. This grid
        of the density field will also be used to calculate the halo collapsed fraction. The subgrid 
        prescription becomes inaccurate for default_dx < 2 Mpc/h
    omega_b: float, optional
        :math:`\Omega_{b}`, the baryon density in units of the critical density at z = 0. This is required 
        because the GADGET-2 snapshot headers do not contain this parameter.
    sigma_8: float, optional
        The normalization of the power spectrum, i.e., the variance when the field is filtered with a top hat
        filter of radius 8 Mpc/h. This is required because the GADGET-2 snapshot headers do not contain this
        parameter.
    ns: float, optional
        The power-law index of the primordial power spectrum. This is required because the GADGET-2 snapshot
        headers do not contain this parameter.
    get_default_density_velocity_fcoll_all_Mmin: bool, optional
        If ``True``, the CIC density and velocity fields and the subgrid halo collapsed fraction fields will
        be computed during initialization, otherwise postponed for later.
    overwrite_files: bool, optional
        If ``True``, overwrite the files for the gridded fields, otherwise, the gridded fields are read 
        from the files if they exist.
    delete_pos_vel: bool, optional
        If ``True``, delete the GADGET-2 particle positions and velocities. Useful for saving memory.
    verbose_level: integer, optional
        Sets the amount of messages to be printed. Set it to 1 for printing messages.
    """

    def __init__(self, snapshot_file, 
                 outpath='./', 
                 default_density_file=None, 
                 default_fcoll_all_Mmin_file=None, 
                 scaledist=1.e-3, 
                 default_dx=2.0, 
                 omega_b=0.048, 
                 sigma_8=0.8, 
                 ns=0.96, 
                 get_default_density_velocity_fcoll_all_Mmin=False,
                 overwrite_files=False,
                 delete_pos_vel=True,
                 verbose_level=0,
    ):

        self.snapshot_file = snapshot_file
        self.scaledist = scaledist
        npart, box, z, omega_m, omega_l, h = script_fortran_modules.matter_fields.read_gadget_header(snapshot_file, scaledist)
        self.cosmo = cosmo(omega_m, omega_l, h, omega_b, sigma_8, ns)
        self.npart = npart
        self.box = box
        self.z = z
        self.default_dx = default_dx
        self.default_ngrid = int(np.rint(box / default_dx))
        
        self.delete_pos_vel = delete_pos_vel
        self.overwrite_files = overwrite_files
        self.get_default_density_velocity_fcoll_all_Mmin = get_default_density_velocity_fcoll_all_Mmin

        self.verbose_level = verbose_level

        ######################

        #print (self.default_ngrid)

        if not os.path.exists(outpath): os.makedirs(outpath)
        self.outpath = outpath

        self.default_density_file = default_density_file
        self.default_fcoll_all_Mmin_file = default_fcoll_all_Mmin_file

        if (get_default_density_velocity_fcoll_all_Mmin):
            self.get_density_velocity_fields()
            self.get_fcoll_all_Mmin_fields()
        else:
            self.default_densitycontr_arr = None
            self.default_velocity_arr = None
            
            self.nMmin = None
            self.Mmin_arr = None
            self.default_fcoll_all_Mmin_arr = None


    def get_density_velocity_fields(self):
        """
        Compute the CIC-smoothed density and velocity fields and write to the files. 
        If `overwrite_files` is ``True`` and the files exist, then simply reads the data.
        """

        if (self.default_density_file is None): self.default_density_file = self.outpath + '/default_density_velocity_ngrid' + '{:04d}'.format(self.default_ngrid) + '_z' + '{:06.2f}'.format(self.z)

        if (os.path.exists(self.default_density_file) and not self.overwrite_files):
            self.default_densitycontr_arr, self.default_velocity_arr, _, _, _, _, _ = script_fortran_modules.matter_fields.read_density_contrast_velocity(self.default_density_file, self.default_ngrid)
            if (self.verbose_level > 0): print ('Done reading default density + velocity file: ', self.default_density_file)
        
        else:
            self.pos, self.vel = script_fortran_modules.matter_fields.read_gadget_dm_pos_vel(self.snapshot_file, self.npart, self.scaledist)
            if (self.verbose_level > 0): print ('Done reading GADGET snapshot file: ', self.snapshot_file)

            self.default_densitycontr_arr, self.default_velocity_arr = script_fortran_modules.matter_fields.smooth_density_velocity_cic(self.pos, self.vel, self.box, self.default_ngrid)

            if (self.delete_pos_vel): 
                del self.pos
                del self.vel
            delta_mean = np.mean(self.default_densitycontr_arr, dtype=np.float64)
            self.default_densitycontr_arr = self.default_densitycontr_arr / delta_mean - 1
            script_fortran_modules.matter_fields.write_density_velocity(self.default_density_file, 
                                                                        self.default_densitycontr_arr, 
                                                                        self.default_velocity_arr, 
                                                                        self.box, 
                                                                        self.z, 
                                                                        self.cosmo.omega_m, 
                                                                        self.cosmo.omega_l, 
                                                                        self.cosmo.h)
            if (self.verbose_level > 0): print ('Generated CIC default density + velocity fields, output: ', self.default_density_file)

    def get_fcoll_all_Mmin_fields(self):
        """
        Compute the subgrid halo collapse fraction field and write to the files. 
        If `overwrite_files` is ``True`` and the file exists, then simply reads the data.
        """

        if (self.default_fcoll_all_Mmin_file is None): self.default_fcoll_all_Mmin_file = self.outpath + '/default_fcollfield_nofluc_ngrid' + '{:04d}'.format(self.default_ngrid) + '_z' + '{:06.2f}'.format(self.z)


        if (os.path.exists(self.default_fcoll_all_Mmin_file) and not self.overwrite_files):
            self.nMmin = script_fortran_modules.matter_fields.mmin_array_size(self.default_fcoll_all_Mmin_file)
            self.Mmin_arr, self.default_fcoll_all_Mmin_arr, _, _, _, _, _, self.cosmo.sigma_8, self.cosmo.ns, self.cosmo.omega_b = script_fortran_modules.matter_fields.read_fcoll(self.default_fcoll_all_Mmin_file, self.default_ngrid, self.nMmin)
            if (self.verbose_level > 0): print ('Done reading default fcoll file for all Mmin: ', self.default_fcoll_all_Mmin_file)
        
        else:
            self.Mmin_arr, self.default_fcoll_all_Mmin_arr = script_fortran_modules.matter_fields.fcoll_nofluc(self.default_densitycontr_arr, self.box, self.z, self.cosmo.omega_m, self.cosmo.omega_l, self.cosmo.h, self.cosmo.sigma_8, self.cosmo.ns, self.cosmo.omega_b)

            self.nMmin = len(self.Mmin_arr)
            script_fortran_modules.matter_fields.write_fcoll_all_mmin(self.default_fcoll_all_Mmin_file, self.Mmin_arr, self.default_fcoll_all_Mmin_arr, self.box, self.z, self.cosmo.omega_m, self.cosmo.omega_l, self.cosmo.h, self.cosmo.sigma_8, self.cosmo.ns, self.cosmo.omega_b)
            if (self.verbose_level > 0): print ('Generated subgrid fcoll fields for all Mmin, output: ', self.default_fcoll_all_Mmin_file)
        

    def get_luminosity_func_analytical(self, M_UV_edges, zeta, fesc, log10Mmin=-np.inf, log10Mmax=np.inf, t_star=1.e7, alpha=-3.0, L_UV_by_L_912=2.0):
            
        def zetafunc(M):
            res = zeta(M) if (callable(zeta)) else zeta
            return res

        def fescfunc(M):
            res = fesc(M) if (callable(fesc)) else fesc
            return res

        def zeta_by_fesc_func(M):
            fesc = fescfunc(M)
            res = zetafunc(M) / fesc if (fesc > 0) else 0.0
            return res
            
        M_UV, Phi_UV, Mhalo_UV = script_fortran_modules.ionization_map.get_luminosity_func_analytical(M_UV_edges, zeta_by_fesc_func, 10 ** log10Mmin, 10 ** log10Mmax, t_star, alpha, L_UV_by_L_912, self.z, self.cosmo.omega_m, self.cosmo.omega_l, self.cosmo.omega_b, self.cosmo.h, self.cosmo.YHe, self.cosmo.sigma_8, self.cosmo.ns)
        return M_UV, Phi_UV, Mhalo_UV

class matter_fields:
    """
    Base class for setting up density, velocity and halo collapsed fraction fields on a uniform grid
    for computing ionization fields.

    Parameters
    ----------
    default_simulation_data: object
        The default_simulation_data class object.
    ngrid: int
        The number of grid cells along each direction. The total number of grids would be ngrid^3.
    outpath: str, optional
        The directory where the outputs (e.g., the CIC-smoothed density and velocity fields) would be stored.
    density_file: str, optional
        The name of the file where the gridded density and velocity fields would be written. The file
        will be created in the `outpath` directory.
    fcoll_all_Mmin_file: str, optional
        The name of the file where the halo collapsed fraction fields (calculated using the subgrid
        prescription) would be written. The file will be created in the `outpath` directory.
    overwrite_files: bool, optional
        If ``True``, overwrite the files for the gridded fields, otherwise, the gridded fields are read 
        from the files if they exist.
    verbose_level: integer, optional
        Sets the amount of messages to be printed. Set it to 1 for printing messages.
    """

    def __init__(self, default_simulation_data, ngrid, 
                 outpath='./', 
                 density_file=None, 
                 fcoll_all_Mmin_file=None, 
                 overwrite_files=False,
                 verbose_level=0,):
        
        self.default_simulation_data = default_simulation_data
        self.ngrid = ngrid
        self.verbose_level = verbose_level

        self.outpath = outpath
        if (density_file is None): density_file = outpath + '/density_velocity_ngrid' + '{:04d}'.format(ngrid) + '_z' + '{:06.2f}'.format(default_simulation_data.z)
        if (fcoll_all_Mmin_file is None): fcoll_all_Mmin_file = outpath + '/fcollfield_nofluc_ngrid' + '{:04d}'.format(ngrid) + '_z' + '{:06.2f}'.format(default_simulation_data.z)

        self.density_file = density_file
        self.fcoll_all_Mmin_file = fcoll_all_Mmin_file

        if (os.path.exists(density_file) and not overwrite_files):
            self.densitycontr_arr, self.velocity_arr, self.box, self.z, _, _, _ = script_fortran_modules.matter_fields.read_density_contrast_velocity(density_file, ngrid)
            if (self.verbose_level > 0): print ('Done reading density + velocity file: ', density_file)
        else:
            if ( (default_simulation_data.default_densitycontr_arr is None) or (default_simulation_data.default_velocity_arr is None) ):
                default_simulation_data.get_density_velocity_fields()
                
            self.densitycontr_arr = script_fortran_modules.matter_fields.smooth_field_cic(default_simulation_data.default_densitycontr_arr, default_simulation_data.box, ngrid, average=True)

            self.velocity_arr = np.zeros([3, ngrid, ngrid, ngrid])
            for i in range(3):
                self.velocity_arr[i, :,:,:] = script_fortran_modules.matter_fields.smooth_field_cic(default_simulation_data.default_velocity_arr[i, :,:,:], default_simulation_data.box, ngrid, average=True)

            script_fortran_modules.matter_fields.write_density_velocity(density_file, 
                                                                        self.densitycontr_arr, 
                                                                        self.velocity_arr, 
                                                                        default_simulation_data.box, 
                                                                        default_simulation_data.z, 
                                                                        default_simulation_data.cosmo.omega_m, 
                                                                        default_simulation_data.cosmo.omega_l, 
                                                                        default_simulation_data.cosmo.h)
            if (self.verbose_level > 0): print ('Generated CIC-smoothed density + velocity fields, output: ', density_file)

        if (os.path.exists(fcoll_all_Mmin_file) and not overwrite_files):
            self.nMmin = script_fortran_modules.matter_fields.mmin_array_size(fcoll_all_Mmin_file)
            self.Mmin_arr, self.fcoll_all_Mmin_arr, _, _, _, _, _, _, _, _ = script_fortran_modules.matter_fields.read_fcoll(fcoll_all_Mmin_file, ngrid, self.nMmin)
            if (self.verbose_level > 0): print ('Done reading fcoll file for all Mmin: ', fcoll_all_Mmin_file)
        else:
            if ( (default_simulation_data.nMmin is None) or (default_simulation_data.Mmin_arr is None) or (default_simulation_data.default_fcoll_all_Mmin_arr is None) ):
                if ( (default_simulation_data.default_densitycontr_arr is None) or (default_simulation_data.default_velocity_arr is None) ):
                    default_simulation_data.get_density_velocity_fields()
                default_simulation_data.get_fcoll_all_Mmin_fields()


            self.nMmin = default_simulation_data.nMmin
            self.Mmin_arr = default_simulation_data.Mmin_arr
            self.fcoll_all_Mmin_arr = np.zeros([ngrid, ngrid, ngrid, self.nMmin])
            for i in range(self.nMmin):
                fcoll_arr = default_simulation_data.default_fcoll_all_Mmin_arr[:,:,:, i] * (1 + default_simulation_data.default_densitycontr_arr[:,:,:])
                fcoll_smooth_arr = script_fortran_modules.matter_fields.smooth_field_cic(fcoll_arr, default_simulation_data.box, ngrid, average=True)
                self.fcoll_all_Mmin_arr[:,:,:, i] = fcoll_smooth_arr / (1 + self.densitycontr_arr)


            script_fortran_modules.matter_fields.write_fcoll_all_mmin(fcoll_all_Mmin_file, 
                                                                      self.Mmin_arr, 
                                                                      self.fcoll_all_Mmin_arr, 
                                                                      default_simulation_data.box, 
                                                                      default_simulation_data.z, 
                                                                      default_simulation_data.cosmo.omega_m, 
                                                                      default_simulation_data.cosmo.omega_l, 
                                                                      default_simulation_data.cosmo.h, 
                                                                      default_simulation_data.cosmo.sigma_8, 
                                                                      default_simulation_data.cosmo.ns, 
                                                                      default_simulation_data.cosmo.omega_b)
            if (self.verbose_level > 0): print ('Generated CIC-smoothed fcoll fields for all Mmin, output:', fcoll_all_Mmin_file)


        self.coeff_spline_arr = script_fortran_modules.matter_fields.set_fcoll_field_spline(self.Mmin_arr, self.fcoll_all_Mmin_arr)


    def get_fcoll_for_Mmin(self, log10Mmin):
        """
        Compute collapsed fraction on a grid for a given Mmin.

        Parameters
        ----------
        log10Mmin: float
            log10 of Mmin in units of M_sun.
        
        Returns
        -------
        fcoll_arr: array of dtype float
            The collapsed fraction calculated in each grid cell. Has dimensions (ngrid, ngrid, ngrid).
        """

        fcoll_arr = script_fortran_modules.matter_fields.fcoll_one_mmin_spline(log10Mmin, self.Mmin_arr, self.fcoll_all_Mmin_arr, self.coeff_spline_arr)
        return fcoll_arr

    def get_zeta_fcoll(self, zeta, log10Mmin=-np.inf, log10Mmax=np.inf, dlog10M=0.1):
        """
        Compute ionizing photon field on a grid for a given zeta(M).

        Parameters
        ----------
        zeta: either a float or a function
            If float, it represents the value of zeta independent of halo mass.
            If function, it gives the mass-dependence zeta(M), where M is in units of M_sun. 
        log10Mmin: float, optional
            The log10 of minimum halo mass that produces ionizing photons.
        log10Mmax: float, optional
            The log10 of maximum halo mass that produces ionizing photons.
        dlog10M: float, optional
            The bin size in log10(M) used while evaluating the M-integral

        Returns
        -------
        zeta_fcoll_arr: array of dtype float
            The collapsed fraction calculated in each grid cell. Has dimensions (ngrid, ngrid, ngrid).
        """

        if (callable(zeta)):
            zeta_fcoll_arr = script_fortran_modules.matter_fields.zeta_fcoll_spline(zeta, 10 ** log10Mmin, 10 ** log10Mmax, dlog10M, self.Mmin_arr, self.fcoll_all_Mmin_arr, self.coeff_spline_arr)
        else:
            log10Mmin = max(log10Mmin, np.log10(self.Mmin_arr[0]))
            zeta_fcoll_arr = zeta * script_fortran_modules.matter_fields.fcoll_one_mmin_spline(log10Mmin, self.Mmin_arr, self.fcoll_all_Mmin_arr, self.coeff_spline_arr)
 
        return zeta_fcoll_arr

    def initialize_powspec(self):
        """
        Initializes plans and computes various quantities related to FFTW for calculating Fourier transforms. Required for calculating power spectrum.
        """

        FFTW_ESTIMATE = 64
        FFTW_IFINV = 1
        self.plan, self.kfft = script_fortran_modules.powspec.initialize_plan(self.ngrid, FFTW_IFINV, FFTW_ESTIMATE, self.default_simulation_data.box)
        self.kmag = script_fortran_modules.powspec.get_kmag(self.kfft)


    def set_k_edges(self, nbins=0, kmin=None, kmax=None, log_bins=False):
        """
        Set the k-bins for power spectrum.

        Parameters
        ----------
        nbins: int, optional
            The number of bins. If 0, it is calculated using the box size and number of grids.
        kmin: float, optional
            The minimum k value. If `None`, it is set to 2 * pi / box.
        kmax: float, optional
            The maximum k value. If `None`, it is set to pi * ngrid / box.
        log_bins: bool, optional
            If `True`, the bins are logarithmically spaced.
        
        Returns
        -------
        k_edges: array of dtype float
            The bin edges for k. Has dimensions ``nbins + 1``
        k_bins: array of dtype float
            The central bin values for k.
        """



        if (kmin is None): kmin = 2 * np.pi / self.default_simulation_data.box
        if (kmax is None): kmax = np.pi * self.ngrid / self.default_simulation_data.box

        if (kmax <= kmin): sys.exit('set_k_bins: kmax is less than kmin')

        if (log_bins):
            if (nbins < 2):
                dlnk = 0.1
                nbins = int( (np.log(kmax) - np.log(kmin)) / dlnk )
            else:
                dlnk = (np.log(kmax) - np.log(kmin)) / (nbins)
            lnk_edges = np.linspace(np.log(kmin), np.log(kmax), num=nbins+1, endpoint=True)
            lnk_bins = (lnk_edges[:-1] + lnk_edges[1:]) / 2
            k_edges = np.exp(lnk_edges)
            k_bins = np.exp(lnk_bins)
        else:
            if (nbins < 2):
                dk = kmin
                nbins = int(self.ngrid / 2) - 1
            else:
                dk = (kmax - kmin) / (nbins)
            k_edges = np.linspace(kmin, kmax, num=nbins+1, endpoint=True)
            k_bins = (k_edges[:-1] + k_edges[1:]) / 2

        return k_edges, k_bins

    def get_luminosity_func(self, M_UV_edges, zeta, fesc, log10Mmin=-np.inf, log10Mmax=np.inf, t_star=1.e7, alpha=-3.0, L_UV_by_L_912=2.0):
            
        def zetafunc(M):
            res = zeta(M) if (callable(zeta)) else zeta
            return res

        def fescfunc(M):
            res = fesc(M) if (callable(fesc)) else fesc
            return res

        def zeta_by_fesc_func(M):
            fesc = fescfunc(M)
            res = zetafunc(M) / fesc if (fesc > 0) else 0.0
            return res
            
        M_UV, Phi_UV, Mhalo_UV = script_fortran_modules.ionization_map.get_luminosity_func(M_UV_edges, self.Mmin_arr, self.fcoll_all_Mmin_arr, self.coeff_spline_arr, self.densitycontr_arr, zeta_by_fesc_func, 10 ** log10Mmin, 10 ** log10Mmax, t_star, alpha, L_UV_by_L_912, self.default_simulation_data.cosmo.omega_m, self.default_simulation_data.cosmo.omega_b, self.default_simulation_data.cosmo.h, self.default_simulation_data.cosmo.YHe)

        return M_UV, Phi_UV, Mhalo_UV


class matter_fields_haloes:
    """
    Base class for setting up density, velocity and halo collapsed fraction fields on a uniform grid
    for computing ionization fields.

    Parameters
    ----------
    default_simulation_data: object
        The default_simulation_data class object.
    ngrid: int
        The number of grid cells along each direction. The total number of grids would be ngrid^3.
    halo_catalogue_file: str
        Full path to the halo catalogue file (in GADGET format) 
    outpath: str, optional
        The directory where the outputs (e.g., the CIC-smoothed density and velocity fields) would be stored.
    density_file: str, optional
        The name of the file where the gridded density and velocity fields would be written. The file
        will be created in the `outpath` directory.
    overwrite_files: bool, optional
        If ``True``, overwrite the files for the gridded fields, otherwise, the gridded fields are read 
        from the files if they exist.
    verbose_level: integer, optional
        Sets the amount of messages to be printed. Set it to 1 for printing messages.
    """

    def __init__(self, default_simulation_data, ngrid, 
                 halo_catalogue_file,
                 outpath='./', 
                 density_file=None, 
                 overwrite_files=False,
                 verbose_level=0,):
        
        self.default_simulation_data = default_simulation_data
        self.ngrid = ngrid
        self.halo_catalogue_file = halo_catalogue_file
        self.verbose_level = verbose_level

        self.outpath = outpath
        if (density_file is None): density_file = outpath + '/density_velocity_ngrid' + '{:04d}'.format(ngrid) + '_z' + '{:06.2f}'.format(default_simulation_data.z)

        self.density_file = density_file

        if (os.path.exists(density_file) and not overwrite_files):
            self.densitycontr_arr, self.velocity_arr, self.box, self.z, _, _, _ = script_fortran_modules.matter_fields.read_density_contrast_velocity(density_file, ngrid)
            if (self.verbose_level > 0): print ('Done reading density + velocity file: ', density_file)
        else:
            if ( (default_simulation_data.default_densitycontr_arr is None) or (default_simulation_data.default_velocity_arr is None) ):
                default_simulation_data.get_density_velocity_fields()
                
            self.densitycontr_arr = script_fortran_modules.matter_fields.smooth_field_cic(default_simulation_data.default_densitycontr_arr, default_simulation_data.box, ngrid, average=True)

            self.velocity_arr = np.zeros([3, ngrid, ngrid, ngrid])
            for i in range(3):
                self.velocity_arr[i, :,:,:] = script_fortran_modules.matter_fields.smooth_field_cic(default_simulation_data.default_velocity_arr[i, :,:,:], default_simulation_data.box, ngrid, average=True)

            script_fortran_modules.matter_fields.write_density_velocity(density_file, 
                                                                        self.densitycontr_arr, 
                                                                        self.velocity_arr, 
                                                                        default_simulation_data.box, 
                                                                        default_simulation_data.z, 
                                                                        default_simulation_data.cosmo.omega_m, 
                                                                        default_simulation_data.cosmo.omega_l, 
                                                                        default_simulation_data.cosmo.h)
            if (self.verbose_level > 0): print ('Generated CIC-smoothed density + velocity fields, output: ', density_file)

 

        self.nhalo = script_fortran_modules.matter_fields_haloes.read_gadget_halo_header(halo_catalogue_file)
        if (self.nhalo <= 0):
            print ('WARNING: No halo found. Setting single halo of mass 1e-32 at (box/2, box/2, box/2)')
            ### To ensure that the subsequent part of the code does not break.
            self.nhalo = 1
            self.nparthalo_arr = np.array([1], dtype=int)
            self.mhalo_arr = np.array([1.e-32])
            self.xhalo_arr = np.array([[default_simulation_data.box / 2], [default_simulation_data.box / 2], [default_simulation_data.box / 2]])
            self.m_DM = 1.e-32
        else:
            self.nparthalo_arr, self.mhalo_arr, self.xhalo_arr =  script_fortran_modules.matter_fields_haloes.read_gadget_halo_catalogue(halo_catalogue_file, self.nhalo, default_simulation_data.scaledist)
            self.m_DM = self.mhalo_arr[0] / self.nparthalo_arr[0]  ## Msun / h

            
    def get_fcoll_for_Mmin(self, log10Mmin):
        """
        Compute collapsed fraction on a grid for a given Mmin.

        Parameters
        ----------
        log10Mmin: float
            log10 of Mmin in units of M_sun.
        
        Returns
        -------
        fcoll_arr: array of dtype float
            The collapsed fraction calculated in each grid cell. Has dimensions (ngrid, ngrid, ngrid).
        """

        # mhalo_arr is in units of Msun / h
        mask_halo = np.log10(self.mhalo_arr / self.default_simulation_data.cosmo.h) >= log10Mmin

        # check for zero sized array
        if (len(self.mhalo_arr[mask_halo]) == 0):
            return np.zeros_like(self.densitycontr_arr)

        halo_density_field_arr = script_fortran_modules.matter_fields_haloes.smooth_halo_field_cic(self.xhalo_arr[:,mask_halo], self.mhalo_arr[mask_halo], self.default_simulation_data.box, self.ngrid) ### Msun / h
        total_density_field_arr = (1 + self.densitycontr_arr) * self.m_DM * self.default_simulation_data.npart / self.ngrid ** 3 ## Msun / h
        fcoll_arr = halo_density_field_arr / total_density_field_arr

        return fcoll_arr

    def get_zeta_fcoll(self, zeta, log10Mmin=-np.inf, log10Mmax=np.inf):
        """
        Compute ionizing photon field on a grid for a given zeta(M).

        Parameters
        ----------
        zeta: either a float or a function
            If float, it represents the value of zeta independent of halo mass.
            If function, it gives the mass-dependence zeta(M), where M is in units of M_sun. 
        log10Mmin: float, optional
            The log10 of minimum halo mass that produces ionizing photons.
        log10Mmax: float, optional
            The log10 of maximum halo mass that produces ionizing photons.

        Returns
        -------
        zeta_fcoll_arr: array of dtype float
            The collapsed fraction calculated in each grid cell. Has dimensions (ngrid, ngrid, ngrid).
        """

        # mhalo_arr is in units of Msun / h
        log10mhalo_arr = np.log10(self.mhalo_arr / self.default_simulation_data.cosmo.h)
        mask_halo = np.logical_and(log10mhalo_arr >= log10Mmin, log10mhalo_arr <= log10Mmax)
        if (len(self.mhalo_arr[mask_halo]) == 0):
            return np.zeros_like(self.densitycontr_arr)

        if (callable(zeta)):
            zeta_halo_density_field_arr = script_fortran_modules.matter_fields_haloes.smooth_halo_field_cic(self.xhalo_arr[:,mask_halo], zeta(self.mhalo_arr[mask_halo] / self.default_simulation_data.cosmo.h) * self.mhalo_arr[mask_halo], self.default_simulation_data.box, self.ngrid) ### Msun / h
        else:
            zeta_halo_density_field_arr = zeta * script_fortran_modules.matter_fields_haloes.smooth_halo_field_cic(self.xhalo_arr[:,mask_halo], self.mhalo_arr[mask_halo], self.default_simulation_data.box, self.ngrid) ### Msun / h
            
        total_density_field_arr = (1 + self.densitycontr_arr) * self.m_DM * self.default_simulation_data.npart / self.ngrid ** 3 ## Msun / h
        zeta_fcoll_arr = zeta_halo_density_field_arr / total_density_field_arr
 
        return zeta_fcoll_arr

    def initialize_powspec(self):
        """
        Initializes plans and computes various quantities related to FFTW for calculating Fourier transforms. Required for calculating power spectrum.
        """

        FFTW_ESTIMATE = 64
        FFTW_IFINV = 1
        self.plan, self.kfft = script_fortran_modules.powspec.initialize_plan(self.ngrid, FFTW_IFINV, FFTW_ESTIMATE, self.default_simulation_data.box)
        self.kmag = script_fortran_modules.powspec.get_kmag(self.kfft)


    def set_k_edges(self, nbins=0, kmin=None, kmax=None, log_bins=False):
        """
        Set the k-bins for power spectrum.

        Parameters
        ----------
        nbins: int, optional
            The number of bins. If 0, it is calculated using the box size and number of grids.
        kmin: float, optional
            The minimum k value. If `None`, it is set to 2 * pi / box.
        kmax: float, optional
            The maximum k value. If `None`, it is set to pi * ngrid / box.
        log_bins: bool, optional
            If `True`, the bins are logarithmically spaced.
        
        Returns
        -------
        k_edges: array of dtype float
            The bin edges for k. Has dimensions ``nbins + 1``
        k_bins: array of dtype float
            The central bin values for k.
        """



        if (kmin is None): kmin = 2 * np.pi / self.default_simulation_data.box
        if (kmax is None): kmax = np.pi * self.ngrid / self.default_simulation_data.box

        if (kmax <= kmin): sys.exit('set_k_bins: kmax is less than kmin')

        if (log_bins):
            if (nbins < 2):
                dlnk = 0.1
                nbins = int( (np.log(kmax) - np.log(kmin)) / dlnk )
            else:
                dlnk = (np.log(kmax) - np.log(kmin)) / (nbins)
            lnk_edges = np.linspace(np.log(kmin), np.log(kmax), num=nbins+1, endpoint=True)
            lnk_bins = (lnk_edges[:-1] + lnk_edges[1:]) / 2
            k_edges = np.exp(lnk_edges)
            k_bins = np.exp(lnk_bins)
        else:
            if (nbins < 2):
                dk = kmin
                nbins = int(self.ngrid / 2) - 1
            else:
                dk = (kmax - kmin) / (nbins)
            k_edges = np.linspace(kmin, kmax, num=nbins+1, endpoint=True)
            k_bins = (k_edges[:-1] + k_edges[1:]) / 2

        return k_edges, k_bins


    # def get_luminosity_func(self, M_UV_edges, zeta, fesc, log10Mmin=-np.inf, log10Mmax=np.inf, t_star=1.e7, alpha=-3.0, L_UV_by_L_912=2.0):
            
    #     def zetafunc(M):
    #         res = zeta(M) if (callable(zeta)) else zeta
    #         return res

    #     def fescfunc(M):
    #         res = fesc(M) if (callable(fesc)) else fesc
    #         return res

    #     def zeta_by_fesc_func(M):
    #         fesc = fescfunc(M)
    #         res = zetafunc(M) / fesc if (fesc > 0) else 0.0
    #         return res
            
    #     M_UV, Phi_UV, Mhalo_UV = script_fortran_modules.ionization_map.get_luminosity_func(M_UV_edges, self.Mmin_arr, self.fcoll_all_Mmin_arr, self.coeff_spline_arr, self.densitycontr_arr, zeta_by_fesc_func, 10 ** log10Mmin, 10 ** log10Mmax, t_star, alpha, L_UV_by_L_912, self.default_simulation_data.cosmo.omega_m, self.default_simulation_data.cosmo.omega_b, self.default_simulation_data.cosmo.h, self.default_simulation_data.cosmo.YHe)

    # Nphot = zeta_correc * DBLE(zeta_by_fesc_func(Mhalo) * Mhalo)
    # L_UV = - Nphot / L_UV_to_Nphot_fac
    # M_UV = 51.6 - log10(L_UV) / 0.4


    #     return M_UV, Phi_UV, Mhalo_UV


class ionization_map:
    """
    Base class for computing ionization fields.

    Parameters
    ----------
    matter_fields: object, optional
        The matter_fields class object. If None, then the other relevant variables must be present.
    densitycontr_arr: array of dtype float, optional
            The density contrast array. Has dimensions (ngrid, ngrid, ngrid). Must be present if matter_fields is None.
    velocity_arr: array of dtype float, optional
            The velocity array. Has dimensions (3, ngrid, ngrid, ngrid).
    box: float, optional
            The box size in cMpc/h. Must be present if matter_fields is None.
    z: float, optional
            Redshift. Must be present if matter_fields is None.
    omega_m: float, optional
            The matter density parameter. Must be present if matter_fields is None.
    omega_l: float, optional
            The cosmological constant parameter.
    h: float, optional
            The Hubble constant in units of 100 km/s/Mpc. Must be present if matter_fields is None.
    method: str, optional
        If ``PC``, use the photon-conserving algorithm (default). If ``ES``, use the excursion-set algorithm.
    ES_filter: str, optional
        The smoothing filter for the excursion-set fields. Possible values are ``sharp-k`` and ``STH``.
    """
    
    def __init__(self, matter_fields=None, densitycontr_arr=None, velocity_arr=None, box=None, z=None, omega_m=None, omega_l=None, h=None, method='PC', ES_filter='sharp-k'):

        self.method = method
        self.matter_fields = matter_fields
        if (matter_fields is not None):

            self.ngrid = matter_fields.ngrid
            self.omega_m = matter_fields.default_simulation_data.cosmo.omega_m
            self.omega_l = matter_fields.default_simulation_data.cosmo.omega_l
            self.h = matter_fields.default_simulation_data.cosmo.h
            self.z = matter_fields.default_simulation_data.z
            self.box = matter_fields.default_simulation_data.box

            self.densitycontr_arr = matter_fields.densitycontr_arr
            self.velocity_arr = matter_fields.velocity_arr
            
        else:
            args_necessary = (densitycontr_arr, box, z, omega_m, h)
            if any(arg is None for arg in args_necessary): sys.exit('class ionization_map: pass either matter_fields class or the necessary variables')

            self.ngrid = np.shape(densitycontr_arr)[0]
            self.omega_m = omega_m
            self.omega_l = omega_l if (omega_l is not None) else 1 - omega_m
            self.h = h
            self.z = z
            self.box = box

            self.densitycontr_arr = densitycontr_arr
            self.velocity_arr = velocity_arr if (velocity_arr is not None) else np.zeros([3, self.ngrid, self.ngrid, self.ngrid])

 
            
        if (method == 'PC'): 
            self.method_flag = 0
            self.i_x, self.i_y, self.i_z, self.dgnrcy, self.ordr, self.Tbarsq = script_fortran_modules.ionization_map.initialize_ionization_map_pc( (self.ngrid) ** 3, self.omega_m, self.h, self.z)

        elif (method == 'ES'):
            self.method_flag = 1
            self.ES_filter = ES_filter
            self.plan_bwd, self.plan_fwd, self.kpow, self.kmag, self.Tbarsq = script_fortran_modules.ionization_map.initialize_ionization_map_es( self.ngrid, self.omega_m, self.h, self.z)

            if (ES_filter == 'sharp-k'):
                self.ES_filter_flag = 1
            elif (ES_filter == 'STH'):
                self.ES_filter_flag = 0
            else:
                sys.exit ('ionization map: ES_filter not recognized')
        else:
            sys.exit ('ionization map: method not recognized')

    def get_qi(self, zeta_times_fcoll_arr):
        """
        Compute ionized hydrogen fraction on a grid.

        Parameters
        ----------
        zeta_times_fcoll_arr: array of dtype float
            The zeta * collapsed fraction array. Has dimensions (ngrid, ngrid, ngrid).
        
        Returns
        -------
        qi_arr: array of dtype float
            The ionized fraction calculated in each grid cell. Has dimensions (ngrid, ngrid, ngrid).
        """

        if (self.method_flag == 0):
            qi_arr = script_fortran_modules.ionization_map.get_ion_map_pc(zeta_times_fcoll_arr, 
                                                                          self.densitycontr_arr, 
                                                                          self.i_x, 
                                                                          self.i_y, 
                                                                          self.i_z, 
                                                                          self.dgnrcy, 
                                                                          self.ordr)
        elif (self.method_flag == 1):
            qi_arr = script_fortran_modules.ionization_map.get_ion_map_es(zeta_times_fcoll_arr, 
                                                                          self.densitycontr_arr, 
                                                                          self.plan_bwd, 
                                                                          self.plan_fwd, 
                                                                          self.kmag, 
                                                                          self.ES_filter_flag)



        return qi_arr

    def add_rsd_box(self, qi_arr, subgrid_num=50):
        """
        Adds redshift space distortions to an existing HI density field based on
        Jensen at al, MNRAS, 435, 460 (2013).

        Parameters
        ----------
        qi_arr: array of dtype float
            The ionized fraction in each grid cell. Has dimensions (ngrid, ngrid, ngrid).
        subgrid_num: int, optional
            The number of sub-cells.
        
        Returns
        -------
        Delta_HI_rsd_arr: array of dtype float
            The HI density field `xHI * (1 + delta)` calculated in each grid cell with redshift space effects
            included. Has dimensions (ngrid, ngrid, ngrid).
        """

        Delta_HI_arr = (1 - qi_arr) * (1 + self.densitycontr_arr)

        Delta_HI_rsd_arr = script_fortran_modules.ionization_map.add_rsd_box(Delta_HI_arr, 
                                                                         self.velocity_arr, 
                                                                         subgrid_num, 
                                                                         self.box, 
                                                                         self.z, 
                                                                         self.omega_m, 
                                                                         self.omega_l)

        return  Delta_HI_rsd_arr

    def compute_HI_powspec(self, Delta_HI_arr, convolve=False):
        """
        Computes the HI power spectrum.

        Parameters
        ----------
        Delta_HI_arr: array of dtype float
            The HI density field `xHI * (1 + delta)` at each grid cell. Has dimensions (ngrid, ngrid, ngrid).
        concolve: bool, optional
            If `True`, de-convolve the power spectrum using an appropriate smoothing kernel.
        
        Returns
        -------
        powspec_HI_arr: array of dtype float
            The HI power spectrum calculated in each grid cell in the k-space.
            Has dimensions (ngrid, ngrid, ngrid).
        """

        Delta_mean = np.mean(Delta_HI_arr, dtype=np.float64)
        input_arr = Delta_HI_arr - Delta_mean
        if (self.matter_fields is not None):
            self.plan_fft = self.matter_fields.plan
            self.kmag_fft = self.matter_fields.kmag
        else:
            FFTW_ESTIMATE = 64
            FFTW_IFINV = 1
            self.plan_fft, self.kfft = script_fortran_modules.powspec.initialize_plan(ngrid, FFTW_IFINV, FFTW_ESTIMATE, box)
            self.kmag_fft = script_fortran_modules.powspec.get_kmag(kfft)

        powspec_HI_arr = script_fortran_modules.powspec.compute_powspec(self.plan_fft, input_arr, self.box, convolve)
        return powspec_HI_arr


    def compute_21cm_powspec(self, Delta_HI_arr, convolve=False):
        """
        Computes the 21 cm power spectrum.

        Parameters
        ----------
        Delta_HI_arr: array of dtype float
            The HI density field `xHI * (1 + delta)` at each grid cell. Has dimensions (ngrid, ngrid, ngrid).
        concolve: bool, optional
            If `True`, de-convolve the power spectrum using an appropriate smoothing kernel.
        
        Returns
        -------
        powspec_HI_arr: array of dtype float
            The 21 cm power spectrum calculated in each grid cell in the k-space. It has units of K^2.
            Has dimensions (ngrid, ngrid, ngrid).
        """

        powspec_21cm_arr = self.compute_HI_powspec(Delta_HI_arr, convolve)
        return self.Tbarsq * powspec_21cm_arr

    def binned_powspec(self, powspec_arr, k_edges):
        """
        Computes the binned power spectrum.

        Parameters
        ----------
        powspec_arr: array of dtype float
             The power spectrum calculated in each grid cell in the k-space. Has dimensions (ngrid, ngrid, ngrid).
        k_edges: array of dtype float
            The bin edges. Must have dimension (nbins + 1)
        
        Returns
        -------
        powspec_binned: array of dtype float
            The 21 power spectrum calculated at each k-bin. Has dimensions nbins.
        kount: array of dtype float
            The number of k-cells that contribute to each bin. Has dimensions nbins.
        k_bins_weighted: array of dtype float
            The weighted k-value of the bin. Has dimensions nbins.
        
        """
        
        powspec_binned, kount, k_bins_weighted = script_fortran_modules.powspec.bin_powspec(k_edges, self.kmag_fft, powspec_arr)

        return powspec_binned, kount, k_bins_weighted

    def get_binned_powspec(self, Delta_HI_arr, k_edges, convolve=False, units='', bin_weighted=False):
        """
        Higher level routine to compute the HI power spectrum.

        Parameters
        ----------
        Delta_HI_arr: array of dtype float
            The HI density field `xHI * (1 + delta)` at each grid cell. Has dimensions (ngrid, ngrid, ngrid).
        k_edges: array of dtype float
            The bin edges. Must have dimension (nbins + 1)
        concolve: bool, optional
            If `True`, de-convolve the power spectrum using an appropriate smoothing kernel.
        units: str, optional
            By default, computes the power spectrum of Delta_HI_arr.
            If `mK`, the units are set to mK^2.
            If `K`, the units are set to K^2. 
            If `xHI`, return the power spectrum of Delta_HI / Delta_HI_mean
        bin_weighted: bool, optional
            If `True`, also returns the weighted k-value of the bin.
        
        Returns
        -------
        powspec_21cm_binned: array of dtype float
            The 21 power spectrum calculated at each k-bin. Has dimensions nbins.
        kount: array of dtype float
            The number of k-cells that contribute to each bin. Has dimensions nbins.
        k_bins_weighted: array of dtype float
            The weighted k-value of the bin. Has dimensions nbins.
        """
        Delta_HI_mean = np.mean(Delta_HI_arr, dtype=np.float64)
        powspec_21cm = self.compute_HI_powspec(Delta_HI_arr, convolve)
        powspec_21cm_binned, kount, k_bins_weighted = self.binned_powspec(powspec_21cm, k_edges)

        if (units == 'mK'):
            powspec_21cm_binned = powspec_21cm_binned * self.Tbarsq * 1.e6
        elif (units == 'K'):
            powspec_21cm_binned = powspec_21cm_binned * self.Tbarsq
        elif (units == 'xHI'):
            if (Delta_HI_mean > 1.e-16):
                powspec_21cm_binned = powspec_21cm_binned / Delta_HI_mean ** 2  ## PS of Delta_HI_arr / Delta_HI_mean
            else:
                powspec_21cm_binned = 0.0

        if (bin_weighted):
            return powspec_21cm_binned, kount, k_bins_weighted
        else:
            return powspec_21cm_binned, kount

    def compute_powspec_qperp(self, qi_arr, convolve=False):
        """
        Computes the perpendicular momentum power.

        Parameters
        ----------
        qi_arr: array of dtype float
            The ionized fraction field `xHI * (1 + delta)` at each grid cell. Has dimensions (ngrid, ngrid, ngrid).
        convolve: bool, optional
            If `True`, de-convolve the power spectrum using an appropriate smoothing kernel.
        
        Returns
        -------
        powspec_qperp_arr: array of dtype float
            The perpendicular momentum power calculated in each grid cell in the k-space.
            Has dimensions (ngrid, ngrid, ngrid).
        """

        if (self.matter_fields is not None):
            self.plan_fft = self.matter_fields.plan
            self.kfft = self.matter_fields.kfft
            self.kmag_fft = self.matter_fields.kmag
        else:
            FFTW_ESTIMATE = 64
            FFTW_IFINV = 1
            self.plan_fft, self.kfft = script_fortran_modules.powspec.initialize_plan(ngrid, FFTW_IFINV, FFTW_ESTIMATE, box)
            self.kmag_fft = script_fortran_modules.powspec.get_kmag(kfft)

        powspec_qperp_arr = script_fortran_modules.ionization_map.compute_powspec_qperp(self.plan_fft, qi_arr, self.densitycontr_arr, self.velocity_arr, self.box, self.kfft, convolve)
        return powspec_qperp_arr
        
        
        
    def get_binned_powspec_qperp(self, qi_arr, l_edges, convolve=False):
        """
        Higher level routine to compute the perpendicular momentum power spectrum.

        Parameters
        ----------
        qi_arr: array of dtype float
            The ionized fraction field `xHI * (1 + delta)` at each grid cell. Has dimensions (ngrid, ngrid, ngrid).
        l_edges: array of dtype float
            The bin edges of the angular multipoles. Must have dimension (nbins + 1)
        convolve: bool, optional
            If `True`, de-convolve the power spectrum using an appropriate smoothing kernel.
        
        Returns
        -------
        powspec_qperp_binned: array of dtype float
            The perpendicular power spectrum calculated at each l-bin. Has dimensions nbins.
        kount: array of dtype float
            The number of k-cells that contribute to each bin. Has dimensions nbins.
        """

        powspec_qperp, _ = self.compute_powspec_qperp(qi_arr, convolve=convolve)
        powspec_qperp_binned, kount, k_l_edges = script_fortran_modules.ionization_map.get_binned_pqperp(l_edges, self.z, self.kmag_fft, powspec_qperp, self.omega_m, self.omega_l, self.h)
        return powspec_qperp_binned, kount, k_l_edges

