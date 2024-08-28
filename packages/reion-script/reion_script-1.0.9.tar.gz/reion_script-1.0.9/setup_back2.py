import os
import sys
import subprocess
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install

NUMPY_MIN_VERSION = '1.24.4'

class CustomBuildExtCommand(build_ext):
    def run(self):
        try:
            import numpy
            print(f"numpy version: {numpy.__version__}")
        except ImportError:
            print("numpy is not installed. Installing now...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', f'numpy=={NUMPY_MIN_VERSION}'])
        build_ext.run(self)

    def build_extensions(self):
        # Customize the compiler options
        for ext in self.extensions:
            if self.compiler.compiler_type == 'unix':
                ext.extra_compile_args += ['-ffree-form', '-ffree-line-length-none']
        build_ext.build_extensions(self)

class CustomInstallCommand(install):
    def run(self):
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', f'numpy=={NUMPY_MIN_VERSION}'])
        install.run(self)

fftw_include_dir = os.path.expanduser('~/fftw/include')
fftw_lib_dir = os.path.expanduser('~/fftw/lib')

fftw_CFLAGS = ['-I' + fftw_include_dir]
fftw_LIBS = ['-L' + fftw_lib_dir, '-l:libfftw3.so', '-lm']

# Define the Fortran extension
fortran_sources = [
    './fortran/onedspline.f90',
    './fortran/nrint.f90',
    './fortran/powspec.f90',
    './fortran/sort_grid_points.f90',
    './fortran/pc.f90',
    './fortran/es.f90',
    './fortran/rsd.f90',
    './fortran/fcoll_grid.f90',
    './fortran/matter_fields.f90',
    './fortran/matter_fields_haloes.f90',
    './fortran/ionization_map.f90'
]

def get_extension():
    return Extension(
        name='script_fortran_modules',
        sources=fortran_sources,
        extra_compile_args=fftw_CFLAGS,
        extra_link_args=fftw_LIBS,
    )

setup(
    name='reion_script',
    version='1.0.5',  # Increment the version number
    author='Tirthankar Roy Choudhury',
    author_email='tirth@ncra.tifr.res.in',
    description='A semi-numerical code for reionization with explicit photon conservation',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    ext_modules=[get_extension()],
    cmdclass={
        'build_ext': CustomBuildExtCommand,
        'install': CustomInstallCommand,
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    setup_requires=[
        f'numpy=={NUMPY_MIN_VERSION}',
        'setuptools>=18.0',
    ],
    install_requires=[f'numpy=={NUMPY_MIN_VERSION}'],
)