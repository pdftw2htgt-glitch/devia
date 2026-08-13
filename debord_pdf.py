import shutil, time

f = "devia.jsx"
shutil.copy(f, f + ".backup_debord_pdf_" + time.strftime("%Y%m%d_%H%M%S"))
c = open(f).read()

ancre = '''    if (result.projet.pente) {
      doc.text("Pente : " + result.projet.pente + " deg", pageW / 2 + 5, yD);
      yD += 4;
    }
  }'''

nouveau = '''    if (result.projet.pente) {
      doc.text("Pente : " + result.projet.pente + " deg", pageW / 2 + 5, yD);
      yD += 4;
    }
    if (view3DParams && view3DParams.debord) {
      doc.text("Depasse de toiture : " + Math.round(view3DParams.debord * 100) + " cm", pageW / 2 + 5, yD);
      yD += 4;
    }
  }'''

n = c.count(ancre)
if n != 1:
    print("ERREUR : ancre trouvee", n, "fois (attendu 1). Rien modifie.")
    raise SystemExit(1)

c = c.replace(ancre, nouveau)
open(f, "w").write(c)
print("OK : ligne Depasse de toiture dans l en-tete du PDF.")
