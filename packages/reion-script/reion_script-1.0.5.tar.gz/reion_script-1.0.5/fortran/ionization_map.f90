MODULE ionization_map

  DOUBLE PRECISION :: omm, oml, omb, hubble, nH0  !!! cosmological parameters for lightcone, tau
  DOUBLE PRECISION, PARAMETER :: c_by_H0_100_Mpc = 2997.92458d0   !!! c / (H0 / h)
  DOUBLE PRECISION, PARAMETER :: c_by_H0_100_cgs = 9.24944d27   !!! c / (H0 / h)
  DOUBLE PRECISION, PARAMETER :: rho_c_cgs = 1.8791d-29, rho_c = 2.7755d11
  DOUBLE PRECISION, PARAMETER :: sigma_T = 6.65246d-25, mprot = 1.672623d-24 !!! cgs
  DOUBLE PRECISION, PARAMETER :: Msun_cgs = 1.9891d33
  DOUBLE PRECISION, PARAMETER :: yr_sec = 3.1536d7
  DOUBLE PRECISION, PARAMETER :: hPlanck = 6.62607004d-27 !!! cgs
  DOUBLE PRECISION, PARAMETER :: T0_CMB = 2.725 !!! K
  DOUBLE PRECISION, PARAMETER :: Mpc_cm = 3.0856d24

