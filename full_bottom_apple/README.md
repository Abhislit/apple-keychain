# Full bottom apple

A **solid lower half of the apple**, derived from the original mesh.

- Built from `apple_original.stl` (byte-for-byte copy of `obj_1_Assembly.stl`,
  SHA-256 `8c2ae8b452da705620cd98764d5ecdc385f55724618e09efbd49740f89dc725e`).
- Uniform 1.5x scale, so the apple keeps its exact round shape — no stretching.
- Only the body below z = 0 is kept, with a flat closed top at z = 0.
- The source apple's flat base was sculpted into a rounded apple bottom: a
  spherical cap 3 mm deeper at the centre plus a 4 mm wide, 2 mm deep calyx
  dimple. The rest of the apple shape is untouched.
- No cavity, shelves, tabs, display window, power/switch holes or chain-ring
  hole. No stem or leaf. It is one solid piece.

`full_bottom.stl` is the printable model; `full_bottom.step` is the CAD version.

## Rebuild

```
snap run freecad.cmd ./build_full_bottom.py
python3 verify_full_bottom.py
```
