"""Lamé press fit: free-ended, isotropic linear-elastic cylinders (sigma_z=0).

Inputs: mm, GPa, dimensionless Poisson/friction. Outputs: MPa, mm, N, N.m.
Zero external hub pressure / internal shaft pressure; uniform interface pressure.
Reference: https://mechanics.ju.se/MachineElements/shaft-hub.html
The two unloaded limit diameters are retained in their respective compliances.
"""
from itertools import product
from math import isfinite, pi, sqrt, ceil, floor

ELASTIC_PRESETS = {
    'Acier': {'young_gpa': 210.0, 'poisson': 0.30},
    'Alu': {'young_gpa': 70.0, 'poisson': 0.33},
    'Titane': {'young_gpa': 110.0, 'poisson': 0.34},
    'Inox': {'young_gpa': 193.0, 'poisson': 0.30},
}


def finite(value, label):
    try:
        result = float(value)
    except (ValueError, TypeError, OverflowError):
        raise ValueError(f'{label} must be numeric.') from None
    if not isfinite(result):
        raise ValueError(f'{label} must be finite.')
    return result


def solve_case(hole_d, shaft_d, hub_outer, shaft_inner, young_h_gpa,
               poisson_h, young_s_gpa, poisson_s, contact_length, friction):
    """Solve one pair of unloaded diameters at the service temperature.

    Diameter changes are 2u from the open-ended Lamé radial-displacement law.
    The pressure enforces equality of the loaded shaft and hole diameters.
    Friction force is the fully engaged, uniform-pressure press-in estimate.
    """
    h, s, od, id_, eh, nh, es, ns, length, mu = [
        finite(v, label) for v, label in zip(
            (hole_d, shaft_d, hub_outer, shaft_inner, young_h_gpa, poisson_h,
             young_s_gpa, poisson_s, contact_length, friction),
            ('Hole diameter', 'Shaft diameter', 'Hub outer diameter',
             'Shaft inner diameter', 'Hub Young modulus', 'Hub Poisson ratio',
             'Shaft Young modulus', 'Shaft Poisson ratio', 'Contact length', 'Friction'))]
    if min(h, s) <= 0:
        raise ValueError('Unloaded interface diameters must be positive.')
    if od <= h:
        raise ValueError('Hub outer diameter must exceed the maximum free hole diameter.')
    if not 0 <= id_ < s:
        raise ValueError('Shaft inner diameter must satisfy 0 ≤ inner Ø < minimum free shaft Ø.')
    if min(eh, es) <= 0:
        raise ValueError('Young moduli must be positive.')
    if not (-1 < nh < 0.5 and -1 < ns < 0.5):
        raise ValueError('Poisson ratios must satisfy -1 < ν < 0.5.')
    if length <= 0 or mu < 0:
        raise ValueError('Contact length must be positive and friction non-negative.')
    eh *= 1000  # GPa -> MPa = N/mm²
    es *= 1000
    ch = h / eh * ((od**2+h**2)/(od**2-h**2) + nh)
    cs = s / es * ((s**2+id_**2)/(s**2-id_**2) - ns)
    interference = s-h
    pressure = max(0.0, interference/(ch+cs))
    hole_loaded = h + pressure*ch
    shaft_loaded = s - pressure*cs
    contact_d = (hole_loaded+shaft_loaded)/2 if pressure > 0 else None
    hub_outer_loaded = od + 2*pressure*h*h*od/(eh*(od*od-h*h))
    shaft_inner_loaded = id_ - 2*pressure*s*s*id_/(es*(s*s-id_*id_))
    if shaft_inner_loaded < 0:
        raise ValueError('Predicted shaft bore collapse: this case is outside the small-strain elastic model.')
    area = pi*contact_d*length if contact_d is not None else 0.0
    force = mu*pressure*area
    torque = force*contact_d/2000 if contact_d is not None else 0.0  # N.mm -> N.m
    strain = max(abs(hole_loaded/h-1), abs(shaft_loaded/s-1),
                 abs(hub_outer_loaded/od-1), abs(shaft_inner_loaded/id_-1) if id_ else 0)
    # Open ends: sigma_z=0. Hub maximum is at the bore; hollow shaft
    # maximum is at its inner wall. Solid shaft has sigma_r=sigma_theta=-p.
    hoop_h = pressure*(od*od+h*h)/(od*od-h*h)
    vm_h = sqrt(hoop_h*hoop_h + pressure*pressure + hoop_h*pressure)
    vm_s = 2*pressure*s*s/(s*s-id_*id_) if id_ else pressure
    result = dict(hub_stress_vm_mpa=vm_h, shaft_stress_vm_mpa=vm_s, hole_free_mm=h, shaft_free_mm=s, hub_outer_free_mm=od,
                  shaft_inner_free_mm=id_, interference_um=interference*1000,
                  pressure_mpa=pressure, contact_diameter_mm=contact_d,
                  hole_loaded_mm=hole_loaded, shaft_loaded_mm=shaft_loaded,
                  hub_outer_loaded_mm=hub_outer_loaded, shaft_inner_loaded_mm=shaft_inner_loaded,
                  press_force_n=force, torque_nm=torque, max_surface_strain=strain,
                  hub_diametral_compliance_mm_per_mpa=ch, shaft_diametral_compliance_mm_per_mpa=cs)
    if any(not isfinite(v) for v in result.values() if v is not None):
        raise ValueError('Numerical overflow: check geometry and material inputs.')
    return result


