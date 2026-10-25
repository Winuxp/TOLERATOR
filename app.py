"""Lancer avec : python -m streamlit run app.py"""
import csv
import io
from decimal import Decimal
from graphics import lame_graphic
import streamlit as st
from lame import calculer_lame_intervalle, ELASTIC_PRESETS, MODEL_README, thermal_assembly
from calcul import calculer, calculer_thermique, MATERIAUX, ALESAGES, ARBRES, classes_disponibles, DATA

st.set_page_config(page_title="Tolerator", page_icon="⚙️", layout="wide")

def readme_text():
    intro = "# Tolerator — README\n\nBased on ISO 286-2:2010 with applicable Cor 1:2013 corrections. Nominal diameters up to 500 mm.\n\n"
    calculation = '## Calculation and tolerance data\n\n**Uppercase: hole. Lowercase: shaft.**\n\nLimit dimension = nominal diameter + deviation in µm / 1,000.\n\nMinimum difference = minimum hole − maximum shaft.\n\nMaximum difference = maximum hole − minimum shaft.\n\nFor H, EI = 0. For h, es = 0. The tolerance width is the selected IT grade.\n\n**Scope:** classes tabulated in ISO 286-2:2010, Tables 2–32, up to 500 mm,\nincluding CD/EF/FG, JS/js and ZA/ZB/ZC. J9–J18 follow Table 8 note a.\nOnly classes tabulated for each part’s nominal diameter are offered. Undefined combinations are not extrapolated.\nGrades IT01/IT0 have widths in Table 1 but no lettered classes in Tables 2–32, so they are not invented here.\nEach part uses its own nominal size range. Both cross-sections use the same amplification.\nNegative differences mean interference. Dimensions and differences are rounded to 1 µm for display;\ncalculations and fit classification use unrounded values.\n\nData extracted from the supplied ISO 286-2:2010 PDF, with applicable official Cor 1:2013 corrections.\nOne additional inconsistent za11 cell (225–250 mm) is reconciled using IT11 and the paired ZA11 table; see the correction log below.\nDisplay is rounded to 1 µm; fine-grade and JS/js half-micrometre values are retained internally.\n\n[Official 2013 corrigendum](https://www.iso.org/obp/ui?_escaped_fragment_=iso:std:iso:286:-2:ed-2:v1:cor:1:v1:en)\n\n'
    thermal = '## Thermal model and material presets\n\n**D(T) = D(T₀) × [1 + α × 10⁻⁶ × (T − T₀)]**, with α entered in µm/m/K.\n\nExpansion is applied to the limit dimensions calculated at T₀. ISO tables are not re-evaluated at the expanded diameter.\n\nLinear model with constant coefficients, free expansion and uniform temperature shared by both parts.\nNo gradients, interference-induced deformation or temperature dependence of α are calculated.\n\nMaterial presets are indicative: steel 12, aluminium 23, titanium 8.4 and austenitic stainless steel 17 µm/m/K.\nFerritic and martensitic stainless steels may differ substantially. Use your material datasheet.\n\nSources: [Nippon Steel](https://www.nipponsteel.com/en/product/titan/feature/pdf/T001en_16-23.pdf), [BSSA](https://bssa.org.uk/bssa_articles/elevated-temperature-physical-properties-of-stainless-steels/).\n\n'
    graph = "## Graphic\n\nThe two cross-sections show minimum hole / maximum shaft and maximum hole / minimum shaft. Deviations are amplified using the same scale in both views. The drawing is not to scale. Values are diametral; radial clearance is half the diametral difference. Without Lamé, red indicates theoretical interference before assembly. With Lamé, an Assembly state selector defaults to After assembly: solid contours show the loaded geometry, dashed contours the free geometry and amber marks the contact pressure. The two views use the actual minimum/maximum initial-interference corners; a clearance corner stays separate with zero pressure. A common monotone schematic radial scale magnifies interface differences and preserves surface order; it is not a physical drawing scale.\n\n"
    coverage = f"## Coverage and correction log\n\n{len(ALESAGES)} hole classes · {len(ARBRES)} shaft classes · {sum(map(len, DATA['classes'].values()))} tabulated size intervals. Each row records its source PDF page (1-based).\n\n"
    columns = ['Tolerance', 'Above (mm)', 'Up to (mm)', 'Field', 'Original (µm)', 'Used (µm)', 'Basis']
    table = '| ' + ' | '.join(columns) + ' |\n|' + '|'.join(['---']*len(columns)) + '|\n'
    for row in DATA['corrections']:
        vals = [row['tolerance'], row['above_mm'], row['up_to_mm'], row['field'], row['original_um'], row['used_um'], row['basis']]
        table += '| ' + ' | '.join(str(v).replace('|', '/') for v in vals) + ' |\n'
    notation = "## Diameter names\n\nDN is the fit/interface diameter (hole ID and shaft OD), D1 is the free hub outer diameter, and d2 is the free shaft inner diameter. The geometry key is schematic, not to scale.\n\n"
    return intro + notation + calculation + thermal + MODEL_README + graph + coverage + table

@st.dialog("README", width="large")
def show_readme():
    content = readme_text()
    st.markdown(content)
    st.download_button("Download README.md", content, file_name="README.md", mime="text/markdown", key="download_readme")

st.markdown("""<style>
.st-key-readme_link button {background:transparent;border:0;padding:0;min-height:1.6rem;color:var(--text-color);text-decoration:underline;font-size:.85rem;}
.st-key-readme_link button:hover {color:#e21b2d;background:transparent;}
</style>""", unsafe_allow_html=True)
heading, branding = st.columns([6, 1.5], vertical_alignment="center")
with heading:
    st.markdown("### Tolerator · Shaft / hole fits")
    st.caption("Version 3.3 · Based on ISO 286-2:2010 · Cor 1:2013 · ≤ 500 mm")
    if st.button("README", key="readme_link", help="Calculation, thermal model, data coverage and corrections"):
        show_readme()
