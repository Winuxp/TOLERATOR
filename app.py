"""Lancer avec : python -m streamlit run app.py"""
import csv
import io
from decimal import Decimal
import streamlit as st
from calcul import calculer, calculer_thermique, MATERIAUX, ALESAGES, ARBRES, classes_disponibles, DATA

st.set_page_config(page_title="Tolerator", page_icon="⚙️", layout="wide")

def readme_text():
    intro = "# Tolerator — README\n\nBased on ISO 286-2:2010 with applicable Cor 1:2013 corrections. Nominal diameters up to 500 mm.\n\n"
    calculation = '## Calculation and tolerance data\n\n**Uppercase: hole. Lowercase: shaft.**\n\nLimit dimension = nominal diameter + deviation in µm / 1,000.\n\nMinimum difference = minimum hole − maximum shaft.\n\nMaximum difference = maximum hole − minimum shaft.\n\nFor H, EI = 0. For h, es = 0. The tolerance width is the selected IT grade.\n\n**Scope:** classes tabulated in ISO 286-2:2010, Tables 2–32, up to 500 mm,\nincluding CD/EF/FG, JS/js and ZA/ZB/ZC. J9–J18 follow Table 8 note a.\nOnly classes tabulated for each part’s nominal diameter are offered. Undefined combinations are not extrapolated.\nGrades IT01/IT0 have widths in Table 1 but no lettered classes in Tables 2–32, so they are not invented here.\nEach part uses its own nominal size range. Both cross-sections use the same amplification.\nNegative differences mean interference. Dimensions and differences are rounded to 1 µm for display;\ncalculations and fit classification use unrounded values.\n\nData extracted from the supplied ISO 286-2:2010 PDF, with applicable official Cor 1:2013 corrections.\nOne additional inconsistent za11 cell (225–250 mm) is reconciled using IT11 and the paired ZA11 table; see the correction log below.\nDisplay is rounded to 1 µm; fine-grade and JS/js half-micrometre values are retained internally.\n\n[Official 2013 corrigendum](https://www.iso.org/obp/ui?_escaped_fragment_=iso:std:iso:286:-2:ed-2:v1:cor:1:v1:en)\n\n'
    thermal = '## Thermal model and material presets\n\n**D(T) = D(T₀) × [1 + α × 10⁻⁶ × (T − T₀)]**, with α entered in µm/m/K.\n\nExpansion is applied to the limit dimensions calculated at T₀. ISO tables are not re-evaluated at the expanded diameter.\n\nLinear model with constant coefficients, free expansion and uniform temperature shared by both parts.\nNo gradients, interference-induced deformation or temperature dependence of α are calculated.\n\nMaterial presets are indicative: steel 12, aluminium 23, titanium 8.4 and austenitic stainless steel 17 µm/m/K.\nFerritic and martensitic stainless steels may differ substantially. Use your material datasheet.\n\nSources: [Nippon Steel](https://www.nipponsteel.com/en/product/titan/feature/pdf/T001en_16-23.pdf), [BSSA](https://bssa.org.uk/bssa_articles/elevated-temperature-physical-properties-of-stainless-steels/).\n\n'
    graph = "## Graphic\n\nThe two cross-sections show minimum hole / maximum shaft and maximum hole / minimum shaft. Deviations are amplified using the same scale in both views. The drawing is not to scale. Values are diametral; radial clearance is half the diametral difference. Red indicates theoretical interference before assembly, without elastic deformation.\n\n"
    coverage = f"## Coverage and correction log\n\n{len(ALESAGES)} hole classes · {len(ARBRES)} shaft classes · {sum(map(len, DATA['classes'].values()))} tabulated size intervals. Each row records its source PDF page (1-based).\n\n"
    columns = ['Tolerance', 'Above (mm)', 'Up to (mm)', 'Field', 'Original (µm)', 'Used (µm)', 'Basis']
    table = '| ' + ' | '.join(columns) + ' |\n|' + '|'.join(['---']*len(columns)) + '|\n'
    for row in DATA['corrections']:
        vals = [row['tolerance'], row['above_mm'], row['up_to_mm'], row['field'], row['original_um'], row['used_um'], row['basis']]
        table += '| ' + ' | '.join(str(v).replace('|', '/') for v in vals) + ' |\n'
    return intro + calculation + thermal + graph + coverage + table

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
    st.caption("Version 2.3 · Based on ISO 286-2:2010 · Cor 1:2013 · ≤ 500 mm")
    if st.button("README", key="readme_link", help="Calculation, thermal model, data coverage and corrections"):
        show_readme()
