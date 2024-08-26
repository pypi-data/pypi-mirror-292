MODULE matter_fields

CONTAINS

  SUBROUTINE smooth_density_velocity_cic(x,v,box,ngrid,density,velocity)
    IMPLICIT NONE

    REAL, DIMENSION(:,:), INTENT(in) :: x,v
    REAL, INTENT(in) :: box
    INTEGER, INTENT(in) :: ngrid
    REAL, DIMENSION(ngrid,ngrid,ngrid), INTENT(out) :: density
    REAL, DIMENSION(3,ngrid,ngrid,ngrid), INTENT(out) :: velocity

    INTEGER :: npart,i,i1,j1,k1,ii,jj,kk,iii,jjj,kkk
    REAL, DIMENSION(2) :: ci,cj,ck

    npart = SIZE(x,dim=2)
    density = 0.0
    velocity = 0.0

    DO i = 1, npart
       CALL cic(x(1,i) * REAL(ngrid) / box, i1, ci)
       CALL cic(x(2,i) * REAL(ngrid) / box, j1, cj)
       CALL cic(x(3,i) * REAL(ngrid) / box, k1, ck)

       DO kk = 1, 2
          kkk = iperi(kk + k1 - 1, ngrid)
          DO jj = 1, 2
             jjj = iperi(jj + j1 - 1, ngrid)
             DO ii = 1, 2
                iii = iperi(ii + i1 - 1, ngrid)
                density(iii, jjj, kkk) = density(iii, jjj, kkk) + ci(ii) * cj(jj) * ck(kk)
                velocity(1:3, iii, jjj, kkk) = velocity(1:3, iii, jjj, kkk) + ci(ii) * cj(jj) * ck(kk) * v(1:3, i)
             ENDDO
          ENDDO
       ENDDO
    END DO

    DO i = 1, 3
       WHERE(density /= 0.0) velocity(i,:,:,:) = velocity(i,:,:,:) / density(:,:,:)
    END DO

  END SUBROUTINE smooth_density_velocity_cic

  SUBROUTINE smooth_field_cic(input_field, box, ngrid_new, smoothed_field, average)
    IMPLICIT NONE

    REAL, DIMENSION(:,:,:), INTENT(in) :: input_field
    REAL, INTENT(in) :: box
    INTEGER, INTENT(in) :: ngrid_new
    REAL, DIMENSION(ngrid_new,ngrid_new,ngrid_new), INTENT(out) :: smoothed_field
    LOGICAL, INTENT(in) :: average

    INTEGER :: ngrid_old, i,j,k,i1,j1,k1,ii,jj,kk,iii,jjj,kkk
    REAL, DIMENSION(2) :: ci,cj,ck
    REAL :: dx
    REAL, DIMENSION(3) :: x
    REAL, DIMENSION(:,:,:), ALLOCATABLE :: kount

    ngrid_old = SIZE(input_field, 1)

    IF (ngrid_new > ngrid_old) STOP 'smooth_field_cic: ngrid_new is greater than ngrid_old'

    IF (ngrid_new == ngrid_old) THEN
       smoothed_field = input_field
       RETURN
    END IF

    dx = box / REAL(ngrid_old)
    IF (average) THEN 
       ALLOCATE(kount(ngrid_new,ngrid_new,ngrid_new))
       kount = 0.0
    END IF
    smoothed_field(:,:,:) = 0.0

    DO k = 1, ngrid_old
       DO j = 1, ngrid_old
          DO i = 1, ngrid_old
             x(1) = REAL(i-1) * dx
             x(2) = REAL(j-1) * dx
             x(3) = REAL(k-1) * dx

             CALL cic(x(1) * REAL(ngrid_new) / box, i1, ci)
             CALL cic(x(2) * REAL(ngrid_new) / box, j1, cj)
             CALL cic(x(3) * REAL(ngrid_new) / box, k1, ck)

             DO kk = 1, 2
                kkk = iperi(kk + k1 - 1, ngrid_new)
                DO jj = 1, 2
                   jjj = iperi(jj + j1 - 1, ngrid_new)
                   DO ii = 1, 2
                      iii = iperi(ii + i1 - 1, ngrid_new)
                      smoothed_field(iii, jjj, kkk) = smoothed_field(iii, jjj, kkk) + ci(ii) * cj(jj) * ck(kk) * input_field(i,j,k)
                      IF (average) kount(iii, jjj, kkk) = kount(iii, jjj, kkk) + ci(ii) * cj(jj) * ck(kk)
                   ENDDO
                ENDDO
             ENDDO
          END DO
       END DO
    END DO


    IF (average) THEN
       WHERE(kount /= 0.0) smoothed_field = smoothed_field / kount
    END IF

    ! PRINT *, 'smooth_field_cic input:', MINVAL(input_field), MAXVAL(input_field)
    ! PRINT *, 'smooth_field_cic smooth:', MINVAL(smoothed_field), MAXVAL(smoothed_field)


  END SUBROUTINE smooth_field_cic


 
  INTEGER FUNCTION iperi(i,n)
    IMPLICIT NONE
    INTEGER, INTENT(in) :: i, n

    iperi = MODULO(i - 1, n) + 1

  END FUNCTION iperi

  SUBROUTINE cic(x,ix,c)

    IMPLICIT NONE

    INTEGER, INTENT(OUT) :: ix
    REAL, INTENT(IN) :: x
    REAL :: dx
    REAL, DIMENSION(2), INTENT(OUT) :: c

    ix = FLOOR(x + 1.)
    !PRINT *,ix,x

    dx = ABS(x + 1. - REAL(ix))

    c(1) = 1.e0 - dx
    c(2) = dx

  END SUBROUTINE cic

  SUBROUTINE read_gadget_header(snap, np, box, z, omega_m, omega_l, h, scaledist)
    IMPLICIT NONE

    CHARACTER(len=*), INTENT(in) :: snap
    INTEGER, INTENT(out) :: np
    REAL, INTENT(out) :: z, box, omega_m, omega_l, h
    REAL, INTENT(in) :: scaledist
