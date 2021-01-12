#    This script is part of navis (http://www.github.com/schlegelp/navis-flybrains).
#    Copyright (C) 2020 Philipp Schlegel
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

import functools
import os
import re
import subprocess
import shutil
import pathlib
import warnings

from textwrap import dedent
from navis import transforms

import numpy as np
import pandas as pd

from .download import get_data_home

__all__ = ['register_transforms', 'report']

# Read in meta data
fp = os.path.dirname(__file__)

data_filepath = os.path.join(fp, 'data')


@functools.lru_cache()
def get_nat_regdirs(verbose=False):
    """Get nat.templatebrain, nat.flybrains and nat.jrcbrains regdirs."""
    regdirs = []

    # Find R binary
    bin = shutil.which('Rscript')

    if not bin:
        if verbose:
            warnings.warn("No R binary found.")
        return []

    # This is the basepath for nat.templatebrains
    # Note that in this case, the registrations will be in subfolders of this
    # path and the subfolders will be named based on the SHA of the URL the
    # registrations were downloaded from
    cmd = "library(rappdirs);file.path(user_data_dir('rpkg-nat.templatebrains', appauthor=NULL), 'regfolders')"

    # Run the command
    proc = subprocess.run([bin, '-e', cmd], capture_output=True)

    # Parse output
    outstr = proc.stdout.decode()
    path = pathlib.Path(re.search('.*?"(.*?)"', outstr).group(1))
    regdirs.append(path)

    # This is basepath for nat.flybrains
    cmd = "regdirs=c('bridgingregistrations', 'mirroringregistrations');system.file('extdata', regdirs, package = 'nat.flybrains')"

    # Run the command
    proc = subprocess.run([bin, '-e', cmd], capture_output=True)

    # Parse output
    outstr = proc.stdout.decode()
    for line in outstr.split('\n'):
        # Skip empty lines
        if not line:
            continue
        match = re.search('.*?"(.*?)"', line)
        if match:
            path = pathlib.Path(match.group(1))
            regdirs.append(path)

    # This is the nat.jrcbrains basepath
    # These are the h5 Saalfeld registrations
    cmd = "library(rappdirs);rappdirs::user_data_dir('R/nat.jrcbrains')"

    # Run the command
    proc = subprocess.run([bin, '-e', cmd], capture_output=True)

    # Parse output
    outstr = proc.stdout.decode()
    path = pathlib.Path(re.search('.*?"(.*?)"', outstr).group(1))
    regdirs.append(path)

    return regdirs


def report():
    """Print report on available transforms and where they are stored."""
    rep = dedent(f"""\
    Flybrains Status Report
    =======================
    Data Home: {get_data_home()}
    """)

    data_home = pathlib.Path(get_data_home())
    # Number of .list CMTK directories
    n_jefferislab = len([p for p in data_home.rglob(f'*.list') if p.is_dir()])
    # Number of .h5 H5 file
    n_saalfeld = len([p for p in data_home.rglob(f'*.h5') if p.is_file()])

    rep += dedent(f"""
    Jefferis lab registrations: {n_jefferislab} of 41
    Saalfeld lab registrations: {n_saalfeld} of 6
    """)

    nat_paths = get_nat_regdirs(verbose=False)
    rep += dedent(f"""
    nat regdirs
    -----------
    """)

    if not nat_paths:
        rep += dedent("""\
        None
        """)
    else:
        for path in nat_paths:
            # Number of .list CMTK directories
            n_cmtk = len([p for p in path.rglob(f'*.list') if p.is_dir()])
            # Number of .h5 H5 file
            n_h5 = len([p for p in path.rglob(f'*.h5') if p.is_file()])
            rep += dedent(f"""\
            {path}: {n_cmtk} CMTK | {n_h5} H5 transforms
            """)

    print(rep)


def inject_paths():
    """Register flybrain paths with navis."""
    # Navis scans paths in order and if the same transform is found again
    # it will be ignored. Hence order matters in some circumstances!
    # First add the data home path
    transforms.registry.register_path(get_data_home(),
                                      trigger_scan=False)

    # Next add default path
    default_path = os.path.expanduser('~/flybrain-data')
    if default_path not in transforms.registry.transpaths:
        transforms.registry.register_path(default_path,
                                          trigger_scan=False)

    # Now add paths with potential nat regdirs
    nat_reglists = get_nat_regdirs()
    if nat_reglists:
        transforms.registry.register_path(nat_reglists,
                                          trigger_scan=False)

    transforms.registry.scan_paths()


