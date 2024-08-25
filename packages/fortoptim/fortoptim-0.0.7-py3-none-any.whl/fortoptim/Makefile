compile: gradient_module.o pso_utils.o

pso_utils.o:
	cd src/fortran/; \
	python -m numpy.f2py -c pso_utils.f90 -m pso_utils; \
	cd -

gradient_module.o:
	cd src/fortran/; \
	python -m numpy.f2py -c gradient_module.f90 -m gradient_module; \
	cd -

clean: 
	rm -f src/fortran/*.o
