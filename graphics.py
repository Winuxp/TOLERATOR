"""SVG view of the same Lamé corner cases used by the calculation engine."""
from html import escape
from math import cos, sin, pi


def lame_graphic(result, after=True, background='#f8fafc', accent='#64748b'):
    """Monotone radial mapping exaggerates the interface without crossing walls.

    All free and loaded surfaces in both views use one common radial mapping.
    Show the actual minimum/maximum interference corners, not mixed envelopes.
    """
    cases=result['cases']
    selected=[min(cases,key=lambda c:c['interference_um']),
              max(cases,key=lambda c:c['interference_um'])]
    reference=sum(c['hole_free_mm'] for c in cases)/len(cases)
    top=max(c[k] for c in cases for k in ('hub_outer_free_mm','hub_outer_loaded_mm'))
    # Magnify a narrow interval around DN, keep the rest of both walls readable.
    # This shared continuous monotone map preserves surface ordering and contact.
    spread=max(.001, max(abs(c[k]-reference) for c in cases
                          for k in ('hole_free_mm','shaft_free_mm'))*1.1)
    band=min(spread,reference*.45,(top-reference)*.45)
    def radius(d):
        if d <= reference-band:
            return 47*d/(reference-band)
        if d <= reference+band:
            return 47+36*(d-reference+band)/(2*band)
        return 83+26*(d-reference-band)/(top-reference-band)
    def circle(cx,r,fill,stroke,width=2,dash=''):
        return f'<circle cx="{cx}" cy="158" r="{r:.6f}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"'+(' stroke-dasharray="5 4"' if dash else '')+'/>'
    def text(cx,y,label,size=13,color='#334155',bold=False):
        return f'<text x="{cx}" y="{y}" text-anchor="middle" font-size="{size}" fill="{color}"'+(' font-weight="700"' if bold else '')+'>'+escape(label)+'</text>'
    state='After assembly' if after else 'Before assembly'
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 438" role="img" aria-label="Lamé {state}: minimum and maximum interference cases"><rect x="1" y="1" width="678" height="436" rx="12" fill="{background}" stroke="{accent}"/><g font-family="Arial,sans-serif">'
    for cx,title,c in zip((175,505),('Minimum interference','Maximum interference'),selected):
        loaded=after and c['pressure_mpa']>0
        h=c['hole_loaded_mm'] if after else c['hole_free_mm']
        s=c['shaft_loaded_mm'] if after else c['shaft_free_mm']
        od=c['hub_outer_loaded_mm'] if after else c['hub_outer_free_mm']
        bore=c['shaft_inner_loaded_mm'] if after else c['shaft_inner_free_mm']
        svg+=text(cx,26,title,16,bold=True)
        svg+=text(cx,46,f"Initial interference: {c['interference_um']:.0f} µm",12)
        svg+=circle(cx,radius(od),'#bfdbfe','#2563eb')
        svg+=circle(cx,radius(h),'white','#2563eb')
        svg+=circle(cx,radius(s),'#5eead4','#0f766e')
        if bore>0:svg+=circle(cx,radius(bore),'white','#0f766e')
        if not after and c['pressure_mpa']>0:
            a,b=radius(h),radius(s)
            svg+=circle(cx,(a+b)/2,'none','#ef4444',max(.2,b-a))
        if loaded:
            # Free surfaces are ghost outlines; loaded contact is one common ring.
            for key,color in [('hub_outer_free_mm','#2563eb'),('hole_free_mm','#2563eb'),
                              ('shaft_free_mm','#0f766e'),('shaft_inner_free_mm','#0f766e')]:
                if c[key]>0:svg+=circle(cx,radius(c[key]),'none',color,1,'dash')
            rc=radius(c['contact_diameter_mm'])
            svg+=circle(cx,rc,'none','#b45309',3)
            # Paired radial arrows at two interface positions: hub outward / shaft inward.
            for angle in (pi/4,5*pi/4):
                for start,end in ((rc+4,rc+16),(rc-4,rc-16)):
                    x1,y1=cx+start*cos(angle),158+start*sin(angle)
                    x2,y2=cx+end*cos(angle),158+end*sin(angle)
                    dx,dy=x2-x1,y2-y1
                    norm=(dx*dx+dy*dy)**.5;ux,uy=dx/norm,dy/norm
                    svg+=f'<path d="M{x1:.2f} {y1:.2f}L{x2:.2f} {y2:.2f}M{x2-5*ux+3*uy:.2f} {y2-5*uy-3*ux:.2f}L{x2:.2f} {y2:.2f}L{x2-5*ux-3*uy:.2f} {y2-5*uy+3*ux:.2f}" fill="none" stroke="#b45309" stroke-width="1.5"/>'
        svg+=f'<path d="M{cx-116} 158H{cx+116}M{cx} 58V274" stroke="#64748b" stroke-width=".7" stroke-dasharray="5 5"/>'
        if loaded:
            svg+=text(cx,294,f"Contact · p = {c['pressure_mpa']:.1f} MPa",15,'#92400e',True)
            svg+=text(cx,316,f"DN = {c['contact_diameter_mm']:.3f} mm",14)
        elif after:
            svg+=text(cx,294,'No contact — p = 0.0 MPa',15,'#15803d',True)
            svg+=text(cx,316,f"Hole {h:.3f} / Shaft {s:.3f} mm",13)
        else:
            svg+=text(cx,294,'Free parts · theoretical overlap' if c['pressure_mpa']>0 else 'Free parts · no interference',14)
            svg+=text(cx,316,f"Hole {h:.3f} / Shaft {s:.3f} mm",13)
        svg+=text(cx,338,f'D1 = {od:.3f} mm · d2 = {bore:.3f} mm',13)
    svg+=text(340,372,state,15,bold=True)
    svg+='<rect x="83" y="390" width="12" height="12" fill="#bfdbfe" stroke="#2563eb"/>'+text(120,401,'Hub',12)
    svg+='<rect x="169" y="390" width="12" height="12" fill="#5eead4" stroke="#0f766e"/>'+text(211,401,'Shaft',12)
    if after:
        svg+='<path d="M268 396H296" stroke="#2563eb" stroke-dasharray="5 4"/>'+text(357,401,'Free outlines',12)
        svg+='<path d="M435 396H459" stroke="#b45309" stroke-width="3"/>'+text(522,401,'Contact',12)
    else:
        svg+='<path d="M283 396H307" stroke="#ef4444" stroke-width="5"/>'+text(380,401,'Interference',12)
    svg+=text(340,423,'Schematic radial scale · small diameter differences exaggerated',12,'#64748b')
    return svg+'</g></svg>'