CONTAINS


  SUBROUTINE initialize_ionization_map_pc(n_all, omega_m, h, z, i_x, i_y, i_z, dgnrcy, ordr, Tbarsq)
    USE sort_grid_points, only : sort_grid
    IMPLICIT NONE

    INTEGER, INTENT(in) :: n_all
    REAL, INTENT(in) :: omega_m, h, z
    INTEGER, DIMENSION(n_all), INTENT(out) :: i_x, i_y, i_z, dgnrcy, ordr
    REAL, INTENT(out) :: Tbarsq

    INTEGER :: ngrid

    Tbarsq = REAL( ( 27.0 * SQRT((1 + z) / 10.0) * SQRT(0.15 / (omega_m * h ** 2)) ) ** 2 ) * 1.e-6 !!! in K^2, ignore the omega_b dependence

    ngrid = NINT(n_all ** (1./3.))
    CALL sort_grid(ngrid, i_x, i_y, i_z, dgnrcy, ordr, read_write_file=.FALSE.)

  END SUBROUTINE initialize_ionization_map_pc

  SUBROUTINE initialize_ionization_map_es(ngrid, omega_m, h, z, plan_bwd, plan_fwd, kpow, kmag, Tbarsq)
    USE powspec, ONLY : initialize_plan, get_kmag

    IMPLICIT NONE

    INTEGER, INTENT(in) :: ngrid
    REAL, INTENT(in) :: omega_m, h, z
    INTEGER*8, INTENT(out) :: plan_bwd, plan_fwd
    REAL, DIMENSION(ngrid), INTENT(out) :: kpow
    REAL, DIMENSION(ngrid,ngrid,ngrid), INTENT(out) :: kmag
    REAL, INTENT(out) :: Tbarsq

    INTEGER :: FFTW_IFINV
    INTEGER, PARAMETER :: FFTW_ESTIMATE=64
    REAL ::  box

    Tbarsq = REAL( ( 27.0 * SQRT((1 + z) / 10.0) * SQRT(0.15 / (omega_m * h ** 2)) ) ** 2 ) * 1.e-6 !!! in K^2, ignore the omega_b dependence

    box = 1.0 !!! all lengths scaled with the box size

    FFTW_IFINV = 1 !!! backward
    CALL initialize_plan(plan_bwd, ngrid, FFTW_IFINV, FFTW_ESTIMATE, box, kpow)
    FFTW_IFINV = -1 !!! forward
    CALL initialize_plan(plan_fwd, ngrid, FFTW_IFINV, FFTW_ESTIMATE, box, kpow)

    CALL get_kmag(kpow, kmag)

  END SUBROUTINE initialize_ionization_map_es



  SUBROUTINE get_ion_map_pc(zeta_times_fcoll_arr, densitycontr_arr, qi_arr, i_x, i_y, i_z, dgnrcy, ordr)

    USE pc, ONLY : ionized_regions_photon_conserving
    IMPLICIT NONE

    REAL, DIMENSION(:,:,:), INTENT(in) :: zeta_times_fcoll_arr, densitycontr_arr
    REAL, DIMENSION(SIZE(zeta_times_fcoll_arr, 1), SIZE(zeta_times_fcoll_arr, 2), SIZE(zeta_times_fcoll_arr, 3)), INTENT(out) :: qi_arr
    INTEGER, DIMENSION(:), INTENT(in) :: i_x, i_y, i_z, dgnrcy, ordr

    INTEGER :: ngrid
    REAL, DIMENSION(:,:,:), ALLOCATABLE :: photon_field, Mhyd_field

    ngrid = SIZE(zeta_times_fcoll_arr, dim=1)
    ALLOCATE(photon_field(ngrid,ngrid,ngrid), Mhyd_field(ngrid,ngrid,ngrid))

    Mhyd_field = REAL(1.d0 + densitycontr_arr)
    photon_field  = Mhyd_field * zeta_times_fcoll_arr

    IF (SUM(DBLE(photon_field)) / SUM(DBLE(Mhyd_field)) >= 1.d0) THEN
       qi_arr(:,:,:) = 1.0
    ELSE
       CALL ionized_regions_photon_conserving(photon_field, Mhyd_field, qi_arr, i_x, i_y, i_z, dgnrcy, ordr)
    END IF

  END SUBROUTINE get_ion_map_pc

  SUBROUTINE get_ion_map_es(zeta_times_fcoll_arr, densitycontr_arr, qi_arr, plan_bwd, plan_fwd, kmag, HIfilter)

    USE es, ONLY: excursion_set_fftw
    IMPLICIT NONE

    REAL, DIMENSION(:,:,:), INTENT(in) :: zeta_times_fcoll_arr, densitycontr_arr
    REAL, DIMENSION(SIZE(zeta_times_fcoll_arr, 1), SIZE(zeta_times_fcoll_arr, 2), SIZE(zeta_times_fcoll_arr, 3)), INTENT(out) :: qi_arr
    INTEGER*8, INTENT(inout) :: plan_bwd, plan_fwd
    REAL, DIMENSION(:,:,:), INTENT(in) :: kmag
    INTEGER, intent(in) :: HIfilter

    INTEGER :: ngrid
    REAL, DIMENSION(:,:,:), ALLOCATABLE :: photon_field, Mhyd_field

    ngrid = SIZE(zeta_times_fcoll_arr, dim=1)
    ALLOCATE(photon_field(ngrid,ngrid,ngrid), Mhyd_field(ngrid,ngrid,ngrid))

    Mhyd_field = REAL(1.d0 + densitycontr_arr)
    photon_field  = Mhyd_field * zeta_times_fcoll_arr

    CALL excursion_set_fftw(photon_field, Mhyd_field, qi_arr, plan_bwd, plan_fwd, kmag, HIfilter)

  END SUBROUTINE get_ion_map_es

  SUBROUTINE add_rsd_box(Delta_HI_arr, Delta_HI_rsd_arr, velocity_arr, subgrid_num, box, z, omega_m, omega_l)
    USE rsd, only : rsd_grid
    IMPLICIT NONE

    REAL, DIMENSION(:,:,:), INTENT(in) :: Delta_HI_arr
    REAL, DIMENSION(:,:,:,:), INTENT(in) :: velocity_arr
    REAL, DIMENSION(SIZE(Delta_HI_arr,1), SIZE(Delta_HI_arr,2), SIZE(Delta_HI_arr,3)), INTENT(out) :: Delta_HI_rsd_arr
    INTEGER, INTENT(in) :: subgrid_num
    REAL, INTENT(in) :: box, z, omega_m, omega_l

    REAL, DIMENSION(:), ALLOCATABLE :: z_los
    INTEGER :: ngrid_los
    LOGICAL :: periodic

    ngrid_los = SIZE(Delta_HI_arr, dim=3)
    ALLOCATE(z_los(ngrid_los))
    z_los(1:ngrid_los) = z
    periodic = .TRUE.

    CALL rsd_grid(box, z_los, omega_m, omega_l, Delta_HI_arr, velocity_arr(3,:,:,:), Delta_HI_rsd_arr, subgrid_num, periodic)

  END SUBROUTINE add_rsd_box


  SUBROUTINE add_rsd_lc(Delta_HI_arr, Delta_HI_rsd_arr, velocity_los_arr, subgrid_num, box_los, z_los, omega_m, omega_l)
    USE rsd, only : rsd_grid
    IMPLICIT NONE

    REAL, DIMENSION(:,:,:), INTENT(in) :: Delta_HI_arr
    REAL, DIMENSION(:,:,:), INTENT(in) :: velocity_los_arr
    REAL, DIMENSION(SIZE(Delta_HI_arr,1), SIZE(Delta_HI_arr,2), SIZE(Delta_HI_arr,3)), INTENT(out) :: Delta_HI_rsd_arr
    INTEGER, INTENT(in) :: subgrid_num
    REAL, INTENT(in) :: box_los, omega_m, omega_l
    REAL, DIMENSION(:), INTENT(in) :: z_los

    INTEGER :: ngrid_los
    LOGICAL :: periodic

    ngrid_los = SIZE(Delta_HI_arr, dim=3)
    periodic = .FALSE.

    CALL rsd_grid(box_los, z_los, omega_m, omega_l, Delta_HI_arr, velocity_los_arr(:,:,:), Delta_HI_rsd_arr, subgrid_num, periodic)

  END SUBROUTINE add_rsd_lc

  INTEGER FUNCTION los_array_size(zmin, zmax, box, ngrid, omega_m, omega_l)
    IMPLICIT NONE
    REAL, INTENT(in) :: zmin, zmax, box, omega_m, omega_l
    INTEGER, INTENT(in) :: ngrid

    REAL :: dx, xcom_min, xcom_max

    IF (zmin >= zmax) STOP ('los_array_size: zmin must be smaller than zmax')
    omm = omega_m
    oml = omega_l

    dx = box / ngrid
    xcom_min = REAL( comoving_dist(DBLE(zmin)) ) !!! Mpc / h
    xcom_max = real( comoving_dist(DBLE(zmax)) ) !!! Mpc / h
    los_array_size = INT(REAL(xcom_max - xcom_min) / dx) + 1

  END FUNCTION los_array_size


  SUBROUTINE create_lightcone_map(z_arr, box, field_z_arr, vlos_z_arr, omega_m, omega_l, add_rsd, nk, light_cone_field_arr, xcom_arr, zgrid_arr)
    USE onedspline, ONLY : spline, splint
    IMPLICIT NONE

    REAL, DIMENSION(:), INTENT(in) :: z_arr
    REAL, INTENT(in) :: box
    REAL, DIMENSION(:,:,:), INTENT(in) :: field_z_arr, vlos_z_arr !!! dimensions (size(z_arr), ngrid_x, ngrid_z)
    REAL, INTENT(in) :: omega_m, omega_l
    LOGICAL, INTENT(in) :: add_rsd
    INTEGER, INTENT(in) :: nk
    REAL, DIMENSION(nk, SIZE(field_z_arr,2)), INTENT(out) :: light_cone_field_arr !!! dimensions (size(z_arr), ngrid_x)
    REAL, DIMENSION(nk), INTENT(out) :: xcom_arr, zgrid_arr

    INTEGER :: i, k
    INTEGER, DIMENSION(1) :: nearest_z_indx
    INTEGER :: nz, ngrid, nspline
    REAL :: dx
    DOUBLE PRECISION, DIMENSION(:), ALLOCATABLE :: xcom_spline_arr, z_spline_arr
    DOUBLE PRECISION, DIMENSION(:,:), ALLOCATABLE :: coeff_spline_arr

    REAL, DIMENSION(:,:,:), ALLOCATABLE :: light_cone_rsd_in_arr, light_cone_rsd_out_arr, light_cone_velocity_arr
    INTEGER :: subgrid_num
    REAL :: box_los

    omm = DBLE(omega_m)
    oml = DBLE(omega_l)

    nz = SIZE(z_arr)
    ngrid = SIZE(field_z_arr, 2)
    dx = box / ngrid

    nspline = MAX(nk, 1000)
    ALLOCATE(xcom_spline_arr(nspline), z_spline_arr(nspline), coeff_spline_arr(3,nspline))
    DO i = 1, nspline
       z_spline_arr(i) = DBLE(z_arr(1)) + DBLE(i - 1) * DBLE(z_arr(nz) - z_arr(1)) / DBLE(nspline - 1)
       xcom_spline_arr(i) = comoving_dist(DBLE(z_spline_arr(i)))  !!! in Mpc / h
    END DO
    CALL spline(LOG10(xcom_spline_arr), LOG10(1.d0 + z_spline_arr), coeff_spline_arr)

    IF (add_rsd) ALLOCATE(light_cone_velocity_arr(1, ngrid, nk))
    DO k = nk, 1, -1
       IF (k == nk) THEN
          xcom_arr(nk) = REAL(comoving_dist(DBLE(z_arr(nz))))
       ELSE
          xcom_arr(k) = xcom_arr(nk) + dx * REAL(nk - k)
       END IF
       zgrid_arr(k) = REAL( splint( LOG10(xcom_spline_arr), LOG10(1.d0 + z_spline_arr), coeff_spline_arr, LOG10(DBLE(xcom_arr(k))) ) )
       zgrid_arr(k) = 10.0 ** zgrid_arr(k) - 1.0

       nearest_z_indx = MINLOC(ABS(z_arr - zgrid_arr(k)))
       light_cone_field_arr(k, 1:ngrid) = field_z_arr(nearest_z_indx(1), 1:ngrid, MOD(nk - k, ngrid) + 1)
       IF (add_rsd) light_cone_velocity_arr(1, 1:ngrid, k) = vlos_z_arr(nearest_z_indx(1), 1:ngrid, MOD(nk - k, ngrid) + 1)
       !PRINT *, i, nk, xcom_arr(i), zgrid_arr(i), z_arr(nearest_z_indx(1)), MOD(nk-i,ngrid)+1
    END DO

    IF (add_rsd) THEN
       ALLOCATE(light_cone_rsd_in_arr(1, ngrid, nk), light_cone_rsd_out_arr(1, ngrid, nk))
       DO i = 1, ngrid
          DO k = 1, nk
             light_cone_rsd_in_arr(1, i, k) = light_cone_field_arr(k, i)
          END DO
       END DO
       subgrid_num = 50
       box_los = xcom_arr(1) - xcom_arr(nk)
       !PRINT *, 'box_los = ', box_los

       CALL add_rsd_lc(light_cone_rsd_in_arr, light_cone_rsd_out_arr, light_cone_velocity_arr, subgrid_num, box_los, zgrid_arr, omega_m, omega_l)

       DO i = 1, ngrid
          DO k = 1, nk
             light_cone_field_arr(k, i) = light_cone_rsd_out_arr(1, i, k)
          END DO
       END DO
    END IF

  END SUBROUTINE create_lightcone_map

  SUBROUTINE create_lightcone_vol(z_arr, box, field_z_arr, vlos_z_arr, omega_m, omega_l, add_rsd, nk, light_cone_field_arr, xcom_arr, zgrid_arr)
    USE onedspline, ONLY : spline, splint
    IMPLICIT NONE

    REAL, DIMENSION(:), INTENT(in) :: z_arr
    REAL, INTENT(in) :: box
    REAL, DIMENSION(:,:,:,:), INTENT(in) :: field_z_arr, vlos_z_arr !!! dimensions (size(z_arr), ngrid_x, ngrid_y, ngrid_z)
    REAL, INTENT(in) :: omega_m, omega_l
    LOGICAL, INTENT(in) :: add_rsd
    INTEGER, INTENT(in) :: nk
    REAL, DIMENSION(nk, SIZE(field_z_arr,2), SIZE(field_z_arr,3)), INTENT(out) :: light_cone_field_arr !!! dimensions (size(z_arr), ngrid_x, ngrid_y)
    REAL, DIMENSION(nk), INTENT(out) :: xcom_arr, zgrid_arr

    INTEGER :: i, j, k
    INTEGER, DIMENSION(1) :: nearest_z_indx
    INTEGER :: nz, ngrid, nspline
    REAL :: dx
    DOUBLE PRECISION, DIMENSION(:), ALLOCATABLE :: xcom_spline_arr, z_spline_arr
    DOUBLE PRECISION, DIMENSION(:,:), ALLOCATABLE :: coeff_spline_arr

    REAL, DIMENSION(:,:,:), ALLOCATABLE :: light_cone_rsd_in_arr, light_cone_rsd_out_arr, light_cone_velocity_arr
    INTEGER :: subgrid_num
    REAL :: box_los

    omm = DBLE(omega_m)
    oml = DBLE(omega_l)

    nz = SIZE(z_arr)
    ngrid = SIZE(field_z_arr, 2)
    dx = box / ngrid

    nspline = MAX(nk, 1000)
    ALLOCATE(xcom_spline_arr(nspline), z_spline_arr(nspline), coeff_spline_arr(3,nspline))
    DO i = 1, nspline
       z_spline_arr(i) = DBLE(z_arr(1)) + DBLE(i - 1) * DBLE(z_arr(nz) - z_arr(1)) / DBLE(nspline - 1)
       xcom_spline_arr(i) = comoving_dist(DBLE(z_spline_arr(i)))  !!! in Mpc / h
    END DO
    CALL spline(LOG10(xcom_spline_arr), LOG10(1.d0 + z_spline_arr), coeff_spline_arr)

    IF (add_rsd) ALLOCATE(light_cone_velocity_arr(ngrid, ngrid, nk))
    DO k = nk, 1, -1
       IF (k == nk) THEN
          xcom_arr(nk) = REAL(comoving_dist(DBLE(z_arr(nz))))
       ELSE
          xcom_arr(k) = xcom_arr(nk) + dx * REAL(nk - k)
       END IF
       zgrid_arr(k) = REAL( splint( LOG10(xcom_spline_arr), LOG10(1.d0 + z_spline_arr), coeff_spline_arr, LOG10(DBLE(xcom_arr(k))) ) )
       zgrid_arr(k) = 10.0 ** zgrid_arr(k) - 1.0

       nearest_z_indx = MINLOC(ABS(z_arr - zgrid_arr(k)))
       light_cone_field_arr(k, 1:ngrid, 1:ngrid) = field_z_arr(nearest_z_indx(1), 1:ngrid, 1:ngrid, MOD(nk - k, ngrid) + 1)
       IF (add_rsd) light_cone_velocity_arr(1:ngrid, 1:ngrid, k) = vlos_z_arr(nearest_z_indx(1), 1:ngrid, 1:ngrid, MOD(nk - k, ngrid) + 1)
       !PRINT *, i, nk, xcom_arr(i), zgrid_arr(i), z_arr(nearest_z_indx(1)), MOD(nk-i,ngrid)+1
    END DO

    IF (add_rsd) THEN
       ALLOCATE(light_cone_rsd_in_arr(ngrid, ngrid, nk), light_cone_rsd_out_arr(ngrid, ngrid, nk))
       DO i = 1, ngrid
          DO j = 1, ngrid
             DO k = 1, nk
                light_cone_rsd_in_arr(i, j, k) = light_cone_field_arr(k, i, j)
             END DO
          END DO
       END DO
       subgrid_num = 50
       box_los = xcom_arr(1) - xcom_arr(nk)
       !PRINT *, 'box_los = ', box_los

       CALL add_rsd_lc(light_cone_rsd_in_arr, light_cone_rsd_out_arr, light_cone_velocity_arr, subgrid_num, box_los, zgrid_arr, omega_m, omega_l)

       DO i = 1, ngrid
          DO j = 1, ngrid
             DO k = 1, nk
                light_cone_field_arr(k, i, j) = light_cone_rsd_out_arr(i, j, k)
             END DO
          END DO
       END DO
    END IF

  END SUBROUTINE create_lightcone_vol

  FUNCTION hubble_dist(z)
    IMPLICIT NONE

    DOUBLE PRECISION, DIMENSION(:), INTENT(in) :: z
    DOUBLE PRECISION, DIMENSION(SIZE(z)) :: hubble_dist
    DOUBLE PRECISION :: omk, Ez_hubble
    INTEGER :: n, i

    omk = 1.d0 - (oml + omm)
    n = SIZE(z)
    DO i = 1, n
       Ez_hubble = SQRT(omk * (1.d0 + z(i)) ** 2 + omm * (1.d0 + z(i)) ** 3 + oml)
       hubble_dist(i) = 1.d0 / Ez_hubble !!! dimensionless
    END DO

  END FUNCTION hubble_dist

  DOUBLE PRECISION FUNCTION comoving_dist(z)
    USE nrint, ONLY : qromb
    IMPLICIT NONE

    DOUBLE PRECISION, INTENT(in) :: z
    DOUBLE PRECISION :: eps

    eps = 1.d-6
    comoving_dist = qromb(hubble_dist, 0.d0, z, eps)
    comoving_dist = c_by_H0_100_Mpc * comoving_dist !!! Mpc/h

  END FUNCTION comoving_dist

  FUNCTION tau_ionized_integrand(z)
    IMPLICIT NONE

    DOUBLE PRECISION, DIMENSION(:), INTENT(in) :: z
    DOUBLE PRECISION, DIMENSION(SIZE(z)) :: tau_ionized_integrand
    DOUBLE PRECISION :: omk, Ez_hubble, chi_He, zHe
    INTEGER :: n, i

    omk = 1.d0 - (oml + omm)
    n = SIZE(z)
    zHe = 3.d0
    DO i = 1, n
       IF (z(i) < zHe) THEN
          chi_He = 1.16
       ELSE
          chi_He = 1.08
       END IF

       Ez_hubble = SQRT(omk * (1.d0 + z(i)) ** 2 + omm * (1.d0 + z(i)) ** 3 + oml)
       tau_ionized_integrand(i) = chi_He * (1.d0 + z(i)) ** 2 / Ez_hubble !!! dimensionless
    END DO

  END FUNCTION tau_ionized_integrand

  DOUBLE PRECISION FUNCTION tau_ionized(z) !!! dimensionless
    USE nrint, ONLY : qromb
    IMPLICIT NONE

    DOUBLE PRECISION, INTENT(in) :: z
    DOUBLE PRECISION :: eps

    eps = 1.d-6
    tau_ionized = qromb(tau_ionized_integrand, 0.d0, z, eps)

  END FUNCTION tau_ionized

  FUNCTION tau_arr(z_arr, QHII_arr, omega_m, omega_l, omega_b, h, YHe)
    IMPLICIT NONE

    REAL, DIMENSION(:), INTENT(in) :: z_arr, QHII_arr
    REAL, INTENT(in) ::  omega_m, omega_l, omega_b, h, YHe
    REAL, DIMENSION(SIZE(z_arr)) :: tau_arr

    INTEGER :: iz, nz
    DOUBLE PRECISION :: tau_prefac, tau_ionized_till_zmin, omk, c_by_H0_cgs
    REAL :: Ez_hubble, integrand_hi, integrand_lo
    REAL, PARAMETER :: chi_He = 1.08


    omm = DBLE(omega_m)
    oml = DBLE(omega_l)
    omb = DBLE(omega_b)
    hubble = DBLE(h)
    nH0 = (1.d0 - DBLE(YHe)) * omb * hubble * hubble * rho_c_cgs / mprot !!! cm^-3

    c_by_H0_cgs = c_by_H0_100_cgs / hubble
    omk = 1.d0 - omm - oml
    nz = SIZE(z_arr)

    tau_prefac = nH0 * sigma_T * c_by_H0_cgs
    tau_ionized_till_zmin = tau_prefac * tau_ionized(DBLE(z_arr(nz)))
    tau_arr(nz) = REAL(tau_ionized_till_zmin)

    Ez_hubble = REAL(SQRT(omk * (1.d0 + z_arr(nz)) ** 2 + omm * (1.d0 + z_arr(nz)) ** 3 + oml))
    integrand_lo = QHII_arr(nz) * (1 + z_arr(nz)) ** 2 / Ez_hubble
    DO iz = nz - 1, 1, -1
       Ez_hubble = REAL(SQRT(omk * (1.d0 + z_arr(iz)) ** 2 + omm * (1.d0 + z_arr(iz)) ** 3 + oml))
       integrand_hi = QHII_arr(iz) * (1 + z_arr(iz)) ** 2 / Ez_hubble

       tau_arr(iz) = tau_arr(iz+1) + REAL(tau_prefac) * chi_He * (0.5 * (integrand_hi + integrand_lo)) * ABS(z_arr(iz) - z_arr(iz+1))
       integrand_lo = integrand_hi
    END DO

  END FUNCTION tau_arr

  SUBROUTINE get_tau_grid_arr(z_arr, QHII_arr, omega_m, omega_l, omega_b, h, YHe, tau_grid_arr)
    IMPLICIT NONE

    REAL, DIMENSION(:), INTENT(in) :: z_arr
    REAL, DIMENSION(:,:,:,:), INTENT(in) :: QHII_arr  !!! dimensions (size(z_arr), ngrid, ngrid, ngrid)
    REAL, INTENT(in) ::  omega_m, omega_l, omega_b, h, YHe
    REAL, DIMENSION(SIZE(QHII_arr, 1), SIZE(QHII_arr, 2), SIZE(QHII_arr, 3), SIZE(QHII_arr, 4)), INTENT(out) :: tau_grid_arr  !!! dimensions (size(z_arr), ngrid, ngrid, ngrid)

    INTEGER :: ngrid, i, j, k

    ngrid = SIZE(QHII_arr, 2)
    DO k = 1, ngrid
       DO j = 1, ngrid
          DO i = 1, ngrid
             tau_grid_arr(:,i,j,k) = tau_arr(z_arr, QHII_arr(:,i,j,k), omega_m, omega_l, omega_b, h, YHe)
          END DO
       END DO
    END DO


  END SUBROUTINE get_tau_grid_arr

  SUBROUTINE get_luminosity_func(M_UV_edges, Mmin_arr, fcoll_all_Mmin_arr, coeff_spline_arr, densitycontr_arr, zeta_by_fesc_func, M_UV_bin, Phi_UV, Mhalo_UV, M_min, M_max, t_star, alpha, L_UV_by_L_912, omega_m, omega_b, h,  YHe)
    USE onedspline, ONLY : splint
    IMPLICIT NONE

    REAL, DIMENSION(:), INTENT(in) :: M_UV_edges
    REAL, DIMENSION(:), INTENT(in) :: Mmin_arr
    REAL, DIMENSION(:,:,:,:), INTENT(in) :: fcoll_all_Mmin_arr
    DOUBLE PRECISION, DIMENSION(:,:,:,:,:), INTENT(in) :: coeff_spline_arr
    REAL, DIMENSION(:,:,:), INTENT(in) :: densitycontr_arr
    REAL, DIMENSION(SIZE(M_UV_edges) - 1), INTENT(out) :: M_UV_bin, Phi_UV, Mhalo_UV
    REAL, INTENT(in) :: M_min, M_max, t_star, alpha, L_UV_by_L_912, omega_m, omega_b, h, YHe
    INTERFACE
       FUNCTION zeta_by_fesc_func(M)
         REAL, INTENT(IN) :: M  !! mass in M_sun
         REAL :: zeta_by_fesc_func
       END FUNCTION zeta_by_fesc_func
    END INTERFACE
    EXTERNAL :: zeta_by_fesc_func

    INTEGER :: nbins, ngrid, nMmin, ibin, errflag_lo, errflag_hi
    DOUBLE PRECISION :: L_UV_to_Nphot_fac, zeta_correc, L_UV_lo, L_UV_hi, Nphot_lo, Nphot_hi
    REAL :: M_lo, M_hi, dM_UV, M_bs_lo, M_bs_hi
    INTEGER :: i, j, k
    REAL :: dn
    DOUBLE PRECISION :: fcoll_lo, fcoll_hi, fc, sum_density, rho_m

    nbins = SIZE(M_UV_edges) - 1
    ngrid = SIZE(fcoll_all_Mmin_arr, dim=1)
    nMmin = SIZE(Mmin_arr)

    L_UV_to_Nphot_fac = (DBLE(t_star) * yr_sec) * L_UV_by_L_912 / (hPlanck * DBLE(alpha)) !!! cgs
    zeta_correc = DBLE( (1.0 - YHe) * (omega_b / omega_m) ) / mprot  !!! 1/gm
    zeta_correc = zeta_correc * Msun_cgs !!! 1/Msun

    rho_m = rho_c * omega_m * h ** 2
    sum_density = SUM(1.d0 + DBLE(densitycontr_arr))

    M_bs_lo = MAX(M_min, Mmin_arr(1))
    M_bs_hi = MIN(M_max, Mmin_arr(nMmin))

    L_UV_lo = 10.d0 ** ( 0.4d0 * (51.6d0 - DBLE(M_UV_edges(1))) )
    Nphot_lo = - L_UV_lo * L_UV_to_Nphot_fac
    CALL bisect(Nphot_lo, zeta_by_fesc_func, zeta_correc, M_lo, M_bs_lo, M_bs_hi, 1.e-6, errflag_lo)

    DO ibin = 1, nbins
       M_UV_bin(ibin) = 0.5 * (M_UV_edges(ibin) + M_UV_edges(ibin+1))
       dM_UV = M_UV_edges(ibin+1) - M_UV_edges(ibin)

       L_UV_hi = 10.d0 ** ( 0.4d0 * (51.6d0 - DBLE(M_UV_edges(ibin+1))) )
       Nphot_hi = - L_UV_hi * L_UV_to_Nphot_fac
       CALL bisect(Nphot_hi, zeta_by_fesc_func, zeta_correc, M_hi, M_bs_lo, M_bs_hi, 1.e-6, errflag_hi)
       IF (errflag_hi + errflag_lo /= 0) THEN
          Phi_UV(ibin) = 0.0
          Mhalo_UV(ibin) = 0.0
       ELSE
          fcoll_lo = 0.d0
          fcoll_hi = 0.d0
          DO k = 1, ngrid
             DO j = 1, ngrid
                DO i = 1, ngrid
                   fc = splint(LOG10(DBLE(Mmin_arr)), LOG10(DBLE(fcoll_all_Mmin_arr(i,j,k, :)) + 1.d-32), coeff_spline_arr(i,j,k,:,:), LOG10(DBLE(M_lo)))
                   fcoll_lo = fcoll_lo + (10.d0 ** fc) * (1.d0 + DBLE(densitycontr_arr(i,j,k)))
                   fc = splint(LOG10(DBLE(Mmin_arr)), LOG10(DBLE(fcoll_all_Mmin_arr(i,j,k, :)) + 1.d-32), coeff_spline_arr(i,j,k,:,:), LOG10(DBLE(M_hi)))
                   fcoll_hi = fcoll_hi + (10.d0 ** fc) * (1.d0 + DBLE(densitycontr_arr(i,j,k)))
                END DO
             END DO
          END DO
          fcoll_lo = fcoll_lo / sum_density
          fcoll_hi = fcoll_hi / sum_density
          Mhalo_UV(ibin) = (M_lo + M_hi) / 2.0
          dn = - REAL(rho_m) / Mhalo_UV(ibin) * REAL(fcoll_lo - fcoll_hi)
          Phi_UV(ibin) = dn / dM_UV
       END IF

       !PRINT *, M_UV_edges(ibin), M_UV_edges(ibin+1), Phi_UV(ibin), M_lo, M_hi, errflag_lo, errflag_hi

       errflag_lo = errflag_hi
       M_lo = M_hi
    END DO

  END SUBROUTINE get_luminosity_func

  SUBROUTINE get_luminosity_func_analytical(M_UV_edges, zeta_by_fesc_func, M_UV_bin, Phi_UV,  Mhalo_UV, M_min, M_max, t_star, alpha, L_UV_by_L_912, z, omega_m, omega_l, omega_b, h, YHe, sigma_8, ns)
    USE fcoll_grid
    IMPLICIT NONE

    REAL, DIMENSION(:), INTENT(in) :: M_UV_edges
    REAL, DIMENSION(SIZE(M_UV_edges) - 1), INTENT(out) :: M_UV_bin, Phi_UV, Mhalo_UV
    REAL, INTENT(in) :: M_min, M_max, t_star, alpha, L_UV_by_L_912, z, omega_m, omega_l, omega_b, h, YHe, sigma_8, ns
    INTERFACE
       FUNCTION zeta_by_fesc_func(M)
         REAL, INTENT(IN) :: M  !! mass in M_sun
         REAL :: zeta_by_fesc_func
       END FUNCTION zeta_by_fesc_func
    END INTERFACE
    EXTERNAL :: zeta_by_fesc_func

    INTEGER :: nbins, ibin, errflag_lo, errflag_hi
    DOUBLE PRECISION :: L_UV_to_Nphot_fac, zeta_correc, L_UV_lo, L_UV_hi, Nphot_lo, Nphot_hi
    REAL :: M_lo, M_hi, dM_UV, M_bs_lo, M_bs_hi
    REAL :: dn
    DOUBLE PRECISION :: rho_m, anorm

    om_m = DBLE(omega_m)
    om_l = DBLE(omega_l)
    h100 = DBLE(h)
    s8 = DBLE(sigma_8)
    n_s = DBLE(ns)
    om_b = DBLE(omega_b)


    rho_m = REAL(rho_c * omega_m * h ** 2)  !!! in Msun / Mpc^3


    dn_dlnk = 0.0
    k_smooth = 1.d5
    om_r = 0.d0

    anorm = norm(s8)
    delta_c = 1.686d0 / SQRT(anorm)
    !PRINT *, 'anorm = ', anorm


    a_ellipcoll = 0.67
    beta_ellipcoll = 0.4
    alpha_ellipcoll = 0.7
    norm_ellipcoll = 1.0

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    nbins = SIZE(M_UV_edges) - 1

    L_UV_to_Nphot_fac = (DBLE(t_star) * yr_sec) * L_UV_by_L_912 / (hPlanck * DBLE(alpha)) !!! cgs
    zeta_correc = DBLE( (1.0 - YHe) * (omega_b / omega_m) ) / mprot  !!! 1/gm
    zeta_correc = zeta_correc * Msun_cgs !!! 1/Msun

    rho_m = rho_c * omega_m * h ** 2

    M_bs_lo = MAX(M_min, 1.e5)
    M_bs_hi = MIN(M_max, 1.e13)

    L_UV_lo = 10.d0 ** ( 0.4d0 * (51.6d0 - DBLE(M_UV_edges(1))) )
    Nphot_lo = - L_UV_lo * L_UV_to_Nphot_fac
    CALL bisect(Nphot_lo, zeta_by_fesc_func, zeta_correc, M_lo, M_bs_lo, M_bs_hi, 1.e-6, errflag_lo)
    DO ibin = 1, nbins
       M_UV_bin(ibin) = 0.5 * (M_UV_edges(ibin) + M_UV_edges(ibin+1))
       dM_UV = M_UV_edges(ibin+1) - M_UV_edges(ibin)

       L_UV_hi = 10.d0 ** ( 0.4d0 * (51.6d0 - DBLE(M_UV_edges(ibin+1))) )
       Nphot_hi = - L_UV_hi * L_UV_to_Nphot_fac
       CALL bisect(Nphot_hi, zeta_by_fesc_func, zeta_correc, M_hi, M_bs_lo, M_bs_hi, 1.e-6, errflag_hi)
       IF (errflag_hi + errflag_lo /= 0) THEN
          Phi_UV(ibin) = 0.0
          Mhalo_UV(ibin) = 0.0 
       ELSE
          Mhalo_UV(ibin) = 0.5 * (M_hi+M_lo)
          dn = (M_hi - M_lo) * REAL( numdenm_ellipcoll(DBLE(Mhalo_UV(ibin)), DBLE(z)) )
          Phi_UV(ibin) = - dn / dM_UV
       END IF

       !PRINT *, M_UV_edges(ibin), M_UV_edges(ibin+1), Phi_UV(ibin), M_lo, M_hi, errflag_lo, errflag_hi

       errflag_lo = errflag_hi
       M_lo = M_hi
    END DO


  END SUBROUTINE get_luminosity_func_analytical

  SUBROUTINE bisect(Nphot, zeta_by_fesc_func, zeta_correc, Mhalo, Mhalo_min, Mhalo_max, eps, errflag)
    IMPLICIT NONE

    DOUBLE PRECISION, INTENT(in) :: Nphot, zeta_correc
    REAL, INTENT(in) :: Mhalo_min, Mhalo_max, eps
    REAL, INTENT(out) :: Mhalo
    INTEGER, INTENT(out) :: errflag
    INTERFACE
       FUNCTION zeta_by_fesc_func(M)
         REAL, INTENT(IN) :: M  !! mass in M_sun
         REAL :: zeta_by_fesc_func
       END FUNCTION zeta_by_fesc_func
    END INTERFACE
    EXTERNAL :: zeta_by_fesc_func

    DOUBLE PRECISION :: f_lo, f_hi, f_mid
    real :: log10M_lo, log10M_hi, log10M_mid
    INTEGER :: i
    INTEGER, parameter :: niter = 1000

    errflag = 0

    f_lo = zeta_correc * DBLE(zeta_by_fesc_func(Mhalo_min) * Mhalo_min) - Nphot
    f_hi = zeta_correc * DBLE(zeta_by_fesc_func(Mhalo_max) * Mhalo_max) - Nphot

    IF (f_lo * f_hi > 0.d0) THEN 
       errflag = 1
       !PRINT *, 'WARNING: bisect limits are not wide enough', Mhalo_min, Mhalo_max, f_lo, f_hi, Nphot
       IF (ABS(f_lo) < ABS(f_hi)) THEN
          Mhalo = Mhalo_min
       ELSE
          Mhalo = Mhalo_max
       END IF
       RETURN
    END IF

    log10M_lo = LOG10(Mhalo_min)
    log10M_hi = LOG10(Mhalo_max)
    !Iterative refining the solution 
    DO i = 1, niter
       log10M_mid = (log10M_hi + log10M_lo) / 2.0

       f_lo = zeta_correc * DBLE(zeta_by_fesc_func(10.0 ** log10M_lo) * 10.0 ** log10M_lo) - Nphot
       f_mid = zeta_correc * DBLE(zeta_by_fesc_func(10.0 ** log10M_mid) * 10.0 ** log10M_mid) - Nphot

       IF (f_lo * f_mid <= 0.d0) THEN
          log10M_hi = log10M_mid
       ELSE
          log10M_lo = log10M_mid
       END IF
       ! condition(s) to stop iterations)
       IF (ABS(log10M_hi - log10M_lo) <= eps) EXIT  
    END DO

    IF (i == niter) errflag = -1
    Mhalo = 10.0 ** ( (log10M_hi + log10M_lo) / 2.0 )


  END SUBROUTINE bisect

  SUBROUTINE compute_powspec_qperp(plan, qi_arr, densitycontr_arr, velocity_arr, box, kpow, convolve, powspec_qperp_arr, kmag)
    USE powspec, ONLY : get_kmag, complexify, pspec_fftw, deconvolve_power
    IMPLICIT NONE
    
    INTEGER*8, INTENT(INOUT) :: plan
    REAL, DIMENSION(:,:,:), INTENT(IN) :: qi_arr, densitycontr_arr
    REAL, DIMENSION(:,:,:,:), INTENT(IN) :: velocity_arr
    REAL, INTENT(IN) :: box
    REAL, DIMENSION(:), INTENT(in) :: kpow
    LOGICAL, INTENT(IN) :: convolve
    REAL, DIMENSION(SIZE(qi_arr,1), SIZE(qi_arr,2), SIZE(qi_arr,3)), INTENT(OUT) :: powspec_qperp_arr
    REAL, DIMENSION(SIZE(kpow),SIZE(kpow),SIZE(kpow)), INTENT(out) :: kmag
    
    REAL :: QHII_mean, momentum_mean
    INTEGER :: ngrid, i, j, k
    REAL, DIMENSION(:,:,:), ALLOCATABLE :: momentum_los, delta_momentum
    DOUBLE COMPLEX, DIMENSION(:,:,:), ALLOCATABLE :: deltak
    DOUBLE COMPLEX, DIMENSION(:,:,:,:), ALLOCATABLE :: qk, qk_perp
    DOUBLE COMPLEX :: qk_dot_k
    
    DOUBLE PRECISION, PARAMETER :: c_km_s = 2.9979d5
    
    CALL get_kmag(kpow, kmag)
    QHII_mean = REAL( SUM(DBLE(qi_arr) * (1.d0 + DBLE(densitycontr_arr))) / DBLE(SIZE(qi_arr)) )
    IF (QHII_mean > 0.99) THEN
       powspec_qperp_arr(:,:,:) = 0.0 !!! if fully ionized, then no signal from patchy reionization
       RETURN
    END IF
    
    ngrid = SIZE(qi_arr,1)
    ALLOCATE(momentum_los(ngrid,ngrid,ngrid), delta_momentum(ngrid,ngrid,ngrid))
    ALLOCATE(deltak(ngrid,ngrid,ngrid), qk(3,ngrid,ngrid,ngrid), qk_perp(3,ngrid,ngrid,ngrid))
    
    DO i = 1, 3
       momentum_los(:,:,:) = qi_arr(:,:,:) * (1.0 + densitycontr_arr(:,:,:)) * velocity_arr(i,:,:,:) / REAL(c_km_s)
       
       momentum_mean = REAL(SUM(DBLE(momentum_los(:,:,:))) / DBLE(ngrid) ** 3)
       delta_momentum = momentum_los(:,:,:) - momentum_mean
       
       CALL complexify(delta_momentum, deltak)
       CALL pspec_fftw(plan, deltak, box, powspec_qperp_arr)
       
       qk(i,:,:,:) = deltak
    END DO
    
    !$OMP PARALLEL DEFAULT(SHARED) PRIVATE (k,j,i,qk_dot_k)
    !$OMP DO  schedule(static)
    DO k = 1, ngrid
       DO j = 1, ngrid
          DO i = 1, ngrid
             IF (kmag(i,j,k) /= 0.0) THEN
                qk_dot_k = qk(1,i,j,k) * kpow(i) + qk(2,i,j,k) * kpow(j) + qk(3,i,j,k) * kpow(k)
                qk_perp(1,i,j,k) = qk(1,i,j,k) - kpow(i) * qk_dot_k / kmag(i,j,k) ** 2
                qk_perp(2,i,j,k) = qk(2,i,j,k) - kpow(j) * qk_dot_k / kmag(i,j,k) ** 2
                qk_perp(3,i,j,k) = qk(3,i,j,k) - kpow(k) * qk_dot_k / kmag(i,j,k) ** 2
                
                powspec_qperp_arr(i,j,k) = REAL( ABS(qk_perp(1,i,j,k)) ** 2 + ABS(qk_perp(2,i,j,k)) ** 2 + ABS(qk_perp(3,i,j,k)) ** 2 )
             END IF
          END DO
       END DO
    END DO
    
    IF (convolve) CALL deconvolve_power(powspec_qperp_arr, box)
    
  END SUBROUTINE compute_powspec_qperp
  
  SUBROUTINE get_k_from_l(lval, z, omega_m, omega_l, h, kval)
    IMPLICIT NONE
    
    REAL, DIMENSION(:), INTENT(in) :: lval
    REAL, INTENT(IN) :: z, h, omega_m, omega_l
    REAL, DIMENSION(SIZE(lval)), INTENT(out) :: kval
    
    omm = DBLE(omega_m)
    oml = DBLE(omega_l)
    hubble = DBLE(h)
    kval = (lval / REAL(comoving_dist(DBLE(z)))) !!! in h/Mpc
    
  END SUBROUTINE get_k_from_l
  
  SUBROUTINE get_binned_Pqperp(l_edges, z, kmag, powspec_qperp, Pqperp_binned, kount, omega_m, omega_l, h, k_edges)
    USE powspec, ONLY : bin_powspec
    IMPLICIT NONE
    
    REAL, DIMENSION(:), INTENT(in) :: l_edges
    REAL, DIMENSION(:,:,:), INTENT(in) :: powspec_qperp, kmag
    REAL, DIMENSION(SIZE(l_edges)-1), INTENT(out) :: Pqperp_binned, kount
    REAL, INTENT(IN) :: z, h, omega_m, omega_l
    REAL, DIMENSION(SIZE(l_edges)), INTENT(out) :: k_edges

    REAL, DIMENSION(SIZE(l_edges)-1) :: k_bins
    
    !INTEGER :: nl_edges
    
    !nl_edges = SIZE(l_edges)

    omm = DBLE(omega_m)
    oml = DBLE(omega_l)
    hubble = DBLE(h)

    CALL get_k_from_l(l_edges, z, omega_m, omega_l, h, k_edges)
    !print *, l_edges, k_edges
    CALL bin_powspec(k_edges, kmag, powspec_qperp, Pqperp_binned, kount, k_bins) !!! k_bins not used, it gives count-weighted bin centre
    
  END SUBROUTINE get_binned_Pqperp
  


  SUBROUTINE get_Cl_kSZ_patchy(z_arr, Pqperp_binned_arr, tau_arr, omega_m, omega_l, omega_b, YHe, h, Cl_kSZ)
    IMPLICIT NONE
    REAL, DIMENSION(:), INTENT(IN) :: z_arr, tau_arr
    REAL, DIMENSION(:,:), INTENT(IN) :: Pqperp_binned_arr !!! dimension(SIZE(z_arr),SIZE(l_arr)),
    REAL, INTENT(IN) :: h, omega_m, omega_l,omega_b, YHe
    REAL, DIMENSION(SIZE(Pqperp_binned_arr,2)), INTENT(OUT) :: Cl_kSZ

    INTEGER :: iz, nz
    DOUBLE PRECISION :: Cl_prefac, omk, c_by_H0_cgs
    REAL :: Ez_hubble, chiz_comoving
    REAL, DIMENSION(SIZE(Pqperp_binned_arr,2)) :: integrand_hi_arr, integrand_lo_arr
    REAL, PARAMETER :: chi_He = 1.08


    omm = DBLE(omega_m)
    oml = DBLE(omega_l)
    omb = DBLE(omega_b)
    hubble = DBLE(h)
    c_by_H0_cgs = c_by_H0_100_cgs / hubble !!! cm
    omk = 1.d0 - omm - oml
    nH0 = (1.d0 - DBLE(YHe)) * omb * hubble * hubble * rho_c_cgs / mprot !!! cm^-3

    Cl_prefac = (nH0 * sigma_T) ** 2 / c_by_H0_cgs
    Cl_prefac = Cl_prefac * (T0_CMB * 1.d6) ** 2 !!! microK^2
    Cl_prefac = Cl_prefac * (Mpc_cm / h) ** 3 !!! to account for units in Pq

    Cl_kSZ(:) = 0.0
    nz = SIZE(z_arr)

    Ez_hubble = REAL(SQRT(omk * (1.d0 + z_arr(nz)) ** 2 + omm * (1.d0 + z_arr(nz)) ** 3 + oml))
    chiz_comoving = REAL(comoving_dist(DBLE(z_arr(nz))) / c_by_H0_100_Mpc) !!! dimensionless; dimensions are accounted for in Cl_prefac
    integrand_lo_arr(:) = EXP(-2 * tau_arr(nz)) * (Pqperp_binned_arr(nz,:) / 2.0) * (1 + z_arr(nz)) ** 4 / (chiz_comoving ** 2 * Ez_hubble)
    DO iz = nz - 1, 1, -1
       Ez_hubble = REAL(SQRT(omk * (1.d0 + z_arr(iz)) ** 2 + omm * (1.d0 + z_arr(iz)) ** 3 + oml))
       chiz_comoving = REAL(comoving_dist(DBLE(z_arr(iz))) / c_by_H0_100_Mpc) !!! dimensionless; dimensions are accounted for in Cl_prefac
       integrand_hi_arr(:) = EXP(-2 * tau_arr(iz)) * (Pqperp_binned_arr(iz,:) / 2.0) * (1 + z_arr(iz)) ** 4 / (chiz_comoving ** 2 * Ez_hubble)

       Cl_kSZ(:) = Cl_kSZ(:) + REAL(Cl_prefac) * chi_He ** 2 * (0.5 * (integrand_hi_arr(:) + integrand_lo_arr(:))) * ABS(z_arr(iz) - z_arr(iz+1))
       integrand_lo_arr(:) = integrand_hi_arr(:)

       !PRINT *, z_arr(iz), tau_arr(iz), Cl_prefac, Cl_kSZ(:) !!, kval ** 3 * Pq / (2 * pi ** 2), Dl_kSZ
    END DO


  END SUBROUTINE get_Cl_kSZ_patchy

  SUBROUTINE add_missing_Pqperp_kSZ(z, QHII_mean, box, k_arr, k_bins, P_ee_binned, P_mm_binned, P_halo_binned, omega_m, omega_l, h, sigma_8, ns, omega_b, box_large, Pqperp_missing_arr)
    USE fcoll_grid
    USE onedspline, ONLY : spline, splint
    IMPLICIT NONE
   
    REAL, INTENT(in) :: z, QHII_mean, box, omega_m, omega_l, h, sigma_8, ns, omega_b, box_large
    REAL, DIMENSION(:), INTENT(in) :: k_arr, k_bins, P_ee_binned, P_mm_binned, P_halo_binned
    REAL, DIMENSION(SIZE(k_arr)), INTENT(out) :: Pqperp_missing_arr
    
    REAL :: bias_ee, bias_halo, prefactor, Ez, f_omega, dota_by_c, Dz
    DOUBLE PRECISION :: anorm
    REAL :: k_box, k_large, k_bins_min, P_lin_large
    INTEGER :: i, n_bins, n_bins_large, n_bins_total
    DOUBLE PRECISION, DIMENSION(:), ALLOCATABLE :: Pee, kee
    DOUBLE PRECISION, DIMENSION(:,:), ALLOCATABLE :: coeff_spline

    INTEGER :: n_edges_prime, k_index, kprime_index, muprime_index, n_edges_prime_masked
    DOUBLE PRECISION, DIMENSION(:), ALLOCATABLE :: kprime, muprime, P_lin_prime, integrand_muprime, integral_muprime, integrand_kprime, muprime_masked
    DOUBLE PRECISION :: k_minus_kprime, Pee_prime, integral_kprime

    REAL, PARAMETER :: chi_He = 1.08


    IF (QHII_mean > 0.99) THEN
       Pqperp_missing_arr(:) = 0.0 !!! if fully ionized, then no signal from patchy reionization
       RETURN
    END IF

