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

__all__ = ["register_transforms", "report"]

# Read in meta data
fp = os.path.dirname(__file__)

data_filepath = os.path.join(fp, "data")

# Define ALIASES here
ALIASES = [
    ("hemibrain", "JRCFIB2018F"),
    ("hemibrainraw", "JRCFIB2018Fraw"),
    ("hemibrainum", "JRCFIB2018Fum"),
    ("FAFB", "FAFB14"),
    ("FAFBum", "FAFB14um"),
    ("FAFBnm", "FAFB14nm"),
    ("FANC", "FANCnm"),
    ("JRCFIB2022M", "JRCFIB2022Mnm"),
    ("MANC", "MANCnm"),
    ("FLYWIRE", "FLYWIREnm"),
]


@functools.lru_cache()
def get_nat_regdirs(verbose=False):
    """Get nat.templatebrain, nat.flybrains and nat.jrcbrains regdirs."""
    regdirs = []

    # Find R binary
    bin = shutil.which("Rscript")

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
    proc = subprocess.run([bin, "-e", cmd], capture_output=True)

    # Parse output
    outstr = proc.stdout.decode()
    match = re.search('.*?"(.*?)"', outstr)
    if match and match.group(1).strip() != "":
        path = pathlib.Path(match.group(1))
        regdirs.append(path)

    # This is basepath for nat.flybrains
    cmd = "regdirs=c('bridgingregistrations', 'mirroringregistrations');system.file('extdata', regdirs, package = 'nat.flybrains')"

    # Run the command
    proc = subprocess.run([bin, "-e", cmd], capture_output=True)

    # Parse output
    outstr = proc.stdout.decode()
    for line in outstr.split("\n"):
        # Skip empty lines
        if not line:
            continue
        match = re.search('.*?"(.*?)"', line)
        if match:
            # Skip empty strings (happens if path not set at all)
            # If we don't skip then we add the current directory
            # `PosixPath('.')` which will lead to A LOT of recursive
            # searching
            if match.group(1).strip() == "":
                continue
            path = pathlib.Path(match.group(1))
            regdirs.append(path)

    # This is the nat.jrcbrains basepath
    # These are the h5 Saalfeld registrations
    cmd = "library(rappdirs);rappdirs::user_data_dir('R/nat.jrcbrains')"

    # Run the command
    proc = subprocess.run([bin, "-e", cmd], capture_output=True)

    # Parse output
    outstr = proc.stdout.decode()
    match = re.search('.*?"(.*?)"', outstr)
    if match and match.group(1).strip() != "":
        path = pathlib.Path(match.group(1))
        regdirs.append(path)

    return regdirs


