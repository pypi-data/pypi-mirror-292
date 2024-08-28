
#FOMP = -fopenmp # -w
F90C = gfortran -ffree-form -ffree-line-length-none #-fbounds-check -fcheck=all -g
#F90C = mpif90 -ffree-form -ffree-line-length-none #-fbounds-check -fcheck=all -g
#FFLAGS_WARN = -pg
#FFLAGS_WARN = -warn argument_checking -warn unused -warn truncated_source
#FFLAGS_WARN = -Wall -Wextra
#FFLAGS_WARN = -warn unused -fpp2
#FFLAGS_WARN = -g -fcheck=all -Wall
#FFLAGS = -lm -Vaxlib -lsvml
FFFTW = -lfftw3f_threads -lfftw3f -lfftw3l -lfftw3l_threads -lfftw3 -lm
#FFFTW = -lfftw3f -lfftw3l -lfftw3 -lm
FLAPACK = -llapack


.SUFFIXES: .f90 .o
.f90.o:
	$(F90C) $(FFLAGS) ${FFLAGS_WARN} -c $<

.SUFFIXES: .F90 .o
.F90.o:
	$(F90C) $(FFLAGS) ${FFLAGS_WARN} -c $<

.f.o:
	$(F90C) $(FFLAGS) ${FFLAGS_WARN} -c $<


script:
	make clean; f2py -c ${FFFTW} -m script onedspline.f90 nrint.f90 powspec.f90 sort_grid_points.f90 pc.f90 es.f90 rsd.f90 fcoll_grid.f90 matter_fields.f90 matter_fields_haloes.f90 ionization_map.f90 --f90flags="-ffree-form -ffree-line-length-none"

check:
	${F90C} -c ${FFFTW} onedspline.f90 nrint.f90 powspec.f90 sort_grid_points.f90 pc.f90 es.f90 rsd.f90 fcoll_grid.f90 matter_fields.f90 matter_fields_haloes.f90 ionization_map.f90

clean:
	@echo 'removing unnecesary files...'
	@rm -f *~
	@rm -f *.mod
	@rm -f *.o
	@rm -f *.flc
	@rm -f *.so
