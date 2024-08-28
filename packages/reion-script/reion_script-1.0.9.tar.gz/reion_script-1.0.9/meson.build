project('reion_script', 'fortran',
        version : '1.0.9',
        default_options : ['warning_level=3'])

py_mod = import('python')
py3 = py_mod.find_installation()
py3_dep = py3.dependency()

# Use Python to find NumPy and ensure the correct version is installed
numpy_include = run_command(py3, '-c', '''
import sys
import subprocess
try:
    import numpy
    from packaging import version
    if version.parse(numpy.__version__) != version.parse("1.24.4"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.24.4"])
        import numpy  # Re-import to get the new version
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.24.4"])
    import numpy
print(numpy.get_include())
''', check: true).stdout().strip()

# Expand user directory for FFTW paths
fftw_include_dir = run_command('sh', '-c', 'echo $HOME/fftw/include').stdout().strip()
fftw_lib_dir = run_command('sh', '-c', 'echo $HOME/fftw/lib').stdout().strip()

fortran_sources = [
    'fortran/onedspline.f90',
    'fortran/nrint.f90',
    'fortran/powspec.f90',
    'fortran/sort_grid_points.f90',
    'fortran/pc.f90',
    'fortran/es.f90',
    'fortran/rsd.f90',
    'fortran/fcoll_grid.f90',
    'fortran/matter_fields.f90',
    'fortran/matter_fields_haloes.f90',
    'fortran/ionization_map.f90'
]

fftw_lib = meson.get_compiler('fortran').find_library('fftw3', dirs : [fftw_lib_dir])

py3.extension_module('script_fortran_modules',
                     fortran_sources,
                     include_directories : [include_directories(fftw_include_dir), include_directories(numpy_include)],
                     dependencies : [py3_dep, fftw_lib],
                     install : true,
                     fortran_args : ['-ffree-form', '-ffree-line-length-none'])

subdir('script')