with branding:
    st.markdown('<div style="display:flex;justify-content:flex-end" aria-label="Audi AFR, silver red and black Formula 1 car">\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 245" preserveAspectRatio="xMidYMid meet" style="width:210px;max-width:100%;height:auto" role="img" aria-label="Audi AFR schematic Formula 1 car">\n<g fill="none" stroke="#9099a5" stroke-width="3"><circle cx="34" cy="28" r="20"/><circle cx="64" cy="28" r="20"/><circle cx="94" cy="28" r="20"/><circle cx="124" cy="28" r="20"/></g>\n<text x="181" y="39" font-family="Arial,sans-serif" font-size="31" font-weight="700" letter-spacing="4" fill="#9099a5">AUDI</text>\n<text x="305" y="39" font-family="Arial,sans-serif" font-size="31" font-weight="700" letter-spacing="4" fill="#f01829">AFR</text>\n<g transform="translate(-55 64)" stroke-linejoin="round">\n<!-- Low, long side profile: 404-unit wheelbase, 86-unit tyre diameter. -->\n<path d="M88 147L111 129 164 120 181 139 172 158 95 158 84 153Z" fill="#15171b" stroke="#58616b" stroke-width="1.5"/>\n<path d="M88 143L145 125 211 107 278 90 321 87 359 90 386 88 430 81 467 79 498 86 555 105 605 117 638 133 635 148 273 148 254 132 198 133 141 144Z" fill="#b8b9b6" stroke="#7d8488" stroke-width="1.6"/>\n<path d="M465 49C493 45 536 55 576 63L603 80 615 116 579 132 466 123Z" fill="#181b1e" stroke="#62666a" stroke-width="1.3"/>\n<path d="M276 120H304L318 132 354 135H584L606 145 599 158H276Z" fill="#171a1e"/>\n<path d="M315 103C363 91 417 89 464 87L486 93 493 132 463 145H369L338 136 314 120Z" fill="#9b9e9b"/>\n<path d="M464 83C501 84 550 95 566 108L570 141 464 144Z" fill="#ff1529"/>\n<path d="M467 85C504 89 544 99 562 110L568 119C532 109 504 108 467 106Z" fill="#ff5c57"/>\n<path d="M319 105C363 98 414 97 461 98" fill="none" stroke="#d8d8d1" stroke-width="3"/>\n<path d="M309 125L321 146H465" fill="none" stroke="#545b5d" stroke-width="2"/>\n<path d="M434 48L435 36 451 35 456 46 454 79H433Z" fill="#9d9f9c" stroke="#62686b" stroke-width="1.5"/>\n<path d="M436 36L439 26H449L453 35Z" fill="#33383a"/>\n<path d="M307 87L329 73 351 73 369 82 351 89Z" fill="#11161a"/>\n<path d="M309 85Q325 61 344 63L398 74 411 81H374" fill="none" stroke="#bfc1bd" stroke-width="7" stroke-linecap="round"/>\n<path d="M368 81L349 90" fill="none" stroke="#7a8387" stroke-width="4"/>\n<ellipse cx="345" cy="102" rx="15" ry="4" fill="#dc2631"/>\n<path d="M268 148H630L650 159H275Z" fill="#0e1115" stroke="#545c60" stroke-width="1.2"/>\n<path d="M640 63V118L656 132 680 130 698 99 706 63Z" fill="#101418" stroke="#515b62" stroke-width="1.5"/>\n<path d="M646 57H709V76L646 72Z" fill="#22282b" stroke="#535d63" stroke-width="1.5"/>\n<path d="M654 120H705V131H656Z" fill="#111619"/>\n<path d="M245 116L315 102M253 143L319 126M590 114L556 103M595 146L569 132" fill="none" stroke="#30383d" stroke-width="4"/>\n<g transform="translate(222 127)">\n<circle r="43" fill="#101316" stroke="#41494d" stroke-width="1.6"/>\n<circle r="36" fill="none" stroke="#e9182b" stroke-width="2.8"/>\n<circle r="26" fill="#1a2023" stroke="#374047" stroke-width="1.5"/>\n<path d="M0-24V24M-24 0H24M-17-17L17 17M-17 17L17-17" stroke="#3a4248" stroke-width="2"/>\n<circle r="7" fill="#171b1e" stroke="#d8202e" stroke-width="2"/>\n<circle r="2.5" fill="#879095"/>\n</g><g transform="translate(626 127)">\n<circle r="43" fill="#101316" stroke="#41494d" stroke-width="1.6"/>\n<circle r="36" fill="none" stroke="#e9182b" stroke-width="2.8"/>\n<circle r="26" fill="#1a2023" stroke="#374047" stroke-width="1.5"/>\n<path d="M0-24V24M-24 0H24M-17-17L17 17M-17 17L17-17" stroke="#3a4248" stroke-width="2"/>\n<circle r="7" fill="#171b1e" stroke="#d8202e" stroke-width="2"/>\n<circle r="2.5" fill="#879095"/>\n</g></g></svg></div>', unsafe_allow_html=True)

# Conserver les diamètres même quand leurs champs changent de disposition.
for cle in ("nominal_alesage", "nominal_arbre"):
    if cle not in st.session_state or st.session_state[cle] is None:
        st.session_state[cle] = 40.0

def memoriser(cle, widget):
    value = st.session_state.get(widget)
    if value is None:
        st.session_state['_input_notice'] = 'Incomplete numeric entry: the previous valid value has been retained.'
        return
    st.session_state[cle] = value

