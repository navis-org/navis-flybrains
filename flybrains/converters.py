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

"""Some functions to parse and convert transforms stored as R .RDS files.

These temporary registrations are on import to add some extra, simple bridgings

See nat.jrcbrains::add_saalfeld_reglist():
https://github.com/natverse/nat.jrcbrains/blob/85ed4a791e0508ff4a00dbfff5796c3a150694e2/R/saalfeld_reg.R#L181

See elmr's .onLoad
https://github.com/natverse/elmr/blob/d1ec56690ac07bfeda2e2832a237fcaf1589ee53/R/zzz.R#L15

"""

import pathlib
import json


def load_rds_transform(filepath, saveto=None):
    """Load nat & Co's custom transforms stored as RDS format.

    These transforms are typically ``reglists`` of a thin plate spine transform
    followed by a affine transform.

    Parameters
    ----------
    filepath :      str
                    Path to `.RDS` file containing the reglist read.
    saveto :        str, optional
                    If provided, will save file straight to json.

    Returns
    -------
    transform :     list of dict

    """
    p = pathlib.Path(filepath)
    if not p.is_file():
        raise ValueError(f'{filepath} does not appear to exist')

    from navis.interfaces import r

    readRDS = r.robjects.r('readRDS')
    cl = r.robjects.r('class')

    # Read data
    data = readRDS(str(p))

    # If not reglist
    if 'reglist' not in data.slots['class']:
        raise TypeError(f'Unknown transform type: {data.slots["class"]}')

    transforms = []
    for reg in data:
        this = {}
        # Thin plate spine reg
        if 'tpsreg' in cl(reg):
            this['type'] = 'tpsreg'
            for name, mat in zip(reg.names, reg):
                this[name] = r.data2py(mat)
        elif 'matrix' in cl(reg):
            this['type'] = 'affine'
            this['affine_matrix'] = r.data2py(reg)
        else:
            raise ValueError(f'Unknown transform type: {reg["class"]}')
        transforms.append(this)

    return transforms
