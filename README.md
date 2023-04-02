<p align="center">
<img src="https://github.com/schlegelp/navis-flybrains/blob/main/_static/flybrains_logo.png?raw=true" width="400">
</p>

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5515281.svg)](https://doi.org/10.5281/zenodo.5515281)

# navis-flybrains
Transforms to map between different _Drosophila_ template brains. Intended to be used with [navis](https://github.com/schlegelp/navis).

This library is analogous to Greg Jefferis' [nat.templatebrains](https://github.com/natverse/nat.templatebrains), [nat.jrcbrains](https://github.com/natverse/nat.jrcbrains) and [nat.flybrains](https://github.com/natverse/nat.flybrains) for R.

`flybrains` ships with:

- meta data + surface meshes for 22 template brains and nerve cords
- an Elastix transform between `FANC` and `JRCVNC2018F` kindly shared by Jasper Phelps
- a landmark-based transform between `MANC` and `FANC`
- mirror transforms for `FAFB14` and `FANC`

There are plenty additional transforms that need to be downloaded separately (see below).

## Installation
You can install `flybrains` from PyPI:

```bash
pip3 install flybrains
```

### External dependencies
In order to use the Jefferis lab or VFB transforms, you will need to have
[CMTK](https://www.nitrc.org/projects/cmtk/) installed.

For the FANC to JRCVNC2018F transform, you will need to download
[elastix](https://elastix.lumc.nl/index.php) and make sure that the path
to the binaries is in your `PATH` variable.

## Usage

<p align="center">
<img src="https://github.com/schlegelp/navis-flybrains/blob/main/_static/bridging_graph.png?raw=true" width="800">
</p>

It's highly recommended that after install, you download the (optional)
bridging transforms to map between template brains/nerve cords.

**IMPORTANT**: the URL for the JRC2018F <-> JRC2018M transform (`JRC2018U_JRC2018M.h5`)
was incorrect in `flybrains` version `0.2.6`. If you downloaded it using that
version of flybrains you need to manually remove the file, update flybrains and
download again using a newer version.

> :exclamation: If you already have downloaded these registrations via `nat.jrcbrains` and/or `nat.flybrains` you can skip this: `flybrains` should be able to find the registrations downloaded via R and register them for you (see also code at the bottom).

```Python
>>> import flybrains

# This downloads (or updates) various CMTK bridging and mirror transforms
# generated or collated by the Jefferis lab - see docstring for details
>>> flybrains.download_jefferislab_transforms()

# This downloads H5 bridging transforms between JRC brain templates
# (Saalfeld lab, Janelia Research Campus) - see docstring for details
>>> flybrains.download_jrc_transforms()

# This downloads H5 bridging transforms between JRC VNC templates
# (Saalfeld lab, Janelia Research Campus) - see docstring for details
>>> flybrains.download_jrc_vnc_transforms()

# This downloads (or updates) various CMTK bridging and mirror transforms
# generated or collated by VirtualFlyBrain.org - see docstring for details
>>> flybrains.download_vfb_transforms()

# Register the transforms - this is only necessary if you just downloaded them
# Alternatively just restart your Python session and import flybrains
>>> flybrains.register_transforms()
```

In the future, simply importing `flybrains` is sufficient to make the
transforms available to [navis](https://navis.readthedocs.io/en/latest/):

```Python
>>> import navis
>>> import flybrains
>>> import numpy as np
>>> points = np.array([[429536, 205240,  38400]])
>>> navis.xform_brain(points, source='FAFB', target='JRC2018F')
array([[241.53969657, 100.99399233,  35.96977733]])
```

Please see the [transform tutorial](https://navis.readthedocs.io/en/latest/source/tutorials/transforming.html)
for `navis` to learn how to transform more complex data.

To check which transforms are available (either downloaded or via R) you can
run this:

```Python
>>> # Generate a report - note the mix of transforms downloaded via Python and R
>>> flybrains.report()
Flybrains Status Report
=======================
Data Home: /Users/philipps/flybrain-data

CMTK registrations (Jefferis lab/VFB): 41 of 45
H5 registrations (JRC/Saalfeld lab): 3 of 8

nat regdirs
-----------
~/Library/Application Support/rpkg-nat.templatebrains/regfolders: 41 CMTK | 0 H5 transforms
/Library/Frameworks/R.framework/Versions/3.6/Resources/library/nat.flybrains/extdata/bridgingregistrations: 5 CMTK | 0 H5 transforms
/Library/Frameworks/R.framework/Versions/3.6/Resources/library/nat.flybrains/extdata/mirroringregistrations: 5 CMTK | 0 H5 transforms
~/Library/Application Support/R/nat.jrcbrains: 0 CMTK | 5 H5 transforms
```

Meta data and surface meshes for the template brains/VNCs are readily accessible:

```Python
>>> flybrains.FAFB14
Template brain
--------------
Name: Full Adult Fly Brain
Short Name: FAFB14
Type: None
Sex:  female
Dimensions: 165372 x 80745 x 6730 voxels
Voxel size:
  x = 4 nanometers
  y = 4 nanometers
  z = 40 nanometers
Bounding box (nanometers):
  x = 192200, y = 75853, z = 2007,
  x = 853686, y = 398832, z = 271205,
Description: SSTEM volume comprising an entire female Drosophila brain was imaged at
 4x4x40nm by Zheng et al. (2018) and is availabe for download at
https://temca2data.org/. The meta data and associated mesh represent
version 14 (FAFB14) of this data set.
DOI: 10.1016/j.cell.2018.06.019
```

Most templates come with a mesh e.g. for plotting via navis:

```Python
>>> flybrains.FAFB14.mesh
<trimesh.Trimesh(vertices.shape=(25047, 3), faces.shape=(50416, 3))>
>>> # You can pass the template object directly to navis' plotting functions
>>> navis.plot3d(flybrains.FAFB14)
```

## Changes
- `0.2.8` (02/04/23): added transform between `JRCFIB2022M` and `FLYWIRE`
- `0.2.7` (05/01/23): fixed `JRC2018M` <-> `JRC2018U` transform download
- ~~`0.2.6` (06/09/22): added `JRC2018M` <-> `JRC2018U` transform~~ (YANKED)
- `0.2.5` (22/05/22): added `JRCFIB2022M` mesh and transform to/from `FAFB14`
- `0.2.4` (12/05/22): added `FLYWIRE` template brain and landmark-based mirror transform
- `0.2.0` (02/02/22): added VirtualFlyBrain.org's (CMTK) and Janelia's (H5) VNC transforms; renamed some download function
- `0.1.14` (21/10/21): added `FANC` <-> `JRCVNC2018F` transform (requires Elastix and navis >=1.0.0)
- `0.1.13` (14/10/21): add template and mirror transform for FANC
- `0.1.12` (18/09/21): fixed directionality of Jefferis lab CMTK transforms
- `0.1.11` (02/08/21): make downloads work if file size unknown
- `0.1.10` (01/08/21): fix bug that led to warnings during transform registration on Windows systems
- `0.1.9` (05/05/21): fixed mesh normals; fixed JRCFIB2018F units to nm and added JRCFIB2018Fum template;
- `0.1.8` (10/04/21): add a simple symmetrization transform for FAFB: `FAFB14sym`
- `0.1.7` (30/03/21): better deal with systems without nat libraries
- `0.1.6` (25/03/21): fix bug that led to excessive recursive scanning of directories
- `0.1.5` (03/03/21): fix bug that led to meshes not being packaged
- `0.1.4` (24/02/21): added "hemibrain" alias for "JRCFIB2018F"; added hemibrain bounding box mesh
- `0.1.3` (12/01/21): improved the warp mirror registration for `FAFB14`
- `0.1.2` (10/01/21): added a warp mirror registration for `FAFB14`
- `0.1.1` (06/01/21): added `um` (for microns) suffix to `JRCFIB2018F` transforms; added affine `JRCFIB2018Fraw` -> `JRCFIB2018F` -> `JRCFIB2018Fum` transforms
- `0.1.0` (03/01/21): first working version  

## Acknowledgements
Critically based on `nat.flybrains` and `nat.jrcbrains` by Greg Jefferis
_et al._ for inspiration for the implementation and meta data on e.g. template
brains.

As reference for the Jefferis lab registrations, please use:

```
The natverse, a versatile toolbox for combining and analysing neuroanatomical data.
A.S. Bates, J.D. Manton, S.R. Jagannathan, M. Costa, P. Schlegel, T. Rohlfing, G.S. Jefferis
eLife. 9 (2020) e53350. doi:10.7554/eLife.53350.
```

As (partial) reference for the Saalfeld lab registrations, please see:

```
An unbiased template of the Drosophila brain and ventral nerve cord.
John A Bogovic, Hideo Otsuna, Larissa Heinrich, Masayoshi Ito, Jennifer Jeter, Geoffrey Meissner, Aljoscha Nern, Jennifer Colonell, Oz Malkesman, Kei Ito, Stephan Saalfeld
PLOS One; doi: https://doi.org/10.1371/journal.pone.0236495
```

For references of individual template brains, please see their docstrings:
```Python
>>> help(flybrains.IBN)
```