def stable_number(label, key, default, **kwargs):
    saved = 'saved_'+key
    if saved not in st.session_state or st.session_state[saved] is None:
        st.session_state[saved] = st.session_state.get(key, default)
    if st.session_state[saved] is None:
        st.session_state[saved] = default
    st.session_state[key] = st.session_state[saved]
    return st.number_input(label, key=key, value=None, on_change=memoriser, args=(saved,key), **kwargs)

def geometry_key_svg():
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 200" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Geometry key: DN interface diameter, D1 hub outside diameter, d2 shaft bore diameter">
<defs><marker id="dim-arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#64748b"/></marker></defs>
<rect width="600" height="200" rx="10" fill="#f8fafc"/>
<rect x="60" y="20" width="240" height="140" fill="#bfdbfe" stroke="#2563eb" stroke-width="2"/>
<rect x="30" y="50" width="300" height="80" fill="#5eead4" stroke="#0f766e" stroke-width="2"/>
<rect x="30" y="80" width="300" height="20" fill="white" stroke="#0f766e" stroke-width="1.5"/>
<path d="M15 90H580" stroke="#94a3b8" stroke-dasharray="5 5"/>
<g fill="none" stroke="#94a3b8" stroke-width="1"><path d="M300 20H360M300 160H360M330 50H440M330 130H440M330 80H530M330 100H530"/></g>
<g stroke="#64748b" stroke-width="1.5" marker-start="url(#dim-arrow)" marker-end="url(#dim-arrow)"><path d="M354 24V156"/><path d="M434 54V126"/><path d="M524 83V97"/></g>
<g font-family="Arial,sans-serif" font-size="18" font-weight="700"><text x="364" y="95" fill="#1d4ed8">D1</text><text x="444" y="95" fill="#334155">DN</text><text x="534" y="95" fill="#0f766e">d2</text></g>
<g font-family="Arial,sans-serif" font-size="13"><text x="60" y="184" fill="#1d4ed8">Hub: outer Ø D1</text><text x="245" y="184" fill="#334155">Fit: Ø DN</text><text x="415" y="184" fill="#0f766e">Shaft bore: Ø d2</text></g></svg>''' 

def champ_diametre(label, cle, widget):
    st.session_state[widget] = st.session_state[cle]
    return st.number_input(label, min_value=0.001, max_value=500.0,
                           step=0.001, format="%.3f", key=widget,
                           on_change=memoriser, args=(cle, widget))


def fit_type(value):
    if value.startswith('Avec jeu'):
        return 'Clearance fit'
    if value.startswith('Avec serrage'):
        return 'Interference fit'
    return 'Transition fit'

def tolerance_selectors(diameter, part, prefix, default_letter, default_grade):
    classes = classes_disponibles(diameter, part)
    pairs = [(c.rstrip('0123456789'), int(c[len(c.rstrip('0123456789')):])) for c in classes]
    letters = list(dict.fromkeys(letter for letter, grade in pairs))
    letter_key, grade_key = 'letter_'+prefix, 'it_'+prefix
    # Preserve a previously selected combined class when upgrading from 2.0.
    old = st.session_state.get(prefix, default_letter+str(default_grade))
    old_letter = old.rstrip('0123456789')
    preferred_letter = st.session_state.get(letter_key, old_letter)
    if preferred_letter not in letters:
        preferred_letter = default_letter
        if letter_key in st.session_state:
            del st.session_state[letter_key]
        st.caption('Previous letter is not tabulated at this diameter; restored the default.')
    letter_col, grade_col, _ = st.columns([1.1, 1, 1.3], gap="small")
    letter = letter_col.selectbox("Zone", letters, help="Tolerance zone letter",
                                 index=letters.index(preferred_letter), key=letter_key)
    grades = sorted(g for l, g in pairs if l == letter)
    preferred_grade = st.session_state.get(grade_key, int(old[len(old_letter):]))
    if preferred_grade not in grades:
        preferred_grade = default_grade if default_grade in grades else min(grades, key=lambda g: abs(g-default_grade))
        if grade_key in st.session_state:
            del st.session_state[grade_key]
        st.caption('Previous IT grade is not tabulated for this selection; selected an available grade.')
    grade = grade_col.selectbox("IT grade", grades, index=grades.index(preferred_grade), key=grade_key)
    return letter+str(grade)

parametres, resultats = st.columns([1, 1.1], gap="large")
with parametres:
    options = st.columns(3)
    separes = options[0].checkbox("Separate diameters", key="separes")
    thermique = options[1].checkbox("Thermal calculation", key="thermique")
    lame = options[2].checkbox("Lamé model", key="lame")
    if '_input_notice' in st.session_state:
        st.caption(st.session_state.pop('_input_notice'))
    if separes and not st.session_state.get("etait_separe", False):
        st.session_state["nominal_arbre"] = st.session_state["nominal_alesage"]
    st.markdown("""<style>
    .st-key-zone_alesage {border-right:1px solid #94a3b8;padding-right:1.2rem;min-height:155px;}
    .fit-summary {padding:12px 18px;border:1px solid;border-radius:12px;margin:8px 0;}
    .fit-heading {display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;margin-bottom:8px;}
    .fit-name, .fit-status {font-family:inherit;font-size:1.8rem;font-weight:700;}
    .fit-values {display:flex;gap:40px;flex-wrap:wrap;}
    .fit-value {font-size:1.35rem;font-weight:600;}
    .fit-label {font-size:.9rem;}
    .fit-graphic svg, .geometry-key svg {display:block;width:100%;height:auto;}
    .geometry-key {max-width:600px;margin:.3rem 0 .6rem;}
    .temperature-results {width:100%;border-collapse:collapse;font-size:.8rem;margin:.5rem 0;}
    .temperature-results th {padding:6px;border-bottom:1px solid #94a3b8;font-weight:600;text-align:right;}
    .temperature-results td {padding:9px 6px;text-align:right;white-space:nowrap;}
    .temperature-results th:first-child,.temperature-results td:first-child {text-align:left;}
    .temperature-results .nominal {background:#f1f5f9;color:#334155;}
    .temperature-results .hot {background:#fff7ed;color:#9a3412;}
    .temperature-results .cold {background:#eff6ff;color:#1e40af;}
    .block-container {padding-top:4.5rem;padding-bottom:1rem;max-width:1550px;}
    [data-testid="stMain"] {scroll-padding-top:4.5rem;}
    [data-testid="stVerticalBlock"] {gap:.65rem;}
    h3 {padding-top:.25rem !important;padding-bottom:.25rem !important;}

    .st-key-chaud input {background-color:#fff7ed !important;color:#9a3412 !important;}
    .st-key-froid input {background-color:#eff6ff !important;color:#1e40af !important;}
    .st-key-t0 input {background-color:#f1f5f9 !important;color:#334155 !important;}
    </style>""", unsafe_allow_html=True)
    if thermique:
        tnom, tchaud, tfroid = st.columns(3)
        with tnom:
            t0 = stable_number("Nominal (°C)", 't0', 20.0, min_value=-273.15, step=1.0, format="%.0f")
        with tchaud:
            chaud = stable_number("Hot (°C)", 'chaud', 80.0, min_value=-273.15, step=1.0, format="%.0f")
        with tfroid:
            froid = stable_number("Cold (°C)", 'froid', -20.0, min_value=-273.15, step=1.0, format="%.0f")
        st.caption("Diameters defined at nominal temperature · same temperature for both parts.")
    if lame:
        st.markdown('<div class="geometry-key">'+geometry_key_svg()+'</div>', unsafe_allow_html=True)

    def changer_materiau(piece):
        material = st.session_state['materiau_'+piece]
        st.session_state['saved_materiau_'+piece] = material
        defaults = dict(alpha=MATERIAUX[material], **ELASTIC_PRESETS[material])
        for prop, value in defaults.items():
            st.session_state[prop+'_'+piece] = value
            st.session_state['saved_'+prop+'_'+piece] = value

    def material_value_changed(piece, prop):
        memoriser('saved_'+prop+'_'+piece, prop+'_'+piece)

    def champ_materiau(piece):
        if 'materiau_'+piece not in st.session_state:
            st.session_state['materiau_'+piece] = st.session_state.get('saved_materiau_'+piece, 'Acier')
        material = st.session_state['materiau_'+piece]
        defaults = dict(alpha=MATERIAUX[material], **ELASTIC_PRESETS[material])
        for prop, value in defaults.items():
            saved, key = 'saved_'+prop+'_'+piece, prop+'_'+piece
            if saved not in st.session_state or st.session_state[saved] is None:
                current = st.session_state.get(key, value)
                st.session_state[saved] = value if current is None else current
            st.session_state[key] = st.session_state[saved]
        if thermique or lame:
            materiau_col, alpha_col = st.columns([1.15, 1], gap="small")
        else:
            materiau_col = st.container()
        materiau_col.selectbox("Material", list(MATERIAUX), format_func=lambda x: {'Acier': 'Steel', 'Alu': 'Aluminium', 'Titane': 'Titanium', 'Inox': 'Stainless steel'}[x],
                              key='materiau_'+piece, on_change=changer_materiau, args=(piece,))
        if thermique or lame:
            alpha_col.number_input("α (µm/m/K)", value=None, step=0.1, format="%.3f", key='alpha_'+piece,
                                   on_change=material_value_changed, args=(piece,'alpha'),
                                   help="12 means 12 × 10⁻⁶ K⁻¹. Indicative preset; edit for the actual grade and temperature range.")
        if lame:
            e_col, nu_col = st.columns([1.15, 1], gap="small")
            e_col.number_input("Young E (GPa)", min_value=0.001, value=None, step=1.0, format="%.3f", key='young_gpa_'+piece,
                               on_change=material_value_changed, args=(piece,'young_gpa'))
            nu_col.number_input("Poisson ν", min_value=-0.99, max_value=0.499, value=None, step=0.01, format="%.3f", key='poisson_'+piece,
                                on_change=material_value_changed, args=(piece,'poisson'))
        return tuple(st.session_state[prop+'_'+piece] for prop in ('alpha','young_gpa','poisson'))

    # A single, fixed-height diameter row for either mode keeps everything
    # below it (part headers, materials and tolerances) in the same position.
    with st.container(key="diameter_row"):
        if separes:
            dn_hole, dn_shaft = st.columns(2)
            with dn_hole:
                diametre = champ_diametre("DN — hole fit Ø (mm)", "nominal_alesage", "diametre_alesage")
            with dn_shaft:
                diametre_arbre = champ_diametre("DN — shaft fit Ø (mm)", "nominal_arbre", "diametre_arbre")
        else:
            diametre = champ_diametre("DN — common fit diameter (mm)", "nominal_alesage", "diametre_commun")
            diametre_arbre = diametre
    gauche, droite = st.columns(2)
    with gauche:
        with st.container(key="zone_alesage"):
            st.subheader("Hub (hole)")
            if thermique or lame:
                alpha_h, young_h, poisson_h = champ_materiau("alesage")
            if lame:
                hub_outer = stable_number("D1 — hub outer Ø (mm)", 'hub_outer', round(float(diametre)*2,3),
                                           min_value=0.001, step=1.0, format="%.3f",
                                           help="Free outer diameter at reference T; must exceed all hole limits.")
            alesage = tolerance_selectors(diametre, 'hole', 'alesage', 'H', 7)
            limites_alesage = st.empty()
    with droite:
        st.subheader("Shaft")
        if thermique or lame:
            alpha_s, young_s, poisson_s = champ_materiau("arbre")
        if lame:
            shaft_inner = stable_number("d2 — shaft inner Ø (mm)", 'shaft_inner', 0.0,
                                        min_value=0.0, step=1.0, format="%.3f",
                                        help="Free bore diameter at reference T. 0 = solid shaft; otherwise smaller than all shaft outer limits.")
        arbre = tolerance_selectors(diametre_arbre, 'shaft', 'arbre', 'g', 6)
        limites_arbre = st.empty()
    if lame:
        length_col, friction_col = st.columns(2)
        with length_col:
            contact_length = stable_number("Contact length L (mm)", 'contact_length', 30.0,
                                           min_value=0.001, step=1.0, format="%.3f",
                                           help="Effective contact length at service T; not automatically thermally expanded.")
        with friction_col:
            friction = stable_number("Friction coefficient μ", 'friction', 0.12,
                                     min_value=0.0, step=0.01, format="%.3f",
                                     help="Same coefficient for the press-in estimate and torque capacity.")
        st.caption("Lamé: free-ended elastic cylinders · E, ν and μ held constant · no yielding check.")
    st.session_state["etait_separe"] = separes
try:
    r = calculer(diametre, arbre, alesage, diametre_arbre)
except ValueError as exc:
    st.error({
        'Diamètre attendu : 3 < d ≤ 50 mm.': 'Diameter must satisfy 3 < d ≤ 50 mm.',
        'Diamètre non numérique.': 'Diameter must be numeric.',
        'Paramètre thermique non numérique.': 'Thermal parameters must be numeric.',
        'Paramètre thermique non fini.': 'Thermal parameters must be finite.',
        'Température inférieure au zéro absolu.': 'Temperature is below absolute zero.',
        'Facteur de dilatation non positif : vérifier les paramètres.': 'Non-positive expansion factor: check thermal parameters.',
    }.get(str(exc), str(exc)))
    st.stop()

with resultats:
    r_reference = r.copy()
    scenarios = {'Nominal': r_reference}
    scenario_errors = {}
    if thermique:
        scenarios = {}
        for name, temperature in [('Nominal',t0), ('Hot',chaud), ('Cold',froid)]:
            try:
                if name=='Hot' and temperature<t0:
                    raise ValueError('Hot temperature must be at least the nominal temperature.')
                if name=='Cold' and temperature>t0:
                    raise ValueError('Cold temperature must not exceed the nominal temperature.')
                scenarios[name] = calculer_thermique(r_reference,t0,temperature,alpha_h,alpha_s)
            except ValueError as exc:
                scenario_errors[name] = str(exc)
        for name, message in scenario_errors.items():
            st.error(name+': '+message)
        # Nominal remains valid even while a hot/cold field is being edited.
        if st.session_state.get('scenario') not in scenarios and 'scenario' in st.session_state:
            del st.session_state['scenario']
        choix = st.radio("Graphic condition", list(scenarios), horizontal=True, key='scenario')
        r = scenarios[choix]
        theme_fond, theme_accent = {'Nominal': ('#f1f5f9', '#475569'),
                                   'Hot': ('#fff7ed', '#c2410c'),
                                   'Cold': ('#eff6ff', '#1d4ed8')}[choix]
        st.markdown(f'<div style="padding:6px 12px;margin:0 0 6px;border-left:5px solid {theme_accent};border-radius:8px;background:{theme_fond};color:{theme_accent};font-weight:700">{choix} · {float(r["temperature"]):.0f} °C</div>', unsafe_allow_html=True)
    else:
        choix = 'Nominal'
        theme_fond, theme_accent = '#f8fafc', '#64748b'

    lame_scenarios, lame_errors = {}, {}
    lame_result = None
    if lame:
        lame_inputs = dict(hub_outer_mm=hub_outer, shaft_inner_mm=shaft_inner,
                           young_h_gpa=young_h, poisson_h=poisson_h,
                           young_s_gpa=young_s, poisson_s=poisson_s,
                           contact_length_mm=contact_length, friction=friction)
        for name, case in scenarios.items():
            try:
                lame_scenarios[name] = calculer_lame_intervalle(case, **lame_inputs)
            except ValueError as exc:
                lame_errors[name] = str(exc)
        lame_result = lame_scenarios.get(choix)

    def afficher_dimensions(zone, minimum, maximum, ecart_inf, ecart_sup):
        zone.markdown(f"""<div style="display:grid;grid-template-columns:1fr auto;gap:6px 12px;align-items:baseline">
    <strong>Ø min. : {minimum:.3f} mm</strong><span style="color:#888">{ecart_inf:+.0f} µm</span>
    <strong>Ø max. : {maximum:.3f} mm</strong><span style="color:#888">{ecart_sup:+.0f} µm</span>
    </div>""", unsafe_allow_html=True)

    afficher_dimensions(limites_alesage, r['alesage_min'], r['alesage_max'], r['EI'], r['ES'])
    afficher_dimensions(limites_arbre, r['arbre_min'], r['arbre_max'], r['ei'], r['es'])

    def nombre(v):
        return f"{float(v):g}"

    def limite(v):
        return f"{v:.0f} µm"

    def nature(v):
        return "interference" if v < 0 else "clearance"

    if r_reference['d_alesage'] == r_reference['d_arbre']:
        designation = f"Ø{nombre(r_reference['d_alesage'])}{alesage}{arbre}"
    else:
        designation = f"Ø{nombre(r_reference['d_alesage'])}{alesage} / Ø{nombre(r_reference['d_arbre'])}{arbre}"
    if r['jeu_min_um'] >= 0:
        fond, texte, bord, statut = '#ecfdf5', '#065f46', '#10b981', 'Clearance fit'
    elif r['jeu_max_um'] <= 0:
        fond, texte, bord, statut = '#fef2f2', '#991b1b', '#ef4444', 'Interference fit'
    else:
        fond, texte, bord, statut = '#fffbeb', '#854d0e', '#eab308', 'Transition fit'
    st.markdown(f"""<section class="fit-summary" style="background:{fond};color:{texte};border-color:{bord}">
    <div class="fit-heading"><div class="fit-name">{designation}</div><div class="fit-status">{statut}</div></div>
    <div class="fit-values">
    <div><div class="fit-label">Min. ({nature(r['jeu_min_um'])})</div><div class="fit-value">{limite(r['jeu_min_um'])}</div></div>
    <div><div class="fit-label">Max. ({nature(r['jeu_max_um'])})</div><div class="fit-value">{limite(r['jeu_max_um'])}</div></div>
    </div></section>""", unsafe_allow_html=True)
    rows = [
        {"Part": f"Hole {alesage}", "Lower deviation (µm)": f"{r['EI']:.0f}", "Upper deviation (µm)": f"{r['ES']:.0f}",
         "Min. diameter (mm)": f"{r['alesage_min']:.3f}", "Max. diameter (mm)": f"{r['alesage_max']:.3f}"},
        {"Part": f"Shaft {arbre}", "Lower deviation (µm)": f"{r['ei']:.0f}", "Upper deviation (µm)": f"{r['es']:.0f}",
         "Min. diameter (mm)": f"{r['arbre_min']:.3f}", "Max. diameter (mm)": f"{r['arbre_max']:.3f}"},
    ]


    if lame and lame_result is not None:
        st.subheader("Shaft inside the hub")
        assembly_view = st.radio("Assembly state", ['After assembly','Before assembly'],
                                 horizontal=True, key='assembly_view')
        after = assembly_view == 'After assembly'
        svg = lame_graphic(lame_result, after=after, background=theme_fond, accent=theme_accent)
        st.markdown('<div class="fit-graphic">'+svg+'</div>', unsafe_allow_html=True)
        st.caption('Both views show actual minimum/maximum initial-interference corners. '+
                   ('Solid surfaces: assembled geometry. Dashed outlines: free geometry. Amber ring/arrows: contact pressure.' if after else
                    'Free geometry before assembly. Red: theoretical overlap, resolved by elastic deformation after assembly.')+
                   ' The same schematic radial scale is used in both views; diameter differences are exaggerated.')
    else:
        if lame:
            st.caption('Lamé geometry is invalid for this condition; showing free parts before assembly.')
        # Vue en coupe de face, avant assemblage : diamètres nominaux comprimés,
        # écarts radiaux amplifiés avec une même échelle dans les deux cas limites.
        st.subheader("Shaft inside the hole")
        st.caption("Schematic cross-section before assembly · deviations exaggerated · same scale in both views.")
        reference = float(r['d_alesage'])
        def ecart_radial(d):
            return (float(d)-reference)*1000/2
        amplitude = max(1, *(abs(ecart_radial(r[k])) for k in
                            ('alesage_min', 'alesage_max', 'arbre_min', 'arbre_max')))
        echelle = 28/amplitude
    
        def rayon(d):
            return 65 + ecart_radial(d)*echelle
    
        svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 390" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Shaft and hole cross-sections at both limit conditions">'
        svg += f'<rect x="1" y="1" width="678" height="388" rx="12" fill="{theme_fond}" stroke="{theme_accent}" stroke-width="2"/>'
        svg += '<g font-family="Arial,sans-serif" fill="#334155">'
        for cx, titre, dh, ds, jeu in [
            (175, 'Min.', r['alesage_min'], r['arbre_max'], r['jeu_min_um']),
            (505, 'Max.', r['alesage_max'], r['arbre_min'], r['jeu_max_um'])]:
            rh, rs = rayon(dh), rayon(ds)
            couleur = '#dc2626' if jeu < 0 else '#15803d'
            svg += f'<text x="{cx}" y="30" text-anchor="middle" font-size="17" font-weight="bold">{titre} ({nature(jeu)}) · {limite(jeu)}</text>'
            # Matière du moyeu en bleu, évidement blanc, arbre vert.
            svg += f'<circle cx="{cx}" cy="160" r="108" fill="#bfdbfe" stroke="#2563eb" stroke-width="2"/>'
            svg += f'<circle cx="{cx}" cy="160" r="{rh}" fill="white" stroke="#2563eb" stroke-width="2"/>'
            svg += f'<circle cx="{cx}" cy="160" r="{rs}" fill="#5eead4" stroke="#0f766e" stroke-width="2"/>'
            if lame_result is not None and lame_result['shaft_inner_free_mm'] > 0:
                bore_radius = rs*lame_result['shaft_inner_free_mm']/float(ds)
                svg += f'<circle cx="{cx}" cy="160" r="{bore_radius}" fill="white" stroke="#0f766e" stroke-width="1.5"/>' 
            if jeu < 0:
                svg += f'<circle cx="{cx}" cy="160" r="{(rh+rs)/2}" fill="none" stroke="#ef4444" stroke-opacity="0.7" stroke-width="{rs-rh}"/>'
                svg += f'<circle cx="{cx}" cy="160" r="{rh}" fill="none" stroke="#2563eb" stroke-dasharray="4 3"/>'
            svg += f'<path d="M {cx-117} 160 H {cx+117} M {cx} 43 V 277" fill="none" stroke="#64748b" stroke-width="0.8" stroke-dasharray="5 5"/>'
            svg += f'<text x="{cx}" y="155" text-anchor="middle" font-size="16" fill="#115e59">Shaft DN · {arbre}</text>'
            svg += f'<text x="{cx}" y="176" text-anchor="middle" font-size="14" fill="#115e59">Ø {ds:.3f} mm</text>'
            svg += f'<text x="{cx}" y="298" text-anchor="middle" font-size="14" fill="#1d4ed8">Hole DN · {alesage} · Ø {dh:.3f} mm</text>'
            svg += f'<text x="{cx}" y="321" text-anchor="middle" font-size="13" fill="{couleur}">{"Overlap before assembly" if jeu < 0 else "Clearance between shaft and hole"}</text>'
        svg += '<rect x="125" y="352" width="14" height="14" fill="#bfdbfe" stroke="#2563eb"/><text x="146" y="364" font-size="13">Hub</text>'
        svg += '<rect x="270" y="352" width="14" height="14" fill="#5eead4" stroke="#0f766e"/><text x="291" y="364" font-size="13">Shaft</text>'
        svg += '<rect x="405" y="352" width="14" height="14" fill="#ef4444"/><text x="426" y="364" font-size="13">Interference</text></g></svg>'
        st.markdown('<div class="fit-graphic">'+svg+'</div>', unsafe_allow_html=True)
        st.caption("Min./Max. values are diametral; radial clearance is half this value. Red shows theoretical overlap before assembly; deformation is not calculated.")
    if lame:
        st.markdown("#### Lamé · Results by temperature" if thermique else "#### Lamé · Elastic press fit")
        names = ['Nominal','Hot','Cold'] if thermique else ['Nominal']
        fields = [('DN · Hole ID','hole_loaded_mm',3,'mm'),
                  ('DN · Shaft OD','shaft_loaded_mm',3,'mm'),
                  ('D1 · Hub OD','hub_outer_loaded_mm',3,'mm'),
                  ('d2 · Shaft ID','shaft_inner_loaded_mm',3,'mm'),
                  ('Pressure','pressure_mpa',1,'MPa'),
                  ('Stress · Hub σvM','hub_stress_vm_mpa',1,'MPa'),
                  ('Stress · Shaft σvM','shaft_stress_vm_mpa',1,'MPa'),
                  ('Press-in force','press_force_n',0,'N'),
                  ('Torque','torque_nm',1,'N·m')]
        headers = '<table class="temperature-results"><thead><tr><th>Result</th>'
        for name in names:
            label = name+(f" · {float({'Nominal':t0,'Hot':chaud,'Cold':froid}[name]):.0f} °C" if thermique else '')
            headers += f'<th colspan="2">{label}</th>'
        headers += '</tr><tr><th>After assembly</th>'+''.join('<th>Min.</th><th>Max.</th>' for _ in names)+'</tr></thead><tbody>'
        for title, field, digits, unit in fields:
            headers += f'<tr data-field="{field}"><td>{title} ({unit})</td>'
            for name in names:
                values = lame_scenarios[name]['bounds'][field] if name in lame_scenarios else (None,None)
                headers += ''.join(f'<td class="{name.lower()}">{v:.{digits}f}</td>' if v is not None else '<td>—</td>' for v in values)
            headers += '</tr>'
        st.markdown(headers+'</tbody></table>',unsafe_allow_html=True)
        st.caption('DN is shared where contact exists; hole and shaft remain separate in clearance cases. Stress: peak von Mises from contact pressure only, without torque or assembly friction loads. No yield-strength check.')
        for name, message in lame_errors.items():
            st.error('Lamé · '+name+': '+message)
        if lame_result is not None:
            if not lame_result['has_contact']:
                st.caption('Selected condition: no contact; pressure and capacities are zero.')
            elif not lame_result['contact_guaranteed']:
                st.caption('Selected condition: contact is not guaranteed; minimum pressure and capacities are zero.')
        if any(lr['max_surface_strain']>0.01 for lr in lame_scenarios.values()):
            st.warning('Predicted deformation exceeds 1%: check the small-strain elastic assumption and material strength.')
        if st.checkbox("Thermal assembly check", key="assembly_check"):
            st.markdown('#### Shrink-fit assembly · independent part temperatures')
            assembly_t0 = t0 if thermique else stable_number('Reference temperature (°C)', 'assembly_t0', 20.0, min_value=-273.15, step=1.0, format="%.0f")
            c1,c2,c3 = st.columns(3)
            with c1:
                target_gap = stable_number('Target diametral clearance (µm)', 'assembly_gap', 20.0, min_value=0.0, step=1.0, format="%.0f")
            with c2:
                assembly_hot = stable_number('Hub temperature (°C)', 'assembly_hot', 80.0, min_value=-273.15, step=1.0, format="%.0f")
            with c3:
                assembly_cold = stable_number('Shaft temperature (°C)', 'assembly_cold', -20.0, min_value=-273.15, step=1.0, format="%.0f")
            try:
                ar = thermal_assembly(r_reference, assembly_t0, alpha_h, alpha_s, target_gap, assembly_hot, assembly_cold)
                status = st.success if ar['assembly_possible'] else st.warning
                status(f"Worst-case clearance: {ar['clearance_um']:.0f} µm · target {target_gap:.0f} µm · "+('target met' if ar['assembly_possible'] else 'target not met'))
                def temperature_label(value):
                    return f'{value:.0f} °C' if value is not None else 'Unavailable'
                st.table([
                    {'Strategy':'Heat hub only','Hub ≥':temperature_label(ar['hub_hot_only_c']),'Shaft ≤':f'{assembly_t0:.0f} °C'},
                    {'Strategy':'Cool shaft only','Hub ≥':f'{assembly_t0:.0f} °C','Shaft ≤':temperature_label(ar['shaft_cold_only_c'])},
                    {'Strategy':'With entered shaft temperature','Hub ≥':temperature_label(ar['hub_required_c']),'Shaft ≤':f'{assembly_cold:.0f} °C'},
                    {'Strategy':'With entered hub temperature','Hub ≥':f'{assembly_hot:.0f} °C','Shaft ≤':temperature_label(ar['shaft_required_c'])}])
                st.caption('Worst tolerance corner: minimum hole / maximum shaft at reference T. Temperatures rounded outward to whole °C. Constant α; check material/process limits and heat transfer during insertion. Thresholds ensure the target clearance within this model only.')
            except ValueError as exc:
                st.error(str(exc))
        st.caption('Fully engaged contact; force and torque capacities apply separately. Elastic model without yielding or roughness corrections. See README.')
    if thermique:
        st.markdown('#### Fit limits by temperature')
        st.table([{'Condition':name,'Temperature (°C)':f"{float(case['temperature']):.0f}",
                   'Min. (µm)':f"{case['jeu_min_um']:.0f}",'Max. (µm)':f"{case['jeu_max_um']:.0f}",
                   'Type':fit_type(case['type'])} for name,case in scenarios.items()])
    with st.expander("Limit dimensions and size ranges"):
        st.table(rows)
        st.caption(f"Hole range: {r['plage']} · Shaft range: {r['plage_arbre']}")
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=';')
    writer.writerow(['Hole diameter at nominal T (mm)', str(r_reference['d_alesage'])])
    writer.writerow(['Shaft diameter at nominal T (mm)', str(r_reference['d_arbre'])])
    if thermique:
        writer.writerow(['Nominal T (°C)', f'{t0:.0f}'])
        writer.writerow(['Hole material', {'Acier':'Steel','Alu':'Aluminium','Titane':'Titanium','Inox':'Stainless steel'}[st.session_state['materiau_alesage']], 'Alpha (µm/m/K)', alpha_h])
        writer.writerow(['Shaft material', {'Acier':'Steel','Alu':'Aluminium','Titane':'Titanium','Inox':'Stainless steel'}[st.session_state['materiau_arbre']], 'Alpha (µm/m/K)', alpha_s])
        writer.writerow(['Condition', 'Temperature (°C)', 'Min (µm)', 'Max (µm)', 'Type'])
        for nom, cas in scenarios.items():
            writer.writerow([nom, f"{float(cas['temperature']):.0f}", f"{cas['jeu_min_um']:.0f}", f"{cas['jeu_max_um']:.0f}", fit_type(cas['type'])])
        writer.writerow(['Detailed dimensions: displayed condition', choix])
    writer.writerow(rows[0].keys())
    writer.writerows(row.values() for row in rows)
    writer.writerow(['Min. difference (µm)', f"{r['jeu_min_um']:.0f}"])
    writer.writerow(['Max. difference (µm)', f"{r['jeu_max_um']:.0f}"])
    if lame_scenarios:
        writer.writerow([])
        writer.writerow(['Lamé model', 'Free-ended elastic cylinders, sigma_z=0'])
        for key, value in lame_inputs.items():
            writer.writerow([key, value])
        writer.writerow(['Condition', 'Result', 'Min', 'Max', 'Unit'])
        for name, lr in lame_scenarios.items():
            for key, unit in [('hub_stress_vm_mpa', 'MPa'), ('shaft_stress_vm_mpa', 'MPa'), ('pressure_mpa', 'MPa'), ('press_force_n', 'N'), ('torque_nm', 'N.m'),
                              ('hole_loaded_mm', 'mm'), ('shaft_loaded_mm', 'mm'),
                              ('hub_outer_loaded_mm', 'mm'), ('shaft_inner_loaded_mm', 'mm')]:
                lo, hi = lr['bounds'][key]
                fmt = '.3f' if unit=='mm' else '.0f' if unit=='N' else '.1f'
                writer.writerow([name,key,format(lo,fmt),format(hi,fmt),unit])
            writer.writerow([name,'contact_guaranteed',lr['contact_guaranteed']])
            writer.writerow([name,'Free hub OD at service T (mm)',f"{lr['hub_outer_free_mm']:.3f}"])
            writer.writerow([name,'Free shaft ID at service T (mm)',f"{lr['shaft_inner_free_mm']:.3f}"])
    for name,message in scenario_errors.items():
        writer.writerow([name,'Thermal input error',message])
    for name,message in lame_errors.items():
        writer.writerow([name,'Lamé input error',message])
    if lame and st.session_state.get('assembly_check') and 'ar' in locals():
        writer.writerow([])
        writer.writerow(['Thermal assembly — worst tolerance corner'])
        for label,value,unit,digits in [
            ('Reference temperature',assembly_t0,'°C',0),('Hub temperature',assembly_hot,'°C',0),
            ('Shaft temperature',assembly_cold,'°C',0),('Target clearance',target_gap,'µm',0),
            ('Worst-case clearance',ar['clearance_um'],'µm',0)]:
            writer.writerow([label,f'{value:.{digits}f}',unit])
        writer.writerow(['Target met',ar['assembly_possible']])
        for field in ('hub_hot_only_c','shaft_cold_only_c','hub_required_c','shaft_required_c'):
            writer.writerow([field,f"{ar[field]:.0f}" if ar[field] is not None else 'Unavailable','°C'])
    st.download_button("Export results as CSV", buffer.getvalue().encode('utf-8-sig'),
                       file_name="fit_results.csv", mime="text/csv")
