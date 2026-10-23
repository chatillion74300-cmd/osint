"""Plan SVG du carré de Jupiter (Agrippa, De occulta philosophia II, 22). Tous les nombres sont calculés."""
import sys

SQ = [[4, 14, 15, 1], [9, 7, 6, 12], [5, 11, 10, 8], [16, 2, 3, 13]]
N = 4
rows = [sum(r) for r in SQ]
cols = [sum(SQ[r][c] for r in range(N)) for c in range(N)]
d1 = sum(SQ[i][i] for i in range(N)); d2 = sum(SQ[i][N - 1 - i] for i in range(N))
total = sum(rows)
assert sorted(v for r in SQ for v in r) == list(range(1, 17))
assert set(rows + cols + [d1, d2]) == {34} and total == 136

# Gématrie hébraïque : Iophiel יהפיאל, Hismael הסמאל
IOPHIEL = [("Y", "י", 10), ("H", "ה", 5), ("P", "פ", 80), ("Y", "י", 10), ("A", "א", 1), ("L", "ל", 30)]
HISMAEL = [("H", "ה", 5), ("S", "ס", 60), ("M", "מ", 40), ("A", "א", 1), ("L", "ל", 30)]
assert sum(v for *_, v in IOPHIEL) == 136 and sum(v for *_, v in HISMAEL) == 136
# Réduction (Aiq Beker) pour tracer sur un carré 1–16 : on retire les zéros
reduce = lambda v: v if v <= 16 else int(str(v).rstrip("0"))
path_vals = [reduce(v) for *_, v in IOPHIEL]  # 10,5,8,10,1,3

BG, INK, DIM, ACC = "#0b4a7a", "#ffffff", "#9cc3e4", "#ffd479"
W, H = 1600, 900
o = []
a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
  'font-family="DejaVu Sans, Arial, sans-serif">')
a('<title>Plan du carré de Jupiter</title>')
a('<defs><pattern id="g" width="20" height="20" patternUnits="userSpaceOnUse">'
  f'<path d="M20 0H0V20" fill="none" stroke="{DIM}" stroke-opacity=".12"/></pattern>'
  f'<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
  f'<path d="M0 0L10 5L0 10z" fill="{ACC}"/></marker></defs>')
a(f'<rect width="{W}" height="{H}" fill="{BG}"/><rect width="{W}" height="{H}" fill="url(#g)"/>')
a(f'<rect x="20" y="20" width="{W-40}" height="{H-40}" fill="none" stroke="{INK}" stroke-width="3"/>')
a(f'<rect x="30" y="30" width="{W-60}" height="{H-60}" fill="none" stroke="{INK}" stroke-width="1"/>')

def text(x, y, s, size=16, fill=INK, anchor="start", weight="normal", extra=""):
    a(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
      f'font-weight="{weight}" {extra}>{s}</text>')

def panel(x, y, w, h, title):
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="1.5"/>')
    a(f'<rect x="{x}" y="{y}" width="{w}" height="30" fill="{INK}" fill-opacity=".1"/>')
    text(x + 12, y + 21, title, 15, weight="bold")

# --- Titre
text(W / 2, 72, "PLAN DU CARRÉ DE JUPITER (ORDRE 4)", 30, anchor="middle", weight="bold")
text(W / 2, 100, "d’après H. C. Agrippa, De occulta philosophia, livre II, chap. 22 (Cologne, 1533)",
     16, DIM, "middle")

