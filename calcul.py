"""ISO 286-2 lookup, up to 500 mm. Diameters: mm; deviations: µm."""
from decimal import Decimal, InvalidOperation
from pathlib import Path
import json
import re

DATA = json.loads(Path(__file__).with_name('iso286_data.json').read_text(encoding='utf-8'))

def cle_classe(classe):
    m = re.fullmatch(r'([A-Za-z]+)([0-9]+)', classe)
    return (m[1], int(m[2]))

ALESAGES = tuple(sorted((c for c in DATA['classes'] if c[0].isupper()), key=cle_classe))
ARBRES = tuple(sorted((c for c in DATA['classes'] if c[0].islower()), key=cle_classe))

def dimension(valeur):
    try:
        d = Decimal(str(valeur).replace(',', '.'))
    except InvalidOperation:
        raise ValueError('Diameter must be numeric.') from None
    if not d.is_finite() or not 0 < d <= 500:
        raise ValueError('Diameter must satisfy 0 < d ≤ 500 mm.')
    return d

def chercher(d, classe):
    for row in DATA['classes'].get(classe, []):
        if Decimal(row['low']) < d <= Decimal(row['high']):
            return row
    raise ValueError(f'{classe} is not tabulated for diameter {d} mm.')

def classes_disponibles(diametre, piece='hole'):
    d = dimension(diametre)
    if piece not in ('hole', 'shaft'):
        raise ValueError('Part must be hole or shaft.')
    catalogue = ALESAGES if piece=='hole' else ARBRES
    return tuple(c for c in catalogue if any(Decimal(row['low']) < d <= Decimal(row['high'])
                                            for row in DATA['classes'][c]))

def calculer(diametre, arbre='g6', alesage='H7', diametre_arbre=None):
    """Independent nominal diameters; default: same nominal for both parts."""
    dh = dimension(diametre)
    ds = dh if diametre_arbre is None else dimension(diametre_arbre)
    if alesage not in ALESAGES:
        raise ValueError(f'Unknown hole tolerance: {alesage}.')
    if arbre not in ARBRES:
        raise ValueError(f'Unknown shaft tolerance: {arbre}.')
    hole, shaft = chercher(dh, alesage), chercher(ds, arbre)
    EI, ES = Decimal(hole['lower']), Decimal(hole['upper'])
    ei, es = Decimal(shaft['lower']), Decimal(shaft['upper'])
    hmin, hmax = dh + EI/1000, dh + ES/1000
    smin, smax = ds + ei/1000, ds + es/1000
    if min(hmin, smin) <= 0:
        raise ValueError('Selected tolerance gives a non-positive diameter; choose a larger nominal or a finer grade.')
    jmin, jmax = (hmin-smax)*1000, (hmax-smin)*1000
    if jmin >= 0:
        nature = 'Avec jeu (jeu minimal nul possible)' if jmin == 0 else 'Avec jeu'
    elif jmax <= 0:
        nature = 'Avec serrage (serrage minimal nul possible)' if jmax == 0 else 'Avec serrage'
    else:
        nature = 'Incertain (jeu ou serrage)'
    return dict(d=dh, d_alesage=dh, d_arbre=ds, arbre=arbre, alesage=alesage,
                plage=f"]{hole['low']} ; {hole['high']}] mm",
                plage_arbre=f"]{shaft['low']} ; {shaft['high']}] mm",
                EI=EI, ES=ES, ei=ei, es=es, alesage_min=hmin, alesage_max=hmax,
                arbre_min=smin, arbre_max=smax, jeu_min_um=jmin, jeu_max_um=jmax,
                source_page_alesage=hole['table_page'], source_page_arbre=shaft['table_page'],
                type=nature)

# Valeurs indicatives en µm/(m·K), à adapter à la nuance et à la plage thermique.
MATERIAUX = {'Acier': 12.0, 'Alu': 23.0, 'Titane': 8.4, 'Inox': 17.0}

def calculer_thermique(reference, temperature_nominale, temperature,
                       alpha_alesage, alpha_arbre):
    """Dilatation libre : D(T)=D(T0)*(1+alpha*1e-6*(T-T0)).

    Les limites ISO sont déterminées une seule fois à T0, puis dilatées.
    Les deux pièces sont supposées à la même température de service.
    """
    def decimal_fini(v):
        try:
            d = Decimal(str(v).replace(',', '.'))
        except InvalidOperation:
            raise ValueError('Paramètre thermique non numérique.') from None
        if not d.is_finite():
            raise ValueError('Paramètre thermique non fini.')
        return d
    t0, t, ah, ass = map(decimal_fini,
                        (temperature_nominale, temperature, alpha_alesage, alpha_arbre))
    if min(t0, t) < Decimal('-273.15'):
        raise ValueError('Température inférieure au zéro absolu.')
    fh = 1 + ah * Decimal('0.000001') * (t-t0)
    fs = 1 + ass * Decimal('0.000001') * (t-t0)
    if min(fh, fs) <= 0:
        raise ValueError('Facteur de dilatation non positif : vérifier les paramètres.')
    r = reference.copy()
    for k in ('d', 'd_alesage', 'alesage_min', 'alesage_max'):
        r[k] *= fh
    for k in ('d_arbre', 'arbre_min', 'arbre_max'):
        r[k] *= fs
    for k in ('EI', 'ES'): r[k] = Decimal(r[k])*fh
    for k in ('ei', 'es'): r[k] = Decimal(r[k])*fs
    r['jeu_min_um'] = (r['alesage_min']-r['arbre_max'])*1000
    r['jeu_max_um'] = (r['alesage_max']-r['arbre_min'])*1000
    r['type'] = ('Avec jeu' if r['jeu_min_um'] >= 0 else
                 'Avec serrage' if r['jeu_max_um'] <= 0 else 'Incertain (jeu ou serrage)')
    r.update(temperature=t, temperature_nominale=t0, alpha_alesage=ah, alpha_arbre=ass)
    return r
