import shutil, time

f = "devia.jsx"
shutil.copy(f, f + ".backup_boussole_bas_" + time.strftime("%Y%m%d_%H%M%S"))
c = open(f).read()

ancien = 'hudBoussole.style.cssText = "position:absolute;top:10px;right:10px;width:54px;height:54px;border-radius:50%;background:rgba(10,12,20,0.72);border:1px solid rgba(240,192,64,0.45);display:flex;align-items:center;justify-content:center;pointer-events:none;z-index:5;";'

nouveau = 'hudBoussole.style.cssText = "position:absolute;bottom:14px;right:14px;width:58px;height:58px;border-radius:50%;background:rgba(10,12,20,0.72);border:1px solid rgba(240,192,64,0.45);display:flex;align-items:center;justify-content:center;pointer-events:none;z-index:5;transform:perspective(160px) rotateX(48deg);transform-origin:center bottom;";'

n = c.count(ancien)
if n != 1:
    print("ERREUR : ancre trouvee", n, "fois (attendu 1). Rien modifie.")
    raise SystemExit(1)

c = c.replace(ancien, nouveau)
open(f, "w").write(c)
print("OK : boussole en bas a droite, couchee a 48 degres.")
