import os
import subprocess
from setuptools import setup, find_packages
from numpy.distutils.core import Extension, setup

# Define local FFTW paths
fftw_include_dir = os.path.expanduser('~/fftw/include')
fftw_lib_dir = os.path.expanduser('~/fftw/lib')

fftw_CFLAGS = ['-I' + fftw_include_dir]
#fftw_LIBS = ['-L' + fftw_lib_dir, '-lfftw3', '-lm']
fftw_LIBS = ['-L' + fftw_lib_dir, '-l:libfftw3.so', '-lm']
# Define the Fortran extension
fortran_extension = Extension(
    name='script_fortran_modules',
    sources=[
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
    ],
    extra_compile_args=fftw_CFLAGS,
    extra_f90_compile_args=['-ffree-form', '-ffree-line-length-none'],
    extra_link_args=fftw_LIBS
)

setup(
    name='diveshscript',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A brief description of the package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/your-repo',
    packages=find_packages(),
    ext_modules=[fortran_extension],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy',
    ],
    setup_requires=[
        'numpy',
    ],
)