# --- Panneau 1 : carré magique avec sommes
px, py, pw, ph = 50, 125, 520, 560
panel(px, py, pw, ph, "1. CARRÉ DE JUPITER — CONSTANTE 34")
cell = 80; gx, gy = px + 90, py + 75
for r in range(N):
    for c in range(N):
        x, y = gx + c * cell, gy + r * cell
        a(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="none" stroke="{INK}" stroke-width="2"/>')
        text(x + cell / 2, y + cell / 2 + 12, SQ[r][c], 34, anchor="middle", weight="bold")
    text(gx + N * cell + 14, gy + r * cell + cell / 2 + 6, f"= {rows[r]}", 18, ACC)
for c in range(N):
    text(gx + c * cell + cell / 2, gy + N * cell + 28, f"{cols[c]}", 18, ACC, "middle")
text(gx - 12, gy + N * cell + 28, "Σ", 18, ACC, "end")
a(f'<line x1="{gx}" y1="{gy}" x2="{gx+N*cell}" y2="{gy+N*cell}" stroke="{ACC}" stroke-dasharray="6 6" stroke-opacity=".6"/>')
a(f'<line x1="{gx+N*cell}" y1="{gy}" x2="{gx}" y2="{gy+N*cell}" stroke="{ACC}" stroke-dasharray="6 6" stroke-opacity=".6"/>')
text(gx - 6, gy - 8, f"{d1} ↘", 16, ACC, "end")
text(gx + N * cell + 6, gy - 8, f"↙ {d2}", 16, ACC)
ty = gy + N * cell + 62
for line in [
    "Nombres 1 à 16, chacun une seule fois.",
    "4 lignes, 4 colonnes, 2 diagonales : toutes = 34.",
    f"Somme totale : 1 + 2 + … + 16 = {total}.",
    "Constante d’un carré d’ordre n : n(n²+1)/2 = 4·17/2 = 34.",
]:
    text(px + 20, ty, line, 15); ty += 24

# --- Panneau 2 : tracé du nom Iophiel
qx, qy, qw, qh = 590, 125, 450, 560
panel(qx, qy, qw, qh, "2. TRACÉ DU NOM « IOPHIEL » SUR LE CARRÉ")
cell2 = 72; hx, hy = qx + (qw - 4 * cell2) / 2, qy + 60
pos = {SQ[r][c]: (hx + c * cell2 + cell2 / 2, hy + r * cell2 + cell2 / 2) for r in range(N) for c in range(N)}
for r in range(N):
    for c in range(N):
        x, y = hx + c * cell2, hy + r * cell2
        a(f'<rect x="{x}" y="{y}" width="{cell2}" height="{cell2}" fill="none" stroke="{DIM}" stroke-width="1"/>')
        text(x + 8, y + 20, SQ[r][c], 13, DIM)
pts = [pos[v] for v in path_vals]
d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
a(f'<path d="{d}" fill="none" stroke="{ACC}" stroke-width="4" stroke-linejoin="round" marker-end="url(#ar)"/>')
sx, sy = pts[0]
a(f'<circle cx="{sx:.0f}" cy="{sy:.0f}" r="9" fill="none" stroke="{ACC}" stroke-width="4"/>')
steps = {}
for i, v in enumerate(path_vals, 1):
    steps.setdefault(v, []).append(str(i))
for v, ns in steps.items():
    x, y = pos[v]
    label = "·".join(ns)
    a(f'<rect x="{x-14:.0f}" y="{y+12:.0f}" width="{14+9*len(label):.0f}" height="20" rx="10" fill="{BG}" stroke="{ACC}"/>')
    text(x - 7, y + 27, label, 13, ACC, weight="bold")
ty = hy + 4 * cell2 + 34
text(qx + 20, ty, "Y-H-P-Y-A-L", 17, weight="bold")
text(qx + 200, ty, "יהפיאל", 19, weight="bold", extra='direction="rtl" unicode-bidi="embed"'); ty += 26
vals = " + ".join(str(v) for *_, v in IOPHIEL)
text(qx + 20, ty, f"Gématrie : {vals} = 136", 15); ty += 22
text(qx + 20, ty, "Réduction à 1–16 (zéros retirés) :", 15); ty += 22
text(qx + 20, ty, " → ".join(map(str, path_vals)), 15, ACC); ty += 30
for line in [
    "○ = départ · ▶ = arrivée · pastilles = ordre des étapes.",
    "Tracé reconstruit ici par la méthode de réduction ;",
    "ce n’est pas une copie du sceau gravé chez Agrippa.",
]:
    text(qx + 20, ty, line, 13, DIM); ty += 19

# --- Panneau 3 : correspondances
rx, ry, rw, rh = 1060, 125, 490, 360
panel(rx, ry, rw, rh, "3. CORRESPONDANCES TRADITIONNELLES")
items = [
    ("Planète", "♃ Jupiter"),
    ("Métal", "Étain (Sn)"),
    ("Jour", "Jeudi"),
    ("Heure", "1ʳᵉ heure après le lever du soleil le jeudi"),
    ("", "(heures planétaires, ordre chaldéen)"),
    ("Domiciles", "♐ Sagittaire · ♓ Poissons"),
    ("Exaltation", "♋ Cancer"),
    ("Intelligence", "Iophiel = 10+5+80+10+1+30 = 136"),
    ("", "HEB:יהפיאל"),
    ("Esprit", "Hismael = 5+60+40+1+30 = 136"),
    ("", "HEB:הסמאל"),
    ("Nombres", "4 · 16 · 34 · 136"),
]
ty = ry + 60
for k, v in items:
    text(rx + 18, ty, k, 15, DIM)
    if v.startswith("HEB:"):
        text(rx + 140, ty, v[4:], 16, anchor="end", extra='direction="rtl" unicode-bidi="embed"')
    else:
        text(rx + 140, ty, v, 15)
    ty += 26

# --- Panneau 4 : plaque d'étain (vue éclatée)
sx0, sy0, sw, sh = 1060, 495, 490, 190
panel(sx0, sy0, sw, sh, "4. PLAQUE D’ÉTAIN — VUE ÉCLATÉE")
def plate(cx, cy, w, h, depth, label):
    a(f'<path d="M{cx-w/2} {cy} L{cx} {cy-h/2} L{cx+w/2} {cy} L{cx} {cy+h/2} Z" fill="{BG}" stroke="{INK}" stroke-width="1.8"/>')
    a(f'<path d="M{cx-w/2} {cy} L{cx-w/2} {cy+depth} L{cx} {cy+h/2+depth} L{cx+w/2} {cy+depth} L{cx+w/2} {cy} '
      f'L{cx} {cy+h/2} Z" fill="{INK}" fill-opacity=".15" stroke="{INK}" stroke-width="1.2"/>')
    a(f'<line x1="{cx+w/2}" y1="{cy}" x2="{cx+w/2+40}" y2="{cy}" stroke="{DIM}"/>')
    text(cx + w / 2 + 46, cy + 5, label, 14)
plate(1180, 560, 150, 50, 7, "Face A : carré gravé (panneau 1)")
plate(1180, 627, 150, 50, 7, "Face B : nom / tracé (panneau 2)")
text(sx0 + 18, sy0 + 180, "Plaque carrée en étain, gravée des deux côtés.", 13, DIM)

# --- Bandeau du bas : vérifications + cartouche
by = 705
a(f'<rect x="50" y="{by}" width="990" height="160" fill="none" stroke="{INK}" stroke-width="1.5"/>')
text(68, by + 28, "VÉRIFICATIONS (calculées)", 15, weight="bold")
checks = [
    f"✓ Lignes : {' · '.join(map(str, rows))}",
    f"✓ Colonnes : {' · '.join(map(str, cols))}",
    f"✓ Diagonales : {d1} · {d2}",
    f"✓ Total : {total} = gématrie de Iophiel = gématrie de Hismael",
]
ty = by + 56
for line in checks:
    text(68, ty, line, 15, ACC); ty += 25
a(f'<rect x="1060" y="{by}" width="490" height="160" fill="none" stroke="{INK}" stroke-width="1.5"/>')
for i, (k, v) in enumerate([
    ("Objet", "Carré de Jupiter, ordre 4"),
    ("Source", "Agrippa, De occ. phil. II, 22"),
    ("Statut", "Plan symbolique et historique"),
    ("Note", "Efficacité magique non démontrée"),
]):
    yy = by + i * 40
    if i:
        a(f'<line x1="1060" y1="{yy}" x2="1550" y2="{yy}" stroke="{INK}"/>')
    text(1076, yy + 26, k.upper(), 13, DIM); text(1180, yy + 26, v, 15)
a(f'<line x1="1170" y1="{by}" x2="1170" y2="{by+160}" stroke="{INK}"/>')
a('</svg>')
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(o))
print("rows", rows, "cols", cols, "diag", d1, d2, "total", total, "path", path_vals)
