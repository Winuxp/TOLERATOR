# Version 3.3

Depuis 3.2.1, remplacer **app.py** et **lame.py**, puis ajouter **graphics.py** à côté. Le titre affiche Version 3.3.

Mode Lamé : vue **After assembly** par défaut ; interface commune en contact, pression affichée à 0,1 MPa ; contours libres en pointillés. Sélecteur **Before assembly / After assembly**. Les cas sans contact restent séparés. Les deux vues correspondent aux cas réels d’interférence initiale minimale/maximale, non à un mélange des bornes indépendantes du tableau. D1 et d2 sont indiqués avec les dimensions déformées après montage. Échelle radiale schématique commune, différences amplifiées.

Sans Lamé : graphique avant montage conservé. Une géométrie Lamé invalide affiche le graphique libre avec une explication.

---

# Version 3.2.1

Champ DN déplacé après le schéma et juste avant les deux parties. Une seule ligne de diamètres dans les deux modes pour stabiliser les blocs lors du passage en diamètres séparés. Depuis 3.2, seul app.py change.

# Tolerator 3.2 — mise à jour

Lancement depuis le dossier tolerator : `python -m streamlit run app.py`.
Le titre doit afficher **Version 3.2**.

Depuis 3.1 : remplacer **app.py et lame.py** (les deux sont nécessaires).

- Résultats Lamé : DN alésage/arbre, D1, d2, pression, contraintes de von Mises moyeu/arbre, effort et couple ; min/max pour chaque température.
- Affichage : dimensions 0,001 mm ; pression/contrainte 0,1 MPa ; effort 1 N ; couple 0,1 N·m ; température 1 °C.
- Option **Thermal assembly check** : jeu diamétral cible (20 µm par défaut), températures indépendantes des pièces, cas défavorable de tolérances ; chauffage seul, refroidissement seul ou combinaison. Les coefficients α restent modifiables même sans mode thermique.
- Les températures proposées sont des seuils du modèle linéaire, arrondis du côté garantissant le jeu. Vérifier les limites matériaux/procédé et les échanges thermiques pendant le montage.
- La contrainte affichée est due à la pression de contact uniquement ; aucune comparaison automatique avec la limite élastique.

---

# Tolerator 3.1 — ISO shaft / hole fits

## Update on Mac
1. Stop the running app with Ctrl+C in the terminal.
2. Copy **app.py**, **calcul.py**, **lame.py** and **iso286_data.json** into your existing project folder.
3. Keep your `.venv` folder. No new dependencies are required.
4. Restart from the project folder:

```bash
.venv/bin/python -m streamlit run app.py
```

The JSON file must stay next to calcul.py. Copying app.py alone is no longer sufficient.

## First installation
Python 3.11 or later. Open a terminal in the extracted `tolerator` folder.