with branding:
    st.markdown('<div style="display:flex;justify-content:flex-end;opacity:.8" aria-label="Audi AFR, stylised Formula 1 car">\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 230 78" width="190" height="65" role="img" aria-label="Audi AFR">\n<g fill="none" stroke="#9099a5" stroke-width="1.7"><circle cx="18" cy="19" r="11"/><circle cx="34" cy="19" r="11"/><circle cx="50" cy="19" r="11"/><circle cx="66" cy="19" r="11"/></g>\n<text x="91" y="24" font-family="Arial,sans-serif" font-size="16" font-weight="700" letter-spacing="2" fill="#9099a5">AUDI</text>\n<text x="151" y="24" font-family="Arial,sans-serif" font-size="16" font-weight="700" letter-spacing="2" fill="#e21b2d">AFR</text>\n<g fill="#9099a5"><circle cx="63" cy="60" r="9"/><circle cx="161" cy="60" r="9"/>\n<path d="M40 49H47V60H40Z M45 55L80 51 97 43H115L126 49 155 53 184 56 191 60H175L151 64H83L75 61H48Z"/>\n<path d="M91 47L96 37H103V42H111L119 48Z M184 53H205V57H184Z M190 57H199V62H190Z"/></g>\n<path d="M104 39H111L118 46" fill="none" stroke="#e21b2d" stroke-width="2" stroke-linecap="round"/>\n</svg></div>', unsafe_allow_html=True)

# Conserver les diamètres même quand leurs champs changent de disposition.
for cle in ("nominal_alesage", "nominal_arbre"):
    if cle not in st.session_state:
        st.session_state[cle] = 40.0

