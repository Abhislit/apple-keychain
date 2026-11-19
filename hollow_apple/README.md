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
- Body and stem are uniformly scaled 1.50x; inner cavity is the same mesh at
  0.90 of the scaled outer (about 2.8 mm wall at the widest point).
- Flat seam at z = -20; everything below it is the removable cap.
- Front window sized to the OLED's **active area only**, 29.42 x 14.7 mm
  (cut 29.72 x 15.0 for 0.15 mm clearance per side); OLED plane at y = -17.5.
  The module bezel stays hidden behind the shell.
- TP4056 power: small 10 x 5 mm rectangle in the **back** wall (y = +),
  centred at z = 12.5 so it does not line up with the display window.
- Slide switch: 9 x 3 mm actuator slot in the right-hand wall.
- Two small internal shelves (OLED edge tabs + electronics platform).
- 5 mm chain-ring hole through the thickest part of the leaf (right prong,
  x = 15, z = 33.3), with about 2.7 mm of wall around it.
- Outputs: `shell.stl` (apple above the seam), `cap.stl` (bottom closure), and
  `apple_complete_hollow.stl` — the **whole apple as one hollow piece** with its
  natural bottom closed and no flat cut seam. Same window, power, switch,
  shelves and leaf hole; ~2.6 mm bottom wall.
- `cap_full_apple.stl` is a byte-for-byte copy of `apple_complete_hollow.stl`,
  provided under the cap name. `cap.stl` and `shell.stl` are unchanged.
- The complete apple's underside is now a real apple base: `build_hollow.py`
  adds a rounded cap and central calyx dimple before hollowing, and
  `sculpt_bottom.py` adds five soft lobes to the STL. The cavity, windows and
  holes stay in place; the lower `cap.stl` also gets the new base.

## Print
- Shell: seam-down on the bed.
- Cap: seam-down as well (flat face on the bed, curved apple bottom upward).
- Both are watertight single solids; no supports needed.

## Build / verify
```
snap run freecad.cmd ./build_hollow.py
python3 sculpt_bottom.py
cp apple_complete_hollow.stl cap_full_apple.stl
python3 verify_hollow.py
python3 render_hollow.py
```

The `.step` files include the rounded cap and calyx dimple but not the five
lobes; the `.stl` files are the fully sculpted, printable versions.
