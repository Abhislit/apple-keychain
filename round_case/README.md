# Round case below the apple

The apple is **not modified**: `apple_original.stl` is a byte-for-byte copy of
`../obj_1_Assembly.stl` (SHA-256 `8c2ae8b452da7056…`). It stays round and solid
and sits on top as decoration. The electronics live in a new 55 mm round case
underneath it.

Files: `case_body.stl` (tray), `case_lid.stl` (lid with socket lip and apple
seat), plus `.step` versions. Rebuild with `snap run freecad.cmd ./build_case.py`;
check with `python3 verify_case.py`.

## Print

| Part | Bed | Notes |
|---|---|---|
| `case_body.stl` | flat bottom (window side) down | no supports; fin reaches the bed |
| `case_lid.stl` | flat top down, lip up | no supports |

0.4 mm nozzle, 0.2 mm layers, 3 walls, 15–20 % infill.

## Assembly (bottom to top)

- **OLED**: glass down in the recess behind the 30×26 bottom window; the module
  sits inside the cavity, so flip the keychain to read it.
- **D1 mini**: rests on the two side shelves at z ≈ 8, flat, USB toward the back.
- **Battery**: 40×20×3.4 flat on top of the D1 (use a thin foam spacer).
- **TP4056**: flat on the battery, USB-C facing the back slot; solder wires
  instead of pin headers to keep the stack low.
- **Switch**: body through the right-wall slot, actuator outside.
- **Lid**: lip presses into the groove. Glue the apple's flat base to the raised
  seat ring on the lid. Keyring goes through the fin hole at the back.

Case 55 mm diameter × 20 mm body + 2 mm lid; with the apple on top the assembly
is about 57 mm tall. `verify_case.py` reports both STLs watertight, single-shell,
all four openings clear, and the apple hash unchanged.
