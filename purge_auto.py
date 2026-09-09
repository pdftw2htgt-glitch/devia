# purge_auto.py — LE STOCKAGE SE VIDE TOUT SEUL
# Un plan televerse ne sert que le temps de la lecture (lien signe 10 min).
# A la fin de chaque analyse - reussie ou non - DEVIA supprime tous les plans
# temporaires du dossier de l utilisateur, y compris les residus laisses par
# les generations precedentes. Le bucket ne sature plus jamais.
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''      setAnalyseFichier("ok");
    } catch (e) {
      console.warn("[DEVIA] Analyse fichier:", e);
      setAnalyseErreur(e && e.message ? String(e.message) : "erreur inconnue");
      setAnalyseFichier("erreur");
    }
  };'''

R1 = r'''      setAnalyseFichier("ok");
    } catch (e) {
      console.warn("[DEVIA] Analyse fichier:", e);
      setAnalyseErreur(e && e.message ? String(e.message) : "erreur inconnue");
      setAnalyseFichier("erreur");
    } finally {
      // NETTOYAGE DU STOCKAGE : les plans televerses ont fini leur office
      // (la lecture est terminee, le lien signe expire). On vide le dossier.
      try {
        const { data: { user: uPurge } } = await supabase.auth.getUser();
        if (uPurge) {
          const { data: restes } = await supabase.storage.from("plans").list(uPurge.id, { limit: 200 });
          if (Array.isArray(restes) && restes.length > 0) {
            const chemins = restes.map(r => uPurge.id + "/" + r.name);
            const { error: eRm } = await supabase.storage.from("plans").remove(chemins);
            if (eRm) console.warn("[DEVIA] Nettoyage du stockage impossible", eRm);
            else console.log("[DEVIA] Stockage nettoye : " + chemins.length + " plan(s) temporaire(s) supprime(s)");
          }
        }
      } catch (ePurge) { console.warn("[DEVIA] Nettoyage du stockage impossible", ePurge); }
    }
  };'''

n = src.count(A1)
if n == 1:
    print("OK ancre : fin de l analyse")
else:
    print("ANCRE : " + str(n) + " occurrence(s) au lieu de 1 — ABANDON, rien ecrit.")
    sys.exit(1)

if src.count("Stockage nettoye") > 0:
    print("ABANDON — script deja passe.")
    sys.exit(1)

tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, F + ".bak_" + tag)
src = src.replace(A1, R1)
open(F, "w", encoding="utf-8").write(src)
print("1 modification ecrite. Backup : " + F + ".bak_" + tag)
