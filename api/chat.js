// api/chat.js
// Passerelle vers l API Anthropic.
//
// ELLE ETAIT OUVERTE A TOUT INTERNET. Aucun controle : n importe qui ayant trouve l adresse
// pouvait l appeler sans compte ni licence. Et comme le corps de la requete etait etale
// APRES model et max_tokens, l appelant choisissait lui-meme le modele et la taille de
// sortie : Opus a 200 000 jetons en boucle, sur la cle de DEVIA.
//
// Desormais, trois verrous :
//   1. un jeton de session Supabase valide, envoye par le navigateur ;
//   2. une licence rattachee au compte que ce jeton designe ;
//   3. un modele pris dans une liste fermee et un budget de sortie plafonne.

export const config = { maxDuration: 60 };

const MODELES_AUTORISES = ["claude-sonnet-5", "claude-fable-5"];
const PLAFOND_SORTIE = 32000;          // le plus gros budget que le logiciel demande

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

  // --- 3. LE CORPS : on ne recopie QUE ce dont l analyse a besoin ---
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
    return res.status(200).json(data);
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}
