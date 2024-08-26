MODULE nrint
CONTAINS

  FUNCTION qromb(func,a,b,eps)
    IMPLICIT NONE
    DOUBLE PRECISION, INTENT(IN) :: a,b,eps
    DOUBLE PRECISION :: qromb
    INTERFACE
       FUNCTION func(x)
         DOUBLE PRECISION, DIMENSION(:), INTENT(IN) :: x
         DOUBLE PRECISION, DIMENSION(size(x)) :: func
       END FUNCTION func
    END INTERFACE
    EXTERNAL :: func

    INTEGER, PARAMETER :: JMAX=20,JMAXP=JMAX+1,K=5,KM=K-1
    !DOUBLE PRECISION, PARAMETER :: EPS=1.0d-6
    DOUBLE PRECISION, DIMENSION(JMAXP) :: h,s
    DOUBLE PRECISION :: dqromb
    INTEGER :: j
    h(1)=1.d0
    do j=1,JMAX
       call trapzd(func,a,b,s(j),j)
       if (j >= K) then
          call polint(h(j-KM:j),s(j-KM:j),0.d0,qromb,dqromb)
          if (abs(dqromb) <= EPS*abs(qromb)) RETURN
       end if
       s(j+1)=s(j)
       h(j+1)=0.25*h(j)
       !PRINT *,'qromb:',j,ABS(dqromb)/ABS(qromb),eps,qromb,a,b
    end do
    PRINT *,'qromb: too many steps',ABS(dqromb)/ABS(qromb),qromb,a,b
  END FUNCTION qromb

  SUBROUTINE trapzd(func,a,b,s,n)
    IMPLICIT NONE
    DOUBLE PRECISION, INTENT(IN) :: a,b
    DOUBLE PRECISION, INTENT(INOUT) :: s
    INTEGER, INTENT(IN) :: n
    INTERFACE
       FUNCTION func(x)
         DOUBLE PRECISION, DIMENSION(:), INTENT(IN) :: x
         DOUBLE PRECISION, DIMENSION(size(x)) :: func
       END FUNCTION func
    END INTERFACE
    EXTERNAL :: func
    DOUBLE PRECISION :: del,fsum
    INTEGER :: it
    if (n == 1) then
       s=0.5*(b-a)*SUM(func( (/ a,b /) ))
    else
       it=2**(n-2)
       del=(b-a)/it
       fsum=sum(func(arth(a+0.5d0*del,del,it)))
       s=0.5*(s+del*fsum)
    end if
  END SUBROUTINE trapzd

  SUBROUTINE polint(xa,ya,x,y,dy)
    IMPLICIT NONE
    DOUBLE PRECISION, DIMENSION(:), INTENT(IN) :: xa,ya
    DOUBLE PRECISION, INTENT(IN) :: x
    DOUBLE PRECISION, INTENT(OUT) :: y,dy
    INTEGER :: m,n,ns
    DOUBLE PRECISION, DIMENSION(size(xa)) :: c,d,den,ho

    n=size(xa)
    c=ya
    d=ya
    ho=xa-x
    ns=iminloc(abs(x-xa))
    y=ya(ns)
    ns=ns-1
    do m=1,n-1
       den(1:n-m)=ho(1:n-m)-ho(1+m:n)
       if (any(den(1:n-m) == 0.0)) &
            stop 'polint: calculation failure'
       den(1:n-m)=(c(2:n-m+1)-d(1:n-m))/den(1:n-m)
       d(1:n-m)=ho(1+m:n)*den(1:n-m)
       c(1:n-m)=ho(1:n-m)*den(1:n-m)
       if (2*ns < n-m) then
          dy=c(ns+1)
       else
          dy=d(ns)
          ns=ns-1
       end if
       y=y+dy
    end do
  END SUBROUTINE polint

  FUNCTION arth(first,increment,n)
    IMPLICIT NONE
    DOUBLE PRECISION, INTENT(IN) :: first,increment
    INTEGER, INTENT(IN) :: n
    DOUBLE PRECISION, DIMENSION(n) :: arth
    INTEGER :: k,k2
    DOUBLE PRECISION :: temp
    INTEGER, PARAMETER :: NPAR_ARTH=16,NPAR2_ARTH=8
    if (n > 0) arth(1)=first
    if (n <= NPAR_ARTH) then
       do k=2,n
          arth(k)=arth(k-1)+increment
       end do
    else
       do k=2,NPAR2_ARTH
          arth(k)=arth(k-1)+increment
       end do
       temp=increment*NPAR2_ARTH
       k=NPAR2_ARTH
       do
          if (k >= n) exit
          k2=k+k
          arth(k+1:min(k2,n))=temp+arth(1:min(k,n-k))
          temp=temp+temp
          k=k2
       end do
    end if
  END FUNCTION arth

  FUNCTION iminloc(arr)
    IMPLICIT NONE
    DOUBLE PRECISION, DIMENSION(:), INTENT(IN) :: arr
    INTEGER, DIMENSION(1) :: imin
    INTEGER :: iminloc
    imin=minloc(arr(:))
    iminloc=imin(1)
  END FUNCTION iminloc


END MODULE nrint