!!!! set values in the fcoll_grid module, needed for linear power spectrum
    om_m = DBLE(omega_m)
    om_l = DBLE(omega_l)
    h100 = DBLE(h)
    s8 = DBLE(sigma_8)
    n_s = DBLE(ns)
    om_b = DBLE(omega_b)
    dn_dlnk = 0.0
    k_smooth = 1.d5
    om_r = 0.d0
    anorm = norm(s8)

    n_bins = SIZE(k_bins)

    ! Compute halo bias
    bias_halo = SQRT(P_halo_binned(1) / P_mm_binned(1))
    bias_ee = bias_halo * QHII_mean * chi_He
    Dz = REAL(D(DBLE(z)))

    k_box = REAL(two_pi / box)
    k_large = REAL(two_pi / box_large)
    k_bins_min = k_bins(1) - (k_bins(2) - k_bins(1))
    n_bins_large = 100
    !IF (MOD(n_bins, 2) == 1) n_bins_large = n_bins_large + 1 !!! total bins should be even
    n_bins_total = n_bins + n_bins_large
    ! setting up spline arrays for Pee calculation
    ALLOCATE (kee(n_bins_total), Pee(n_bins_total), coeff_spline(3, n_bins_total))
    kee(n_bins_large+1:n_bins_total) = k_bins(1:n_bins)
    Pee(n_bins_large+1:n_bins_total) = chi_He ** 2 * P_ee_binned(1:n_bins)
    DO i = 1, n_bins_large
       kee(i) = DBLE(k_large + REAL(i - 1) * (k_bins_min - k_large) / REAL(n_bins_large - 1))
       P_lin_large =  Dz ** 2 * REAL(anorm * pspec(DBLE(kee(i)) * h100) * h100 ** 3) !!! appropriate factors of h accounted for and checked
       Pee(i) = DBLE(bias_ee ** 2 * P_lin_large)
    END DO
    ! DO i = 1, n_bins_total
    !    PRINT *, kee(i), Pee(i)
    ! END DO
    CALL spline(LOG10(kee), LOG10(Pee), coeff_spline)
    
    !zgrid_arr(k) = REAL( splint( LOG10(xcom_spline_arr), LOG10(1.d0 + z_spline_arr), coeff_spline_arr, LOG10(DBLE(xcom_arr(k))) ) )




    !PRINT *, z, D(DBLE(z)), anorm, om_m, om_l, h100, s8, n_s, om_b, SQRT(anorm * sigmasq(8.0/h100))
    !PRINT *, z, QHII_mean, bias_ee, chi_He * SQRT(P_ee_binned(1) / P_mm_binned(1))!, P_mm_binned(2) / P_lin_binned(2)
    
    ! Compute other constants
    Ez = REAL(1.d0 / hubbledist(DBLE(z)))
    f_omega = ( (omega_m * (1.0 + z) ** 3) / Ez ** 2 ) ** (4.0 / 7.0)
    dota_by_c = Ez / REAL(c_by_H0_100_Mpc * (1.d0 + z)) !!! h/Mpc
    prefactor = REAL(f_omega * dota_by_c / two_pi) ** 2
    !PRINT *, 'prefactor', z, prefactor, f_omega, dota_by_c

    n_edges_prime = 51 !!! both kprime and muprime integrals, keep it odd if possible
    !IF (MOD(n_edges_prime, 2) == 0) n_edges_prime = n_edges_prime + 1
    ALLOCATE(kprime(n_edges_prime), muprime(n_edges_prime), P_lin_prime(n_edges_prime), integrand_muprime(n_edges_prime), integral_muprime(n_edges_prime), integrand_kprime(n_edges_prime), muprime_masked(n_edges_prime))
    DO i = 1, n_edges_prime
       kprime(i) = DBLE(k_large + REAL(i - 1) * (k_box - k_large) / REAL(n_edges_prime - 1))
       muprime(i) = -1.d0 + DBLE(i - 1) * 2.d0 / DBLE(n_edges_prime - 1)
       P_lin_prime(i) = DBLE(Dz) ** 2 * anorm * pspec(kprime(i) * h100) * h100 ** 3 !!! appropriate factors of h accounted for and checked
       !PRINT *, kprime(i), muprime(i), P_lin_prime(i)
    END DO
    

    DO k_index = 1, SIZE(k_arr)
       DO kprime_index = 1, n_edges_prime
          n_edges_prime_masked = 0
          DO muprime_index = 1, n_edges_prime
             !! k_minus_kprime_sq
             k_minus_kprime = DBLE(k_arr(k_index)) ** 2 + kprime(kprime_index) ** 2 - 2.d0 * muprime(muprime_index) * DBLE(k_arr(k_index)) * kprime(kprime_index)
             !! check and then take sqrt
             IF (k_minus_kprime >= 0.d0) THEN
                k_minus_kprime = SQRT(k_minus_kprime)
             ELSE
                !PRINT *, 'k-kp:', k_minus_kprime
                k_minus_kprime = 0.d0
             END IF
             IF (k_minus_kprime <= kee(n_bins_total) .AND. k_minus_kprime >= kee(1)) THEN
                Pee_prime = splint(LOG10(kee), LOG10(Pee), coeff_spline, LOG10(k_minus_kprime))
                Pee_prime = 10.d0 ** Pee_prime
                n_edges_prime_masked = n_edges_prime_masked + 1
                muprime_masked(n_edges_prime_masked) = muprime(muprime_index)
                !IF (ABS(k_minus_kprime - 0.385) < 0.001) PRINT *, z, k_minus_kprime, Pee_prime
                integrand_muprime(n_edges_prime_masked) = (1.d0 - muprime_masked(n_edges_prime_masked) ** 2) * Pee_prime
                !ELSE
                !   !PRINT *, 'k-k:', z, k_minus_kprime, kee(n_bins_total), kee(1)
                !   Pee_prime = 0.d0
             END IF
          END DO
          IF (n_edges_prime_masked > 1) THEN 
             CALL simpson_composite(integrand_muprime(1:n_edges_prime_masked), muprime_masked(1:n_edges_prime_masked), integral_muprime(kprime_index))
             IF (integral_muprime(kprime_index) > 1.d5) PRINT *, z, integral_muprime(kprime_index), n_edges_prime_masked
             !PRINT *, n_edges_prime_masked, n_edges_prime
          ELSE
             integral_muprime(kprime_index) = 0.d0
          END IF
          integrand_kprime(kprime_index) = P_lin_prime(kprime_index) *  integral_muprime(kprime_index)
       END DO
       !PRINT *, z, kprime(1), integrand_muprime(1)
       CALL simpson_composite(integrand_kprime, kprime, integral_kprime)
       Pqperp_missing_arr(k_index) = prefactor * REAL(integral_kprime)
       ! IF (Pqperp_missing_arr(k_index) > 1.0) THEN 
       !    PRINT *, 'Pqperp:', z, k_arr(k_index), Pqperp_missing_arr(k_index), integral_kprime
       !    !PRINT *, integral_muprime
       ! END IF
    END DO

  END SUBROUTINE add_missing_Pqperp_kSZ

  SUBROUTINE simpson_composite(func, x, res)
    !!! Composite Simpson's rule for irregularly spaced data
    !!! See the wikipedia page: https://en.wikipedia.org/wiki/Simpson%27s_rule#Composite_Simpson's_rule_for_irregularly_spaced_data

    IMPLICIT NONE
    DOUBLE PRECISION, DIMENSION(:), INTENT(in) :: func, x
    DOUBLE PRECISION, INTENT(out) :: res

    DOUBLE PRECISION, DIMENSION(:), ALLOCATABLE :: h
    DOUBLE PRECISION :: h0, h1, hph, hdh, hmh
    INTEGER :: n_bins, i

    n_bins = SIZE(x) - 1

    IF (n_bins == 0) STOP ('simpson_composite: problem in n_bins')
    IF (n_bins == 1) THEN
       res = 0.5d0 * (func(1) + func(2)) * (x(2) - x(1))
       !!!! trapezoidal rule
       RETURN
    END IF

    ALLOCATE(h(n_bins))
    DO i = 1, n_bins
       h(i) = x(i+1) - x(i)
    END DO
    
    res = 0.d0
    DO i = 2, n_bins, 2
       h0 = h(i-1)
       h1 = h(i)
       hph = h1 + h0
       hdh = h1 / h0
       hmh = h1 * h0
       res = res + (hph / 6.d0) * ( (2.d0 - hdh) * func(i - 1) + (hph ** 2 / hmh) * func(i) + (2.d0 - 1.0 / hdh) * func(i + 1) ) 
    END DO

    IF (MOD(n_bins, 2) == 1) THEN
       h0 = h(n_bins-1)
       h1 = h(n_bins)
       res = res + func(n_bins + 1) * (2.d0 * h1 ** 2 + 3.d0 * h0 * h1) / (6.d0 * (h0 + h1))
       res = res + func(n_bins) * (h1 ** 2 + 3.0 * h1 * h0) / (6.d0 * h0)
       res = res - func(n_bins-1) * h1 ** 3 / (6.d0 * h0 * (h0 + h1))
    END IF


  END SUBROUTINE simpson_composite
END MODULE ionization_map