def register_transforms():
    """Register transforms with navis."""
    # These are the paths we need to scan
    data_home = pathlib.Path(get_data_home()).expanduser()
    default_path = pathlib.Path('~/flybrain-data').expanduser()
    nat_paths = get_nat_regdirs()

    # Combine while retaining order
    search_paths = [data_home]
    if default_path not in search_paths:
        search_paths.append(default_path)
    search_paths += nat_paths

    # Go over all paths and add transforms
    for path in search_paths:
        path = pathlib.Path(path).expanduser()
        # Skip if path does not exist
        if not path.is_dir():
            continue

        # Find transform files/directories
        for ext, tr in zip(['.h5', '.list'],
                           [transforms.h5reg.H5transform, transforms.cmtk.CMTKtransform]):
            for hit in path.rglob(f'*{ext}'):
                if hit.is_dir() or hit.is_file():
                    # Register this transform
                    try:
                        if 'mirror' in hit.name or 'imgflip' in hit.name:
                            transform_type = 'mirror'
                            source = hit.name.split('_')[0]
                            target = None
                        else:
                            transform_type = 'bridging'
                            target = hit.name.split('_')[0]
                            source = hit.name.split('_')[1].split('.')[0]

                        # "FAFB" refers to FAFB14 and requires microns
                        # we will change its label to make this explicit
                        # and later add a bridging transform
                        if target == 'FAFB':
                            target = 'FAFB14um'

                        if source == 'FAFB':
                            source = 'FAFB14um'

                        # "JRCFIB2018F" likewise requires microns
                        if target == 'JRCFIB2018F':
                            target = 'JRCFIB2018Fum'

                        if source == 'JRCFIB2018F':
                            source = 'JRCFIB2018Fum'

                        # For reasons I have not yet figured out, source
                        # and target appear to be swapped for the h5 regfiles.
                        # Need to ask Greg about this.
                        if ext == '.h5' and target:
                            source, target = target, source

                        # Initialize the transform
                        transform = tr(hit)

                        transforms.registry.register_transform(transform=transform,
                                                               source=source,
                                                               target=target,
                                                               transform_type=transform_type)
                    except BaseException as e:
                        warnings.warn(f'Error registering {hit} as transform: {str(e)}')

    # Add transform between JRCFIB2018Fraw (8nm voxel) and JRCFIB2018F (nm)
    tr = transforms.affine.AffineTransform(np.diag([8, 8, 8, 1]))
    transforms.registry.register_transform(transform=tr,
                                           source='JRCFIB2018Fraw',
                                           target='JRCFIB2018F',
                                           transform_type='bridging')

    # Add transform between JRCFIB2018F (nm) and JRCFIB2018Fum (um)
    tr = transforms.affine.AffineTransform(np.diag([1e3, 1e3, 1e3, 1]))
    transforms.registry.register_transform(transform=tr,
                                           source='JRCFIB2018Fum',
                                           target='JRCFIB2018F',
                                           transform_type='bridging')

    # Add transform between FAFB14um and FAFB14 (nm)
    tr = transforms.affine.AffineTransform(np.diag([1e3, 1e3, 1e3, 1]))
    transforms.registry.register_transform(transform=tr,
                                           source='FAFB14um',
                                           target='FAFB14',
                                           transform_type='bridging')

    # Add alias transform between FAFB and FAFB14 (they are synonymous)
    tr = transforms.base.AliasTransform()
    transforms.registry.register_transform(transform=tr,
                                           source='FAFB',
                                           target='FAFB14',
                                           transform_type='bridging')

    # Bogovic et al seem to have a difference in Z calibration
    tr = transforms.affine.AffineTransform(np.diag([1, 1, 1/0.6220880, 1]))
    transforms.registry.register_transform(transform=tr,
                                           source='JFRC2',
                                           target='JFRC2010',
                                           transform_type='bridging')

    # Add a simple mirror transform for FAFB14
    fp = os.path.join(data_filepath, 'FAFB14_mirror_landmarks.csv')
    lm = pd.read_csv(fp)
    tr = transforms.thinplate.TPStransform(lm[['x_flip', 'y_flip', 'z_flip']].values,
                                           lm[['x_mirr', 'y_mirr', 'z_mirr']].values)
    transforms.registry.register_transform(transform=tr,
                                           source='FAFB14',
                                           target=None,
                                           transform_type='mirror')
