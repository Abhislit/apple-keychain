# Apple keychain enclosure

ESP8266 D1 mini + 402035-class LiPo (40×20×3.4) + TP4056 (USB-C) + 1.3" 7-pin
SPI OLED (35.4×33.5 mm) + slide switch, inside the supplied apple mesh.

The shell is the original mesh scaled to 60 mm wide and 35 mm deep; its body,
stem and leaf keep their shape. A 5 mm cap cut from the bottom closes the
compartment, with a keyring bail at the back. The depth is 35 mm because the
apple's domed back leaves only ~8 mm at the board corners at 22.5 mm — the
four-part stack needs ~16 mm. The front silhouette is unchanged.

Files: `build/front.stl` (shell), `build/base.stl` (cap), also `.step`.
Rebuild with `snap run freecad.cmd ./build_model.py`; views with
`python3 render.py`; checks with `python3 verify.py`.

## Print

| Part | Bed | Notes |
|---|---|---|
| `front.stl` | seam (flat bottom) down | no supports; front, window and switch face sideways |
| `base.stl` | apple bottom down, lip up | no supports; 5 mm tall |

0.4 mm nozzle, 0.2 mm layers, 3 walls, 15–20 % infill. The shell flares outward
only ~14° from the seam, so it prints unsupported; the leaf tip may need a
small support. Print both, then check the cap fit before wiring.

## Fit-up (front to back)

- **OLED**: glass at y ≈ 4.8, behind the 30×26 window, in a 37×35 recess in the
  curved front. Its PCB back protrudes ~1 mm into the cavity. The 7-pin header
  must be right-angled/bent or replaced with wires or it hits the TP4056.
- **TP4056**: stands on the cap floor on its 19.5 mm edge, USB-C down through
  the tunnel at y 11.5–14.9. Its face is 26.5 mm tall (to z ≈ 8.4).
- **D1 mini**: sits on the two side shelves at y 15.1–19.8, between the guides.
  Its USB is enclosed: flash over OTA or drop the cap.
- **Battery**: flat against the back, y 20.0–23.4, 40 mm across and 20 mm tall;
  nothing protrudes below the cap.
- **Switch**: glue the body into the right-wall slot, actuator outside.

Everything loads through the cap opening with the cap off: TP4056 first (plug
its USB into the tunnel), then D1, battery, and finally the OLED slid into its
front recess.

- **Cap**: full lip ring following the cavity wall, 0.04 mm gap. Sand the lip
  if it is too tight; a wrap of tape on it takes up slack if it is loose. Pry
  notch at the back of the seam.

Overall 60 × 46.3 × 35 mm (leaf tip 38 mm above mid-height).
