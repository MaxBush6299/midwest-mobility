import math

# palette (matches deck)
NAVY="#0B2942"; AZURE="#1B6CA8"; TEAL="#2A9D8F"; AMBER="#E9A23B"
LIGHT="#F4F7FB"; CARD="#FFFFFF"; INK="#16242F"; MUTED="#5A6B7B"; LINE="#DCE5EF"
AZ_SOFT="#E7F0F8"; TE_SOFT="#E4F2EF"

W,H=1440,1660

# two ring centers (stacked vertically)
cxr=720
cy_top=470
cy_bot=1080
ring_r=330        # radius nodes sit on
nr=86             # node radius
ncore=104         # orchestrator radius
cx_core, cy_core = cxr, (cy_top+cy_bot)//2  # orchestrator between rings

plant=[("EHS","guarding · incidents"),("Maintenance","PM · work orders"),
       ("Quality","NCR/CAPA · specs"),("Shift Ops","changeover · handover"),
       ("Training","LOTO · competency")]
ent=[("Supply Chain","suppliers · logistics"),("Procurement","POs · contracts"),
     ("Engineering","ECO · part numbers"),("Quality","warranty · recall"),
     ("Demand","programs · allocation")]

def pos(cx,cy,r,deg):
    a=math.radians(deg); return cx+r*math.cos(a), cy+r*math.sin(a)

svg=[]
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Trebuchet MS, sans-serif">')
svg.append(f'<rect width="{W}" height="{H}" fill="{LIGHT}"/>')
svg.append(f'<rect x="0" y="0" width="{W}" height="8" fill="{AMBER}"/>')

# title
svg.append(f'<text x="80" y="86" font-size="40" font-weight="700" fill="{INK}">The MMC agent network</text>')
svg.append(f'<text x="80" y="126" font-size="20" fill="{MUTED}">One orchestrator \u00b7 two tiers \u00b7 ten specialists</text>')

# node angles: 5 around each ring, evenly spaced starting at top (-90)
angs=[-90+i*72 for i in range(5)]

def ring_band(cx,cy,color,fill):
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{ring_r}" fill="{fill}" stroke="{color}" stroke-width="2" stroke-dasharray="3 9"/>')

# connectors core -> each node (drawn first)
def connectors(cx,cy,color,dashed):
    da='stroke-dasharray="2 7"' if dashed else ''
    for d in angs:
        x,y=pos(cx,cy,ring_r,d)
        # from core edge toward node
        dx,dy=x-cx_core,y-cy_core
        dist=math.hypot(dx,dy)
        sx=cx_core+dx/dist*(ncore-6); sy=cy_core+dy/dist*(ncore-6)
        ex=x-dx/dist*(nr-4); ey=y-dy/dist*(nr-4)
        svg.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{color}" stroke-width="2.4" opacity="0.5" {da}/>')

# bands
ring_band(cxr,cy_top,AZURE,AZ_SOFT)
ring_band(cxr,cy_bot,TEAL,TE_SOFT)

# connectors
connectors(cxr,cy_top,AZURE,False)
connectors(cxr,cy_bot,TEAL,True)

def node(x,y,fill,stroke,name,role):
    svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{nr}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>')
    svg.append(f'<text x="{x:.1f}" y="{y-4:.1f}" font-size="20" font-weight="700" fill="#FFFFFF" text-anchor="middle">{name}</text>')
    svg.append(f'<text x="{x:.1f}" y="{y+20:.1f}" font-size="13" fill="#E8F1F8" text-anchor="middle">{role}</text>')

# top ring nodes (plant – azure)
for d,(nm,rl) in zip(angs,plant):
    x,y=pos(cxr,cy_top,ring_r,d); node(x,y,AZURE,"#0F548A",nm,rl)
# bottom ring nodes (enterprise – teal)
for d,(nm,rl) in zip(angs,ent):
    x,y=pos(cxr,cy_bot,ring_r,d); node(x,y,TEAL,"#1F7468",nm,rl)

# tier labels (pills) to the right of each ring center
def tier_pill(cx,cy,txt,fill):
    w=len(txt)*12.2+44
    x=cx+ring_r+90
    svg.append(f'<rect x="{x-w/2:.0f}" y="{cy-22:.0f}" width="{w:.0f}" height="44" rx="22" fill="{fill}"/>')
    svg.append(f'<text x="{x:.0f}" y="{cy+7:.0f}" font-size="17" font-weight="700" fill="#FFFFFF" text-anchor="middle" letter-spacing="1.5">{txt}</text>')
tier_pill(cxr,cy_top,"PLANT TIER",AZURE)
tier_pill(cxr,cy_bot,"ENTERPRISE TIER",TEAL)

# orchestrator core between rings
svg.append(f'<circle cx="{cx_core}" cy="{cy_core}" r="{ncore}" fill="{NAVY}" stroke="{AMBER}" stroke-width="4"/>')
svg.append(f'<text x="{cx_core}" y="{cy_core-16}" font-size="21" font-weight="700" fill="#FFFFFF" text-anchor="middle">Magentic</text>')
svg.append(f'<text x="{cx_core}" y="{cy_core+11}" font-size="21" font-weight="700" fill="#FFFFFF" text-anchor="middle">Orchestrator</text>')
svg.append(f'<text x="{cx_core}" y="{cy_core+37}" font-size="13" fill="{AMBER}" text-anchor="middle">plan \u00b7 dispatch \u00b7 replan</text>')

# legend (bottom)
ly=H-70
svg.append(f'<circle cx="120" cy="{ly}" r="14" fill="{AZURE}"/>')
svg.append(f'<text x="146" y="{ly+6}" font-size="17" fill="{INK}">Plant agents \u2014 mmc-plant (top ring)</text>')
svg.append(f'<circle cx="640" cy="{ly}" r="14" fill="{TEAL}"/>')
svg.append(f'<text x="666" y="{ly+6}" font-size="17" fill="{INK}">Enterprise agents \u2014 mmc-enterprise (bottom ring)</text>')

svg.append('</svg>')
svg="".join(svg)

html=f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:{LIGHT};}}</style></head><body>{svg}</body></html>'
open("agent-rings.html","w",encoding="utf-8").write(html)
open("agent-rings.svg","w",encoding="utf-8").write(svg)
print("wrote agent-rings.html/.svg", W, H)