!!! scaledist = 1.0   if GADGET output positions are in units of Mpc/h
!!! scaledist = 1.e-3 if GADGET output positions are in units of kpc/h

    CHARACTER(len=200) :: infile
    LOGICAL :: multiple_files

    INTEGER*4 npart(6), nall(6)
    REAL*8    massarr(6)
    REAL*8    a,redshift,boxsize,omega_0,omega_v,hubble
    INTEGER*4 unused(24)
    INTEGER*4 flag_sfr,flag_feedback,flag_cooling
    INTEGER*4 Nfiles

    INQUIRE(FILE=TRIM(snap) // '.0', EXIST=multiple_files)
    IF (multiple_files) THEN
       infile = TRIM(snap) // '.0'
    ELSE
       infile = snap
    END IF

    OPEN (1, file=TRIM(infile), form='unformatted', status='old', action='read')
    READ (1) npart, massarr, a, redshift, flag_sfr,flag_feedback, &
         &nall, flag_cooling,Nfiles,boxsize,omega_0,omega_v,hubble,unused
    CLOSE (1)
    np = nall(2)

    omega_m = REAL(omega_0)
    omega_l = REAL(omega_v)
    h = REAL(hubble)
    box = REAL(boxsize) * scaledist
    z = REAL(redshift)


  END SUBROUTINE read_gadget_header

  SUBROUTINE read_gadget_dm_pos_vel(snap, np, pos, vel, scaledist)
    IMPLICIT NONE

    CHARACTER(len=*), INTENT(in) :: snap
    INTEGER, INTENT(in) :: np
    REAL, DIMENSION(3,np), INTENT(out) :: pos,vel
    REAL, INTENT(in) :: scaledist
!!! scaledist = 1.0   if GADGET output positions are in units of Mpc/h
!!! scaledist = 1.e-3 if GADGET output positions are in units of kpc/h

    LOGICAL :: multiple_files

    INQUIRE(FILE=TRIM(snap) // '.0', EXIST=multiple_files)
    IF (multiple_files) THEN
       CALL read_gadget_dm_pos_vel_multiple(snap, np, pos, vel, scaledist)
    ELSE
       CALL read_gadget_dm_pos_vel_single(snap, np, pos, vel, scaledist)
    END IF

  END SUBROUTINE read_gadget_dm_pos_vel

  SUBROUTINE read_gadget_dm_pos_vel_single(snap, np, pos, vel, scaledist)
    IMPLICIT NONE

    CHARACTER(len=*), INTENT(in) :: snap
    INTEGER, INTENT(in) :: np
    REAL, DIMENSION(3,np), INTENT(out) :: pos, vel
    REAL, INTENT(in) :: scaledist
!!! scaledist = 1.0   if GADGET output positions are in units of Mpc/h
!!! scaledist = 1.e-3 if GADGET output positions are in units of kpc/h

    INTEGER*4 npart(6), nall(6)
    REAL*8    massarr(6)
    REAL*8    a,redshift,boxsize,omega_0,omega_v,hubble
    INTEGER*4 unused(24)
    INTEGER*4 flag_sfr,flag_feedback,flag_cooling
    INTEGER*4 Nfiles

    ! now, read in the header
    OPEN (1, file=snap, form='unformatted', status='old', action='read')
    READ (1) npart, massarr, a, redshift, flag_sfr,flag_feedback, &
         &nall, flag_cooling,Nfiles,boxsize,omega_0,omega_v,hubble,unused


    READ (1) pos
    READ (1) vel
    CLOSE(1)

    pos = pos * scaledist
    vel = vel * REAL(SQRT(a))

    !PRINT *, 'done with GADGET snapshot ' // snap(1:LEN_TRIM(snap))

  END SUBROUTINE read_gadget_dm_pos_vel_single

  SUBROUTINE read_gadget_dm_pos_vel_multiple(snap, np, pos, vel, scaledist)
    IMPLICIT NONE

    CHARACTER(len=*), INTENT(in) :: snap
    INTEGER, INTENT(in) :: np
    REAL, DIMENSION(3,np), INTENT(out) :: pos,vel
    REAL, INTENT(in) :: scaledist
!!! scaledist = 1.0   if GADGET output positions are in units of Mpc/h
!!! scaledist = 1.e-3 if GADGET output positions are in units of kpc/h

    INTEGER*4 npart(6), nall(6)
    REAL*8    massarr(6)
    REAL*8    a,redshift,boxsize,omega_0,omega_v,hubble
    INTEGER*4 unused(24)
    INTEGER*4 i, istart, iend, Nfiles
    INTEGER*4 flag_sfr,flag_feedback,flag_cooling
    CHARACTER*200 fnumber, filename


    OPEN (1, file=snap(1:len_TRIM(snap))//'.0', form='unformatted',status='old',action='read')!, access='stream')
    READ (1) npart, massarr, a, redshift, flag_sfr,flag_feedback, &
         &nall, flag_cooling,Nfiles,boxsize,omega_0,omega_v,hubble,unused
    CLOSE(1)


    fnumber = ''
    istart = 1
    DO i = 0, Nfiles-1
       IF (i < 10) THEN
          WRITE(fnumber,'(I1)') i
       ELSEIF (i < 100) THEN
          WRITE(fnumber,'(I2)') i
       ELSEIF (i < 1000) THEN
          WRITE(fnumber,'(I3)') i
       END IF

       filename = snap(1:len_TRIM(snap)) // '.' // fnumber(1:LEN_TRIM(fnumber))
       OPEN (1, file=filename, form='unformatted',status='old',action='read')!, access='stream')
       READ (1) npart, massarr, a, redshift, flag_sfr,flag_feedback, &
            &nall, flag_cooling,Nfiles,boxsize,omega_0,omega_v,hubble,unused
       iend = istart + npart(2) - 1
       READ (1) pos(:,istart:iend)
       READ (1) vel(:,istart:iend)
       CLOSE(1)
       !PRINT *,'done with snapshot ' // TRIM(filename)
       istart = iend + 1
    END DO

    pos = pos * scaledist
    vel = vel * REAL(SQRT(a))

    !PRINT *, 'done with GADGET snapshot ' // snap(1:LEN_TRIM(snap))

  END SUBROUTINE read_gadget_dm_pos_vel_multiple

  SUBROUTINE fcoll_nofluc(densitycontr_arr, box, z, omega_m, omega_l, h, sigma_8, ns, omega_b, Mmin_arr, fcoll_all_Mmin_arr)

    USE onedspline, ONLY : spline, splint
    USE fcoll_grid!, ONLY : omega_m, omega_l, h, sigma_8, ns, omega_b, dn_dlnk, k_smooth, omega_r, delta_c, norm, rho_c, two_pi, D, conditional_dNdlnm_ellipcoll, a_ellipcoll, beta_ellipcoll, alpha_ellipcoll, norm_ellipcoll

    IMPLICIT NONE

    REAL, DIMENSION(:,:,:), INTENT(in) :: densitycontr_arr
    REAL, INTENT(in) :: box, z, omega_m, omega_l, h, sigma_8, ns, omega_b
    REAL, DIMENSION(21), INTENT(out) :: Mmin_arr
    REAL, DIMENSION(SIZE(densitycontr_arr,1), SIZE(densitycontr_arr,2), SIZE(densitycontr_arr,3), 21), INTENT(out) :: fcoll_all_Mmin_arr

    REAL :: dx, rho_m
    INTEGER :: ngrid, nMmin
    INTEGER :: num_spl
    DOUBLE PRECISION :: theta_spl, delta_lin_spl
    DOUBLE PRECISION, DIMENSION(:), ALLOCATABLE :: delta_NL_spl
    DOUBLE PRECISION, DIMENSION(:,:), ALLOCATABLE :: coeff 
    DOUBLE PRECISION :: theta_min, theta_max, dtheta

    DOUBLE PRECISION, DIMENSION(:), ALLOCATABLE :: mass_ell, fcoll_cond, dNdlnm_cond
    DOUBLE PRECISION, DIMENSION(:,:), ALLOCATABLE :: fcoll_cond_spl
    DOUBLE PRECISION :: log10Mmin, log10Mmax, dlog10m, dlnm, Mbig_spl

    INTEGER :: i, j, k, imass, isave
    DOUBLE PRECISION :: anorm, Dz

    om_m = DBLE(omega_m)
    om_l = DBLE(omega_l)
    h100 = DBLE(h)
    s8 = DBLE(sigma_8)
    n_s = DBLE(ns)
    om_b = DBLE(omega_b)


    ngrid = SIZE(densitycontr_arr, 1)

    rho_m = REAL(rho_c * omega_m * h ** 2)  !!! in Msun / Mpc^3
    dx = box / REAL(ngrid) / REAL(h)  !!! in Mpc


    dn_dlnk = 0.0
    k_smooth = 1.d5
    om_r = 0.d0

    anorm = norm(s8)
    delta_c = 1.686d0 / SQRT(anorm)


!!!! these bins are hard-coded because we have checked the results only for similar values
    log10Mmin = 7.0 !!! Msun
    log10mmax = 13.0 !!! Msun
    dlog10m = 0.01d0  !!! so 601 points
    dlnm = dlog10m * LOG(10.0)
    nMmin = 21

    ALLOCATE(mass_ell(601))
    isave = 0
    DO imass = 1, 601
       mass_ell(imass) = 10.d0 ** ( DBLE(imass-1) * dlog10m + log10Mmin)

       IF ( (MOD(imass,20) == 1) .AND. (LOG10(mass_ell(imass)) <= 11.0) ) THEN
          isave = isave + 1
          Mmin_arr(isave) = REAL(mass_ell(imass))
          !PRINT *, imass, LOG10(mass_ell(imass)), isave, imass / 20 + 1
       END IF
    END DO

    Dz = D(DBLE(z))

    a_ellipcoll = 0.67
    beta_ellipcoll = 0.4
    alpha_ellipcoll = 0.7
    norm_ellipcoll = 1.0

!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!


    theta_min = -two_pi
    theta_max = -theta_min
    num_spl = 50
    dtheta = (theta_max - theta_min) / DBLE(num_spl + 2)
    ALLOCATE(fcoll_cond_spl(nMmin, num_spl), delta_NL_spl(num_spl))

    DO i = 1, num_spl
       ALLOCATE(fcoll_cond(601), dNdlnm_cond(601))

       theta_spl = theta_min + DBLE(i) * dtheta
       IF (theta_spl < -1.e-12) THEN
          delta_lin_spl = - (3. / 20.) * 6 ** (2./3.) * (ABS(SINH(theta_spl) - theta_spl)) ** (2./3.)
          delta_NL_spl(i) =  - (10. * delta_lin_spl / (3. * (COSH(theta_spl) - 1.0))) ** 3 - 1.0
       ELSEIF (ABS(theta_spl) <= 1.e-12) THEN
          delta_lin_spl = 0.0
          delta_NL_spl(i) = 0.0
       ELSEIF (theta_spl > 1.e-12) THEN
          delta_lin_spl = (3. / 20.) * 6 ** (2./3.) * (theta_spl - SIN(theta_spl)) ** (2./3.)
          delta_NL_spl(i) =  (10. * delta_lin_spl / (3. * (1.0 - COS(theta_spl)))) ** 3 - 1.0
       END IF

       Mbig_spl = rho_m * (1.0 + delta_NL_spl(i)) * dx ** 3 !!! Msun
       dNdlnm_cond(601) = conditional_dNdlnm_ellipcoll(mass_ell(601), DBLE(Mbig_spl), DBLE(delta_lin_spl), Dz, SQRT(anorm))
       fcoll_cond(601) = 0.0


       DO imass = 600, 1, -1
          dNdlnm_cond(imass) = conditional_dNdlnm_ellipcoll(mass_ell(imass), DBLE(Mbig_spl), DBLE(delta_lin_spl), Dz, SQRT(anorm))
          fcoll_cond(imass) = fcoll_cond(imass+1) + 0.5 * REAL(dNdlnm_cond(imass) * mass_ell(imass) + dNdlnm_cond(imass+1) * mass_ell(imass+1)) * dlnm / Mbig_spl

          IF ( (MOD(imass,20) == 1) .AND. (LOG10(mass_ell(imass)) <= 11.0) ) THEN
             isave = imass / 20 + 1
             fcoll_cond_spl(isave, i) = fcoll_cond(imass)
          END IF


       END DO
       DEALLOCATE(fcoll_cond, dNdlnm_cond)
    END DO

    ALLOCATE(coeff(3,num_spl))

    DO isave = 1, nMmin
       CALL spline(delta_NL_spl, fcoll_cond_spl(isave,:), coeff(:, :))
       DO k = 1, ngrid
          DO j = 1, ngrid
             DO i = 1, ngrid
                fcoll_all_Mmin_arr(i,j,k, isave) = REAL( splint(delta_NL_spl, fcoll_cond_spl(isave,:), coeff(:,:), DBLE(densitycontr_arr(i,j,k))) )

                IF (fcoll_all_Mmin_arr(i,j,k, isave) < 0.0) THEN
                   IF (ABS(fcoll_all_Mmin_arr(i,j,k, isave)) > 1.e-6) THEN
                      PRINT *, 'Warning: problem with fcoll spline: ', isave,i,j,k, fcoll_all_Mmin_arr(i,j,k, isave)
                   ELSE
                      fcoll_all_Mmin_arr(i,j,k, isave) = 0.0
                   END IF
                END IF

             END DO
          END DO
       END DO
       !PRINT *, 'mass, ave fcoll, min, max fcoll = ', Mmin_arr(isave), SUM(DBLE(fcoll_all_Mmin_arr(:,:,:,isave)) * (1.d0 + DBLE(densitycontr_arr(:,:,:)))) / REAL(ngrid) ** 3, MINVAL(fcoll_all_Mmin_arr(:,:,:,isave)), MAXVAL(fcoll_all_Mmin_arr(:,:,:,isave))
    END DO



  END SUBROUTINE fcoll_nofluc

  INTEGER FUNCTION density_array_size(filename)
    IMPLICIT NONE
    CHARACTER(len=*), INTENT(in) :: filename

    OPEN (1, file=filename, form='unformatted',status='old',action='read')!, access='stream')
    READ(1)  density_array_size
    CLOSE(1)

  END FUNCTION density_array_size

  SUBROUTINE read_density_contrast_velocity(filename, ngrid, densitycontr_arr, velocity_arr, box, z, omega_m, omega_l, h)
    IMPLICIT NONE

    CHARACTER(len=*), INTENT(in) :: filename
    INTEGER, INTENT(in) :: ngrid
    REAL, DIMENSION(ngrid,ngrid,ngrid), INTENT(out) :: densitycontr_arr
    REAL, DIMENSION(3,ngrid,ngrid,ngrid), INTENT(out) :: velocity_arr
    REAL, INTENT(out) :: box, z, omega_m, omega_l, h

    INTEGER :: dummy_ngrid

    OPEN (1, file=filename, form='unformatted',status='old',action='read')!, access='stream')
    READ(1) dummy_ngrid, box, z, omega_m, omega_l, h
    !PRINT *,'Redshift, box, h = ',z,box,h
    !PRINT *,'omega_m, omega_l, h = ', omega_m,omega_l,h
    READ(1) densitycontr_arr
    READ(1) velocity_arr
    CLOSE(1)

    !PRINT *, 'done with density+velocity file ', TRIM(filename)

  END SUBROUTINE read_density_contrast_velocity

  INTEGER FUNCTION Mmin_array_size(filename)
    IMPLICIT NONE
    CHARACTER(len=*), INTENT(in) :: filename

    OPEN (1, file=filename, form='unformatted',status='old',action='read')!, access='stream')
    READ (1)  !!! header with cosmological parameters
    READ(1)  Mmin_array_size
    CLOSE(1)

  END FUNCTION Mmin_array_size



  SUBROUTINE read_fcoll(filename, ngrid, nMmin, Mmin_arr, fcoll_all_Mmin_arr, box, z, omega_m, omega_l, h, sigma_8, ns, omega_b)
    IMPLICIT NONE

    CHARACTER(len=*), INTENT(in) :: filename
    INTEGER, INTENT(in) :: ngrid, nMmin
    REAL, DIMENSION(nMmin), INTENT(out) :: Mmin_arr
    REAL, DIMENSION(ngrid,ngrid,ngrid,nMmin), INTENT(out) :: fcoll_all_Mmin_arr
    REAL, INTENT(out) :: box, z, omega_m, omega_l, h, sigma_8, ns, omega_b

    INTEGER :: dummy_ngrid, dummy_nMmin

    OPEN (1, file=filename, form='unformatted',status='old',action='read')!, access='stream')
    READ(1) dummy_ngrid, box, z, omega_m, omega_l, h, sigma_8, ns, omega_b
    !PRINT *,'Redshift=',z,box,h
    !PRINT *,'omega_m, omega_l, h = ', omega_m,omega_l,h
    READ(1) dummy_nMmin
    READ(1) Mmin_arr
    READ(1) fcoll_all_Mmin_arr
    CLOSE(1)

    !PRINT *, 'done with fcoll file ', TRIM(filename)

  END SUBROUTINE read_fcoll


  SUBROUTINE read_fcoll_one_Mmin(filename, ngrid, fcoll_arr, log10Mmin, box, z, omega_m, omega_l, h, sigma_8, ns, omega_b)
    IMPLICIT NONE

    CHARACTER(len=*), INTENT(in) :: filename
    INTEGER, INTENT(in) :: ngrid
    REAL, DIMENSION(ngrid,ngrid,ngrid), INTENT(out) :: fcoll_arr
    REAL, INTENT(out) :: log10Mmin, box, z, omega_m, omega_l, h, sigma_8, ns, omega_b

    INTEGER :: dummy_ngrid

    OPEN (1, file=filename, form='unformatted',status='old',action='read')!, access='stream')
    READ(1) dummy_ngrid, box, z, omega_m, omega_l, h, sigma_8, ns, omega_b
    READ(1) log10Mmin
    !PRINT *,'Redshift, box, h =',z,box,h
    !PRINT *,'omega_m, omega_l, h = ', omega_m,omega_l,h
    READ(1) fcoll_arr
    CLOSE(1)

    !PRINT *, 'done with fcoll file ', TRIM(filename)


  END SUBROUTINE read_fcoll_one_Mmin



  SUBROUTINE set_fcoll_field_spline(Mmin_arr, fcoll_all_Mmin_arr, coeff_spline_arr)
    USE onedspline, ONLY : spline
    IMPLICIT NONE

    REAL, DIMENSION(:), INTENT(in) :: Mmin_arr
    REAL, DIMENSION(:,:,:,:), INTENT(in) :: fcoll_all_Mmin_arr
    DOUBLE PRECISION, DIMENSION(SIZE(fcoll_all_Mmin_arr,1),SIZE(fcoll_all_Mmin_arr,2),SIZE(fcoll_all_Mmin_arr,3),3,SIZE(Mmin_arr)), INTENT(out) :: coeff_spline_arr
    

    INTEGER :: nMmin, ngrid
    INTEGER :: i, j, k


    IF (SIZE(Mmin_arr) == 1) RETURN

    nMmin = SIZE(Mmin_arr)
    ngrid = SIZE(fcoll_all_Mmin_arr, dim=1)

    DO k = 1, ngrid
       DO j = 1, ngrid
          DO i = 1, ngrid
             CALL spline(LOG10(DBLE(Mmin_arr)), LOG10(DBLE(fcoll_all_Mmin_arr(i,j,k, :)) + 1.d-32), coeff_spline_arr(i,j,k,:,:))
          END DO
       END DO
    END DO

  END SUBROUTINE set_fcoll_field_spline
 

  SUBROUTINE fcoll_one_Mmin_spline(log10Mmin, Mmin_arr, fcoll_all_Mmin_arr, coeff_spline_arr, fcoll_one_Mmin_arr)
    USE onedspline, ONLY : splint
    IMPLICIT NONE

    REAL, INTENT(in) :: log10Mmin
    REAL, DIMENSION(:), INTENT(in) :: Mmin_arr
    REAL, DIMENSION(:,:,:,:), INTENT(in) :: fcoll_all_Mmin_arr
    DOUBLE PRECISION, DIMENSION(:,:,:,:,:), INTENT(in) :: coeff_spline_arr
    REAL, DIMENSION(SIZE(fcoll_all_Mmin_arr,1), SIZE(fcoll_all_Mmin_arr,2), SIZE(fcoll_all_Mmin_arr,3)), INTENT(out) :: fcoll_one_Mmin_arr

    INTEGER :: ngrid
    INTEGER :: i, j, k

    ngrid = SIZE(fcoll_all_Mmin_arr, dim=1)

    DO k = 1, ngrid
       DO j = 1, ngrid
          DO i = 1, ngrid
             fcoll_one_Mmin_arr(i,j,k) = REAL(splint(LOG10(DBLE(Mmin_arr)), LOG10(DBLE(fcoll_all_Mmin_arr(i,j,k, :)) + 1.d-32), coeff_spline_arr(i,j,k,:,:), DBLE(log10Mmin)))
             fcoll_one_Mmin_arr(i,j,k) = 10.0 ** fcoll_one_Mmin_arr(i,j,k)
          END DO
       END DO
    END DO

  END SUBROUTINE fcoll_one_Mmin_spline

  SUBROUTINE zeta_fcoll_spline(zetafunc, Mmin, Mmax, dlog10M, Mmin_arr, fcoll_all_Mmin_arr, coeff_spline_arr, zeta_fcoll_arr)
    USE onedspline, ONLY : splint
    IMPLICIT NONE

    REAL, INTENT(inout) :: Mmin, Mmax, dlog10M !!! all masses are in M_sun
    REAL, DIMENSION(:), INTENT(in) :: Mmin_arr
    REAL, DIMENSION(:,:,:,:), INTENT(in) :: fcoll_all_Mmin_arr
    DOUBLE PRECISION, DIMENSION(:,:,:,:,:), INTENT(in) :: coeff_spline_arr
    REAL, DIMENSION(SIZE(fcoll_all_Mmin_arr,1), SIZE(fcoll_all_Mmin_arr,2), SIZE(fcoll_all_Mmin_arr,3)), INTENT(out) :: zeta_fcoll_arr
    INTERFACE
       FUNCTION zetafunc(M)
         REAL, INTENT(IN) :: M  !! mass in M_sun
         REAL :: zetafunc
       END FUNCTION zetafunc
    END INTERFACE
    EXTERNAL :: zetafunc


    INTEGER :: ngrid, nMmin, nMbins
    INTEGER :: i, j, k, iM
    REAL, DIMENSION(:), ALLOCATABLE :: log10M_arr, zeta_arr
    DOUBLE PRECISION, DIMENSION(:), ALLOCATABLE :: log10M_edge_arr
    REAL :: fcoll_lo, fcoll_hi
    

    ngrid = SIZE(fcoll_all_Mmin_arr, dim=1)
    nMmin = SIZE(Mmin_arr)

    Mmin = MAX(Mmin, Mmin_arr(1)) !! * 10.0 ** dlog10M)
    IF (LOG10(Mmax) > Mmin_arr(nMmin)) THEN 
       zeta_fcoll_arr(:,:,:) = zetafunc(Mmin_arr(nMmin)) * fcoll_all_Mmin_arr(:,:,:,nMmin) !! for M > 1.e11 M_sun, we assume zeta_fcoll = zeta(1.e11 M_sun) * fcoll(1.e11 M_sun - 1.e13 M_sun)
       Mmax = Mmin_arr(nMmin) !! / 10.0 ** dlog10M
    ELSE
       zeta_fcoll_arr(:,:,:) = 0.0
    END IF

    nMbins = CEILING( (LOG10(Mmax) - LOG10(Mmin)) / dlog10M)
    dlog10M = (LOG10(Mmax) - LOG10(Mmin)) / REAL(nMbins)
    !PRINT *, 'Mmin, Mmax, dlog10M = ', Mmin, Mmax, dlog10M

    ALLOCATE(log10M_arr(nMbins), zeta_arr(nMbins), log10M_edge_arr(nMbins+1))
    log10M_edge_arr(1) = LOG10(Mmin)
    DO iM = 1, nMbins
       log10M_edge_arr(iM+1) = log10M_edge_arr(iM) + DBLE(dlog10M)
       log10M_arr(iM) = REAL(0.5 * ( log10M_edge_arr(iM) + log10M_edge_arr(iM+1) ))
       zeta_arr(iM) = zetafunc(10.0 ** log10M_arr(iM))
    END DO
    !PRINT *, 'M_edge: ', log10M_edge_arr(1), log10M_edge_arr(nMbins + 1)
    !PRINT *, 'M_arr: ', log10M_arr(1), log10M_arr(nMbins)
    !PRINT *, 'zeta_arr: ', zeta_arr(1), zeta_arr(nMbins)
 
    DO k = 1, ngrid
       DO j = 1, ngrid
          DO i = 1, ngrid
             fcoll_lo = REAL(splint(LOG10(DBLE(Mmin_arr)), LOG10(DBLE(fcoll_all_Mmin_arr(i,j,k, :)) + 1.d-32), coeff_spline_arr(i,j,k,:,:), log10M_edge_arr(1)))
             fcoll_lo = 10.0 ** fcoll_lo
             DO iM = 1, nMbins
                fcoll_hi = REAL(splint(LOG10(DBLE(Mmin_arr)), LOG10(DBLE(fcoll_all_Mmin_arr(i,j,k, :)) + 1.d-32), coeff_spline_arr(i,j,k,:,:), log10M_edge_arr(iM+1)))
                fcoll_hi = 10.0 ** fcoll_hi
                zeta_fcoll_arr(i,j,k) = zeta_fcoll_arr(i,j,k) + (fcoll_lo - fcoll_hi) * zeta_arr(iM)
                fcoll_lo = fcoll_hi
             END DO
          END DO
       END DO
    END DO

  END SUBROUTINE zeta_fcoll_spline

  SUBROUTINE write_smooth_fields_from_gadget(gadget_snap, density_file, ngrid, scaledist)
    IMPLICIT NONE

    CHARACTER(len=*), INTENT(in) :: gadget_snap, density_file
    INTEGER, INTENT(in) :: ngrid
    REAL, INTENT(in) :: scaledist

    REAL, DIMENSION(:,:), ALLOCATABLE :: pos, vel
    REAL :: z, box, omega_m, omega_l, h

    INTEGER :: npart
    REAL, DIMENSION(ngrid,ngrid,ngrid) :: densitycontr_arr
    REAL, DIMENSION(3,ngrid,ngrid,ngrid) :: velocity_arr
    double precision :: delta_mean

    CALL read_gadget_header(gadget_snap, npart, box, z, omega_m, omega_l, h, scaledist)
    ALLOCATE(pos(3,npart), vel(3,npart))
    CALL read_gadget_dm_pos_vel(gadget_snap, npart, pos, vel, scaledist)

    CALL smooth_density_velocity_cic(pos,vel,box,ngrid,densitycontr_arr,velocity_arr)
    delta_mean = SUM(DBLE(densitycontr_arr)) / REAL(ngrid) ** 3
    densitycontr_arr = densitycontr_arr / REAL(delta_mean) - 1.0


    CALL write_density_velocity(density_file, densitycontr_arr, velocity_arr, z,box,omega_m,omega_l,h)


  END SUBROUTINE write_smooth_fields_from_gadget

  SUBROUTINE write_density_velocity(density_file, densitycontr_arr, velocity_arr, box, z, omega_m, omega_l, h)
    IMPLICIT NONE
    
    CHARACTER(len=*), INTENT(in) :: density_file
    REAL, DIMENSION(:,:,:), INTENT(in) :: densitycontr_arr
    REAL, DIMENSION(:,:,:,:), INTENT(in) :: velocity_arr
    REAL, INTENT(in) :: box, z, omega_m, omega_l, h

    INTEGER :: ngrid

    ngrid = SIZE(densitycontr_arr, 1)
    OPEN (1, file=TRIM(density_file), form='unformatted')
    WRITE(1) ngrid, box, z, omega_m, omega_l, h
    WRITE(1) densitycontr_arr
    WRITE(1) velocity_arr
    CLOSE(1)

  END SUBROUTINE write_density_velocity



  SUBROUTINE write_fcoll_all_Mmin_from_density(density_file, fcoll_all_Mmin_file, sigma_8, ns, omega_b)
    IMPLICIT NONE

    CHARACTER(len=*), INTENT(in) :: density_file, fcoll_all_Mmin_file
    REAL, INTENT(in) :: sigma_8, ns, omega_b

    REAL, DIMENSION(:,:,:), ALLOCATABLE :: densitycontr_arr
    REAL, DIMENSION(:), ALLOCATABLE :: Mmin_arr
    REAL, DIMENSION(:,:,:,:), ALLOCATABLE :: fcoll_all_Mmin_arr
    REAL :: box, z, omega_m, omega_l, h
    INTEGER :: ngrid, nMmin

    OPEN(1, file=TRIM(density_file), status='old', action='read', form='unformatted')
    READ(1) ngrid, box, z, omega_m, omega_l, h
    ALLOCATE(densitycontr_arr(ngrid,ngrid,ngrid))
    READ(1) densitycontr_arr
    CLOSE(1)

    nMmin = 21
    ALLOCATE(Mmin_arr(nMmin), fcoll_all_Mmin_arr(ngrid,ngrid,ngrid,nMmin))
    CALL fcoll_nofluc(densitycontr_arr, box, z, omega_m, omega_l, h, sigma_8, ns, omega_b, Mmin_arr, fcoll_all_Mmin_arr)

    CALL write_fcoll_all_Mmin(fcoll_all_Mmin_file, Mmin_arr, fcoll_all_Mmin_arr, box, z, omega_m, omega_l, h, sigma_8, ns, omega_b)

  END SUBROUTINE write_fcoll_all_Mmin_from_density



  SUBROUTINE write_fcoll_all_Mmin(fcoll_all_Mmin_file, Mmin_arr, fcoll_all_Mmin_arr, box, z, omega_m, omega_l, h, sigma_8, ns, omega_b)
    IMPLICIT NONE

    CHARACTER(len=*), INTENT(in) :: fcoll_all_Mmin_file
    REAL, DIMENSION(:), INTENT(in) :: Mmin_arr
    REAL, DIMENSION(:,:,:,:), INTENT(in) :: fcoll_all_Mmin_arr
    REAL, INTENT(in) :: box, z, omega_m, omega_l, h, sigma_8, ns, omega_b

    INTEGER :: nMmin, ngrid


    nMmin = SIZE(Mmin_arr)
    ngrid = SIZE(fcoll_all_Mmin_arr, 1)

    OPEN (1, file=TRIM(fcoll_all_Mmin_file), form='unformatted')
    WRITE(1) ngrid, box, z, omega_m, omega_l, h, sigma_8, ns, omega_b
    WRITE(1) nMmin
    WRITE(1) Mmin_arr
    WRITE(1) fcoll_all_Mmin_arr
    CLOSE(1)


  END SUBROUTINE write_fcoll_all_Mmin



END MODULE matter_fields
