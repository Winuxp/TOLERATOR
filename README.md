# Tolerator — README

Based on ISO 286-2:2010 with applicable Cor 1:2013 corrections. Nominal diameters up to 500 mm.

## Diameter names

DN is the fit/interface diameter (hole ID and shaft OD), D1 is the free hub outer diameter, and d2 is the free shaft inner diameter. The geometry key is schematic, not to scale.

## Calculation and tolerance data

**Uppercase: hole. Lowercase: shaft.**

Limit dimension = nominal diameter + deviation in µm / 1,000.

Minimum difference = minimum hole − maximum shaft.

Maximum difference = maximum hole − minimum shaft.

For H, EI = 0. For h, es = 0. The tolerance width is the selected IT grade.

**Scope:** classes tabulated in ISO 286-2:2010, Tables 2–32, up to 500 mm,
including CD/EF/FG, JS/js and ZA/ZB/ZC. J9–J18 follow Table 8 note a.
Only classes tabulated for each part’s nominal diameter are offered. Undefined combinations are not extrapolated.
Grades IT01/IT0 have widths in Table 1 but no lettered classes in Tables 2–32, so they are not invented here.
Each part uses its own nominal size range. Both cross-sections use the same amplification.
Negative differences mean interference. Dimensions and differences are rounded to 1 µm for display;
calculations and fit classification use unrounded values.

Data extracted from the supplied ISO 286-2:2010 PDF, with applicable official Cor 1:2013 corrections.
One additional inconsistent za11 cell (225–250 mm) is reconciled using IT11 and the paired ZA11 table; see the correction log below.
Display is rounded to 1 µm; fine-grade and JS/js half-micrometre values are retained internally.

