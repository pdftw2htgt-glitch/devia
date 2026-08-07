# Fichiers de plus de 3 Mo : upload Supabase Storage (bucket plans) + URL signee
# -> contourne la limite serveur 4,5 Mo (HTTP 413). Petits fichiers : inchanges.
import shutil, datetime, sys

stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"

with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''  // Construit les blocs multimodaux Anthropic pour une liste de File
  const buildFileBlocks = async (fileList) => {
    const blocks = [];
    for (const f of fileList) {
      const b64 = await fileToBase64(f);
      if (f.type === "application/pdf") {
        blocks.push({ type: "document", source: { type: "base64", media_type: "application/pdf", data: b64 } });
      } else if (f.type.startsWith("image/")) {
        blocks.push({ type: "image", source: { type: "base64", media_type: f.type, data: b64 } });
      }
    }
    return blocks;
  };'''
NEW1 = '''  // Construit les blocs multimodaux Anthropic pour une liste de File.
  // Fichier lourd (plus de 3 Mo) : upload Supabase Storage + URL signee,
  // pour rester sous la limite serveur de 4,5 Mo (sinon HTTP 413).
  const SEUIL_FICHIER_LOURD = 3 * 1024 * 1024;
  const uploadFichierLourd = async (f) => {
    const { data: { user } } = await supabase.auth.getUser();
    if (user === null || user === undefined) throw new Error("Fichier de plus de 3 Mo : connexion requise (stockage securise du plan)");
    const ext = ((f.name.split(".").pop() || "bin").toLowerCase().replace(/[^a-z0-9]/g, "") || "bin").slice(0, 8);
    const chemin = user.id + "/plan_" + Date.now() + "_" + Math.floor(Math.random() * 100000) + "." + ext;
    const { error: upErr } = await supabase.storage.from("plans").upload(chemin, f, { upsert: true, cacheControl: "0" });
    if (upErr) throw new Error("Upload du plan impossible : " + (upErr.message || "erreur stockage") + " - le bucket prive plans existe-t-il ?");
    const { data: signed, error: signErr } = await supabase.storage.from("plans").createSignedUrl(chemin, 600);
    if (signErr) throw new Error("URL signee impossible : " + (signErr.message || "erreur stockage"));
    const urlOk = signed && typeof signed.signedUrl === "string";
    if (urlOk === false) throw new Error("URL signee impossible : reponse stockage vide");
    return signed.signedUrl;
  };
  const buildFileBlocks = async (fileList) => {
    const blocks = [];
    for (const f of fileList) {
      const estPdf = f.type === "application/pdf";
      const estImage = f.type.startsWith("image/");
      if (estPdf === false && estImage === false) continue;
      if (f.size > SEUIL_FICHIER_LOURD) {
        const url = await uploadFichierLourd(f);
        console.log("[DEVIA] Fichier lourd envoye par URL signee : " + f.name + " (" + Math.round(f.size / 1048576 * 10) / 10 + " Mo)");
        if (estPdf) blocks.push({ type: "document", source: { type: "url", url: url } });
        else blocks.push({ type: "image", source: { type: "url", url: url } });
      } else {
        const b64 = await fileToBase64(f);
        if (estPdf) blocks.push({ type: "document", source: { type: "base64", media_type: "application/pdf", data: b64 } });
        else blocks.push({ type: "image", source: { type: "base64", media_type: f.type, data: b64 } });
      }
    }
    return blocks;
  };'''

n = c.count(OLD1)
if n != 1:
    print("ERREUR ancre (buildFileBlocks) : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
    sys.exit(1)

shutil.copy2(F, F + ".backup_" + stamp + "_fichiers_lourds")
c = c.replace(OLD1, NEW1)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : fichiers lourds envoyes par URL signee Supabase (petits fichiers inchanges)")
