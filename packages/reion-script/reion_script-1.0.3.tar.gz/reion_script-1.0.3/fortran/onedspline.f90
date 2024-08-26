MODULE onedspline

CONTAINS

  SUBROUTINE spline(x,f,c)
    IMPLICIT NONE

    DOUBLE PRECISION, DIMENSION(:), INTENT(in) :: x,f
    DOUBLE PRECISION, DIMENSION(3,SIZE(x)), INTENT(out) :: c
    INTEGER :: i,j,n
    DOUBLE PRECISION :: div12,div23,c1,cn,g

    n=SIZE(x)
    IF(n <= 1) THEN
       PRINT *, 'bad n input in splint'
       STOP

    ELSE IF(n == 2) THEN
       c(1,1)=(f(2)-f(1))/(x(2)-x(1))
       c(2,1)=0.d0
       c(3,1)=0.d0
       RETURN

    ELSE IF(n == 3) THEN
       div12=(f(2)-f(1))/(x(2)-x(1))
       div23=(f(3)-f(2))/(x(3)-x(2))
       c(3,1)=0.d0
       c(3,2)=0.d0
       c(2,1)=(div23-div12)/(x(3)-x(1))
       c(2,2)=c(2,1)
       c(1,1)=div12+c(2,1)*(x(1)-x(2))
       c(1,2)=div23+c(2,1)*(x(2)-x(3))
       RETURN

    ELSE
       c(3,n)=(f(n)-f(n-1))/(x(n)-x(n-1))
       DO i=n-1,2,-1
          c(3,i)=(f(i)-f(i-1))/(x(i)-x(i-1))
          c(2,i)=2.d0*(x(i+1)-x(i-1))
          c(1,i)=3.d0*(c(3,i)*(x(i+1)-x(i))+c(3,i+1)*(x(i)-x(i-1)))
       ENDDO
       c1=x(3)-x(1)
       c(2,1)=x(3)-x(2)
       c(1,1)=c(3,2)*c(2,1)*(2.d0*c1+x(2)-x(1))+c(3,3)*(x(2)-x(1))**2
       c(1,1)=c(1,1)/c1
       cn=x(n)-x(n-2)
       c(2,n)=x(n-1)-x(n-2)
       c(1,n)=c(3,n)*c(2,n)*(2.d0*cn+x(n)-x(n-1))
       c(1,n)=(c(1,n)+c(3,n-1)*(x(n)-x(n-1))**2)/cn

       !PRINT *, 'spline [c(1,n)-1]:', c(1,n)

       g=(x(3)-x(2))/c(2,1)
       c(2,2)=c(2,2)-g*c1
       c(1,2)=c(1,2)-g*c(1,1)
       DO j=2,n-2
          g=(x(j+2)-x(j+1))/c(2,j)
          c(2,j+1)=c(2,j+1)-g*(x(j)-x(j-1))
          c(1,j+1)=c(1,j+1)-g*c(1,j)
       ENDDO
       g=cn/c(2,n-1)
       c(2,n)=c(2,n)-g*(x(n-1)-x(n-2))
       c(1,n)=c(1,n)-g*c(1,n-1)
       !PRINT *, 'spline [c(1,n)-2]:', c(1,n)


       c(1,n)=c(1,n)/c(2,n)
       !PRINT *, 'spline [c(1,n)-3]:', c(1,n)
       !IF (n==19) PRINT *, 'spline-1:', c(1:3, 8),c(1:3, 1)
       DO i=n-1,2,-1
          c(1,i)=(c(1,i)-c(1,i+1)*(x(i)-x(i-1)))/c(2,i)
          !IF (n==19) PRINT *, 'spline-loop:', i,n,c(1,i), c(1,i+1), c(2,i), x(i), x(i-1)
       ENDDO
       !IF (n==19) PRINT *, 'spline-2:', c(1:3, 8),c(1:3, 1)
       c(1,1)=(c(1,1)-c(1,2)*c1)/c(2,1)

       DO i=1,n-1
          c(2,i)=(3.d0*c(3,i+1)-2.d0*c(1,i)-c(1,i+1))/(x(i+1)-x(i))
          c(3,i)=(c(1,i)+c(1,i+1)-2.d0*c(3,i+1))/(x(i+1)-x(i))**2
       ENDDO
       c(2,n)=0.d0
       c(3,n)=0.d0
    ENDIF


    RETURN
  END SUBROUTINE spline


  FUNCTION splint(x,f,c,xb)
    IMPLICIT NONE

    DOUBLE PRECISION, INTENT(in) :: xb
    DOUBLE PRECISION, DIMENSION(:), INTENT(in) :: x,f
    DOUBLE PRECISION, DIMENSION(3,SIZE(x)), INTENT(in) :: c
    DOUBLE PRECISION :: splint
    INTEGER :: n,low
    DOUBLE PRECISION :: dx

    n=SIZE(x)
    low=0
    IF(n <= 1) THEN
       PRINT *, 'bad n input in splint'
       STOP
    END IF

    low=locate(x,xb)
    dx=xb-x(low)
    splint=((c(3,low)*dx+c(2,low))*dx+c(1,low))*dx+f(low)
    !IF (n==19) PRINT *, 'splint:', xb, low, dx, splint, c(1:3, low), f(low)

  END FUNCTION splint


  FUNCTION locate(xx,x)
    IMPLICIT NONE
    DOUBLE PRECISION, DIMENSION(:), INTENT(IN) :: xx
    DOUBLE PRECISION, INTENT(IN) :: x
    INTEGER :: locate

    INTEGER :: n,jl,jm,ju
    LOGICAL :: ascnd

    n=SIZE(xx)
    ascnd = (xx(n) >= xx(1))
    jl=0
    ju=n+1
    DO
       IF (ju-jl <= 1) EXIT
       jm=(ju+jl)/2
       IF (ascnd .EQV. (x >= xx(jm))) THEN
          jl=jm
       ELSE
          ju=jm
       END IF
    END DO
    IF (x == xx(1)) THEN
       locate=1
    ELSE IF (x == xx(n)) THEN
       locate=n-1
    ELSE
       locate=jl
    END IF
  END FUNCTION locate

END MODULE onedspline
