# Hollow apple enclosure

## Intent
Use the supplied apple mesh itself as the enclosure: keep its exact outer shape
and structure (round, not squashed), hollow it, and leave room for the listed
electronics. The source STL is never modified.

## Constraints
- `apple_original.stl` stays byte-for-byte unchanged (SHA-256
  `8c2ae8b452da705620cd98764d5ecdc385f55724618e09efbd49740f89dc725e`).
- The outer surface is a **uniform** scale of the original. No axis is
  stretched independently; the apple remains perfectly round.
- Parts to fit: D1 mini, 402035 40x20x3.4 LiPo, TP4056 USB-C,
  1.3" 7-pin SPI OLED (35.4x33.5), slide switch.
- Closure is below the apple.

## Approaches considered
1. **Uniform scale 1.25x** - rejected. Mesh check showed the OLED corners fall
   completely outside the inner cavity (no depth fits) because the apple
   narrows near the top.
2. **Separate round case below the apple** - rejected; drops the requirement
   that the apple itself be hollow.
3. **Uniform scale 1.50x** - chosen. Original 44.8 mm body becomes 67.2 mm;
   inner cavity ~60 mm across. The OLED corners sit ~0.9 mm inside the inner
   wall, with the same margin on the battery. Shape is unchanged; only size.

## Design (approved approach)
- The apple body is uniformly scaled 1.50x; inner cavity is the same mesh at
  0.90 of the scaled outer (about 2.8 mm wall at the widest point).
- Flat seam at z = -20; everything below it is the removable cap.
- Front window sized to the OLED's **active area only**, 29.42 x 14.7 mm
  (cut 29.72 x 15.0 for 0.15 mm clearance per side); OLED plane at y = -17.5.
  The module bezel stays hidden behind the shell.
- TP4056 power: small 10 x 5 mm rectangle in the **back** wall (y = +),
  centred at z = 12.5 so it does not line up with the display window.
- Slide switch: 9 x 3 mm actuator slot in the right-hand wall.
- Two small internal shelves (OLED edge tabs + electronics platform).
- The stem and leaf are **not part of the apple outputs**. They are exported
  separately as `stem_leaf.stl` and `stem_leaf.step`, retaining the 5 mm
  chain-ring hole through the thickest part of the leaf (right prong,
  x = 15, z = 33.3 in assembly coordinates) with about 2.7 mm of wall around
  it. Its small base is capped so the printable part is watertight.
- Outputs: `shell.stl` (apple above the seam), `cap.stl` (bottom closure), and
  `apple_complete_hollow.stl` — the **whole apple as one hollow piece** with its
  natural bottom closed and no flat cut seam. Same window, power, switch and
  shelves; no stem or leaf; ~2.6 mm bottom wall.
- `cap_full_apple.stl` is a byte-for-byte copy of `apple_complete_hollow.stl`,
  provided under the cap name.
- Only the complete apple's underside is a real apple base: `build_hollow.py`
  adds a rounded cap and central calyx dimple to the one-piece apple, and
  `sculpt_bottom.py` adds five soft lobes to its STL. The two-piece `shell.stl`
  and `cap.stl` keep the original flat seam.

## Print
- `cap.stl`, `shell.stl` and `stem_leaf.stl` are exported **bed-aligned**: each
  one's lowest point sits at z = 0, so all three can be dropped straight into a
  slicer. The complete-apple files stay in assembly coordinates.
- Shell: seam-down on the bed. Cap: flat face down. Stem/leaf: small base down.
- All are watertight single solids; no supports needed.

## Build / verify
```
snap run freecad.cmd ./build_hollow.py
python3 sculpt_bottom.py
cp apple_complete_hollow.stl cap_full_apple.stl
python3 verify_hollow.py
python3 render_hollow.py
```

The apple `.step` files include the rounded cap and calyx dimple but not the
five lobes; the `.stl` files are the fully sculpted, printable versions.
`stem_leaf.step` matches `stem_leaf.stl`.
