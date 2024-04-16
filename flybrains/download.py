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

import os
import requests

from tqdm.auto import tqdm

from typing import Optional
from navis import utils

import git

__all__ = ['download_vfb_transforms', 'download_jefferislab_transforms',
           'download_jrc_transforms', 'download_jrc_vnc_transforms']


def download_vfb_transforms(repos=("VfbBridgingRegistrations", ),
                                   update_existing=True,
                                   use_ssh=False,
                                   data_home=None):
    """Download VirtualFlyBrain.org (VFB) CMTK transforms.

    BridgingRegistrations (~6Mb):
      - COURT2017VNS_JRCVNC2018F: DrosAdultVNSdomains_Court2017_template_Neuropil_LPS -> JRC2018_VNC_FEMALE_4iso_LPS
      - COURT2018VNS_JRCVNC2018U: 20x_flyVNCtemplate_Female_symmetric -> JRC2018_VNC_UNISEX_4iso

    Important
    ---------
    The VFB CMTK transforms _between_ JRCVNC2018 template brains were removed
    in version 0.2.10 as they no longer available for download. Please use the
    JRC H5 transforms from the Saalfeld lab instead.

    Parameters
    ----------
    repos :             "VfbBridgingRegistrations" | list of str
                        Which registrations to download. These are Github
                        repositories (e.g. ``VirtualFlyBrain/VfbBridgingRegistrations``)
                        which will be cloned into ``~/flybrain-data/``.
    update_existing :   bool
                        If True, already downloaded transforms will be updated.
                        If False, these will be skipped.
    use_ssh :           bool
                        If True, will use SSH to clone the Github repositories
                        containing the VFB registrations. See
                        `here <https://docs.github.com/en/free-pro-team@latest
                        /github/authenticating-to-github/connecting-to-github-
                        with-sshhttps://docs.github.com/en/free-pro-team@latest
                        /github/authenticating-to-github/connecting-to-
                        github-with-ssh>`_ for an explanation on how to generate
                        and configure SSH access to Github.
    data_home :         str
                        Directory to download files to. If not specified, it
                        tries to read from the ``FLYBRAINS_DATA`` environment
                        variable and defaults to ``~/flybrain-data``.

    See Also
    --------
    :func:`~flybrains.update_transforms``
                Use to update already downloaded transforms.

    """
    data_home = get_data_home(data_home, create=True)
    repos = utils.make_iterable(repos)

    print(f'Downloading VFB transforms into {data_home}')
    for repo in tqdm(repos, desc='Repos', leave=False):
        download_reg_repo(f'VirtualFlyBrain/{repo}',
                          use_ssh=use_ssh,
                          data_home=data_home,
                          update_existing=update_existing)


def download_jefferislab_transforms(repos=("BridgingRegistrations",
                                           "MirrorRegistrations",
                                           "DrosophilidBridgingRegistrations"),
                                    update_existing=True,
                                    use_ssh=False,
                                    data_home=None):
    """Download Jefferis lab CMTK transforms.

    BridgingRegistrations (~50Mb):
      - Cell07 <-> IS2
      - JFRC2013 <-> JFRC2013DS
      - JFRC2 <-> JFRC2013
      - FCWB <-> IS2
      - JFRC2013 <-> JFRC2014
      - FCWB <-> JFRC2
      - JFRC2014DS <-> JFRC2014
      - T1 <-> FCWB
      - IBNWB <-> IBN
      - JFRC2014 <-> JFRC2014DS
      - T1 <-> IS2
      - IS2 <-> Cell07
      - JFRC2 <-> FCWB
      - T1 <-> JFRC2
      - IS2 <-> T1
      - JFRC2 <-> IBNWB
      - VNCIS1 <-> V2
      - JFRC2013DS <-> JFRC2013
      - JFRC2 <-> IS2

    MirrorRegistrations (~40Mb):
      - ATAG
      - FCWB
      - IS2
      - JFRC2
      - JFRC2
      - JFRC
      - T1
      - V2
      - VNCIS1

    DrosophilidBridgingRegistrations (~100Mb):
     - Dmel <-> DsecI.list
     - Dmel <-> Dyak.list
     - DsecI <-> DsecF.list
     - DsecI <-> JFRC2.list
     - JFRC2 <-> DsecI.list
     - Dmel <-> Dsim.list
     - Dmel <-> IS2.list
     - DsecI <-> DsecM.list
     - Dsim <-> DsecI.list
     - Dmel <-> Dvir.list
     - Dmel <-> JFRC2.list
     - DsecI <-> IS2.list
     - IS2 <-> DsecI.list

    Parameters
    ----------
    repos :             "BridgingRegistrations" | "MirrorRegistrations" | "DrosophilidBridgingRegistrations" | list thereof
                        Which registrations to download. These are Github
                        repositories (e.g. ``jefferislab/BridgingRegistrations``)
                        which will be cloned into ``~/flybrain-data/``.
    update_existing :   bool
                        If True, already downloaded transforms will be updated.
                        If False, these will be skipped.
    use_ssh :           bool
                        If True, will use SSH to clone the Github repositories
                        containing the Jefferis lab registrations. See
                        `here <https://docs.github.com/en/free-pro-team@latest
                        /github/authenticating-to-github/connecting-to-github-
                        with-sshhttps://docs.github.com/en/free-pro-team@latest
                        /github/authenticating-to-github/connecting-to-
                        github-with-ssh>`_ for an explanation on how to generate
                        and configure SSH access to Github.
    data_home :         str
                        Directory to download files to. If not specified, it
                        tries to read from the ``FLYBRAINS_DATA`` environment
                        variable and defaults to ``~/flybrain-data``.

    See Also
    --------
    :func:`~flybrains.update_transforms``
                Use to update already downloaded transforms.

    """
    data_home = get_data_home(data_home, create=True)
    repos = utils.make_iterable(repos)

    print(f'Downloading Jefferis lab transforms into {data_home}')
    for repo in tqdm(repos, desc='Repos', leave=False):
        download_reg_repo(f'jefferislab/{repo}',
                          use_ssh=use_ssh,
                          data_home=data_home,
                          update_existing=update_existing)


