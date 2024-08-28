MODULE powspec

  REAL, PARAMETER :: pi=3.14159265
  REAL, PARAMETER :: two_pi=2.0*pi

CONTAINS

  SUBROUTINE initialize_plan(plan, n, FFTW_IFINV,FFTW_estimate, box, kfft)
    IMPLICIT NONE

    INTEGER*8, INTENT(out) :: plan
    INTEGER, INTENT(in) :: n, FFTW_IFINV, FFTW_ESTIMATE
    REAL, INTENT(in) :: box
    REAL, DIMENSION(n), INTENT(out) :: kfft

    DOUBLE COMPLEX, DIMENSION(:,:,:), ALLOCATABLE :: deltak

    INTEGER :: i

    ALLOCATE(deltak(n,n,n))
    
    !Note : kmax=2*pi*range and delta_k=delta*2*pi
    !l=2*pi/delta_k=n/(2*range) is the total box size.
    
    FORALL (i=1:n) kfft(i)=(REAL(i-1) - 0.5*REAL(n)) / box *2.0*pi

    CALL dfftw_plan_dft_3d(plan,n,n,n,deltak,deltak,FFTW_IFINV,FFTW_estimate)
  END SUBROUTINE initialize_plan

  SUBROUTINE get_kmag(kpow, kmag)
    IMPLICIT NONE

    REAL, DIMENSION(:), INTENT(in) :: kpow
    REAL, DIMENSION(SIZE(kpow),SIZE(kpow),SIZE(kpow)), INTENT(out) :: kmag
    
    INTEGER :: ngrid, i,j,k

    ngrid = SIZE(kpow)
    DO k = 1, ngrid
       DO j = 1, ngrid
          DO i = 1, ngrid
             kmag(i,j,k) = SQRT(kpow(i) ** 2 + kpow(j) ** 2 + kpow(k) ** 2)
          END DO
       END DO
    END DO
  END SUBROUTINE get_kmag

  SUBROUTINE complexify(delta, deltak)
    IMPLICIT NONE
    REAL, DIMENSION(:,:,:), INTENT(in) :: delta
    DOUBLE COMPLEX, DIMENSION(SIZE(delta,1), SIZE(delta,2), SIZE(delta,3)), INTENT(out) :: deltak

    INTEGER :: i,j,k,n

    n = SIZE(delta, dim=1)

    !!$OMP PARALLEL DO DEFAULT(SHARED) PRIVATE (i,j,k)
    DO k=1,n
       DO j=1,n
          DO i=1,n
             deltak(i,j,k) = CMPLX(DBLE(delta(i,j,k))/(-1.d0)**(i+j+k-3), 0.d0, kind=8)
