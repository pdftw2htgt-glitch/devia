// api/chat.js
// Passerelle vers l API Anthropic.
//
// ELLE ETAIT OUVERTE A TOUT INTERNET. Aucun controle : n importe qui ayant trouve l adresse
// pouvait l appeler sans compte ni licence. Et comme le corps de la requete etait etale
// APRES model et max_tokens, l appelant choisissait lui-meme le modele et la taille de
// sortie : Opus a 200 000 jetons en boucle, sur la cle de DEVIA.
//
// Quatre verrous :
//   1. un jeton de session Supabase valide, envoye par le navigateur ;
//   2. une licence rattachee au compte que ce jeton designe ;
//   3. un modele pris dans une liste fermee et un budget de sortie plafonne ;
//   4. un quota par compte, compte sur usage_logs.
//
// POURQUOI LE QUOTA EST FIABLE : c est la passerelle qui ecrit la ligne usage_logs, plus le
// navigateur. La table n a ni politique DELETE ni politique UPDATE, donc une ligne ecrite ne
// peut etre ni effacee ni modifiee, meme avec un jeton vole. Le compteur ne sait que monter.
// Effet de bord voulu : les tokens affiches dans le logiciel deviennent les VRAIS, ceux
// qu Anthropic renvoie, pour chacun des appels d une analyse et pas seulement pour le dernier.

export const config = { maxDuration: 60 };

const MODELES_AUTORISES = ["claude-sonnet-5", "claude-fable-5"];
const PLAFOND_SORTIE = 32000;    // le plus gros budget que le logiciel demande

// Une analyse complete = 7 passes + 1 appel devis, soit ~8 appels, plus les reprises.
// Garde-fou volontairement large : il doit arreter un script emballe ou un jeton vole,
// jamais un charpentier qui travaille (2 a 5 analyses par jour).
const PLAFOND_JOUR = 150;        // ~18 analyses par 24 h
const PLAFOND_MOIS = 1500;       // ~185 analyses par 30 jours

// Le compte designe par le jeton. On lit la charge utile sans la verifier : inutile de le
// faire ici, car Supabase revalide la signature et la politique RLS refuse l insertion si
// user_id ne correspond pas a auth.uid(). Une valeur fausse ne passe pas.
function compteDuJeton(jeton) {
  try {
    const part = String(jeton).split(".")[1] || "";
    const b64 = part.replace(/-/g, "+").replace(/_/g, "/");
    const charge = JSON.parse(Buffer.from(b64, "base64").toString("utf8"));
    return String(charge.sub || "");
  } catch (e) {
    return "";
  }
}