def download_reg_repo(repo: str, data_home=None, use_ssh=False, update_existing=True):
    """Download git repository containing registrations.

    Parameters
    ----------
    repo :      str
                Github repo to download.
    data_home : str
                Directory to download files to. If not specified, it tries to
                read from the ``FLYBRAINS_DATA`` environment variable and
                defaults to ``~/flybrain-data``.

    """
    data_home = get_data_home(data_home, create=True)

    if use_ssh:
        url = f'git@github.com:{repo}'
    else:
        url = f'https://github.com/{repo}'

    # Generate target path for this repo
    clone_to = os.path.join(data_home, repo.split('/')[-1])

    # If target path exists, check if it's an already initialized Github repo
    if os.path.isdir(clone_to):
        try:
            # This will fail if target path is not a Github repo
            r = git.Repo(clone_to)

            # If we were able to initialize
            if update_existing:
                with tqdm(desc='Updating', leave=False) as pbar:
                    # We have to define a function that clone_from can call to show progress
                    def update_pbar(_, cur_count, max_count=None, message=''):
                        """Update progress bar from .clone_from callbar."""
                        if max_count is not None:
                            pbar.total = max_count

                        pbar.update(cur_count - pbar.n)

                    # Pull from remote origin
                    r.remotes.origin.pull(progress=update_pbar)

            return
        except git.InvalidGitRepositoryError:
            raise ValueError(f'Target directory "{clone_to}" already exists but'
                             'is not a valid repository.')
        except BaseException:
            raise

    # If Folder does not yet exist, clone the repo into that folder
    with tqdm(desc='Downloading', leave=False) as pbar:
        # We have to define a function that clone_from can call to show progress
        def update_pbar(_, cur_count, max_count=None, message=''):
            """Update progress bar from .clone_from callbar."""
            if max_count is not None:
                pbar.total = max_count

            pbar.update(cur_count - pbar.n)

        git.Repo.clone_from(url, clone_to, progress=update_pbar)


def download_jrc_transforms(data_home=None, skip_existing=True):
    """Download H5 transforms between the Janelia Research Campus (JRC) brain templates.

    Generated and kindly provided by the Saalfeld lab (Janelia):
    https://www.janelia.org/open-science/jrc-2018-brain-templates

    Includes:
      - JRC2018F <-> FAFB
      - JRC2018F <-> JFRC2013
      - JRC2018F <-> FCWB
      - JRC2018F <-> JRCFIB2018F (hemibrain)
      - JRC2018U <-> JRC2018F
      - JRC2018U <-> JRC2018M
      - JRC2018F <-> JFRC2010
      - JRC2018M <-> JRCFIB2022M (maleCNS)

    Note that these transforms are fairly large: between 550Mb and 2Gb each.

    Parameters
    ----------
    data_home :     str
                    Directory to download files to. If not specified, it tries to
                    read from the ``FLYBRAINS_DATA`` environment variable and
                    defaults to ``~/flybrain-data``.
    skip_existing : bool
                    If True, existing files will be skipped. If False, they
                    will be overwritten.

    """
    data_home = get_data_home(data_home, create=True)
    urls = (
        "14362754?private_link=3a8b1d84c5e197edc97c",
        "14368703?private_link=2a684586d5014e31076c",
        "14369093?private_link=d5965dad295e46241ae1",
        "21749535?private_link=ca603876efb33fdf3028",
        "14371574?private_link=b7120207f38b35f1e372",
        "14448911?private_link=2afde323b12274d3243b",
        "14368358?private_link=b29e25b6e47ccf9187a8",
        "42106125?private_link=bfbfc18d24fe959b78c0",
            )
    urls = [f"https://ndownloader.figshare.com/files/{f}" for f in urls]

    filenames = (
        'JRC2018F_FAFB.h5',
        'JRC2018F_JFRC2013.h5',
        'JRC2018F_FCWB.h5',
        'JRC2018F_JRCFIB2018F.h5',
        'JRC2018U_JRC2018F.h5',
        'JRC2018U_JRC2018M.h5',
        'JRC2018F_JFRC2010.h5',
        'JRCFIB2022M_JRC2018M.h5'  # originally: MaleCNS_JRC2018M_d2.h5
      )

    print(f'Downloading JRC (Saalfeld lab) brain transforms into {data_home}')
    for url, file in tqdm(zip(urls, filenames), leave=False,
                          total=len(urls), desc='Transforms'):
        dst = os.path.join(data_home, file)
        if skip_existing and os.path.exists(dst):
            continue
        _ = download_from_url(url, dst)


