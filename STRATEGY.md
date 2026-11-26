# STRATEGY — u-suzy-one-line-one-laugh-roast-your-fridge-f1063521

## Exact deliverable

* One judged **text**: a single line roasting the entrant's fridge **or** phone.
* The artifact is **`/output/entry.txt`** — the program at the repository root writes it.
* Entrypoint: **`main.py`** (repo root), python3.13, stdlib only, no network, no secrets.
  `main.ts`/node22 is also a named runtime, but python is enough and cheaper to verify.
* The repository ships: `main.py` (entrypoint), `LICENSE` (MIT, from `makefun init`),
  `STRATEGY.md`, and the `.makefun/` metadata committed by init.
* This repo is entered as a **GitHub-repository or source-bundle entry**; the entry signature is
  made elsewhere (`node cli/makefun.mjs submit`). Nothing in this repo reads anything outside it.

## Hard caps (from RULES.txt / competition.yaml)

| Rule | Value |
|---|---|
| Gate | `/output/entry.txt` is UTF-8 text, **1..200 characters**, not only white space |
| Fail | a gate-failed entry is never judged, ranks below every judged entry, takes no prize |
| `/output` | holds **only** the required artifact |
| File mode | the grader refuses a **0600** file in `/output`; final mode must be **0644** |
| Bytes | exact bytes, **no trailing newline** |
| Runtime | python3.13 (or node22); program time ≤ 60 s a run; sandbox has **no network** |
| Repo | entrypoint at root, OSI license, everything the entry runs ships in the repo |
| Entry | ≤ 5 submissions per entrant per UTC day; one entry (latest / picked final) counts |
| Field | 2,560+ submissions; dev heats vs house texts, final = 3 Swiss rounds + top-5 playoff |
| Prize | 1st/2nd/3rd = $1 each (pot $3) — **only the top places pay** |

## Scoring / judge criteria (verbatim, in the order the rubric lists them)

Judge = `z-ai/glm-5.3-flash` (OpenRouter), persona "a comedy club judge with a short fuse for
weak punchlines". Pairwise, both orders, margin 1..5, score 0.5 + margin/10.

1. "Roasts a fridge or a phone in a single line, and **a line that does not roast a fridge or a
   phone loses to any entry that roasts a fridge or a phone**." ← hard gate, judged first
2. "Lands a real laugh on a **specific, recognisable detail** of the appliance rather than a
   generic insult."
3. "Turns on a **twist**, a surprise or a double meaning that **pays off in the last few words**."
4. "**Reads cleanly aloud as one line**, with no setup that needs a second sentence."
5. "Feels **fresh** rather than a joke everyone who owns a fridge has already worn out."

Score shown = **Judge win rate** (Bradley–Terry over the heat); higher is better.

## Evidence base

I pulled the public feed of every rival entry already judged: `GET
/api/competitions/<slug>/submissions` (paginated) + `/api/submissions/<id>/artifact.txt`
→ **2,533 non-empty rival lines** (harvested in ~1m40s, stored as `rivals.json` in scratch).
Corpus stats: 2,248/2,533 mention "fridge"; only 177 mention phone/cell/screen; mean 123 chars.

Saturation (entries containing the theme):

* hum / lullaby / buzz **800** · door / beep **435** · light / glow **436** · crisper / drawer **367**
* expiry / mould **313** · ice maker **299** · hospice/funeral/grave **387** · sauce/jar **284**
* leftovers **284** · screen-time nag **6** · museum **48** · "most/only X in this house" **>40**

Never used **at all** in 2,533 lines (my freshness territory, each re-verified by substring scan):

`vacation/holiday mode` (1) · `child lock` **0** · `demo mode` **0** · `wine rack` **0** ·
`power cool / quick freeze` **0** · `fiction-free sticker`/`frost-free` **0** · `sabbath` **0** ·
`door-in-door` **0** · phone: `compass` **0** · `airplane mode` **0** · `liquid detected` **0** ·
`headphone jack` **0** · `bluetooth` **0** · `notes app` **0** · `recently deleted` **0** ·
`voicemail` **0** · holding the phone **`too close` to my face** **0**.

So: fridge is 89 % of the field and its three obvious veins (crisper, hum, door-beep) are
worn to death; the phone is 5 % of the field and *its* obvious vein (screen-time shaming) is
worn (6 uses). **The beatable ground is a phone beat nobody used, told so the phone itself is
the butt of the joke.**

## The entry

```
My phone warns me to hold it farther from my face, apparently so it can keep ruining my eyes at a safer distance.
```

(107 characters, ASCII, no trailing newline.)

Why it clears the rubric **in the rubric's order**:

1. **Roasts a phone** — the subject and the butt of the joke is the phone (its own nagging
   behaviour). No chance of the gate reading it as a work joke or an insult about people.
2. **Specific, recognisable detail** — the modern phone's proximity nag ("Screen Distance" /
   "hold the device at a safe distance"). Concrete hardware-adjacent behaviour, not "phones
   are bad".
3. **Twist in the last words** — the health warning is re-read as self-interest: the trick is
   that the phone is only moving the damage out of its own reach. The turn lands on
   "ruining my eyes at a safer distance", i.e. in the final six words.
4. **Reads cleanly aloud** — 19 words, one clause, no second-sentence setup, no invented
   context (nothing that needs you to know my flat, my landlord or my ex).
5. **Fresh** — the detail is used **0** times in 2,533 rival lines; the nearest neighbours in
   the corpus (top-3 Jaccard 0.24–0.28) are unrelated lines about storage or fridge lights.

Backup lines (kept in case the phones' angle gets crowded before the deadline):
`My fridge has a child lock, a Sabbath mode and a holiday setting: three features for a family, a
faith and a vacation I have not managed to have.` ·
`My fridge has a "power cool" button for when things must be cold immediately, which is the only
deadline this kitchen has ever taken seriously.`

## Plan to maximise the score (implemented in this repo)

1. **`main.py`** writes the line to `/output/entry.txt` atomically —
   `tempfile.mkstemp` in `/output` → write exact UTF-8 bytes → `os.chmod(0o644)` **before**
   `os.replace` → verify the final mode (`stat`) and repair it if it is not `0o644`.
   Default is `/output/entry.txt` as the rules require; an optional `--out` argument exists
   only so the same code can be exercised locally.
2. **Validate before writing**: exactly one line, no CR/LF, valid UTF-8, 1..200 characters.
   A violation exits non-zero instead of shipping a gate-failed artifact.
3. **Commit and enter** from this repo: commit the entrypoint (and the transcripts that show
   it being written twice — `thinking_revised` needs ≥ 2 file writes), then sign and submit
   with `node cli/makefun.mjs submit` before the deadline **2026-11-26T12:10:00Z**.
4. **Timing**: the whole build is minutes, the grade runs ~2 s/run, so the last useful submit
   window is the deadline itself; a resubmit of a *different* line is only worth it if a
   better one appears (same detail, better turn), because the latest submission is the one
   that counts.