export default async function handler(req, res) {
  if (req.method === "POST" === false) {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const urlSupa = process.env.VITE_SUPABASE_URL || "";
  const cleAnon = process.env.VITE_SUPABASE_ANON_KEY || "";
  const cleIA = process.env.ANTHROPIC_API_KEY || "";
  if (urlSupa === "" || cleAnon === "" || cleIA === "") {
    return res.status(500).json({ error: "configuration serveur incomplete" });
  }

  // --- 1. LE JETON DE SESSION ---
  const entete = String(req.headers.authorization || "");
  const jeton = entete.startsWith("Bearer ") ? entete.slice(7).trim() : "";
  if (jeton === "") {
    return res.status(401).json({ error: "Connecte-toi pour lancer une analyse." });
  }

  // --- 2. LA LICENCE ---
  // check_my_license tourne en SECURITY DEFINER et lit auth.uid() : c est le JETON qui
  // designe le compte, pas le corps de la requete. Rien n est usurpable depuis le client.
  let licence = null;
  try {
    const rl = await fetch(urlSupa + "/rest/v1/rpc/check_my_license", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        apikey: cleAnon,
        Authorization: "Bearer " + jeton,
      },
      body: "{}",
    });
    if (rl.ok === false) {
      return res.status(401).json({ error: "Session expiree. Reconnecte-toi." });
    }
    licence = await rl.json();
  } catch (e) {
    return res.status(503).json({ error: "Verification de licence indisponible." });
  }
  // On exige une licence RATTACHEE, pas un abonnement valide : c est exactement la regle
  // que le logiciel applique a son entree. Exiger subscription_valid fermerait la porte
  // aux comptes dont l abonnement est en statut "none", dont celui de Mathis.
  const aLicence = ((licence && licence.status === "ok") === true);
  if (aLicence === false) {
    return res.status(403).json({ error: "Aucune licence sur ce compte." });
  }

  // --- 3. LE QUOTA ---
  // Compte exact sans transferer les lignes : PostgREST renvoie le total dans content-range.
  // La politique RLS limite d elle-meme le decompte aux lignes du compte.
  const compterDepuis = async (iso) => {
    try {
      const url = urlSupa + "/rest/v1/usage_logs?select=id&limit=1&created_at=gte." + encodeURIComponent(iso);
      const r = await fetch(url, {
        headers: { apikey: cleAnon, Authorization: "Bearer " + jeton, Prefer: "count=exact" },
      });
      if (r.ok === false) return -1;
      const plage = String(r.headers.get("content-range") || "");
      const total = Number(plage.split("/")[1]);
      return Number.isFinite(total) ? total : -1;
    } catch (e) {
      return -1;
    }
  };

  const maintenant = Date.now();
  const bornes = await Promise.all([
    compterDepuis(new Date(maintenant - 24 * 3600 * 1000).toISOString()),
    compterDepuis(new Date(maintenant - 30 * 24 * 3600 * 1000).toISOString()),
  ]);
  const nJour = bornes[0];
  const nMois = bornes[1];
  // -1 = decompte indisponible. On laisse passer : une panne de Supabase ne doit pas
  // arreter le logiciel, et les trois autres verrous tiennent toujours.
  if (nJour >= PLAFOND_JOUR) {
    return res.status(429).json({ error: "Quota journalier atteint sur ce compte (" + PLAFOND_JOUR + " appels en 24 h). Reessaie demain ou contacte DEVIA." });
  }
  if (nMois >= PLAFOND_MOIS) {
    return res.status(429).json({ error: "Quota mensuel atteint sur ce compte (" + PLAFOND_MOIS + " appels sur 30 jours). Contacte DEVIA." });
  }

  // --- 4. LE CORPS : on ne recopie QUE ce dont l analyse a besoin ---
  const recu = (req.body && typeof req.body === "object") ? req.body : {};
  const modeleDemande = String(recu.model || "");
  const modele = MODELES_AUTORISES.indexOf(modeleDemande) >= 0 ? modeleDemande : MODELES_AUTORISES[0];
  const budget = Math.min(Math.max(1, Number(recu.max_tokens) || 12000), PLAFOND_SORTIE);
  const envoi = {
    model: modele,
    max_tokens: budget,
    messages: Array.isArray(recu.messages) ? recu.messages : [],
  };
  if (typeof recu.system === "string") envoi.system = recu.system;
  if (recu.output_config && typeof recu.output_config === "object") envoi.output_config = recu.output_config;
  if (recu.thinking && typeof recu.thinking === "object") envoi.thinking = recu.thinking;

  try {
    const reponse = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": cleIA,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify(envoi),
    });
    const data = await reponse.json();

    // --- 5. LA CONSOMMATION REELLE ---
    // Attendue avant de repondre : une fonction Vercel peut etre arretee des que la reponse
    // est partie, et une ecriture laissee en vol serait perdue - donc non comptee.
    const compte = compteDuJeton(jeton);
    const usage = (data && data.usage) || {};
    const entrants = Number(usage.input_tokens || 0)
      + Number(usage.cache_creation_input_tokens || 0)
      + Number(usage.cache_read_input_tokens || 0);
    const sortants = Number(usage.output_tokens || 0);
    if ((compte === "") === false && (entrants + sortants) > 0) {
      try {
        await fetch(urlSupa + "/rest/v1/usage_logs", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            apikey: cleAnon,
            Authorization: "Bearer " + jeton,
            Prefer: "return=minimal",
          },
          body: JSON.stringify({
            user_id: compte,
            tokens_in: entrants,
            tokens_out: sortants,
            model: modele,
          }),
        });
      } catch (eLog) {
        console.error("usage_logs non ecrit", eLog);
      }
    }

    return res.status(200).json(data);
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}
