# Landmarks

## `lm-em-landmarks_v14.csv`
`lm-em-landmarks_v14.csv` contains landmarks to map locations in EM (FAFB v14)
space to JFRC2013 (aka DPX) space using a thin plate spline transform.

X,Y,Z correspond to locations in JFRC2013 template brain.
However, they are in raw voxel coordinates.
In contrast, X1,Y1,Z1 (which contain locations in FAFB space) are in nm.

See https://github.com/saalfeldlab/elm for the original source of the landmarks.

## `FLYWIRE_mirror_landmarks.csv`
`FLYWIRE_mirror_landmarks.csv` contains landmarks to compensate for left/right
asymmetries in FLYWIRE. These ~2k landmarks were generated by:
1. Evenly sampling the bounding box of the FAFB/FLYWIRE neuropil
2. Flip the points across the x-axis (`x_flip`, `y_flip`, `z_flip` columns)
3. Mirror the points properly via `JRC2018F` (`x_mirr`, `y_mirr`, `z_mirr` columns)

A thin plate spine transform based on those landmarks potentially 1 order of
magnitude faster than via `JRC2018F` but comes at a loss in precision: on
average, the direct transform is on average less than a nanometer off compared to the
long transform.

![](https://github.com/schlegelp/navis-flybrains/blob/main/flybrains/data/FLYWIRE_mirror_evaluation.png?raw=true)

The code for the generation and the evaluation lives in `FLYWIR4_mirror_landmarks.ipynb`.

## `FAFB14_mirror_landmarks.csv`

These were generated by xforming coordinates in `FLYWIRE_mirror_landmarks.csv` to
FlyWire space.

## `FLYWIRE/FAFB14_symmetrize_landmarks_nm.csv`
`FLYWIRE/FAFB14_symmetrize_landmarks_nm.csv` contains landmarks to transform FLYWIRE/FAFB14
data into a symmetrical space. These ~2k landmarks were generated by:
1. Evenly sampling the bounding box of the FAFB neuropil
2. Mirroring left points to the right via `JRC2018F`
3. Flipping the mirrored points back to the left without any warp transform

This is a quick-and-dirty alternative to transforming FLYWIRE/FAFB14 data to `JRC2018F`
(which is a symmetrical template brain).

The code for the generation of these landmarks lives in `FLYWIRE_symmetrize_landmarks.ipynb`.

## `FANC_mirror_landmarks.csv`
`FANC_mirror_landmarks.csv` contains landmarks to compensate for left/right
asymmetries in FANC. These ~1k landmarks were generated by:
1. Evenly sampling the bounding box of the FANC neuropil
2. Flip the points across the x-axis (`x_flip`, `y_flip`, `z_flip` columns)
3. Mirror the points properly via `MANCsym` (`x_mirr`, `y_mirr`, `z_mirr` columns)

The code for the generation of these landmarks lives in `FANC_mirror_landmarks.ipynb`.

## `MANC_FANC_landmarks_nm.csv`
`MANC_FANC_landmarks_nm.csv` contains landmarks to transform between the
male adult nerve cord (MANC) and female adult nerve cord (FANC) VNC data sets.

These landmarks were manually placed at cross-identifiable locations in both
datasets.

## `maleCNS_brain_FAFB_landmarks_nm.csv`
This file contains landmarks to transform between the brain portion of the
Janelia full male CNS and the FAFB datasets.

These landmarks were manually placed using the Big Warp on the images created
from synapse clouds.

# Transforms

## `TransformParameters.FixedFANC.txt` & TransformParameters.FixedTemplate.txt
These files represent Elastix transforms for FANC (v3) -> JRCVNC2018F and
JRCVNC2018F -> FANC (v3), respectively. They have been provided by Jasper
Phelps (see https://github.com/htem/FANC_auto_recon/tree/main/transforms).