Mac/Linux:
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```
Windows:
```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app.py
```

## ISO coverage
- 213 hole classes and 204 shaft classes, 5,939 size-dependent intervals.
- Nominal diameter: greater than 0 and up to and including 500 mm. Input resolution: 0.001 mm.
- All nonempty entries up to 500 mm from Tables 2–32 of the supplied ISO 286-2:2010 PDF.
- J9–J18 use the symmetric JS rule specified in Table 8 note a.
- Includes CD/cd, EF/ef, FG/fg, JS/js, ZA/za, ZB/zb and ZC/zc where tabulated.
- Each list is filtered by that part's own nominal diameter. For example, V/v entries start above 14 mm; T/t entries start above 24 mm; Y/y entries start above 18 mm.
- Bounds use `low < nominal <= high`. Restrictions at or below 1 mm are applied from the relevant notes.
- Table 1 gives IT01/IT0 widths, but Tables 2–32 do not tabulate lettered IT01/IT0 classes; none are invented.
- Empty cells remain unavailable. No interpolation or guessed tolerance combinations.
- When a diameter change invalidates the selected class, the app resets that part to H7 or g6 and displays a short message.
- Very small nominal diameters with a tolerance that would produce a non-positive diameter are rejected.

## Data source and corrections
The data is extracted from the user-supplied ISO 286-2:2010 PDF, rather than from the earlier public subset.
The applicable table corrections in ISO 286-2:2010/Cor 1:2013 are incorporated, including A9, JS1, J6, S9, S10, c12, k13 and x9.
Official corrigendum:
https://www.iso.org/obp/ui?_escaped_fragment_=iso:std:iso:286:-2:ed-2:v1:cor:1:v1:en

One additional discrepancy in the supplied PDF is documented separately:
- Table 31, shaft za11, 225 < d <= 250 mm: upper deviation +1100 µm is inconsistent with lower deviation +820 µm and IT11=290 µm.
- The app uses +1110 µm, consistent with Table 1 and the paired ZA11 hole interval (-820/-1110 µm) in Table 15.

All 11 amended entries are recorded in iso286_data.json and shown in the collapsed data-audit panel.
JS/js intervals use exactly ±IT/2, as defined in the table notes.
Each record retains the source PDF page number (1-based, including cover/front matter).
The source PDF is not duplicated in the application archive.

## Thermal calculation
Enable Thermal calculation. Enter the nominal definition temperature and the hot/cold temperatures.
Required: cold <= nominal <= hot. Both parts share the same service temperature in each scenario.
Select a material for each part; its coefficient is preset but editable in µm/(m·K).
Presets are indicative: steel 12; aluminium 23; titanium 8.4; austenitic stainless steel 17.
Changing material replaces that part's coefficient with the preset. Other changes retain manual coefficient edits.

D(T) = D(T0) × [1 + alpha × 10^-6 × (T−T0)].
Both limit dimensions are expanded from T0. ISO tables are not re-read at the expanded diameter.
The 500 mm limit applies to the nominal input at T0, not the expanded dimensions.
Model: free expansion, constant coefficient, uniform temperature. No stress/deformation model or gradients.

## Display and export
English interface, side-by-side controls and results. Tables and data notes are collapsed by default.
Dimensions are displayed to 0.001 mm; deviations and fit differences to whole µm.
Sub-micrometre and half-micrometre values remain exact internally; classification is performed before rounding.
Negative differences indicate interference; positive differences indicate clearance.
The graph shows the two limit combinations before assembly. Deviations are exaggerated with one scale shared by both views. It is not a scale drawing.
The radial gap/overlap is half the diametral difference shown. Red overlap represents interference before assembly without elastic deformation.

## Files and verification
- app.py: English Streamlit interface and graphics.
- calcul.py: independent lookup and thermal calculations.
- iso286_data.json: tolerance intervals, IT widths, traceability and correction log.
- requirements.txt: Streamlit dependency.
- test_calcul.py, test_thermique.py, test_iso286.py: verification.

Run from the project folder:
```bash
.venv/bin/python -m unittest -v
```
Tests check all 5,939 intervals against Table 1 widths, every interval boundary, known fit examples, note restrictions, corrected cells, thermal expansion and validation.
Before production drawing release, review the recorded corrections against your controlled standard copy and drawing requirements.

## Python API
```python
from calcul import calculer, classes_disponibles, calculer_thermique

