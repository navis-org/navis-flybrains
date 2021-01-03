from setuptools import setup, find_packages

import re

VERSIONFILE = "flybrains/__version__.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    requirements = [l for l in requirements if l and not l.startswith('#')]

LONG_DESCRIPTION = """
NAVis is a Python 3 library for Neuron Analysis and
Visualization with focus on hierarchical tree-like neuron data.

Features:

  - interactive 2D (matplotlib) and 3D (vispy/plotly) plotting of neurons
  - virtual neuron surgery: cutting, pruning, rerooting
  - clustering methods (e.g. by connectivity or synapse placement)
  - R bindings (e.g. for libraries nat, rcatmaid, elmr)
  - interfaces with neuprint, Blender 3D and Cytoscape

Check out the `Documentation <http://navis.readthedocs.io/>`_.
"""

setup(
    name='flybrains',
    version=verstr,
    packages=find_packages(),
    license='GNU GPL V3',
    description='Transforms to map between different Drosophila template brains',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/schlegelp/navis-flybrains',
    author='Philipp Schlegel',
    author_email='pms70@cam.ac.uk',
    keywords='Drosophila Template Registration Brain',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',

        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=requirements,
    extras_require={'extras': []},
    python_requires='>=3.6',
    zip_safe=False,

    include_package_data=True

)
