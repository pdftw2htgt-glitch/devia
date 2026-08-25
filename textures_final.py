import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

# --- Ancres simples ---
A_PIN = 'douglas: "bois_douglas",'
B_PIN = 'douglas: "bois_douglas",\n    pin: "bois_pin",'
A_BETON = 'const betonMat = new THREE.MeshStandardMaterial({ color: 0xb4b4b8, roughness: 0.95, metalness: 0.0 });'
B_BETON = A_BETON + '\n' + \
'  (function chargeBeton() {\n' + \
'    const modeB = (opts && opts.mode) ? opts.mode : "technique";\n' + \
'    if (modeB === "realiste") {\n' + \
'      new THREE.TextureLoader().load("/textures/beton_mur.png", (img) => {\n' + \
'        img.colorSpace = THREE.SRGBColorSpace;\n' + \
'        img.wrapS = THREE.RepeatWrapping;\n' + \
'        img.wrapT = THREE.RepeatWrapping;\n' + \
'        betonMat.map = img;\n' + \
'        betonMat.color.set(0xffffff);\n' + \
'        betonMat.needsUpdate = true;\n' + \
'      });\n' + \
'    }\n' + \
'  })();'

# --- Region du chargeur bois (entre 2 marqueurs) ---
m1 = 'const code = TEXTURES_BOIS[essenceKey];'
m2 = 'const roofMat = new THREE.MeshStandardMaterial'

ANCRES = [(A_PIN, 1), (A_BETON, 1), (m1, 1), (m2, 1)]
ok = True
for a, attendu in ANCRES:
    n = txt.count(a)
    if n != attendu:
        print("ABANDON : ancre en", n, "exemplaire(s), attendu", attendu, ":", a[:60])
        ok = False
if ok == False:
    raise SystemExit(1)

i1 = txt.find(m1)
i2 = txt.find(m2)
region = txt[i1:i2]

REMPL = [
    ("const tryLoad = (ext, onFail) => {",
     'const finRaw = ((opts && opts.finition) || (params && params.finition) || "").toString().toLowerCase();\n'
     '    const codeFin = finRaw.length > 0 ? code + "_" + finRaw : "";\n'
     "    const tryLoad = (base, ext, onFail) => {"),
    ('"/textures/" + code + "." + ext,',
     '"/textures/" + base + "." + ext,'),
    ('tryLoad("png", () => tryLoad("jpg", () => {',
     'const chargeEssence = () => tryLoad(code, "png", () => tryLoad(code, "jpg", () => {'),
    ("}));",
     "}));\n"
     "    if (codeFin.length > 0) {\n"
     '      tryLoad(codeFin, "png", () => tryLoad(codeFin, "jpg", chargeEssence));\n'
     "    } else {\n"
     "      chargeEssence();\n"
     "    }"),
]
for a, b in REMPL:
    n = region.count(a)
    if n != 1:
        print("ABANDON : ancre region en", n, "exemplaire(s) :", a[:60])
        print("---- Region reelle ----")
        print(region)
        raise SystemExit(1)

for a, b in REMPL:
    region = region.replace(a, b)
txt = txt[:i1] + region + txt[i2:]
txt = txt.replace(A_PIN, B_PIN)
txt = txt.replace(A_BETON, B_BETON)

shutil.copy(CHEMIN, CHEMIN + ".backup_textures_final_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : finitions bois + pin maritime + texture murs beton")
