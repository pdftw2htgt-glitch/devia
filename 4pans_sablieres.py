#!/usr/bin/env python3
import shutil
from datetime import datetime
lines = open("devia.jsx", encoding="utf-8").read().split("\n")
idx0 = next((i for i,l in enumerate(lines) if "const draw4Pans" in l), None)
idx1 = next((i for i,l in enumerate(lines) if "const drawEmpannonsGrandPan" in l), None)
def ind_of(s): return s[:len(s)-len(s.lstrip())]
repl = [
    ('addBox(L + 0.2, 0.16, 0.16, 0, Ht, lg/2, woodMat);',
     lambda ind: f'{ind}const [sbB, sbH] = sec("Sabliere", 0.16, 0.16);\n{ind}addBox(L + 0.2, sbH, sbB, 0, Ht, lg/2, woodMat);'),
    ('addBox(L + 0.2, 0.16, 0.16, 0, Ht, -lg/2, woodMat);',
     lambda ind: f'{ind}addBox(L + 0.2, sbH, sbB, 0, Ht, -lg/2, woodMat);'),
    ('addBox(0.16, 0.16, lg, -L/2, Ht, 0, woodMat);',
     lambda ind: f'{ind}addBox(sbB, sbH, lg, -L/2, Ht, 0, woodMat);'),
    ('addBox(0.16, 0.16, lg, L/2, Ht, 0, woodMat);',
     lambda ind: f'{ind}addBox(sbB, sbH, lg, L/2, Ht, 0, woodMat);'),
]
for needle, builder in repl:
    for i in range(idx0, idx1):
        if needle in lines[i]:
            lines[i] = builder(ind_of(lines[i])); print(f"[OK] {needle[:40]}"); break
backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_4pans_debug"
shutil.copy("devia.jsx", backup)
open("devia.jsx", "w", encoding="utf-8").write("\n".join(lines))
print(f"[OK] Backup : {backup}")
