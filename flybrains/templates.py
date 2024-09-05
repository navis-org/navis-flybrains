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

"""Module constructing templatebrains"""

import json
import navis
import os

import trimesh as tm

from textwrap import dedent

from navis import transforms
from navis.transforms.templates import TemplateBrain


__all__ = ['FCWB', 'IBN', 'IBNWB', 'IS2', 'JFRC2', 'T1', 'Dmel', 'DsecI',
           'Dsim', 'Dvir',
           'JFRC2013', 'JFRC2013DS',
           'JRC2018F', 'JRC2018U', 'JRC2018M',
           'JRCFIB2018F', 'JRCFIB2018Fraw', 'JRCFIB2018Fum',
           'JRCFIB2022M', 'JRCFIB2022Mraw',
           'JRCVNC2018F',
           'JRCVNC2018M',
           'JRCVNC2018U',
           'VNCIS1',
           'FAFB14', 'FAFB',
           'FLYWIRE',
           'FANC',
           "MANC", "MANCraw",
           'DmelL1CNS_Seymour',
           'COURT2017VNS', 'COURT2018VNS',
           'register_templates']

# Read in meta data
fp = os.path.dirname(__file__)

meta_filepath = os.path.join(fp, 'data/template_meta.json')
mesh_filepath = os.path.join(fp, 'meshes')

with open(meta_filepath, 'r', encoding='utf-8') as f:
    template_meta = json.load(f)

# Index by short label
template_meta = {e['label']: e for e in template_meta}


