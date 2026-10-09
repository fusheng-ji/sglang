# Hunyuan3D mesh validation renders

Assets for https://github.com/sgl-project/sglang/pull/43215.

- Code: `22c540f1407398d80c441807b2d59764a30e1a01`.
- Fixed reference GLB SHA-256: `c7d023605bdc85a9f343fe698857eecb68439524883e14d9cba9dd12136e5f77`.
- Real API GLB SHA-256: `59a445a00ea6fc4d8fba9a2520407485e2d2aee23e635f50c8a1927e5ff2cf76`.
- Reference: https://raw.githubusercontent.com/sgl-project/ci-data/395f6e49c37d22a57d79fbcd3653d43984099ae2/diffusion-ci/consistency_gt/1-gpu/hunyuan3d_2_0/hunyuan3d.glb
- Generation: existing `hunyuan3d_shape_gen` case, real API download on a B200. Model `tencent/Hunyuan3D-2@9cd649ba6913f7a852e3286bad86bfa9a2d83dcf`.

Blender 4.2.3 Cycles, **CPU**, 8 threads, 32 samples with denoising. Three shared orthographic cameras are framed using only reference bounds. GLTF's coordinate conversion is applied by Blender's importer; meshes are never individually aligned, translated, normalized, or scaled. Comparison panels use the same clay material, smooth shading, lighting and camera. The separate textured panel uses the API GLB's original material.

The visualization is supplementary: acceptance is based on the numerical metric, not visual resemblance. Reference diagonal D=2.9875327625237875; normalized bidirectional squared-distance sum C=0.0001331739111231968 <= 0.003 (the PR's default threshold). Full API case fails because the B200 performance baseline is absent; independent mesh replay passes.

## Reproduce

Put `reference.glb` and `generated.glb` in an input directory, then:

```bash
CUDA_VISIBLE_DEVICES='' blender -b -t 8 --python render_meshes.py -- /absolute/input/directory
# Copy compose.py to that directory's render/ folder, then:
python /absolute/input/directory/render/compose.py
```

The raw GLBs are not committed; only rendered images and their provenance are.
