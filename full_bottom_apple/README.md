# Apple base sculpts

Solid lower halves of the apple, derived from the original mesh.

- Built from `apple_original.stl` (byte-for-byte copy of `obj_1_Assembly.stl`,
  SHA-256 `8c2ae8b452da705620cd98764d5ecdc385f55724618e09efbd49740f89dc725e`).
- Uniform 1.5x scale, so the apple keeps its exact round shape — no stretching.
- Only the body below z = 0 is kept, with a flat closed top at z = 0.
- The source apple's flat base was sculpted into a rounded apple bottom: a
  spherical cap 3 mm deeper at the centre and a 4 mm wide, 2 mm deep calyx
  dimple. The rest of the apple shape is untouched.
- No cavity, shelves, tabs, display window, power/switch holes or chain-ring
  hole. No stem or leaf. One solid, printable piece.

| Model | Lobes | Printable file |
| --- | --- | --- |
| `full_bottom` | 3 smooth lobes, 4 mm deep, at 0/120/240 deg | `full_bottom.stl` |
| `apple_base_five` | 5 small blunt lobes, 2.5 mm deep | `apple_base_five.stl` |

`apple_base_five_render.png` shows the five-lobe model on a white background.

## Rebuild

```
# three-lobe version
snap run freecad.cmd ./build_full_bottom.py
python3 sculpt_lobes.py
python3 verify_full_bottom.py

# five-lobe version
APPLE_OUT=apple_base_five snap run freecad.cmd ./build_full_bottom.py
python3 sculpt_lobes.py apple_base_five 5 2.5
python3 verify_full_bottom.py apple_base_five 5
python3 render_base.py apple_base_five
```

The `.step` files are the pre-lobe CAD solids; the `.stl` files are the
sculpted, printable versions.
