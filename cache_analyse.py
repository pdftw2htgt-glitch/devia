# Etape 1 : cache d'analyse par empreinte SHA-256 du fichier + version du prompt
# Meme fichier + meme prompt -> resultat identique servi depuis Supabase, sans appel IA
import shutil, datetime, sys

stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"

with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''        "Mets null quand l'info n'est pas lisible sur le document. Les dimensions en metres.";
      const response = await fetch("/api/chat", {'''
NEW1 = '''        "Mets null quand l'info n'est pas lisible sur le document. Les dimensions en metres.";
      // CACHE D'ANALYSE : empreinte des fichiers + version du prompt
      const bufs = [];
      for (const f of fileList) bufs.push(new Uint8Array(await f.arrayBuffer()));
      const totalOctets = bufs.reduce((a, b) => a + b.length, 0);
      const concat = new Uint8Array(totalOctets);
      { let off = 0; for (const b of bufs) { concat.set(b, off); off += b.length; } }
      const dig = await crypto.subtle.digest("SHA-256", concat);
      const empreinte = Array.from(new Uint8Array(dig)).map(x => x.toString(16).padStart(2, "0")).join("");
      let vh = 5381;
      for (let vi = 0; vi < sysAnalyse.length; vi++) { vh = ((vh * 33) ^ sysAnalyse.charCodeAt(vi)) >>> 0; }
      const versionPrompt = vh.toString(36);
      let jCache = null;
      const { data: { user: uCache } } = await supabase.auth.getUser();
      if (uCache) {
        const { data: ligneCache } = await supabase.from("analyses_plans").select("resultat").eq("empreinte", empreinte).eq("version", versionPrompt).limit(1).maybeSingle();
        if (ligneCache && ligneCache.resultat) jCache = ligneCache.resultat;
      }
      let j = null;
      if (jCache === null) {
      const response = await fetch("/api/chat", {'''

OLD2 = '''      const j = JSON.parse(m[0]);'''
NEW2 = '''      j = JSON.parse(m[0]);
      if (uCache) {
        try {
          await supabase.from("analyses_plans").upsert({ user_id: uCache.id, empreinte: empreinte, version: versionPrompt, resultat: j }, { onConflict: "user_id,empreinte,version" });
          console.log("[DEVIA] Analyse mise en cache (" + empreinte.slice(0, 8) + ", v" + versionPrompt + ")");
        } catch (eCache) { console.warn("[DEVIA] Cache analyse : stockage impossible", eCache); }
      }
      } else {
        j = jCache;
        console.log("[DEVIA] Analyse servie par le cache (" + empreinte.slice(0, 8) + ")");
      }'''

anchors = [("insertion cache avant appel", OLD1, NEW1), ("parse et stockage", OLD2, NEW2)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)

shutil.copy2(F, F + ".backup_" + stamp + "_cache_analyse")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK etape 1 : cache d'analyse par empreinte en place")