def memoriser(cle, widget):
    st.session_state[cle] = st.session_state[widget]

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
    letter_col, grade_col = st.columns([1, 1], gap="small")
    letter = letter_col.selectbox("Tolerance zone", letters,
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
    options = st.columns(2)
    separes = options[0].checkbox("Separate diameters", key="separes")
    thermique = options[1].checkbox("Thermal calculation", key="thermique")
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
    .block-container {padding-top:4.5rem;padding-bottom:1rem;max-width:1550px;}
    [data-testid="stMain"] {scroll-padding-top:4.5rem;}
    [data-testid="stVerticalBlock"] {gap:.65rem;}
    h3 {padding-top:.25rem !important;padding-bottom:.25rem !important;}

    .st-key-chaud input {background-color:#fff7ed !important;color:#9a3412 !important;}
    .st-key-froid input {background-color:#eff6ff !important;color:#1e40af !important;}
    .st-key-t0 input {background-color:#f1f5f9 !important;color:#334155 !important;}
    </style>""", unsafe_allow_html=True)
    if not separes:
        diametre = champ_diametre("Common nominal diameter (mm)", "nominal_alesage", "diametre_commun")
    if thermique:
        tnom, tchaud, tfroid = st.columns(3)
        t0 = tnom.number_input("Nominal (°C)", min_value=-273.15, value=20.0, step=1.0, key="t0")
        chaud = tchaud.number_input("Hot (°C)", min_value=-273.15, value=80.0, step=1.0, key="chaud")
        froid = tfroid.number_input("Cold (°C)", min_value=-273.15, value=-20.0, step=1.0, key="froid")
        if not froid <= t0 <= chaud:
            st.error("Required: cold ≤ nominal ≤ hot temperature.")
            st.stop()
        st.caption("Diameters defined at nominal temperature · same temperature for both parts.")

    def changer_materiau(piece):
        st.session_state['alpha_'+piece] = MATERIAUX[st.session_state['materiau_'+piece]]

    def champ_materiau(piece):
        if 'alpha_'+piece not in st.session_state:
            st.session_state['alpha_'+piece] = MATERIAUX['Acier']
        materiau_col, alpha_col = st.columns([1.15, 1], gap="small")
        materiau_col.selectbox("Material", list(MATERIAUX), format_func=lambda x: {'Acier': 'Steel', 'Alu': 'Aluminium', 'Titane': 'Titanium', 'Inox': 'Stainless steel'}[x], key='materiau_'+piece,
                     on_change=changer_materiau, args=(piece,))
        return alpha_col.number_input("α (µm/m/K)", value=None, step=0.1, format="%.3f",
                               key='alpha_'+piece,
                               help="12 means 12 × 10⁻⁶ K⁻¹. Indicative value; edit to match your material grade.")

    gauche, droite = st.columns(2)
    with gauche:
        with st.container(key="zone_alesage"):
            st.subheader("Hole")
            if separes:
                diametre = champ_diametre("Hole diameter (mm)", "nominal_alesage", "diametre_alesage")
            if thermique:
                alpha_h = champ_materiau("alesage")
            alesage = tolerance_selectors(diametre, 'hole', 'alesage', 'H', 7)
            limites_alesage = st.empty()
    with droite:
        st.subheader("Shaft")
        if separes:
            diametre_arbre = champ_diametre("Shaft diameter (mm)", "nominal_arbre", "diametre_arbre")
        else:
            diametre_arbre = diametre
        if thermique:
            alpha_s = champ_materiau("arbre")
        arbre = tolerance_selectors(diametre_arbre, 'shaft', 'arbre', 'g', 6)
        limites_arbre = st.empty()
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
    if thermique:
        try:
            scenarios = {nom: calculer_thermique(r_reference, t0, t, alpha_h, alpha_s)
                         for nom, t in [('Nominal', t0), ('Hot', chaud), ('Cold', froid)]}
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
        choix = st.radio("Displayed condition", list(scenarios), horizontal=True, key='scenario')
        r = scenarios[choix]
        theme_fond, theme_accent = {'Nominal': ('#f1f5f9', '#475569'),
                                   'Hot': ('#fff7ed', '#c2410c'),
                                   'Cold': ('#eff6ff', '#1d4ed8')}[choix]
        st.markdown(f'<div style="padding:6px 12px;margin:0 0 6px;border-left:5px solid {theme_accent};border-radius:8px;background:{theme_fond};color:{theme_accent};font-weight:700">{choix} · {float(r["temperature"]):g} °C</div>', unsafe_allow_html=True)
    else:
        theme_fond, theme_accent = '#f8fafc', '#64748b' 

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

    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 390" role="img" aria-label="Shaft and hole cross-sections at both limit conditions">'
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
        if jeu < 0:
            svg += f'<circle cx="{cx}" cy="160" r="{(rh+rs)/2}" fill="none" stroke="#ef4444" stroke-opacity="0.7" stroke-width="{rs-rh}"/>'
            svg += f'<circle cx="{cx}" cy="160" r="{rh}" fill="none" stroke="#2563eb" stroke-dasharray="4 3"/>'
        svg += f'<path d="M {cx-117} 160 H {cx+117} M {cx} 43 V 277" fill="none" stroke="#64748b" stroke-width="0.8" stroke-dasharray="5 5"/>'
        svg += f'<text x="{cx}" y="155" text-anchor="middle" font-size="16" fill="#115e59">Shaft {arbre}</text>'
        svg += f'<text x="{cx}" y="176" text-anchor="middle" font-size="14" fill="#115e59">Ø {ds:.3f} mm</text>'
        svg += f'<text x="{cx}" y="298" text-anchor="middle" font-size="14" fill="#1d4ed8">Hole {alesage} · Ø {dh:.3f} mm</text>'
        svg += f'<text x="{cx}" y="321" text-anchor="middle" font-size="13" fill="{couleur}">{"Overlap before assembly" if jeu < 0 else "Clearance between shaft and hole"}</text>'
    svg += '<rect x="125" y="352" width="14" height="14" fill="#bfdbfe" stroke="#2563eb"/><text x="146" y="364" font-size="13">Hub</text>'
    svg += '<rect x="270" y="352" width="14" height="14" fill="#5eead4" stroke="#0f766e"/><text x="291" y="364" font-size="13">Shaft</text>'
    svg += '<rect x="405" y="352" width="14" height="14" fill="#ef4444"/><text x="426" y="364" font-size="13">Interference</text></g></svg>'
    st.image(svg, use_container_width=True)
    st.caption("Min./Max. values are diametral; radial clearance is half this value. Red shows theoretical overlap before assembly; deformation is not calculated.")
    if thermique:
        with st.expander("Thermal comparison — nominal / hot / cold", expanded=False):
            st.table([{
                "Condition": nom, "Temperature (°C)": float(cas['temperature']),
                "Min. (µm)": f"{cas['jeu_min_um']:.0f}",
                "Max. (µm)": f"{cas['jeu_max_um']:.0f}",
                "Type": fit_type(cas['type']),
            } for nom, cas in scenarios.items()])
    with st.expander("Limit dimensions and size ranges"):
        st.table(rows)
        st.caption(f"Hole range: {r['plage']} · Shaft range: {r['plage_arbre']}")
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=';')
    writer.writerow(['Hole diameter at nominal T (mm)', str(r_reference['d_alesage'])])
    writer.writerow(['Shaft diameter at nominal T (mm)', str(r_reference['d_arbre'])])
    if thermique:
        writer.writerow(['Nominal T (°C)', t0])
        writer.writerow(['Hole material', {'Acier':'Steel','Alu':'Aluminium','Titane':'Titanium','Inox':'Stainless steel'}[st.session_state['materiau_alesage']], 'Alpha (µm/m/K)', alpha_h])
        writer.writerow(['Shaft material', {'Acier':'Steel','Alu':'Aluminium','Titane':'Titanium','Inox':'Stainless steel'}[st.session_state['materiau_arbre']], 'Alpha (µm/m/K)', alpha_s])
        writer.writerow(['Condition', 'Temperature (°C)', 'Min (µm)', 'Max (µm)', 'Type'])
        for nom, cas in scenarios.items():
            writer.writerow([nom, cas['temperature'], f"{cas['jeu_min_um']:.0f}", f"{cas['jeu_max_um']:.0f}", fit_type(cas['type'])])
        writer.writerow(['Detailed dimensions: displayed condition', choix])
    writer.writerow(rows[0].keys())
    writer.writerows(row.values() for row in rows)
    writer.writerow(['Min. difference (µm)', f"{r['jeu_min_um']:.0f}"])
    writer.writerow(['Max. difference (µm)', f"{r['jeu_max_um']:.0f}"])
    st.download_button("Export results as CSV", buffer.getvalue().encode('utf-8-sig'),
                       file_name="fit_results.csv", mime="text/csv")