[Official 2013 corrigendum](https://www.iso.org/obp/ui?_escaped_fragment_=iso:std:iso:286:-2:ed-2:v1:cor:1:v1:en)

## Thermal model and material presets

**D(T) = D(T₀) × [1 + α × 10⁻⁶ × (T − T₀)]**, with α entered in µm/m/K.

Expansion is applied to the limit dimensions calculated at T₀. ISO tables are not re-evaluated at the expanded diameter.

Linear model with constant coefficients, free expansion and uniform temperature shared by both parts.
No gradients, interference-induced deformation or temperature dependence of α are calculated.

Material presets are indicative: steel 12, aluminium 23, titanium 8.4 and austenitic stainless steel 17 µm/m/K.
Ferritic and martensitic stainless steels may differ substantially. Use your material datasheet.

Sources: [Nippon Steel](https://www.nipponsteel.com/en/product/titan/feature/pdf/T001en_16-23.pdf), [BSSA](https://bssa.org.uk/bssa_articles/elevated-temperature-physical-properties-of-stainless-steels/).

## Lamé elastic press-fit model

Enable **Lamé model**. For each part, select a material and edit **Young E (GPa)** and **Poisson ν**. Presets are representative, not grade-specific: steel 210/0.30; aluminium 70/0.33; titanium 110/0.34; austenitic stainless steel 193/0.30.

Enter the **free hub outer diameter** and **free shaft inner diameter** at the nominal reference temperature. A shaft inner diameter of 0 means solid. Outer diameter must exceed all hole limits; inner diameter must be smaller than all shaft outer limits.

Enter the effective **contact length L at service temperature** and one **friction coefficient μ**. L is kept constant between scenarios, not automatically expanded. The same μ is used for the sliding press-in estimate and static torque capacity; these coefficients can differ in a real assembly.

### Pressure and compatibility

Assumptions: axisymmetric, homogeneous isotropic linear elasticity; open/free ends, σz = 0; uniform contact pressure; no external pressure on the hub or internal pressure in the shaft. End effects, chamfers, roughness flattening, yielding, buckling and centrifugal effects are not modelled. Axial-force-induced Poisson changes in pressure and combined loading are not resolved. This is a Lamé estimate, not a DIN 7190 compliance calculation.

Let Dh and Ds be the free limit diameters of hole and shaft, Do the free hub outer diameter, and Di the free shaft bore diameter. Use mm and E in MPa (GPa × 1000):

Ch = Dh/Eh × [(Do² + Dh²)/(Do² − Dh²) + νh]

Cs = Ds/Es × [(Ds² + Di²)/(Ds² − Di²) − νs]

p = max[0, (Ds − Dh)/(Ch + Cs)]

For positive interference, Dcontact = Dh + p Ch = Ds − p Cs. The two compliances are evaluated on each cylinder's unloaded geometry. They reduce to the usual common-interface Lamé formula as the interference becomes small relative to diameter.

The new free-surface diameters are also derived from the Lamé displacement field:

Do_loaded = Do + 2 p Dh² Do / [Eh (Do² − Dh²)]

Di_loaded = Di − 2 p Ds² Di / [Es (Ds² − Di²)]

### Friction and output ranges

A = π Dcontact L

Fpress = μ p A (N), for full engagement, neglecting entry effects and plastic deformation.

T = Fpress Dcontact / 2000 (N·m, when diameter is in mm).

The axial sliding/holding capacity has the same idealised expression with the same μ. These nominal force and torque capacities apply separately; their maxima cannot be used simultaneously without a combined-load check. No safety factor is included.

All four hole/shaft tolerance corners are evaluated. Pressure, press-in force, torque and deformed-diameter envelopes are the minima and maxima of these corner predictions. For a clearance corner, p=F=T=0 and the two diameters remain separate. A transition fit has zero guaranteed minimum capacity. The contact-diameter range includes only corners actually in contact.

### Thermal combination and display

For each nominal/hot/cold scenario, thermal expansion is applied first to all free diameters, including Do and Di, using each part's α. Elastic contact is then solved at that temperature. E, ν and μ remain constant. The length input is interpreted at service temperature. In Lamé mode the main graphic defaults to **after assembly**, with a selector for before assembly. The actual minimum/maximum initial-interference corners are shown; dashed outlines show free geometry, an amber ring shows loaded contact, and clearance cases remain separate. All deformed-diameter envelopes are also shown first in the Lamé results table and exported for every scenario. The radial drawing scale is schematic and magnifies diameter differences.

Dimensions are displayed to 1 µm; computations and contact detection use unrounded values. Very small physical interference can therefore appear as zero after rounding, without its pressure being exactly zero.

Reference: [Jönköping University — shaft–hub joints, Lamé pressure and friction capacity](https://mechanics.ju.se/MachineElements/shaft-hub.html).

### Stress and assembly temperatures (v3.2)

Stress is the peak von Mises stress caused by the contact pressure only, separately for hub and shaft, with sigma_z=0. At the hub bore: hoop=p(D1²+Dh²)/(D1²−Dh²), radial=−p; von Mises=sqrt(hoop²+p²+hoop*p). For a hollow shaft the maximum is at its free bore: 2p Ds²/(Ds²−d2²). For a solid shaft it is p. This does not include transmitted torque or assembly friction stresses and does not compare with yield strength.

Thermal assembly uses the worst tolerance corner: minimum free hole and maximum free shaft at T0. Independent temperatures are applied to the two parts. The required diametral assembly clearance is editable (default 20 µm). Heating-only and cooling-only options hold the other part at T0; combined options hold one part at the entered temperature. There is no unique pair of hot/cold temperatures. Recommended limits are rounded outward to whole °C. An impossible cooling temperature below absolute zero is reported unavailable. Material/process temperature limits, gradients and heat transfer during insertion must be checked separately. Coefficients are constant; recommendations are thresholds in this model, not a complete process validation.

Reference for stress field: [Cambridge — thick cylinders](https://www-mdp.eng.cam.ac.uk/web/library/enginfo/textbooks_dvd_only/DAN/cylinders/thick/thick.html).

## Graphic

The two cross-sections show minimum hole / maximum shaft and maximum hole / minimum shaft. Deviations are amplified using the same scale in both views. The drawing is not to scale. Values are diametral; radial clearance is half the diametral difference. Without Lamé, red indicates theoretical interference before assembly. With Lamé, an Assembly state selector defaults to After assembly: solid contours show the loaded geometry, dashed contours the free geometry and amber marks the contact pressure. The two views use the actual minimum/maximum initial-interference corners; a clearance corner stays separate with zero pressure. A common monotone schematic radial scale magnifies interface differences and preserves surface order; it is not a physical drawing scale.

## Coverage and correction log

213 hole classes · 204 shaft classes · 5939 tabulated size intervals. Each row records its source PDF page (1-based).

| Tolerance | Above (mm) | Up to (mm) | Field | Original (µm) | Used (µm) | Basis |
|---|---|---|---|---|---|---|
| A9 | 180 | 200 | lower | 60 | 660 | ISO 286-2:2010/Cor 1:2013 |
| J6 | 250 | 315 | lower | -5 | -7 | ISO 286-2:2010/Cor 1:2013 |
| S9 | 100 | 120 | lower | -165 | -166 | ISO 286-2:2010/Cor 1:2013 |
| S9 | 450 | 500 | lower | -387 | -407 | ISO 286-2:2010/Cor 1:2013 |
| S10 | 10 | 18 | lower | -96 | -98 | ISO 286-2:2010/Cor 1:2013 |
| c12 | 0 | 3 | lower | -150 | -160 | ISO 286-2:2010/Cor 1:2013 |
| k13 | 3 | 6 | upper | 190 | 180 | ISO 286-2:2010/Cor 1:2013 |
| x9 | 250 | 280 | upper | 650 | 605 | ISO 286-2:2010/Cor 1:2013 |
| za11 | 225 | 250 | upper | 1100 | 1110 | Table 1: IT11=290 µm; Table 15: ZA11=-820/-1110 µm; Table 31: ei=820 µm |
| JS1 | 3 | 6 | upper/lower | ±0,05 | ±0.5 | ISO 286-2:2010/Cor 1:2013; Table 7 symmetry note |
| JS1 | 6 | 10 | upper/lower | ±0,05 | ±0.5 | ISO 286-2:2010/Cor 1:2013; Table 7 symmetry note |