def calculer_lame_intervalle(fit, hub_outer_mm, shaft_inner_mm, young_h_gpa,
                            poisson_h, young_s_gpa, poisson_s,
                            contact_length_mm, friction):
    """Evaluate all four hole/shaft tolerance corners, then return envelopes.

    OD and ID are free dimensions at the nominal reference temperature.
    They follow their material's thermal factor when fit contains thermal data.
    Contact length is supplied at service temperature (not auto-expanded).
    E, nu and mu are taken constant over the specified temperature range.
    """
    od = finite(hub_outer_mm, 'Hub outer diameter')
    id_ = finite(shaft_inner_mm, 'Shaft inner diameter')
    if 'temperature' in fit:
        dt = float(fit['temperature']-fit['temperature_nominale'])
        od *= 1+float(fit['alpha_alesage'])*1e-6*dt
        id_ *= 1+float(fit['alpha_arbre'])*1e-6*dt
    cases = []
    for htag, stag in product(('min','max'), repeat=2):
        case = solve_case(fit['alesage_'+htag], fit['arbre_'+stag], od, id_,
                          young_h_gpa, poisson_h, young_s_gpa, poisson_s,
                          contact_length_mm, friction)
        case['case'] = f'Hole {htag} / shaft {stag}'
        cases.append(case)
    keys = ('hub_stress_vm_mpa', 'shaft_stress_vm_mpa', 'pressure_mpa', 'press_force_n', 'torque_nm', 'hole_loaded_mm',
            'shaft_loaded_mm', 'hub_outer_loaded_mm', 'shaft_inner_loaded_mm')
    bounds = {key: (min(c[key] for c in cases), max(c[key] for c in cases)) for key in keys}
    contact = [c['contact_diameter_mm'] for c in cases if c['contact_diameter_mm'] is not None]
    bounds['contact_diameter_mm'] = (min(contact), max(contact)) if contact else (None, None)
    return dict(bounds=bounds, cases=cases, contact_guaranteed=all(c['pressure_mpa']>0 for c in cases),
                has_contact=bool(contact), hub_outer_free_mm=od, shaft_inner_free_mm=id_,
                contact_length_mm=float(contact_length_mm), friction=float(friction),
                max_surface_strain=max(c['max_surface_strain'] for c in cases))

MODEL_README = r"""## Lamé elastic press-fit model

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

"""


def thermal_assembly(fit, reference_temperature, alpha_h, alpha_s,
                     target_clearance_um, hub_temperature, shaft_temperature):
    """Worst tolerance corner, free parts at independent uniform temperatures.

    Heating-only/cooling-only recommendations round outward to whole degrees.
    No mechanical contact is applied before assembly. Alpha in µm/m/K.
    """
    t0, ah, ass, target, th, ts = [finite(v, n) for v, n in zip(
        (reference_temperature, alpha_h, alpha_s, target_clearance_um,
         hub_temperature, shaft_temperature),
        ('Reference temperature','Hub alpha','Shaft alpha','Target clearance',
         'Hub temperature','Shaft temperature'))]
    if min(t0, th, ts) < -273.15 or target < 0:
        raise ValueError('Temperatures must be ≥ −273.15 °C and clearance non-negative.')
    if ah < 0 or ass < 0:
        raise ValueError('Assembly heating/cooling recommendations require non-negative expansion coefficients.')
    h, shaft = float(fit['alesage_min']), float(fit['arbre_max'])
    target /= 1000
    def clearance(hot, cold):
        fh, fs = 1+ah*1e-6*(hot-t0), 1+ass*1e-6*(cold-t0)
        if min(fh,fs) <= 0:
            raise ValueError('Thermal diameter factors must be positive.')
        return h*fh-shaft*fs
    def required_hot(cold):
        missing = target-clearance(t0,cold)
        return ceil(t0+max(0,missing)/(h*ah*1e-6)-1e-9) if ah else (ceil(t0) if missing<=0 else None)
    def required_cold(hot):
        missing = target-clearance(hot,t0)
        value = floor(t0-max(0,missing)/(shaft*ass*1e-6)+1e-9) if ass else (floor(t0) if missing<=0 else None)
        return value if value is not None and value >= -273.15 else None
    gap = clearance(th,ts)
    return dict(clearance_um=gap*1000, target_um=target*1000,
                assembly_possible=gap >= target-1e-12,
                hub_hot_only_c=required_hot(t0), shaft_cold_only_c=required_cold(t0),
                hub_required_c=required_hot(ts), shaft_required_c=required_cold(th))
