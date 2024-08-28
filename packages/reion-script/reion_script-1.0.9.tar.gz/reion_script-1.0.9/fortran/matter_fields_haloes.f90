MODULE matter_fields_haloes
CONTAINS

  SUBROUTINE read_gadget_halo_header(cataloguefile, nhalo)
    IMPLICIT NONE

    CHARACTER(len=*), INTENT(in) :: cataloguefile
    INTEGER, INTENT(out) :: nhalo
    INTEGER :: dum_int

    CHARACTER(len=200) :: infile
    LOGICAL :: multiple_files

    INQUIRE(FILE=TRIM(cataloguefile) // '.0', EXIST=multiple_files)
    IF (multiple_files) THEN
       infile = TRIM(cataloguefile) // '.0'
    ELSE
       infile = cataloguefile
    END IF

    OPEN (1, file=infile, form='unformatted', status='old', action='read', access='stream')
    READ(1) dum_int, dum_int, nhalo, dum_int
    CLOSE(1)
  END SUBROUTINE read_gadget_halo_header

  SUBROUTINE read_gadget_halo_catalogue(cataloguefile, nhalo, nparthalo, mhalo, xhalo, scaledist)
    IMPLICIT NONE

    CHARACTER(len=*), INTENT(in) :: cataloguefile
    INTEGER, INTENT(in) :: nhalo
    REAL, DIMENSION(3,nhalo), INTENT(out) :: xhalo
    REAL, DIMENSION(nhalo), INTENT(out) :: mhalo
    INTEGER, DIMENSION(nhalo), INTENT(out) :: nparthalo
    REAL, INTENT(in) :: scaledist
!!! scaledist = 1.0   if GADGET output positions are in units of Mpc/h
!!! scaledist = 1.e-3 if GADGET output positions are in units of kpc/h


    LOGICAL :: multiple_files

    INQUIRE(FILE=TRIM(cataloguefile) // '.0', EXIST=multiple_files)
    IF (multiple_files) THEN
       CALL read_gadget_halo_catalogue_multiple(cataloguefile, nhalo, nparthalo, mhalo, xhalo, scaledist)
    ELSE
       CALL read_gadget_halo_catalogue_single(cataloguefile, nhalo, nparthalo, mhalo, xhalo, scaledist)
    END IF

  END SUBROUTINE read_gadget_halo_catalogue

  SUBROUTINE read_gadget_halo_catalogue_single(cataloguefile, nhalo, nparthalo, mhalo, xhalo, scaledist)
    IMPLICIT NONE

    CHARACTER(len=*), INTENT(in) :: cataloguefile
    INTEGER, INTENT(in) :: nhalo
    REAL, DIMENSION(3,nhalo), INTENT(out) :: xhalo
    REAL, DIMENSION(nhalo), INTENT(out) :: mhalo
    INTEGER, DIMENSION(nhalo), INTENT(out) :: nparthalo
    REAL, INTENT(in) :: scaledist
!!! scaledist = 1.0   if GADGET output positions are in units of Mpc/h
!!! scaledist = 1.e-3 if GADGET output positions are in units of kpc/h
    
    INTEGER :: ngrp, dum_int, nfiles, i
    REAL, ALLOCATABLE :: grpCM(:,:)
    INTEGER, ALLOCATABLE :: grplen(:), grpoffset(:)
    INTEGER, ALLOCATABLE :: grplen_all(:,:)
    DOUBLE PRECISION, ALLOCATABLE :: grpmass_all(:,:)

    OPEN (1, file=cataloguefile, form='unformatted', status='old', action='read', access='stream')
    READ(1) ngrp, dum_int, ngrp, nfiles
    !PRINT *,'# of haloes', ngrp,  nhalo
    ALLOCATE(grplen(ngrp), grpoffset(ngrp), grpCM(3,ngrp))
    ALLOCATE(grplen_all(6,ngrp), grpmass_all(6,ngrp))
    READ(1) grplen, grpoffset, grplen_all, grpmass_all, grpCM
    CLOSE(1)

    !PRINT *,'sum grplen = ',SUM(grplen)
    DO i = 1, nhalo
       mhalo(i) = REAL(SUM(grpmass_all(:, i))) * 1.e10  !!! Msun / h
    END DO
    xhalo(:,:) = grpCM(:,:) * scaledist
    nparthalo(:) = grplen(:)
    !PRINT *,'sum nparthalo = ',SUM(nparthalo)
 

  END SUBROUTINE read_gadget_halo_catalogue_single

  SUBROUTINE read_gadget_halo_catalogue_multiple(cataloguefile, nhalo, nparthalo, mhalo, xhalo, scaledist)
    IMPLICIT NONE

    CHARACTER(len=*), INTENT(in) :: cataloguefile
    INTEGER, INTENT(in) :: nhalo
    REAL, DIMENSION(3,nhalo), INTENT(out) :: xhalo
    REAL, DIMENSION(nhalo), INTENT(out) :: mhalo
    INTEGER, DIMENSION(nhalo), INTENT(out) :: nparthalo
    REAL, INTENT(in) :: scaledist
!!! scaledist = 1.0   if GADGET output positions are in units of Mpc/h
!!! scaledist = 1.e-3 if GADGET output positions are in units of kpc/h


    INTEGER :: ngrp, dum_int, ngrp_i, nfiles, i, istart, iend
    REAL, ALLOCATABLE :: grpCM(:,:)
    INTEGER, ALLOCATABLE :: grplen(:), grpoffset(:)
    INTEGER, ALLOCATABLE :: grplen_all(:,:)
    DOUBLE PRECISION, ALLOCATABLE :: grpmass_all(:,:)
    CHARACTER*200 fnumber, filename

    OPEN (1, file=cataloguefile//'.0', form='unformatted', status='old', action='read', access='stream')
    READ(1) ngrp_i, dum_int, ngrp, nfiles
    !PRINT *,'# of haloes', ngrp,  nhalo
    CLOSE(1)
    ALLOCATE(grplen(ngrp), grpoffset(ngrp), grpCM(3,ngrp))
    ALLOCATE(grplen_all(6,ngrp), grpmass_all(6,ngrp))

    fnumber = ''
    istart = 1
    DO i = 0, nfiles-1
       IF (i < 10) THEN
          WRITE(fnumber,'(I1)') i
       ELSEIF (i < 100) THEN
          WRITE(fnumber,'(I2)') i
       ELSEIF (i < 1000) THEN
          WRITE(fnumber,'(I3)') i
       END IF
       filename = cataloguefile(1:len_TRIM(cataloguefile)) // '.' // fnumber(1:LEN_TRIM(fnumber))
       OPEN (1, file=filename, form='unformatted', status='old', action='read', access='stream')
       READ(1) ngrp_i, dum_int, ngrp, nfiles
       iend = istart + ngrp_i - 1
       
       READ(1) grplen(istart:iend), grpoffset(istart:iend), grplen_all(:,istart:iend), grpmass_all(:,istart:iend), grpCM(:,istart:iend)
       CLOSE(1)
       istart = iend + 1
    END DO

    !PRINT *,'sum grplen = ',SUM(grplen)
    DO i = 1, nhalo
       mhalo(i) = REAL(SUM(grpmass_all(:, i))) * 1.e10  !!! Msun / h
    END DO
    xhalo(:,:) = grpCM(:,:) * scaledist
    nparthalo(:) = grplen(:)
    !PRINT *,'sum nparthalo = ',SUM(nparthalo)

  END SUBROUTINE read_gadget_halo_catalogue_multiple

  SUBROUTINE smooth_halo_field_cic(xhalo,mhalo,box,ngrid,density)
    USE matter_fields
    IMPLICIT NONE
    REAL, DIMENSION(:,:), INTENT(in) :: xhalo
    REAL, DIMENSION(:), INTENT(in) :: mhalo
    REAL, intent(in) :: box
    INTEGER, INTENT(in) :: ngrid
    REAL, DIMENSION(ngrid,ngrid,ngrid), INTENT(out) :: density

    INTEGER :: nhalo,i,i1,j1,k1,ii,jj,kk,iii,jjj,kkk
    REAL, DIMENSION(2) :: ci,cj,ck

    nhalo = SIZE(xhalo,dim=2)
    density = 0.0
    DO i = 1, nhalo
       CALL cic(xhalo(1,i) * REAL(ngrid) / box,i1,ci)
       CALL cic(xhalo(2,i) * REAL(ngrid) / box,j1,cj)
       CALL cic(xhalo(3,i) * REAL(ngrid) / box,k1,ck)

       DO kk = 1, 2
          kkk = iperi(kk + k1 - 1, ngrid)
          DO jj = 1, 2
             jjj = iperi(jj + j1 - 1, ngrid)
             DO ii = 1, 2
                iii = iperi(ii + i1 - 1, ngrid)
                density(iii,jjj,kkk) = density(iii,jjj,kkk) + ci(ii) * cj(jj) * ck(kk) * mhalo(i)
             ENDDO
          ENDDO
       ENDDO
    END DO
  END SUBROUTINE smooth_halo_field_cic

END MODULE matter_fields_haloes
