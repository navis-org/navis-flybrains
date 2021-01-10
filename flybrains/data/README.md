# Landmarks

`lm-em-landmarks_v14.csv` contains landmarks to map locations in EM (FAFB v14)
space to JFRC2013 (aka DPX) space using a thin plate spline transform.

X,Y,Z correspond to locations in JFRC2013 template brain.
However, they are in raw voxel coordinates.
In contrast, X1,Y1,Z1 (which contain locations in FAFB space) are in nm.

See https://github.com/saalfeldlab/elm for the original source of the landmarks.

`FAFB14_mirror_landmarks.csv` contains landmarks to compensate for left/right
asymmetries in FAFB14. Pairs of landmarks (e.g. "antlers L" and "antler R")
were placed manually to approximately corresponding locations on the left and
right hemisphere. To generate a mirror transform, for each landmark (e.g.
"antlers L") the corresponding landmark on the other side (e.g. "antlers R")
was mirrored to the same side using an affine transform. 
