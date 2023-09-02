The FlyWire whole brain tissue mesh was made from the tissue mask from
the FAFB segmentation by Peter Li (Google) available at
`precomputed://gs://fafb-ffn1-20190805/tissue_mask_argmax`.

In short:
1. Download MIP 5 (512x512x640nm resolution) volume
2. Combine the various tissues
3. Various rounds of binary erosion + fill holes
4. Marching cubes to generate the mesh
5. Manual clean up using Blender
6. Transform from FAFB14 to FlyWire space