!!$             deltak(i,j,k)=CMPLX(delflux(i,j,k),0.0)
          END DO
       END DO
    END DO
    !PRINT *,'ps_delta: done delta, start fft'
  END SUBROUTINE complexify

  SUBROUTINE destroy_plan(plan)
    IMPLICIT NONE
    INTEGER*8, INTENT(inout) :: plan

    CALL dfftw_destroy_plan(plan)
  END SUBROUTINE destroy_plan

  SUBROUTINE pspec_fftw(plan, deltak, box, power)
    IMPLICIT NONE

    REAL, INTENT(in) :: box
    DOUBLE COMPLEX, DIMENSION(:,:,:), INTENT(inout) :: deltak
    REAL, DIMENSION(SIZE(deltak,1), SIZE(deltak,2), SIZE(deltak,3)), INTENT(out) :: power
    INTEGER*8, INTENT(inout) :: plan

    INTEGER :: n

    n = SIZE(deltak, dim=1)

    !CALL dfftw_execute(plan)
    CALL dfftw_execute_dft(plan, deltak, deltak)
    !!$OMP WORKSHARE
    deltak=deltak*SQRT(box**3)/n**3
    power = REAL(ABS(deltak)) ** 2
    !!$OMP END WORKSHARE
    
  END SUBROUTINE pspec_fftw

  SUBROUTINE pspec_cross_fftw(plan, deltak1, deltak2, box, power)
    IMPLICIT NONE

    REAL, INTENT(in) :: box
    DOUBLE COMPLEX, DIMENSION(:,:,:), INTENT(inout) :: deltak1, deltak2
    REAL, DIMENSION(SIZE(deltak1,1), SIZE(deltak1,2), SIZE(deltak1,3)), INTENT(out) :: power
    INTEGER*8, INTENT(inout) :: plan

    INTEGER :: n

    n = SIZE(deltak1, dim=1)

    !CALL dfftw_execute(plan)
    CALL dfftw_execute_dft(plan, deltak1, deltak1)
    CALL dfftw_execute_dft(plan, deltak2, deltak2)
    !!$OMP WORKSHARE
    deltak1=deltak1*SQRT(box**3)/n**3
    deltak2=deltak2*SQRT(box**3)/n**3
    power = REAL( REAL(deltak1) * REAL(deltak2) + AIMAG(deltak1) * AIMAG(deltak2) )
    !!$OMP END WORKSHARE
    
  END SUBROUTINE pspec_cross_fftw

  SUBROUTINE compute_powspec(plan, input_field, box, powspec_field, convolve)
    IMPLICIT NONE

    INTEGER*8, INTENT(inout) :: plan
    REAL, DIMENSION(:,:,:), INTENT(in) :: input_field
    REAL, INTENT(in) :: box
    REAL, DIMENSION(SIZE(input_field,1), SIZE(input_field,2), SIZE(input_field,3)), INTENT(out) :: powspec_field
    LOGICAL, INTENT(in) :: convolve

    DOUBLE COMPLEX, DIMENSION(:,:,:), ALLOCATABLE :: deltak
    INTEGER :: ngrid

    ngrid = SIZE(input_field,1)
    ALLOCATE(deltak(ngrid,ngrid,ngrid))

    CALL complexify(input_field, deltak)
    CALL pspec_fftw(plan, deltak, box, powspec_field)

    IF (convolve) CALL deconvolve_power(powspec_field, box)

  END SUBROUTINE compute_powspec

  SUBROUTINE compute_cross_powspec(plan, input_field1, input_field2, box, powspec_field, convolve)
    IMPLICIT NONE

    INTEGER*8, INTENT(inout) :: plan
    REAL, DIMENSION(:,:,:), INTENT(in) :: input_field1, input_field2
    REAL, INTENT(in) :: box
    REAL, DIMENSION(SIZE(input_field1,1), SIZE(input_field1,2), SIZE(input_field1,3)), INTENT(out) :: powspec_field
    LOGICAL, INTENT(in) :: convolve

    DOUBLE COMPLEX, DIMENSION(:,:,:), ALLOCATABLE :: deltak1, deltak2
    INTEGER :: ngrid

    ngrid = SIZE(input_field1,1)
    ALLOCATE(deltak1(ngrid,ngrid,ngrid), deltak2(ngrid,ngrid,ngrid))

    CALL complexify(input_field1, deltak1)
    CALL complexify(input_field2, deltak2)
    CALL pspec_cross_fftw(plan, deltak1, deltak2, box, powspec_field)

    IF (convolve) CALL deconvolve_power(powspec_field, box)

  END SUBROUTINE compute_cross_powspec


  SUBROUTINE deconvolve_power(power, box)
    IMPLICIT NONE

    REAL, INTENT(in) :: box
    REAL, DIMENSION(:,:,:), INTENT(inout) :: power

    REAL, DIMENSION(:), ALLOCATABLE :: kfft
    INTEGER :: n, i, j, k
    REAL :: dx, kernel

    n = SIZE(power, dim=1)
    dx = box / REAL(n)
    ALLOCATE(kfft(n))
    FORALL (i=1:n) kfft(i) = (REAL(i-1) - 0.5 * REAL(n)) / box * two_pi

    !PRINT *, 'dx = ', dx, dx * MINVAL(ABS(kfft)), dx * MAXVAL(ABS(kfft))
    DO k = 1, n
       DO j = 1, n
          DO i = 1, n
             IF (kfft(i) * kfft(j) * kfft(k) /= 0.0) THEN
                kernel = (SIN(0.5 * kfft(i) * dx) * SIN(0.5 * kfft(j) * dx) * SIN(0.5 * kfft(k) * dx)) / ((0.5 * kfft(i) * dx) * (0.5 * kfft(j) * dx) * (0.5 * kfft(k) * dx))
                power(i,j,k) = power(i,j,k) / kernel ** 2
                !IF (kernel ** 2 < 0.1) PRINT *, 'kernel: ', kfft(i), kfft(j), kfft(k), SQRT(kfft(i) ** 2 + kernel
             END IF
          END DO
       END DO
    END DO

    DEALLOCATE(kfft)

    
  END SUBROUTINE deconvolve_power
 

  SUBROUTINE bin_powspec(k_edges, kmag, pspec, pspec_binned, kount, k_bins)
    IMPLICIT NONE

    REAL, DIMENSION(:), INTENT(in) :: k_edges
    REAL, DIMENSION(:,:,:), INTENT(in) :: pspec, kmag
    REAL, DIMENSION(SIZE(k_edges)-1), INTENT(out) :: pspec_binned, kount, k_bins
    
    LOGICAL, DIMENSION(:,:,:), ALLOCATABLE :: mask
    REAL :: pow
    
    INTEGER ::  ngrid, nbins
    INTEGER :: ibin
    
    ngrid = SIZE(kmag, dim=1)
    nbins = SIZE(k_edges) - 1

    ALLOCATE(mask(ngrid, ngrid, ngrid))    
    
    DO ibin = 1, nbins
       mask =  kmag >= k_edges(ibin) .AND. kmag < k_edges(ibin+1)
       
       kount(ibin) = REAL(COUNT(mask))

       IF (kount(ibin) > 0) THEN
          pow = REAL(SUM(DBLE(pspec), mask))
          pspec_binned(ibin) = pow / kount(ibin)
          pow = REAL(SUM(DBLE(kmag), mask))  !!!! this is the sum of all k-values
          k_bins(ibin) = pow / kount(ibin)
       ELSE
          pspec_binned(ibin) = 0.0
          k_bins(ibin) = 0.5 * (k_edges(ibin) + k_edges(ibin+1))
       END IF
    END DO
    RETURN

  END SUBROUTINE bin_powspec

END MODULE powspec
