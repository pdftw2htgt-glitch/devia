import os, sys
if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable"); sys.exit(1)
with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()
BT = chr(96)
old_d = 'text.replace(/' + BT*3 + 'json|' + BT*3 + '/g, "")'
new_d = 'text.replace(/\\x60\\x60\\x60json|\\x60\\x60\\x60/g, "")'
old_s = "text.replace(/" + BT*3 + "json|" + BT*3 + "/g, '')"
new_s = "text.replace(/\\x60\\x60\\x60json|\\x60\\x60\\x60/g, '')"
p = 0
if old_d in content:
    content = content.replace(old_d, new_d); p += 1; print("[FIX] double quotes")
if old_s in content:
    content = content.replace(old_s, new_s); p += 1; print("[FIX] single quotes")
if p > 0:
    with open("devia.jsx", "w", encoding="utf-8") as f:
        f.write(content)
    print("Termine :", p, "patch(s)")
else:
    print("Aucun patch. Ligne 385 :")
    lines = content.split("\n")
    for i in range(383, min(len(lines), 387)):
        print(" ", i+1, ":", lines[i])