options = classes_disponibles(40, 'shaft')
fit = calculer(40, arbre='p6', alesage='H7')
fit_separate = calculer(40, arbre='m6', alesage='G7', diametre_arbre=40.010)
hot_fit = calculer_thermique(fit, 20, 80, 23, 12)
```
The existing French parameter/result names are retained for compatibility.

## Version 2.1 — split tolerance selectors
Each part has two side-by-side dropdowns: Tolerance zone (H, G, JS, etc.) and IT grade (5, 6, 7, etc.).
Defaults: H / 7 for the hole; g / 6 for the shaft.
The letter list is filtered by nominal diameter; the IT list is filtered by letter and diameter.
Update from 2.0: replace app.py only. Keep calcul.py and iso286_data.json unchanged.

## Version 2.2 — full-width graph
The cross-section graphic stretches to the width of the results panel, matching the fit-summary rectangle.
Its aspect ratio is preserved, so the circles stay circular. Update from 2.1: replace app.py only.

## Version 2.3 — README and header branding
One README link in the header opens the calculation notes, thermal model, coverage and full correction log.
The README can also be downloaded from that view; README.md is included in the archive.
The header includes a discreet vector Audi AFR signature with a stylised F1 car and the ISO reference.
The graphic is embedded in app.py; no external image or additional package is required.
Update from 2.2: replace app.py only. The README is generated within the app.

## Version 2.4 — compact selectors and revised F1 signature
Zone and IT dropdowns now use a narrower section within each part column.
The schematic car has a long, low profile based on the supplied side-view reference,
with silver front bodywork, a red rear sidepod, black aero surfaces and red tyre accents.
The SVG preserves its aspect ratio and remains embedded in app.py.
Update from 2.3: replace app.py only.

## Version 3.0 — optional Lamé press fit
Update from 2.4: replace app.py and add lame.py next to it. No new dependency is required.
The optional test_lame.py is included for verification.

Enable Lamé model. Set material / Young E (GPa) / Poisson ratio for each part.
Enter the hub outside diameter and shaft inside diameter (0 = solid shaft).
Those diameters are free dimensions at the nominal reference temperature.
Set the effective full contact length at the service temperature and the friction coefficient.
The same friction coefficient is used for the sliding press-in estimate and static torque capacity.

Outputs: min/max contact pressure (MPa), fully engaged press-in force (N), torque capacity (N.m),
and deformed hole, shaft, hub outer and shaft bore diameters (mm).
The assembled-diameters panel is collapsed to retain the compact main view.
Four tolerance corners are solved. Clearance corners have zero pressure and capacities;
transition fits have no guaranteed positive minimum capacity.

Thermal mode first expands all four free diameters, then solves elastic contact.
The service contact length is held fixed across the scenarios; it is not thermally expanded.
E, Poisson and friction are constant. Results for all three temperatures are included in the CSV export.
The graph remains a before-assembly schematic; a shaft bore is shown if specified.
Material presets update alpha, E and Poisson together, and every property remains editable.
Manual material properties persist when toggling the calculation modes.

Model: homogeneous isotropic small-strain elasticity, zero axial normal stress, uniform contact pressure.
Entry/chamfer effects, roughness loss, plasticity, yielding, end effects, buckling, gradients and rotation are not calculated.
The force and torque estimates apply separately; no combined-load factor or safety factor is included.
Full equations, assumptions, units and the academic reference are available through README.

Verification: 29 tests including the solid-shaft analytical limiting case, hollow-shaft compliance,
loaded-diameter compatibility, material/length/friction scaling, pressure envelopes, clearance,
transition fits, thermal scaling, thermal release and invalid geometry.

## Version 3.1 — stable graph, geometry key and temperature envelopes
Update from 3.0: replace app.py only. No new dependencies or calculation-data changes.

Bug fix: a blank numeric edit in a material field could previously propagate None and
stop the thermal calculations before rendering the graph. The last valid value is now
retained. Optional temperatures and geometry values also persist when modes are toggled.
Invalid hot/cold conditions are reported individually; the remaining valid conditions
and their fit graph remain available. A Lamé geometry error no longer hides the fit diagram.
The fit SVG is rendered inline at full panel width and placed before the Lamé calculations.

The left panel includes a schematic geometry key above the two part columns:
- DN: fit/interface diameter (hole ID and shaft OD).
- D1: free outside diameter of the hub at the reference temperature.
- d2: free bore diameter of the shaft at the reference temperature (0 = solid shaft).
D1 corresponds to Do and d2 to Di in the original formula notation.

The Lamé summary displays all three temperatures simultaneously, with separate Min./Max.
columns for pressure, fully engaged press-in force and torque capacity. Colour coding:
nominal grey, hot orange, cold blue. The graphic-condition selector changes the diagram
and the selected fit summary without hiding the other temperature rows.
The collapsed DN/D1/d2 assembled-diameters panel contains Min./Max. values for every temperature.
Fit limits by temperature are also visible without expanding a table.

Regression checks in test_ui.py cover incomplete coefficient edits, option toggles,
invalid secondary inputs, the DN/D1/d2 labels, graph ordering and independently checked
pressure envelopes for all three temperatures. Total verification: 32 tests.
