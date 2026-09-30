"""Gemini multimodal extraction (audio or text, any Indian language) with an offline fallback."""
import os, json, re
from .phonetic import similarity

ISSUES=["connectivity_gap","road_damage","other"]

def _client():
    k=os.getenv("GEMINI_API_KEY")
    if not k: return None
    from google import genai
    return genai.Client(api_key=k)

MODEL=os.getenv("GEMINI_MODEL","gemini-2.5-flash")

def extract(text=None,audio=None,mime="audio/ogg",blocks=()):
    c=_client()
    if c is None: return _fallback(text or "",blocks)
    from google.genai import types
    prompt=("You read a citizen request about a rural road (voice or text, Hindi/Bhojpuri/other). Return JSON: "
      "{transcript, detected_block (exactly one of %s or null), village_mention_latin (the village/hamlet name the speaker said, "
      "transliterated to Latin script as spoken, or null), landmark_mention (or null), issue_category (one of %s), urgency (0-1)}. "
      "Do not guess a village that was not said."%(list(blocks),ISSUES))
    parts=[prompt]+([text] if text else [])+([types.Part.from_bytes(data=audio,mime_type=mime)] if audio else [])
    try:
        r=c.models.generate_content(model=MODEL,contents=parts,config=types.GenerateContentConfig(response_mime_type="application/json"))
        d=json.loads(r.text); d["engine"]="gemini"; return d
    except Exception as e:
        d=_fallback(text or "",blocks); d["engine"]=f"fallback:{type(e).__name__}"; return d

def _fallback(text,blocks):
    t=text.lower(); blk=None
    for b in blocks:
        if b.lower() in t: blk=b;break
    issue="road_damage" if re.search(r"damage|broken|toot|dhans|caved|pothole|टूट|धंस|गड्ढ",t) else "connectivity_gap"
    return dict(transcript=text,detected_block=blk,village_mention_latin=None,landmark_mention=None,
                issue_category=issue,urgency=0.5,engine="rules")

def gemini_arbiter(mention,cands):
    """Pick hab_id among shortlist or None. Only called for near-ties."""
    c=_client()
    if c is None: return None
    from google.genai import types
    try:
        r=c.models.generate_content(model=MODEL,
          contents=f"Spoken name: {mention}. Candidates: {json.dumps(cands)}. Return JSON {{\"hab_id\": id or null}}. Return null unless one is clearly the same place.",
          config=types.GenerateContentConfig(response_mime_type="application/json"))
        v=json.loads(r.text).get("hab_id")
        return v if v in [x["hab_id"] for x in cands] else None
    except Exception:
        return None
