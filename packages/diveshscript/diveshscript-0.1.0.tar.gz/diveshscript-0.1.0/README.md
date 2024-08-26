# script
## (*S*emi-numerical *C*ode for *R*e*I*onization with *P*ho*T*on-conservation)

This package allows you to generate the ionization field during the epoch of cosmological reionization using the photon-conserving algorithm of **Choudhury & Paranjape (2018)**.

# Download and Stay Updated

The most straightforward way to download the code and stay updated is to clone the latest version from [bitbucket](https://bitbucket.org/rctirthankar/script) to your local computer via git. While downloading the first time, you can clone the repository as:

~~~Bash
> git clone https://bitbucket.org/rctirthankar/script
~~~

For subsequent updates, just type:

~~~Bash
> git pull
~~~

# Installing the Code

After downloading the code, go to the folder **script** and type:

~~~Bash
> python setup.py install --user    ## assuming you do not have root access and want to install locally
~~~

Sometimes, after downloading the latest update of the code or after updating your OS, you may find difficulty in re-installing. This is because of some files leftover from the previous installation. In that case, try the following:
~~~Bash
> python setup.py clean --all
~~~

### Fortran compiler
Note that the installation requires a fortran compiler present in your computer (assumed to be gfortran). The default `setup.py` should be able to locate the compiler if it exists in the usual locations. In case the fortran compiler cannot be located (but is installed on your system), you can specify it explicitly using

~~~Bash
> F90=/full/path/to/f90 python setup.py install --user
~~~

### FFTW3 libraries
The FFTW3 libraries are needed for power spectra calculations. The `setup.py` looks for the FFTW3 installations in the usual locations. 

In case the FFTW3 libraries are already installed but could not be found, you can add the paths to the environmental variables as
~~~Bash
> export LIBRARY_PATH=$LIBRARY_PATH:/full/path/to/lib
> export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/full/path/to/lib
~~~

In case the above does not work, you can specify the path to the FFTW3 libraries by setting a new environmental variable
~~~Bash
> export FFTW_DIR=/full/path/to/fftw/
~~~
The above command(s) should be put in your .bash_profile or .bashrc file so that they are executed as soon as you login.

If the FFTW3 libraries are not installed on your machine, please install either using the software repository of your operating system or by directly downloading from [the FFTW3 website](http://www.fftw.org/download.html). Usually the following sequence is sufficient (do *not* forget the ``--enable-shared`` flag):
~~~Bash
> ./configure --enable-shared
> make
> make install
~~~
In case you do *not* have root access, you need to customize the configure command, for example:
~~~Bash
> ./configure --enable-shared --prefix=/full/path/to/installation/directory
~~~

### Optional: Download and Install MUSIC
`script` depends on density and velocity files obtained using a *N*-body simulation. A faster method of generating these fields is to use a 2LPT code. We recommend downloading and installing `MUSIC` from the [official website](https://bitbucket.org/ohahn/music/src/master/).

# Running the Code

For accessing the script modules, type

~~~python
import script
~~~

If you also want to use the utilities for running MUSIC, type

~~~python
from script import two_lpt
~~~

There are three main class objects which are used to run the code:

* *script.default_simulation_data*: Class object for reading GADGET-2 snapshot file and setting up CIC density and velocity fields.
* *script.matter_fields*: Class object containing the density, velocity and collapsed halo fields smoothed to the resolution at which the maps will be generated.
* *script.ionization_map*: Class object for making the ionization maps.

Please take a look at the examples below to get an idea about how to use the code.

# Examples

You can carry out some simple examples by running the python codes provided under the **script/examples** folder.

1. Simple examples which show how to make ionization maps, compute power spectra and plot them. These examples require a GADGET-2 snapshot, one sample is provided in **script/examples/snap_008**
	1. *example_1p01_plot_maps_and_power_spectrum.py*: plot two-dimensional slices of the matter and HI density fields and also plot the 21 cm power spectrum.
	2. *example_1p02_plot_maps_for_different_parameters.py*: plot two-dimensional slices of the HI density fields for different parameters and resolutions.
	3. *example_1p03_compare_photon_conserving_excursion_set.py*: compare HI maps and power spectra obtained using the photon-conserving (PC) and excursion-set (ES) methods.
	4. *example_1p04_make_reionization_movie.py*: make a movie of the HI fields by varying the global ionized fraction and also simultaneously plot the 21 cm power spectrum. Needs `ffmpeg` installed.
2. Examples which require MUSIC to be installed.
	1. *example_2p01_run_2lpt_music.py*: run MUSIC to generate 2LPT particle positions and velocities that are needed for ionization maps.
	2. *example_2p02_redshift_movie.py*: make a movie of the HI fields for a reionization history using the outputs from MUSIC and also simultaneously plot the 21 cm power spectrum.
	3. *example_2p03_light_cone.py*: make light cone map for a reionization history using the outputs from MUSIC.
3. Other examples.
	1. *example_3p01_zeta_function.py*: make HI maps using a mass-dependent efficiency parameter zeta.
	2. *example_3p02_UV_luminosity_function.py*: compute the UV luminosity function for the mass function used.

3. *script.ipynb*: a sample Jupyter notebook showing the basic capabilities of **script**.