class FlyTemplateBrain(TemplateBrain):
    """Base Class for fly template brains.

    This is mostly syntactic sugar to:
        1. Produce a nicely formatted string representation
        2. On-demand mesh-loading from ./data

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        units = getattr(self, 'units', 'units NA')

        if isinstance(units, list):
            units = units[0]

        if getattr(self, 'boundingbox'):
            bbox = f"""\
            Bounding box ({units}):
              x = {self.boundingbox[0]}, y = {self.boundingbox[2]}, z = {self.boundingbox[4]},
              x = {self.boundingbox[1]}, y = {self.boundingbox[3]}, z = {self.boundingbox[5]},"""
        else:
            bbox = f"""\
            Bounding box ({units}):
              NA"""

        if getattr(self, 'dims'):
            dims = f"{self.dims[0]} x {self.dims[1]} x {self.dims[2]} voxels"
        else:
            dims = "NA"

        if getattr(self, 'voxdims'):
            units = getattr(self, 'units', None)

            if not units:
                units = ['dimensionless', 'dimensionless', 'dimensionless']
            elif not navis.utils.is_iterable(units):
                units = [units, units, units]

            vxsize = f"""\
            Voxel size:
              x = {self.voxdims[0]} {units[0]}
              y = {self.voxdims[1]} {units[1]}
              z = {self.voxdims[2]} {units[2]}"""
        else:
            vxsize = """\
            Voxel size:
              NA"""

        # Can't use f-strings here because we need to dedent before we can
        # fill in the values
        msg = """\
        Template brain
        --------------
        Name: {name}
        Short Name: {label}
        Type: {type}
        Sex:  {sex}
        Dimensions: {dims}
        {vxsize}
        {bbox}
        Description: {description}
        DOI: {doi}"""

        msg = dedent(msg).format(name=getattr(self, 'name', 'NA'),
                                 label=getattr(self, 'label', 'NA'),
                                 type=getattr(self, 'type', 'NA'),
                                 sex=getattr(self, 'sex', 'NA'),
                                 dims=dims,
                                 vxsize=dedent(vxsize),
                                 bbox=dedent(bbox),
                                 description=getattr(self, 'description', 'NA'),
                                 doi=getattr(self, 'doi', 'NA'))
        return msg

    @property
    def mesh(self):
        """On-demand loading of surface mesh."""
        if not hasattr(self, '_mesh'):
            fp = os.path.join(mesh_filepath, f'{self.label}.ply')

            if not os.path.isfile(fp):
                raise ValueError(f'{self.label} does not appear to have a mesh')

            self._mesh = tm.load_mesh(fp)

        return self._mesh


class _FCWB(FlyTemplateBrain):
    """FCWB FlyCircuit reference brain.

    The FCWB reference brain is a shape averaged template brain generated using
    the CMTK avg_adm tool. See https://github.com/jefferislab/MakeAverageBrain
    for the relevant code.

    The FCWB.surf surface model was generated in Amira by constructing an
    isosurface model based on the FCWB brain.

    References
    ----------
    Ann-Shyn Chiang, Chih-Yung Lin, Chao-Chun Chuang, Hsiu-Ming Chang,
    Chang-Huain Hsieh11, Chang-Wei Yeh, Chi-Tin Shih, Jian-Jheng Wu,
    Guo-Tzau Wang, Yung-Chang Chen, Cheng-Chi Wu, Guan-Yu Chen, Yu-Tai Ching,
    Ping-Chang Lee, Chih-Yang Lin, Hui-Hao Lin, Chia-Chou Wu, Hao-Wei Hsu,
    Yun-Ann Huang, Jing-Yi Chen, Hsin-Jung Chiang, Chun-Fang Lu, Ru-Fen Ni,
    Chao-Yuan Yeh, Jenn-Kang Hwang (2011). Three-dimensional reconstruction of
    brain-wide wiring networks in Drosophila at single-cell resolution.
    Current Biology 21, 1-11. doi:10.1016/j.cub.2010.11.056

    FCWB is available for download at http://dx.doi.org/10.5281/zenodo.10568

    """

FCWB = _FCWB(**template_meta['FCWB'])


class _IBN(FlyTemplateBrain):
    """Insect Brain Nomenclature reference brain.

    Template used for the study "A Systematic Nomenclature for the Insect Brain"
    (doi:10.1016/j.neuron.2013.12.017).

    Details
    -------
    Constructed from the green channel of serial sections of a Drosophila
    melanogaster brain that was tricolor-labeled with a combination of the
    following reporters:

        - cytoplasmic DsRed (UAS-DsRed; Verkhusha et al., 2001; red channel)
        - presynaptic GFP (synaptic-vesicles-targeted UAS-n-syb-GFP; Estes
          et al., 2000; green channel)
        - postsynaptic Rdl-hemagglutinin (GABA-receptor-targeted UAS-Rdl-HA;
          Sanchez-Soriano et al., 2005; blue channel)

    These were expressed with the pan-neuronal elav-GAL4 expression driver
    (C155; Lin and Goodman, 1994).

    Note that, because of the excess amount of ectopic protein expression, the
    presynaptic and postsynaptic labelling (especially the latter) was not
    completely specific, visualizing not only synaptic sites but also cell
    bodies and large fiber bundles.

    The image was acquired using a confocal laser-scanning microscope LSM510
    (Zeiss) with a 40x water-immersion C-Apochromat objective (NA = 1.2). Each
    section, of 135 total, was recorded with a resolution of 1024 by 1024 pixels
    and 1.41 micron optical z-slice steps. These were then down-sampled to a
    resolution of 512 by 512 pixels.

    References
    ----------
    Kei Ito, Kazunori Shinomiya, Masayoshi Ito, J. Douglas Armstrong, George
    Boyan, Volker Hartenstein, Steffen Harzsch, Martin Heisenberg, Uwe Homberg,
    Arnim Jenett, Haig Keshishian, Linda L. Restifo, Wolfgang Rössler,
    Julie H. Simpson, Nicholas J. Strausfeld, Roland Strauss, Leslie B. Vosshall,
    Insect Brain Name Working Group (2013). A systematic nomenclature for the
    insect brain. Neuron 81 (4), 755-765. doi:10.1016/j.neuron.2013.12.017

    """

IBN = _IBN(**template_meta['IBN'])


class _IBNWB(FlyTemplateBrain):
    """Insect Brain Nomenclature Whole Brain reference brain.

    A synthetic whole brain constructed from the Insect Brain Nomenclature
    template brain. The original confocal stack was duplicated, mirrored about a
    vertical axis and then displaced by 392 pixels in x and then merged with the
    original, with a linear blend in the overlapping region.

    The surface model was constructed in Amira in the Jefferis Lab using a
    simple median filter, followed by thresholding and a surface simplification.

    References
    ----------
    Kei Ito, Kazunori Shinomiya, Masayoshi Ito, J. Douglas Armstrong, George
    Boyan, Volker Hartenstein, Steffen Harzsch, Martin Heisenberg, Uwe Homberg,
    Arnim Jenett, Haig Keshishian, Linda L. Restifo, Wolfgang Rössler, Julie H.
    Simpson, Nicholas J. Strausfeld, Roland Strauss, Leslie B. Vosshall, Insect
    Brain Name Working Group (2013). A systematic nomenclature for the insect
    brain. Neuron 81 (4), 755-765. doi:10.1016/j.neuron.2013.12.017

    """

IBNWB = _IBNWB(**template_meta['IBNWB'])


class _IS2(FlyTemplateBrain):
    """IS2 reference brain.

    References
    ----------
    Cachero S., Ostrovsky A.D., Yu J.Y., Dickson B.J., and Jefferis G.S.X.E.
    (2010). Sexual dimorphism in the fly brain. Curr Biol 20 (18), 1589-601.
    doi:10.1016/j.cub.2010.07.045

    """

IS2 = _IS2(**template_meta['IS2'])


class _JFRC2(FlyTemplateBrain):
    """JFRC2 reference brain.

    The JFRC2 reference brain is a spatially calibrated version of the original
    FlyLight reference brain (JFRC), which was delivered uncalibrated. This in
    turn was derived from a single female brain stained with nc82, that was
    imaged at 1 micron spacing in Z. It was then interpolated in Z to give an
    isotropic voxel size of 0.622088 microns.

    The JFRC2.surf surface model was constructed in Amira in the Jefferis Lab
    using a simple threshold, followed by a surface simplification.

    References
    ----------
    Arnim Jenett, Gerald M. Rubin, Teri-T.B. Ngo, David Shepherd, Christine
    Murphy, Heather Dionne, Barret D. Pfeiffer, Amanda Cavallaro, Donald Hall,
    Jennifer Jeter, Nirmala Iyer, Dona Fetter, Joanna H. Hausenfluck,
    Hanchuan Peng, Eric T. Trautman, Robert R. Svirskas, Eugene W. Myers,
    Zbigniew R. Iwinski, Yoshinori Aso, Gina M. DePasquale, Adrianne Enos,
    Phuson Hulamm, Shing Chun Benny Lam, Hsing-Hsi Li, Todd R. Laverty, Fuhui
    Long, Lei Qu, Sean D. Murphy, Konrad Rokicki, Todd Safford, Kshiti Shaw,
    Julie H. Simpson, Allison Sowell, Susana Tae, Yang Yu,
    Christopher T. Zugates (2012). A GAL4-Driver Line Resource for Drosophila
    Neurobiology. Cell Reports 2 (4), 991 - 1001. doi:10.1016/j.celrep.2012.09.011

    """

JFRC2 = _JFRC2(**template_meta['JFRC2'])


class _T1(FlyTemplateBrain):
    """T1 reference brain.

    Template information and surface model for the T1 reference brain

    The surface model was constructed in Amira in the Jefferis Lab using a
    simple threshold, followed by a surface simplification.

    References
    ----------
    Jai Y. Yu, Makoto I. Kanai, Ebru Demir, Gregory S. X. E. Jefferis,
    Barry J. Dickson (2010). Cellular Organization of the Neural Circuit that
    Drives Drosophila Courtship Behavior. Current Biology 20 (18), 1602-1614.
    doi:10.1016/j.cub.2010.08.025

    Jai Y. Yu, Makoto I. Kanai, Ebru Demir, Gregory S. X. E. Jefferis,
    Barry J. Dickson (2010). Cellular Organization of the Neural Circuit that
    Drives Drosophila Courtship Behavior. Current Biology 20 (18), 1602-1614.
    doi:10.1016/j.cub.2010.08.025

    """

T1 = _T1(**template_meta['T1'])


class _Dmel(FlyTemplateBrain):
    """D. melanogaster reference brain.

    The Dmel reference brain is a shape averaged template brain generated using
    the CMTK avg_adm tool. See https://github.com/jefferislab/MakeAverageBrain
    for the relevant code.

    The surface model was constructed in Amira by L. Goetz and G. Jefferis using
    a simple threshold, followed by a surface simplification to ~ 18,000 faces.

    References
    ----------
    doi:10.5281/zenodo.10591

    """

Dmel = _Dmel(**template_meta['Dmel'])


class _DsecI(FlyTemplateBrain):
    """D. sechellia reference brain.

    The DsecI reference brain is a shape averaged template brain generated using
    the CMTK avg_adm tool. See https://github.com/jefferislab/MakeAverageBrain
    for the relevant code.

    The surface model was constructed in Amira by G. Jefferis and R. Benton
    using a Z drop correction of the DsecI reference brain in Amira (e^u)
    followed by a simple threshold (10000), surface simplification to ~ 18,000
    faces, default surface smoothing and manual editing in meshlab to remove a
    small unconnected island of points.

    """

DsecI = _DsecI(**template_meta['DsecI'])


class _Dsim(FlyTemplateBrain):
    """D. simulans reference brain.

    The Dsim reference brain is a shape averaged template brain generated using
    the CMTK avg_adm tool. See https://github.com/jefferislab/MakeAverageBrain
    for the relevant code.

    The surface model was constructed in Amira by L. Goetz and G. Jefferis using
    a simple threshold, followed by a surface simplification to ~ 18,000 faces.

    References
    ----------
    doi:10.5281/zenodo.10594

    """

Dsim = _Dsim(**template_meta['Dsim'])


class _Dvir(FlyTemplateBrain):
    """D. virilis reference brain.

    The Dvir reference brain is a shape averaged template brain generated using
    the CMTK avg_adm tool. See https://github.com/jefferislab/MakeAverageBrain
    for the relevant code.

    The surface model was constructed in Amira by L. Goetz and G. Jefferis using
    a simple threshold, followed by a surface simplification to ~ 18,000 faces.

    References
    ----------
    doi:10.5281/zenodo.10593

    """

Dvir = _Dvir(**template_meta['Dvir'])


class _JFRC2013(FlyTemplateBrain):
    """JFRC2013 reference brain.

    The JFRC2013 reference brain is a single female brain. It is a spatially
    calibrated version of the brain used in Aso et al. 2014, "The neuronal
    architecture of the mushroom body provides a logic for associative learning".

    JFRC2013.surf was generated in Amira from a 2 micron downsampled and median
    filtered version of the JFRC2013 template brain. Further cleaning was then
    carried out in MeshLab to remove non-manifold edges and fill holes.

    JFRC2013DS is a downsampled version of the JFRC2013 reference brain,
    designed for use with images taken on a microscope with 20 x magnification.
    The downsampling has shrunk the z direction, such that the brain appears
    flattened when compared with the original.

    Calibration
    -----------
    The isotropic calibration of 0.38 microns is based on a personal
    communication from Yoshi Aso on 21st May 2014, where he noted:

    "It is 0.38um isotropic. Due to dehydration steps with EtOH, tissues are
    about 20% smaller than when mounted in Vectashield or other glycerol based
    mounting medium."

    No attempt was made to correct for this shrinkage artefact.

    References
    ----------
    Aso, Y., Sitaraman, D., Ichinose, T., Kaun, K. R., Vogt, K.,
    Belliart-Guerin, G., Placais, P.-Y., Robie, A. A., Yamagata, N.,
    Schnaitmann, C., Rowell, W. J., Johnston, R. M., Ngo, T.-T. B., Chen, N.,
    Korff, W., Nitabach, M. N., Heberlein, U., Preat, T., Branson, K. M.,
    Tanimoto, H. and Rubin, G. M. (2014b). Mushroom body output neurons encode
    valence and guide memory-based action selection in Drosophila. Elife 3,
    e04580. doi:10.7554/eLife.04577

    """

JFRC2013 = _JFRC2013(**template_meta['JFRC2013'])


class _JFRC2013DS(FlyTemplateBrain):
    """JFRC2013DS reference brain.

    The JFRC2013 reference brain is a single female brain. It is a spatially
    calibrated version of the brain used in Aso et al. 2014, "The neuronal
    architecture of the mushroom body provides a logic for associative learning".

    JFRC2013.surf was generated in Amira from a 2 micron downsampled and median
    filtered version of the JFRC2013 template brain. Further cleaning was then
    carried out in MeshLab to remove non-manifold edges and fill holes.

    JFRC2013DS is a downsampled version of the JFRC2013 reference brain,
    designed for use with images taken on a microscope with 20 x magnification.
    The downsampling has shrunk the z direction, such that the brain appears
    flattened when compared with the original.

    Calibration
    -----------
    The isotropic calibration of 0.38 microns is based on a personal
    communication from Yoshi Aso on 21st May 2014, where he noted:

    "It is 0.38um isotropic. Due to dehydration steps with EtOH, tissues are
    about 20% smaller than when mounted in Vectashield or other glycerol based
    mounting medium."

    No attempt was made to correct for this shrinkage artefact.

    References
    Aso, Y., Sitaraman, D., Ichinose, T., Kaun, K. R., Vogt, K.,
    Belliart-Guerin, G., Placais, P.-Y., Robie, A. A., Yamagata, N.,
    Schnaitmann, C., Rowell, W. J., Johnston, R. M., Ngo, T.-T. B., Chen, N.,
    Korff, W., Nitabach, M. N., Heberlein, U., Preat, T., Branson, K. M.,
    Tanimoto, H. and Rubin, G. M. (2014b). Mushroom body output neurons encode
    valence and guide memory-based action selection in Drosophila. Elife 3,
    e04580. doi:10.7554/eLife.04577

    """

JFRC2013DS = _JFRC2013DS(**template_meta['JFRC2013DS'])


class _JRC2018F(FlyTemplateBrain):
    """JRC2018F reference brain.

    The JRC2018F reference brain is an average template brain constructed from
    brains labelled with brp-SNAP, dehydrated, and mounted in DPX and imaged at
    0.19 x 0.19 x 0.38 microns. The image was downsampled in XY to result in a
    0.38 micron isotropic voxel size, which we take to be the standard JRC2018F
    space.

    The JRC2018U reference brain was constructed as for JRC2018F brain but
    pooling both male and female brains.

    JRC2018F.surf, JRC2018U.surf were generated in Amira from a 2 micron
    downsampled, Lanczos filtered 8 bit version of the respective template
    brain. A surface was then generated with a threshold level of 20 in case
    of brains this was then smoothed and downsampled.

    Details
    -------
    For the central brain, Bogovic and Saalfeld used 36 female individuals (72
    images including left-right flips) for the female template, 26 male
    individuals (52 image with left-right flips) for the male template, and the
    union of both for the unisex brain template: 62 individuals (124 images with
    left-right flips).

    Downloaded from https://www.janelia.org/open-science/jrc-2018-brain-templates

    References
    ----------
    An unbiased template of the Drosophila brain and ventral nerve cord.
    John A Bogovic, Hideo Otsuna, Larissa Heinrich, Masayoshi Ito,
    Jennifer Jeter, Geoffrey Meissner, Aljoscha Nern, Jennifer Colonell,
    Oz Malkesman, Kei Ito, Stephan Saalfeld.
    PLOS One; doi: https://doi.org/10.1371/journal.pone.0236495

    """

JRC2018F = _JRC2018F(**template_meta['JRC2018F'])


class _JRC2018U(FlyTemplateBrain):
    """JRC2018U reference brain.

    The JRC2018F reference brain is an average template brain constructed from
    brains labelled with brp-SNAP, dehydrated, and mounted in DPX and imaged at
    0.19 x 0.19 x 0.38 microns. The image was downsampled in XY to result in a
    0.38 micron isotropic voxel size, which we take to be the standard JRC2018F
    space.

    The JRC2018U reference brain was constructed as for JRC2018F brain but
    pooling both male and female brains.

    JRC2018F.surf, JRC2018U.surf were generated in Amira from a 2 micron
    downsampled, Lanczos filtered 8 bit version of the respective template
    brain. A surface was then generated with a threshold level of 20 in case
    of brains this was then smoothed and downsampled.

    Details
    -------
    For the central brain, Bogovic and Saalfeld used 36 female individuals (72
    images including left-right flips) for the female template, 26 male
    individuals (52 image with left-right flips) for the male template, and the
    union of both for the unisex brain template: 62 individuals (124 images with
    left-right flips).

    Downloaded from https://www.janelia.org/open-science/jrc-2018-brain-templates

    References
    ----------
    An unbiased template of the Drosophila brain and ventral nerve cord.
    John A Bogovic, Hideo Otsuna, Larissa Heinrich, Masayoshi Ito,
    Jennifer Jeter, Geoffrey Meissner, Aljoscha Nern, Jennifer Colonell,
    Oz Malkesman, Kei Ito, Stephan Saalfeld.
    PLOS One; doi: https://doi.org/10.1371/journal.pone.0236495

    """

JRC2018U = _JRC2018U(**template_meta['JRC2018U'])


class _JRC2018M(FlyTemplateBrain):
    """JRC2018M reference brain.

    The JRC2018M reference brain is an average template brain constructed from
    brains labelled with brp-SNAP, dehydrated, and mounted in DPX and imaged at
    0.19 x 0.19 x 0.38 microns. The image was downsampled in XY to result in a
    0.38 micron isotropic voxel size, which we take to be the standard JRC2018M
    space.

    The JRC2018M reference brain was constructed as for JRC2018F brain but from
    male instead of female brains.

    JRC2018M mesh was generated using a downsampled, 8 bit version of the
    template brain. A surface was then generated with a threshold level of 40
    which was subsequently smoothed, downsampled and minimally cleaned-up
    in Blender.

    Details
    -------
    For the central brain, Bogovic and Saalfeld used 36 female individuals (72
    images including left-right flips) for the female template, 26 male
    individuals (52 image with left-right flips) for the male template, and the
    union of both for the unisex brain template: 62 individuals (124 images with
    left-right flips).

    Downloaded from https://www.janelia.org/open-science/jrc-2018-brain-templates

    References
    ----------
    An unbiased template of the Drosophila brain and ventral nerve cord.
    John A Bogovic, Hideo Otsuna, Larissa Heinrich, Masayoshi Ito,
    Jennifer Jeter, Geoffrey Meissner, Aljoscha Nern, Jennifer Colonell,
    Oz Malkesman, Kei Ito, Stephan Saalfeld.
    PLOS One; doi: https://doi.org/10.1371/journal.pone.0236495

    """

JRC2018M = _JRC2018M(**template_meta['JRC2018M'])


class _JRCFIB2018F(FlyTemplateBrain):
    """JRCFIB2018F aka "hemibrain" dataset.

    The JRCFIB2018F reference brain is a stitched FIB SEM volume completed at
    HHMI Janelia Research Campus in 2018.

    The JRCFIB2018Fraw reference brain is uncalibrated (i.e. has units of raw
    pixels), whereas JRCFIB2018F and JRCFIB2018Fum have units of nanometers
    and microns with 8x8x8nm isotropic voxels, respectively.

    References
    ----------
    A Connectome of the Adult Drosophila Central Brain Shan Xu, C; Januszewski,
    Michal; Lu, Zhiyuan; Takemura, Shin-Ya; Hayworth, Kenneth; Huang, Gary;
    Shinomiya, Kazunori; Maitin-Shepard, Jeremy; Ackerman, David; Berg, Stuart;
    Blakely, Tim; Bogovic, John; Clements, Jody; Dolafi, Tom; Hubbard, Philip;
    Kainmueller, Dagmar; Katz, William; Kawase, Takashi; Khairy, Khaled;
    Leavitt, Laramie; Li, Peter H; Lindsey, Larry; Neubarth, Nicole;
    Olbris, Donald J; Otsuna, Hideo; Troutman, Eric T; Umayam, Lowell;
    Zhao, Ting; Ito, Masayoshi; Goldammer, Jens; Wolff, Tanya; Svirskas, Robert;
    Schlegel, Philipp; Neace, Erika R; Knecht, Christopher J;
    Alvarado, Chelsea X; Bailey, Dennis; Ballinger, Samantha; Borycz, Jolanta A;
    Canino, Brandon; Cheatham, Natasha; Cook, Michael; Dreyer, Marisa;
    Duclos, Octave; Eubanks, Bryon; Fairbanks, Kelli; Finley, Samantha;
    Forknall, Nora; Francis, Audrey; Hopkins, Gary Patrick; Joyce, Emily M;
    Kim, Sungjin; Kirk, Nicole A; Kovalyak, Julie; Lauchie, Shirley A;
    Lohff, Alanna; Maldonado, Charli; Manley, Emily A; McLin, Sari;
    Mooney, Caroline; Ndama, Miatta; Ogundeyi, Omotara; Okeoma, Nneoma;
    Ordish, Christopher; Padilla, Nicholas; Patrick, Christopher;
    Paterson, Tyler; Phillips, Elliott E; Phillips, Emily M; Rampally, Neha;
    Ribeiro, Caitlin; Robertson, Madelaine K; Rymer, Jon Thomson; Ryan, Sean M;
    Sammons, Megan; Scott, Anne K; Scott, Ashley L; Shinomiya, Aya;
    Smith, Claire; Smith, Kelsey; Smith, Natalie L; Sobeski, Margaret A;
    Suleiman, Alia; Swift, Jackie; Takemura, Satoko; Talebi, Iris;
    Tarnogorska, Dorota; Tenshaw, Emily; Tokhi, Temour; Walsh, John J;
    Yang, Tansy; Horne, Jane Anne; Li, Feng; Parekh, Ruchi; Rivlin, Patricia K;
    Jayaraman, Vivek; Ito, Kei; Saalfeld, Stephan; George, Reed;
    Meinertzhagen, Ian; Rubin, Gerald M; Hess, Harald F; Scheffer, Louis K;
    Jain, Viren; Plaza, Stephen M bioRxiv doi:10.1101/2020.01.21.911859.

    """
    @property
    def mesh(self):
        """On-demand loading of surface mesh."""
        if not hasattr(self, '_mesh'):
            # Load the raw mesh (voxels)
            fp = os.path.join(mesh_filepath, f'{self.label}raw.ply')
            self._mesh = tm.load_mesh(fp)
            # Convert voxels to nanometers
            self._mesh.vertices *= 8
        return self._mesh

    @property
    def bbox(self):
        """On-demand loading of approximate bounding box."""
        if not hasattr(self, '_mesh_bbox'):
            # Load the raw mesh (voxels)
            fp = os.path.join(mesh_filepath, f'{self.label}raw_bbox.ply')
            self._mesh_bbox = tm.load_mesh(fp)
            # Convert voxels to nanometers
            self._mesh_bbox.vertices *= 8
        return self._mesh_bbox

JRCFIB2018F = _JRCFIB2018F(**template_meta['JRCFIB2018F'])


class _JRCFIB2018Fum(_JRCFIB2018F):
    @property
    def mesh(self):
        """On-demand loading of surface mesh."""
        if not hasattr(self, '_mesh'):
            # Load the raw mesh (voxels)
            fp = os.path.join(mesh_filepath, f'{self.label}raw.ply')
            self._mesh = tm.load_mesh(fp)
            # Convert voxels to microns
            self._mesh.vertices *= (8 / 1000)
        return self._mesh

    @property
    def bbox(self):
        """On-demand loading of approximate bounding box."""
        if not hasattr(self, '_mesh_bbox'):
            # Load the raw mesh (voxels)
            fp = os.path.join(mesh_filepath, f'{self.label}raw_bbox.ply')
            self._mesh_bbox = tm.load_mesh(fp)
            # Convert voxels to microns
            self._mesh_bbox.vertices *= (8 / 1000)
        return self._mesh_bbox

JRCFIB2018Fum = _JRCFIB2018Fum(**template_meta['JRCFIB2018Fum'])


class _JRCFIB2018Fraw(_JRCFIB2018F):
    @property
    def mesh(self):
        """On-demand loading of surface mesh."""
        if not hasattr(self, '_mesh'):
            # Load the raw mesh (voxels)
            fp = os.path.join(mesh_filepath, f'{self.label}.ply')
            self._mesh = tm.load_mesh(fp)
        return self._mesh

    @property
    def bbox(self):
        """On-demand loading of approximate bounding box."""
        if not hasattr(self, '_mesh_bbox'):
            # Load the raw mesh (voxels)
            fp = os.path.join(mesh_filepath, f'{self.label}_bbox.ply')
            self._mesh_bbox = tm.load_mesh(fp)
        return self._mesh_bbox

JRCFIB2018Fraw = _JRCFIB2018Fraw(**template_meta['JRCFIB2018Fraw'])

class _JRCFIB2022M(FlyTemplateBrain):
    """JRCFIB2022M aka "male CNS" dataset.

    The JRCFIB2022M EM volume is a whole male CNS (brain + VNC) currently being
    generated by FlyEM at HHMI Janelia Research Campus. At this point, only the
    brain portion of the volume is available.

    The mesh was generated from a point cloud of automaticaly detected synaptic
    t-bars.

    The JRCFIB2022Mraw reference brain is uncalibrated (i.e. has units of raw
    pixels), whereas JRCFIB2022M and JRCFIB2022Mum have units of nanometers
    and microns with 8x8x8nm isotropic voxels, respectively.

    """
    @property
    def mesh(self):
        """On-demand loading of surface mesh."""
        if not hasattr(self, '_mesh'):
            # Load the raw mesh (voxels)
            fp1 = os.path.join(mesh_filepath, 'JRCFIB2022M_brain.ply')
            fp2 = os.path.join(mesh_filepath, 'JRCFIB2022M_vnc.ply')
            self._mesh = tm.util.concatenate(
                tm.load_mesh(fp1), tm.load_mesh(fp2)
                )
        return self._mesh

    @property
    def mesh_brain(self):
        """On-demand loading of brain surface mesh."""
        if not hasattr(self, '_mesh_brain'):
            # Load the raw mesh (voxels)
            fp = os.path.join(mesh_filepath, 'JRCFIB2022M_brain.ply')
            self._mesh_brain = tm.load_mesh(fp)
        return self._mesh_brain

    @property
    def mesh_vnc(self):
        """On-demand loading of VNC surface mesh."""
        if not hasattr(self, '_mesh_vnc'):
            # Load the raw mesh (voxels)
            fp = os.path.join(mesh_filepath, 'JRCFIB2022M_vnc.ply')
            self._mesh_vnc = tm.load_mesh(fp)
        return self._mesh_vnc

JRCFIB2022M = _JRCFIB2022M(**template_meta['JRCFIB2022M'])

class _JRCFIB2022Mraw(_JRCFIB2022M):
    @property
    def mesh(self):
        mesh = super().mesh.copy()
        # Convert nanometers to voxels
        mesh.vertices /= 8
        return mesh

    @property
    def mesh_brain(self):
        mesh = super().mesh_brain.copy()
        # Convert nanometers to voxels
        mesh.vertices /= 8
        return mesh

    @property
    def mesh_vnc(self):
        mesh = super().mesh_vnc.copy()
        # Convert nanometers to voxels
        mesh.vertices /= 8
        return mesh

JRCFIB2022Mraw = _JRCFIB2022Mraw(**template_meta['JRCFIB2022Mraw'])


class _JRCVNC2018F(FlyTemplateBrain):
    """JRC2018 reference ventral nerve chords.

    The JRCVNC2018F reference VNC is an average template VNC constructed from
    VNCs labelled with brp-SNAP, dehydrated, and mounted in DPX and imaged at
    0.19 x 0.19 x 0.38 microns. The image was downsampled to result in a 0.4
    micron isotropic voxel size, which we take to be the standard JRCVNC2018F
    space.

    The JRCVNC2018U reference VNC was constructed as for JRCVNC2018F VNC but
    pooling both male and female brains.

    The JRCVNC2018F mesh, was generated in Amira from a 2 micron downsampled,
    Lanczos filtered version of the respective template VNC. A surface was then
    generated with a threshold level of 2800 and then smoothed and downsampled.

    The JRCVNC2018U mesh, was generated in Amira from a 2 micron downsampled,
    Lanczos filtered 8 bit version of the respective template VNC. A surface was
    then generated with a threshold level of 20 and then smoothed and
    downsampled.

    Details
    -------
    For the VNC, Bogovic and Saalfeld used 36 female individuals (72 images
    including left-right flips) for the female template, 39 male individuals
    (78 image with left-right flips) for the male template, and the union of
    both for the unisex brain template: 75 individuals (150 images with
    left-right flips).

    Downloaded from https://www.janelia.org/open-science/jrc-2018-brain-templates

    References
    ----------
    An unbiased template of the Drosophila brain and ventral nerve cord.
    John A Bogovic, Hideo Otsuna, Larissa Heinrich, Masayoshi Ito,
    Jennifer Jeter, Geoffrey Meissner, Aljoscha Nern, Jennifer Colonell,
    Oz Malkesman, Kei Ito, Stephan Saalfeld.
    PLOS One; doi: https://doi.org/10.1371/journal.pone.0236495

    """

JRCVNC2018F = _JRCVNC2018F(**template_meta['JRCVNC2018F'])


class _JRCVNC2018M(FlyTemplateBrain):
    """JRC2018 reference ventral nerve chords.

    The JRCVNC2018M reference VNC is an average template VNC constructed from
    VNCs labelled with brp-SNAP, dehydrated, and mounted in DPX and imaged at
    0.19 x 0.19 x 0.38 microns. The image was downsampled to result in a 0.4
    micron isotropic voxel size, which we take to be the standard JRCVNC2018F
    space.

    The JRCVNC2018U reference VNC was constructed as for JRCVNC2018F VNC but
    pooling both male and female brains.

    The JRCVNC2018M mesh, was generated in Amira from a 2 micron downsampled,
    Lanczos filtered version of the respective template VNC. A surface was then
    generated with a threshold level of 2800 and then smoothed and downsampled.

    The JRCVNC2018U mesh, was generated in Amira from a 2 micron downsampled,
    Lanczos filtered 8 bit version of the respective template VNC. A surface was
    then generated with a threshold level of 20 and then smoothed and
    downsampled.

    Details
    -------
    For the VNC, Bogovic and Saalfeld used 36 female individuals (72 images
    including left-right flips) for the female template, 39 male individuals
    (78 image with left-right flips) for the male template, and the union of
    both for the unisex brain template: 75 individuals (150 images with
    left-right flips).

    Downloaded from https://www.janelia.org/open-science/jrc-2018-brain-templates

    References
    ----------
    An unbiased template of the Drosophila brain and ventral nerve cord.
    John A Bogovic, Hideo Otsuna, Larissa Heinrich, Masayoshi Ito,
    Jennifer Jeter, Geoffrey Meissner, Aljoscha Nern, Jennifer Colonell,
    Oz Malkesman, Kei Ito, Stephan Saalfeld.
    PLOS One; doi: https://doi.org/10.1371/journal.pone.0236495
    """

JRCVNC2018M = _JRCVNC2018M(**template_meta['JRCVNC2018M'])


class _JRCVNC2018U(FlyTemplateBrain):
    """JRC2018 reference ventral nerve chords.

    The JRCVNC2018U reference VNC is an average template VNC constructed from
    VNCs labelled with brp-SNAP, dehydrated, and mounted in DPX and imaged at
    0.19 x 0.19 x 0.38 microns. The image was downsampled to result in a 0.4
    micron isotropic voxel size, which we take to be the standard JRCVNC2018F
    space.

    The JRCVNC2018U reference VNC was constructed as for JRCVNC2018F/M VNCs but
    pooling both male and female brains.

    The JRCVNC2018F mesh, was generated in Amira from a 2 micron downsampled,
    Lanczos filtered version of the respective template VNC. A surface was then
    generated with a threshold level of 2800 and then smoothed and downsampled.

    The JRCVNC2018U mesh, was generated in Amira from a 2 micron downsampled,
    Lanczos filtered 8 bit version of the respective template VNC. A surface was
    then generated with a threshold level of 20 and then smoothed and
    downsampled.

    Details
    -------
    For the VNC, Bogovic and Saalfeld used 36 female individuals (72 images
    including left-right flips) for the female template, 39 male individuals
    (78 image with left-right flips) for the male template, and the union of
    both for the unisex brain template: 75 individuals (150 images with
    left-right flips).

    Downloaded from https://www.janelia.org/open-science/jrc-2018-brain-templates

    References
    ----------
    An unbiased template of the Drosophila brain and ventral nerve cord.
    John A Bogovic, Hideo Otsuna, Larissa Heinrich, Masayoshi Ito,
    Jennifer Jeter, Geoffrey Meissner, Aljoscha Nern, Jennifer Colonell,
    Oz Malkesman, Kei Ito, Stephan Saalfeld.
    PLOS One; doi: https://doi.org/10.1371/journal.pone.0236495
    """

JRCVNC2018U = _JRCVNC2018U(**template_meta['JRCVNC2018U'])


class _VNCIS1(FlyTemplateBrain):
    """VNCIS1 reference neuropil.

    The VNCIS1 template is a shape-averaged, intersex template containing the
    D. melanogaster adult ventral nerve cord (more properly the
    thoracico-abdominal ganglion) generated using the CMTK avg_adm tool.

    References
    ----------
    Cachero S., Ostrovsky A.D., Yu J.Y., Dickson B.J., and Jefferis G.S.X.E.
    (2010). Sexual dimorphism in the fly brain. Curr Biol 20 (18), 1589-601.
    doi:10.1016/j.cub.2010.07.045

    """

VNCIS1 = _VNCIS1(**template_meta['VNCIS1'])


class _FAFB14(FlyTemplateBrain):
    """Full Adult Fly Brain (FAFB) EM volume.

    This SSTEM volume comprising an entire female Drosophila brain was imaged at
    4x4x40nm by Zheng et al. (2018) and is availabe for download at
    https://temca2data.org/. The meta data and associated mesh represent
    version 14 (FAFB14) of this data set.

    The FAFB mesh was generated from automatically detected synapses in this
    dataset (Buhmann et al., 2019). For this the synapses were grouped into
    2 micron bins which were then used to generate a mesh using a marching
    cube algorithm. This raw mesh was then cleaned up, smoothed and downsampled
    in Blender 3D.

    References
    ----------
    Zheng Z, Lauritzen JS, Perlman E, Robinson CG, Nichols M, Milkie D,
    Torrens O, Price J, Fisher CB, Sharifi N, Calle-Schuler SA, Kmecova L,
    Ali IJ, Karsh B, Trautman ET, Bogovic JA, Hanslovsky P, Jefferis GSXE,
    Kazhdan M, Khairy K, Saalfeld S, Fetter RD, Bock DD.
    A Complete Electron Microscopy Volume of the Brain of Adult Drosophila
    melanogaster. Cell. 2018 Jul 26;174(3):730-743.e22.
    doi: 10.1016/j.cell.2018.06.019.

    Julia Buhmann, Arlo Sheridan, Stephan Gerhard, Renate Krause, Tri Nguyen,
    Larissa Heinrich, Philipp Schlegel, Wei-Chung Allen Lee, Rachel Wilson,
    Stephan Saalfeld, Gregory Jefferis, Davi Bock, Srinivas Turaga,
    Matthew Cook, Jan Funke.
    Automatic Detection of Synaptic Partners in a Whole-Brain Drosophila EM Dataset
    bioRxiv 2019.12.12.874172; doi: https://doi.org/10.1101/2019.12.12.874172

    """

FAFB14 = FAFB = _FAFB14(**template_meta['FAFB14'])


class _FLYWIRE(FlyTemplateBrain):
    """Re-aligned version of the Full Adult Fly Brain (FAFB) SSTEM volume.

    The original volume was imaged by Zhen et al. (2018). Dorkenwald et al.
    (2022) re-aligned the volume to help with automatic segmentation. On
    average the offset between FAFB14 and FlyWire is less than a micron.

    The neuropil mesh was created by transforming the FAFB14 mesh into FlyWire
    space (effectively applying the FAFB14->FlyWire re-alignment vector field).

    References
    ----------
    Dorkenwald, S., McKellar, C.E., Macrina, T. et al.
    FlyWire: online community for whole-brain connectomics.
    Nat Methods 19, 119–128 (2022).
    https://doi.org/10.1038/s41592-021-01330-0

    Zheng Z, Lauritzen JS, Perlman E, Robinson CG, Nichols M, Milkie D,
    Torrens O, Price J, Fisher CB, Sharifi N, Calle-Schuler SA, Kmecova L,
    Ali IJ, Karsh B, Trautman ET, Bogovic JA, Hanslovsky P, Jefferis GSXE,
    Kazhdan M, Khairy K, Saalfeld S, Fetter RD, Bock DD.
    A Complete Electron Microscopy Volume of the Brain of Adult Drosophila
    melanogaster. Cell. 2018 Jul 26;174(3):730-743.e22.
    doi: 10.1016/j.cell.2018.06.019.
    """
    @property
    def mesh_whole_brain(self):
        """On-demand loading of whole brain mesh."""
        if not hasattr(self, '_mesh_whole_brain'):
            fp = os.path.join(mesh_filepath, f'{self.label}_whole_brain.ply')

            self._mesh_whole_brain = tm.load_mesh(fp)

        return self._mesh_whole_brain

FLYWIRE = _FLYWIRE(**template_meta['FLYWIRE'])


class _COURT2017VNS(FlyTemplateBrain):
    """Female Adult Nervous System (NC82).

    Original image provided by Wyatt Korff at Janelia Research Campus with a
    neuropil background stain (NC82). The sample was adjusted to align with the
    image axis.

    References
    ----------
    Court RC.
    Dissecting the ventral nervous system in Drosophila melanogaster
    PhD Thesis 2017; http://hdl.handle.net/1842/25704

    Robert Christopher Court, James Armstrong, Jana Börner, Gwyneth Card,
    Marta Costa, Michael Dickinson, Carsten Duch, Wyatt Korff, Richard Mann,
    David Merritt, Rod Murphey, Shigehiro Namiki, Andrew Seeds, David Shepherd,
    Troy Shirangi, Julie Simpson, James Truman, John Tuthill, Darren Williams
    A Systematic Nomenclature for the Drosophila Ventral Nervous System
    biorxiv. 2017. doi: https://doi.org/10.1101/122952
    """

COURT2017VNS = _COURT2017VNS(**template_meta['COURT2017VNS'])


class _COURT2018VNS(FlyTemplateBrain):
    """Female Adult Nervous System.

    A warped version of Court2017 to straighten the midline to make the template
    symmetric (work done by Hideo Otsuna) leading to JRCVNC2018F.

    References
    ----------
    Robert Court, Shigehiro Namiki, J Douglas Armstrong, Jana Börner, Gwyneth Card,
    Marta Costa, Michael Dickinson, Carsten Duch, Wyatt Korff, Richard Mann,
    David Merritt, Rod K Murphey, Andrew Seeds, Troy Shirangi, Julie H. Simpson,
    James W Truman, John Tuthill, Darren Williams, David Shepherd
    biorxiv. 2020. doi: https://doi.org/10.1101/122952

    An unbiased template of the Drosophila brain and ventral nerve cord.
    John A Bogovic, Hideo Otsuna, Larissa Heinrich, Masayoshi Ito,
    Jennifer Jeter, Geoffrey Meissner, Aljoscha Nern, Jennifer Colonell,
    Oz Malkesman, Kei Ito, Stephan Saalfeld.
    PLOS One; doi: https://doi.org/10.1371/journal.pone.0236495
    """

COURT2018VNS = _COURT2018VNS(**template_meta['COURT2018VNS'])


class _FANC(FlyTemplateBrain):
    """Female Adult Nerve Cord

    Using a serial-section electron microscopy (EM) to acquire a synapse-resolution
    dataset containing the ventral nerve cord (VNC) of an adult female Drosophila
    melanogaster.

    References
    ----------
    Reconstruction of motor control circuits in adult Drosophila using automated
    transmission electron microscopy
    Jasper S Phelps, David Grant Colburn Hildebrand, Brett J Graham, Aaron T Kuan,
    Logan A Thomas, Tri M Nguyen, Julia Buhmann, Anthony W Azevedo, Anne Sustar,
    Sweta Agrawal, Mingguan Liu, Brendan L Shanny, Jan Funke, John C Tuthill,
    Wei-Chung Allen Lee
    Cell 2021 Feb 4;184(3):759-774.e18. doi: 10.1016/j.cell.2020.12.013.

    """

FANC = _FANC(**template_meta['FANC'])


class _MANC(FlyTemplateBrain):
    """Male Adult Nerve Cord.

    A FIBSEM volume containing a ventral nerve cord of an adult male
    Drosophila melanogaster.

    References
    ----------
    A Connectome of the Male Drosophila Ventral Nerve Cord
    Shin-ya Takemura, Kenneth J Hayworth, Gary B Huang, Michal Januszewski,
    Zhiyuan Lu, Elizabeth C Marin, Stephan Preibisch, C Shan Xu, John Bogovic,
    Andrew S Champion, Han SJ Cheong, Marta Costa, Katharina Eichler,
    William Katz, Christopher Knecht, Feng Li, Billy J Morris, Christopher Ordish,
    Patricia K Rivlin, Philipp Schlegel, Kazunori Shinomiya, Tomke Stürner,
    Ting Zhao, Griffin Badalamente, Dennis Bailey, Paul Brooks, Brandon S Canino,
    Jody Clements, Michael Cook, Octave Duclos, Christopher R Dunne, Kelli Fairbanks,
    Siqi Fang, Samantha Finley-May, Audrey Francis, Reed George, Marina Gkantia,
    Kyle Harrington, Gary Patrick Hopkins, Joseph Hsu, Philip M Hubbard,
    Alexandre Javier, Dagmar Kainmueller, Wyatt Korff, Julie Kovalyak,
    Dominik Krzemiński, Shirley A Lauchie, Alanna Lohff, Charli Maldonado,
    Emily A Manley, Caroline Mooney, Erika Neace, Matthew Nichols, Omotara Ogundeyi,
    Nneoma Okeoma, Tyler Paterson, Elliott Phillips, Emily M Phillips,
    Caitlin Ribeiro, Sean M Ryan, Jon Thomson Rymer, Anne K Scott, Ashley L Scott,
    David Shepherd, Aya Shinomiya, Claire Smith, Natalie Smith, Alia Suleiman,
    Satoko Takemura, Iris Talebi, Imaan FM Tamimi, Eric T Trautman, Lowell Umayam,
    John J Walsh, Tansy Yang, Gerald M Rubin, Louis K Scheffer, Jan Funke,
    Stephan Saalfeld, Harald F Hess, Stephen M Plaza, Gwyneth M Card,
    Gregory SXE Jefferis, Stuart Berg
    bioRxiv 2023.06.05.543757; doi: https://doi.org/10.1101/2023.06.05.543757

    """
    @property
    def mesh(self):
        """On-demand loading of surface mesh."""
        if not hasattr(self, '_mesh'):
            # Load the raw mesh (voxels)
            fp = os.path.join(mesh_filepath, f'{self.label}raw.ply')
            self._mesh = tm.load_mesh(fp)
            # Convert voxels to nanometers
            if self.units[0] == 'nm':
                self._mesh.vertices *= 8
        return self._mesh


# MANC in nanometers
MANC = _MANC(**template_meta['MANC'])
MANC.boundingbox = [b * 8 for b in MANC.boundingbox]
MANC.dims = [b * 8 for b in MANC.dims]
MANC.units = ['nm', 'nm', 'nm']


class _MANCraw(FlyTemplateBrain):
    """Male Adult Nerve Cord."""


# MANC in raw voxels (original)
MANCraw = _MANCraw(**template_meta['MANC'])
MANCraw.label = 'MANCraw'


class _DmelL1CNS_Seymour(FlyTemplateBrain):
    """L1 CNS ssTEM at 3.8x3.8x50 nm of whole Drosophila 1st instar larval CNS.

    Imaged and assembled by Rick Fetter and Albert Cardona.

    References
    ----------
    A multilevel multimodal circuit enhances action selection in Drosophila.
    Ohyama, T., Schneider-Mizell, C., Fetter, R. et al. Nature 520, 633–639 (2015).
    https://doi.org/10.1038/nature14297

    """

DmelL1CNS_Seymour = _DmelL1CNS_Seymour(**template_meta['Dmel-L1-CNS-Seymour'])


def register_templates():
    """Register template brains with navis."""
    templates = [FCWB, IBN, IBNWB, IS2, JFRC2, T1, Dmel, DsecI, Dsim, Dvir,
                 JFRC2013, JFRC2013DS,
                 JRC2018F, JRC2018U, JRC2018M,
                 JRCVNC2018F, JRCVNC2018U, JRCVNC2018M, VNCIS1,
                 FAFB14, FAFB, FLYWIRE,
                 JRCFIB2022M,JRCFIB2022Mraw,
                 JRCFIB2018F, JRCFIB2018Fraw,
                 FANC, MANC, MANCraw,
                 DmelL1CNS_Seymour,
                 COURT2017VNS, COURT2018VNS]

    for tmp in templates:
        transforms.registry.register_templatebrain(tmp, skip_existing=True)