def download_jrc_vnc_transforms(data_home=None, skip_existing=True):
    """Download H5 transforms between the Janelia Research Campus (JRC) VNC templates.

    Generated and kindly provided by the Saalfeld lab (Janelia):
    https://www.janelia.org/open-science/jrc-2018-brain-templates

    Includes:
      - JRCVNC2018U <-> JRCVNC2018F (110Mb)
      - JRCVNC2018U <-> JRCVNC2018M (150Mb)
      - JRCVNC2018M <-> MANC (1Gb)

    Parameters
    ----------
    data_home :     str
                    Directory to download files to. If not specified, it tries to
                    read from the ``FLYBRAINS_DATA`` environment variable and
                    defaults to ``~/flybrain-data``.
    skip_existing : bool
                    If True, existing files will be skipped. If False, they
                    will be overwritten.

    """
    data_home = get_data_home(data_home, create=True)
    urls = (
        "28909212?private_link=c4589cef9180e1dd4ee1",
        "28908795?private_link=42ad71eb14e7dd51e81a",
        "38827794")
    urls = [f"https://ndownloader.figshare.com/files/{f}" for f in urls]

    # Note that we are renaming the files upon download!
    filenames = (
        'JRCVNC2018U_JRCVNC2018F.h5',  # originally: JRC2018VncU_JRC2018VncF.h5
        'JRCVNC2018M_JRCVNC2018U.h5',  # originally: JRC2018VncM_JRC2018VncU.h5
        'JRCVNC2018M_MANC.h5',  # originally: JRC2018VncM_MANC.h5
      )

    print(f'Downloading JRC (Saalfeld lab) VNC transforms into {data_home}')
    for url, file in tqdm(zip(urls, filenames), leave=False,
                          total=len(urls), desc='Transforms'):
        dst = os.path.join(data_home, file)
        if skip_existing and os.path.exists(dst):
            continue
        _ = download_from_url(url, dst)


def download_from_url(url, dst, resume=False):
    """Download file with progress bar.

    Parameters
    ----------
    url :       str
                URL to download from.
    dst :       str
                Destination filepath.
    resume :    bool
                If True, will attempt to resume download if file exists. If
                False, will overwrite existing files!

    Returns
    -------
    filesize
                Filesize in bytes.

    """
    try:
        file_size = int(requests.head(url, allow_redirects=True).headers["Content-Length"])
    except KeyError:
        file_size = None

    if file_size and os.path.exists(dst) and resume:
        first_byte = os.path.getsize(dst)
        mode = 'ab'
    else:
        first_byte = 0
        mode = 'wb'

    if file_size and first_byte >= file_size:
        return file_size

    header = {"Range": f"bytes={first_byte}-{file_size}"}
    with tqdm(total=file_size, initial=first_byte,
              unit='B', unit_scale=True, desc=os.path.basename(dst)) as pbar:
        req = requests.get(url, headers=header, stream=True, allow_redirects=True)
        with open(dst, mode) as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(1024)

    return file_size


def get_data_home(data_home: Optional[str] = None, create=False) -> str:
    """Return a path to the cache directory for transforms.

    If the ``data_home`` argument is not specified, it tries to read from the
    ``FLYBRAINS_DATA`` environment variable and defaults to ``~/flybrain-data``.
    """
    if data_home is None:
        data_home = os.environ.get('FLYBRAINS_DATA',
                                   os.path.join('~', 'flybrain-data'))

    data_home = os.path.expanduser(data_home)
    if not os.path.exists(data_home) and create:
        os.makedirs(data_home)

    return data_home