def report():
    """Print report on available transforms and where they are stored."""
    rep = dedent(f"""\
    Flybrains Status Report
    =======================
    Data Home: {get_data_home()}
    """)

    data_home = pathlib.Path(get_data_home()).expanduser()
    # Number of .list CMTK directories
    n_cmtk = len([p for p in data_home.rglob(f"*.list") if p.is_dir()])
    # Number of .h5 H5 file
    n_h5 = len([p for p in data_home.rglob(f"*.h5") if p.is_file()])

    rep += dedent(f"""
    CMTK registrations (Jefferis lab/VFB): {n_cmtk} of 45
    H5 registrations (JRC/Saalfeld lab): {n_h5} of 8
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
            n_cmtk = len([p for p in path.expanduser().rglob("*.list") if p.is_dir()])
            # Number of .h5 H5 file
            n_h5 = len([p for p in path.expanduser().rglob("*.h5") if p.is_file()])
            rep += dedent(f"""\
            {path}: {n_cmtk} CMTK | {n_h5} H5 transforms
            """)

    print(rep)


def inject_paths():
    """Register flybrain paths with navis."""
    # Navis scans paths in order and if the same transform is found again
    # it will be ignored. Hence order matters in some circumstances!
    # First add the data home path
    transforms.registry.register_path(get_data_home(), trigger_scan=False)

    # Next add default path
    default_path = os.path.expanduser("~/flybrain-data")
    if default_path not in transforms.registry.transpaths:
        transforms.registry.register_path(default_path, trigger_scan=False)

    # Now add paths with potential nat regdirs
    nat_reglists = get_nat_regdirs()
    if nat_reglists:
        transforms.registry.register_path(nat_reglists, trigger_scan=False)

    transforms.registry.scan_paths()


def _FANCnm_JRCVNC2018F_pre(points):
    """Apply necessary pre-transforms for FANC -> JRCVNC2018F elastix transform."""
    # Dark magic transforms see:
    # https://github.com/htem/GridTape_VNC_paper/blob/main/template_registration_pipeline/register_EM_dataset_to_template/README.md
    points -= (533.2, 533.2, 945)  # (1.24, 1.24, 2.1) vox at (430, 430, 450)nm/vox
    points /= (430, 430, 450)
    points *= (300, 300, 400)
    points[:, 2] = 435 * 400 - points[:, 2]  # z flipping a stack with 436 slices

    # Convert to microns
    points /= 1000

    return points


def _FANCnm_JRCVNC2018F_reflect(points):
    """Apply reflect."""
    # Unreflect
    template_plane_of_symmetry_x_microns = 329 * 0.4
    points[:, 0] = template_plane_of_symmetry_x_microns * 2 - points[:, 0]

    return points


def _JRCVNC2018F_FANCnm_post(points):
    """Apply necessary post-transforms for JRCVNC2018F -> FANCnm elastix transform."""
    points *= 1000  # Convert microns to nm so that the math below works

    # Dark magic transforms see:
    # https://github.com/htem/GridTape_VNC_paper/blob/main/template_registration_pipeline/register_EM_dataset_to_template/README.md
    points[:, 2] = 435 * 400 - points[:, 2]  # z flipping a stack with 436 slices
    points /= (300, 300, 400)
    points *= (430, 430, 450)
    points += (533.2, 533.2, 945)  # (1.24, 1.24, 2.1) vox at (430, 430, 450)nm/vox

    return points


def search_register_path(path, verbose=False):
    """Search a single path for transforms and register them."""
    path = pathlib.Path(path).expanduser()

    if verbose:
        print(f"Searching {path}")

    # Skip if this isn't an actual path
    if not path.is_dir():
        return

    # Find transform files/directories
    for ext, tr in zip(
        [".h5", ".list"], [transforms.h5reg.H5transform, transforms.cmtk.CMTKtransform]
    ):
        for hit in path.rglob(f"*{ext}"):
            if hit.is_dir() or hit.is_file():
                # These files are inside the CMTK folders and show as
                # symlinks in OSX/Linux but as files (?) in Windows
                # Hence we need to manually exclude them.
                if hit.name in ("orig.list", "original.list"):
                    continue

                # Register this transform
                try:
                    if "mirror" in hit.name or "imgflip" in hit.name:
                        transform_type = "mirror"
                        source = hit.name.split("_")[0]
                        target = None
                    else:
                        transform_type = "bridging"
                        source = hit.name.split("_")[0]
                        target = hit.name.split("_")[1].split(".")[0]

                    # By convention these transforms expect the source and target coordinates
                    # to be in microns. For the EM datasets, the native coordinates are typically
                    # in nanometers or voxels. Therefore, we need to be explicit about the units
                    # here by adding "um" to the source and target names:
                    for template in (
                        "FAFB",
                        "FAFB14",
                        "FLYWIRE",
                        "JRCFIB2018F",
                        "JRCFIB2022M",
                        "MANC",
                        "FANC",
                    ):
                        if source == template:
                            source += "um"
                        if target == template:
                            target += "um"

                    # Initialize the transform
                    transform = tr(hit)

                    if verbose:
                        print(
                            f"Registering {hit} ({tr.__name__}) "
                            f'as "{source}" -> "{target}"'
                        )

                    transforms.registry.register_transform(
                        transform=transform,
                        source=source,
                        target=target,
                        transform_type=transform_type,
                    )
                except BaseException as e:
                    warnings.warn(f"Error registering {hit} as transform: {str(e)}")


def register_aliases():
    """Register alias transforms (defined at the top of this file)."""
    for a1, a2 in ALIASES:
        tr = transforms.AliasTransform()
        transforms.registry.register_transform(
            transform=tr, source=a1, target=a2, transform_type="bridging", weight=0
        )


def register_mirror_transforms():
    """Register mirror transforms."""
    # 1. MaleCNS
    fp = os.path.join(data_filepath, "maleCNS_mirror_landmarks_nm.csv")
    lm = pd.read_csv(fp)
    tr = transforms.TPStransform(
        lm[["x_flip", "y_flip", "z_flip"]].values,
        lm[["x_mirr", "y_mirr", "z_mirr"]].values,
    )
    transforms.registry.register_transform(
        transform=tr, source="JRCFIB2022M", target=None, transform_type="mirror"
    )
    tr = transforms.TPStransform(
        lm[["x_flip", "y_flip", "z_flip"]].values / 8,
        lm[["x_mirr", "y_mirr", "z_mirr"]].values / 8,
    )
    transforms.registry.register_transform(
        transform=tr, source="JRCFIB2022Mraw", target=None, transform_type="mirror"
    )
    # 2. FANC (based on subsampling a FANC -> MANCsym transform)
    fp = os.path.join(data_filepath, "FANC_mirror_landmarks.csv")
    lm = pd.read_csv(fp)
    tr = transforms.TPStransform(
        lm[["x_flip", "y_flip", "z_flip"]].values,
        lm[["x_mirr", "y_mirr", "z_mirr"]].values,
    )
    transforms.registry.register_transform(
        transform=tr, source="FANC", target=None, transform_type="mirror"
    )
    # 3. FlyWire
    fp = os.path.join(data_filepath, "FLYWIRE_mirror_landmarks.csv")
    lm = pd.read_csv(fp)
    tr = transforms.TPStransform(
        lm[["x_flip", "y_flip", "z_flip"]].values,
        lm[["x_mirr", "y_mirr", "z_mirr"]].values,
    )
    transforms.registry.register_transform(
        transform=tr, source="FLYWIRE", target=None, transform_type="mirror"
    )
    # 4.1 FAFB14 (created by xforming landmarks for FlyWire mirror into FAFB14 space)
    fp = os.path.join(data_filepath, "FAFB14_mirror_landmarks.csv")
    lm = pd.read_csv(fp)
    tr = transforms.TPStransform(
        lm[["x_flip", "y_flip", "z_flip"]].values,
        lm[["x_mirr", "y_mirr", "z_mirr"]].values,
    )
    transforms.registry.register_transform(
        transform=tr, source="FAFB14", target=None, transform_type="mirror"
    )
    # 4.2 "FAFB" (synonym to "FAFB14" since this is its alias on the chart)
    transforms.registry.register_transform(
        transform=tr, source="FAFB", target=None, transform_type="mirror"
    )


def register_unit_transforms():
    """Add transform between raw (voxel) and nanometer space."""
    # Hemibrain, MANC and MaleCNS are in 8x8x8 nm voxels
    for template in ("JRCFIB2022M", "MANC", "JRCFIB2018F"):
        tr = transforms.AffineTransform(np.diag([8, 8, 8, 1]))
        transforms.registry.register_transform(
            transform=tr,
            source=f"{template}raw",
            target=template,
            transform_type="bridging",
            weight=0.1,
        )
    # FAFB and FLYWIRE are in 4x4x40 nm voxels
    for template in ("FLYWIRE", "FAFB14"):
        tr = transforms.AffineTransform(np.diag([4, 4, 40, 1]))
        transforms.registry.register_transform(
            transform=tr,
            source=f"{template}raw",
            target=template,
            transform_type="bridging",
            weight=0.1,
        )
    # FANC is in 4.3x4.3x45 nm voxels
    tr = transforms.AffineTransform(np.diag([4.3, 4.3, 45, 1]))
    transforms.registry.register_transform(
        transform=tr,
        source="FANCraw",
        target="FANC",
        transform_type="bridging",
        weight=0.1,
    )

    # Bogovic et al seem to have a difference in Z calibration
    tr = transforms.AffineTransform(np.diag([1, 1, 1 / 0.6220880, 1]))
    transforms.registry.register_transform(
        transform=tr,
        source="JFRC2",
        target="JFRC2010",
        transform_type="bridging",
        weight=0.1,
    )

    #### Add transforms between nanometer and microns space for:
    for template in ("FAFB14", "FLYWIRE", "MANC", "JRCFIB2018F", "FANC", "JRCFIB2022M"):
        tr = transforms.AffineTransform(np.diag([1e3, 1e3, 1e3, 1]))
        transforms.registry.register_transform(
            transform=tr,
            source=f"{template}um",
            target=template,
            transform_type="bridging",
            weight=0.1,
        )


def register_manual_transforms():
    """Manually add some transforms (e.g. from landmark files)."""
    # Add a simple symmetrization transform for FAFB14
    fp = os.path.join(data_filepath, "FAFB14_symmetrize_landmarks_nm.csv")
    lm = pd.read_csv(fp)
    tr = transforms.TPStransform(
        lm[["x", "y", "z"]].values, lm[["x_sym", "y_sym", "z_sym"]].values
    )
    transforms.registry.register_transform(
        transform=tr, source="FAFB14", target="FAFB14sym", transform_type="bridging"
    )
    # Add a simple symmetrization transform for FLYWIRE
    fp = os.path.join(data_filepath, "FLYWIRE_symmetrize_landmarks_nm.csv")
    lm = pd.read_csv(fp)
    tr = transforms.TPStransform(
        lm[["x", "y", "z"]].values, lm[["x_sym", "y_sym", "z_sym"]].values
    )
    transforms.registry.register_transform(
        transform=tr, source="FLYWIRE", target="FLYWIREsym", transform_type="bridging"
    )

    # Add a male CNS <-> FAFB transform
    fp = os.path.join(data_filepath, "maleCNS_brain_FAFB_landmarks_nm.csv")
    lm = pd.read_csv(fp)
    tr = transforms.TPStransform(
        lm[["fafb_x", "fafb_y", "fafb_z"]].values,
        lm[["cns_x", "cns_y", "cns_z"]].values,
    )
    transforms.registry.register_transform(
        transform=tr, source="FAFB14", target="JRCFIB2022M", transform_type="bridging"
    )

    # Add male CNS <-> FlyWire transform. This was generated from the
    # CNS <-> FAFB transform by simply xforming the FAFB coordinates
    fp = os.path.join(data_filepath, "maleCNS_brain_FLYWIRE_landmarks_nm.csv")
    lm = pd.read_csv(fp)
    tr = transforms.TPStransform(
        lm[["flywire_x", "flywire_y", "flywire_z"]].values,
        lm[["cns_x", "cns_y", "cns_z"]].values,
    )
    transforms.registry.register_transform(
        transform=tr, source="FLYWIRE", target="JRCFIB2022M", transform_type="bridging"
    )

    # Add a FANC-MANC transform. These landmarks are created from the
    # CMTK transforms between FANC -> MANCsym -> MANC
    fp = os.path.join(data_filepath, "MANC_FANC_landmarks_nm.csv")
    lm = pd.read_csv(fp)
    tr = transforms.TPStransform(
        lm[["x_manc", "y_manc", "z_manc"]].values,
        lm[["x_fanc", "y_fanc", "z_fanc"]].values,
    )
    transforms.registry.register_transform(
        transform=tr, source="MANC", target="FANC", transform_type="bridging"
    )


def register_fanc_jrcvnc2018f():
    """Register FANC -> JRCVNC2018F and reverse transforms."""
    # Some general notes for the Elastix transform between FANC and JRCVNC2018F:
    # 1. Elastix transforms are not invertible - hence there are two separate
    #    transforms for forward and reverse directions
    # 2. Both directions require some pre-/postprocessing: unit conversion,
    #    some offset correction and an inversion across the x-axis.
    #    These extra steps are realized via two intermediate template spaces:
    #    FANCum_fixed and JRCVNC2018F_reflected. The bridging path is hence:
    #    FANC <-> FANC_fixed <-(elastix)-> JRCVNC2018F_reflected <-> JRCVNC2018F
    # 3. This transform is technically for FANC v3 but according to Jasper can
    #    also be applied to v4.

    # First up: forward FANC (nm) -> JRCVNC2018F
    # Preflight for FANCnm (v3) -> JRCVNC2018F
    tr = transforms.FunctionTransform(_FANCnm_JRCVNC2018F_pre)
    transforms.registry.register_transform(
        transform=tr, source="FANC", target="FANCum_fixed", transform_type="bridging"
    )

    # Elastix FANC_fixed -> JRCVNC2018F (reflected) transform
    fp = os.path.join(data_filepath, "TransformParameters.FixedFANC.txt")
    tr = transforms.ElastixTransform(fp)
    transforms.registry.register_transform(
        transform=tr,
        source="FANCum_fixed",
        target="JRCVNC2018F_reflected",
        transform_type="bridging",
    )

    # Unreflect
    tr = transforms.FunctionTransform(_FANCnm_JRCVNC2018F_reflect)
    transforms.registry.register_transform(
        transform=tr,
        source="JRCVNC2018F_reflected",
        target="JRCVNC2018F",
        transform_type="bridging",
    )

    # Now the reverse: JRCVNC2018F -> FANC (nm)
    # First reflect
    tr = transforms.FunctionTransform(_FANCnm_JRCVNC2018F_reflect)
    transforms.registry.register_transform(
        transform=tr,
        source="JRCVNC2018F",
        target="JRCVNC2018F_reflected",
        transform_type="bridging",
    )

    # Second apply Elastix FANC_fixed -> JRCVNC2018F transform
    fp1 = os.path.join(data_filepath, "TransformParameters.FixedTemplate.Bspline.txt")
    fp2 = os.path.join(data_filepath, "TransformParameters.FixedTemplate.affine.txt")
    tr = transforms.ElastixTransform(fp1, copy_files=[fp2])
    transforms.registry.register_transform(
        transform=tr,
        source="JRCVNC2018F_reflected",
        target="FANCum_fixed",
        transform_type="bridging",
    )

    # Postflight for JRCVNC2018F -> FANCnm (v3)
    tr = transforms.FunctionTransform(_JRCVNC2018F_FANCnm_post)
    transforms.registry.register_transform(
        transform=tr, source="FANCum_fixed", target="FANC", transform_type="bridging"
    )


def register_transforms():
    """Register transforms with navis."""
    # These are the paths we need to scan
    data_home = pathlib.Path(get_data_home()).expanduser()
    default_path = pathlib.Path("~/flybrain-data").expanduser()
    nat_paths = get_nat_regdirs()

    # Combine while retaining order
    search_paths = [data_home]
    if default_path not in search_paths:
        search_paths.append(default_path)
    search_paths += nat_paths

    # Go over all paths and add transforms
    for path in search_paths:
        # Do not (re-)move this line! Otherwise is_dir() might fail
        path = pathlib.Path(path).expanduser()

        # Skip if path does not exist
        if not path.is_dir():
            continue

        search_register_path(path)

    # Register some manual transforms
    register_manual_transforms()

    # Register FANC -> JRCVNC2018F transform
    # (we put this in a separate function as it is a bit more involved)
    register_fanc_jrcvnc2018f()

    # Add transforms between raw and um space
    register_unit_transforms()

    # Register (additional) mirror transforms
    register_mirror_transforms()

    # Register aliases
    register_aliases()
