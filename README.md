# Mo

**A provenance-first, agentic natural-language companion for the patients severe-asthma medicine still fails: the non-T2 / T2-low endotype.**

[![Live demo](https://img.shields.io/badge/demo-live-5A4FE4)](https://mo-companion-asthme.netlify.app)
![Status](https://img.shields.io/badge/status-prototype-orange)
![Data](https://img.shields.io/badge/data-synthetic-lightgrey)
![Not a medical device](https://img.shields.io/badge/regulatory-non--MDSW%20by%20design-informational)

> Clickable HTML prototype. Every patient journey is navigable end to end. Patient data is synthetic. The interaction model and the provenance UX are fully built; the underlying RAG and agent orchestration are documented below as the target architecture the prototype is designed to sit on.

**Live prototype → https://mo-companion-asthme.netlify.app**

<!-- Add a hero screenshot here: ./docs/screens/hero.png -->

---

## The problem

The last decade of severe-asthma care was built around the type-2 (T2) inflammatory axis. Anti-IL5 and anti-IL4/13 biologics transformed outcomes for patients with high eosinophils and high FeNO. The patients left behind are the **non-T2 / T2-low endotype**: low or fluctuating biomarkers, no companion biologic aimed squarely at their biology, and a diagnostic apparatus that tends to read their fluctuation as poor adherence rather than a distinct disease mechanism.

For that patient, concretely:

- they cycle through biologics by trial and error, each attempt a 4 to 6 month bet
- they carry the oral corticosteroid (OCS) burden longer, with its cumulative harm
- they are alone with the hardest part: reading their own trajectory, preparing the consultation, arguing their case in front of a specialist
- generic advice ignores them, because it assumes the T2 playbook that does not apply

Mo is built for that gap.

## What Mo does

Mo is a longitudinal companion the patient talks to in natural language. It does four things, and refuses a fifth.

- **Documents.** Turns unstructured patient narrative ("bad night, cold air on the morning run, two puffs of rescue") into a structured, timestamped clinical record.
- **Explains.** General mechanism first, then personalization, with every claim tagged by where it comes from.
- **Surfaces.** Assembles the longitudinal view (exacerbation history, OCS exposure, trigger patterns, control scores) that the patient and the clinician otherwise never see in one place.
- **Prepares.** Builds the consultation argument: what changed, what was tried, what the record actually shows.

It **never advises on therapeutic conduct**. No dosing, no "increase your", no diagnosis. That refusal is a designed component, not an afterthought (see the MDSW boundary).

## The technical point of view

The prototype demonstrates the interaction model and the provenance UX end to end. The architecture it is designed to run on rests on five commitments.

### 1. Natural language is the only interface

No forms as the primary surface. The patient narrates; the system extracts structure. The back-office ("Mon espace asthme") is the **readable projection** of what the conversation accumulated, not a data-entry chore bolted onto a chatbot. The conversation is the input layer; the structured record is its output.

### 2. Provenance-first generation (typed-source RAG)

Every statement Mo makes is grounded and carries a **visible source class**:

| Source class | Meaning |
|---|---|
| `personal` | what the patient told Mo |
| `clinical` | the medical knowledge base, guidelines, literature |
| `log` | the patient's own longitudinal record |
| `guard` | the safety or regulatory rule that shaped the answer |

This is the core design commitment: **no ungrounded generation reaches the patient.** The source chip is not decoration, it is the contract. It makes retrieval legible and forces the distinction between "the literature says" and "your own log shows" to be explicit at every single turn. For a RAG system aimed at a clinical population, that legibility is the feature, not a nicety.

### 3. Agentic orchestration behind a single conversation

The surface is one dialogue. Behind it sit bounded, specialized capabilities: education, structured logging, trigger correlation, appointment preparation, crisis triage, care-pathway mapping, sub-group stratification. Each has its own retrieval scope and its own guardrails, orchestrated behind one natural-language entry point. The patient sees a companion; the system runs a router over specialists.

### 4. The guardrail is a first-class component

The MDSW boundary is not a disclaimer stapled on top. It is a **constrained-generation layer**. A defined set of intents (dosing, diagnosis, treatment change) is hard-refused and rerouted to "document this and prepare it for your clinician." In an LLM product this is the genuinely hard engineering problem: an assistant that stays maximally useful while reliably refusing to cross a regulatory line, and that shows the user *why* it stopped rather than going silent.

### 5. Structured extraction feeds an endotype-oriented longitudinal record

Every conversation enriches a typed record. Over time, that record is what makes the non-T2 patient **legible**, the exact object the current standard of care fails to produce. The companion is the acquisition instrument; the longitudinal, structured, provenance-tagged trajectory is what it builds.

```
patient narrative (NL)
        │
        ▼
  intent router ──► guard layer ──► refuse + reroute (dosing / dx / tx change)
        │
        ▼
 specialist agent ──► typed-source retrieval (personal | clinical | log)
        │
        ▼
 grounded answer + visible source chips
        │
        ▼
 structured extraction ──► longitudinal endotype-oriented record
```

## Clinical grounding

Nothing in the prototype is generic filler. It is anchored to a sourced reference patient.

**John D., 34, severe non-T2 asthma.** FEV1 at 62%, ACT at 14. Sequential biologic failures (mepolizumab, then dupilumab). Anchored to April 2026, pre-tezepelumab (anti-TSLP). Non-T2 trigger set: cold and dry air, seasonal viral infection, irritants and pollution, exercise, stress. OCS exposure tracked across the trajectory.

Pain points and clinical content are traced to the literature, including Kai et al. (Respirology Case Reports, 2024), O'Neill et al. (2016), the Alismail et al. meta-analysis (2019), ERS guidance (2017), and contemporary path-to-diagnosis work.

### The MDSW boundary, by design

Under the EU Medical Device Regulation, software that provides information used for diagnostic or therapeutic decisions can be regulated as Medical Device Software (MDSW). Mo is designed to stay on the non-device side of that line **by construction**, through a hard rule rather than by accident:

- Mo documents, logs, explains, and prepares the clinical argument.
- Mo does not advise on conduct, does not adjust a dose, does not diagnose.
- Patient hypotheses are logged as the patient's own, never promoted to clinical fact.
- General explanation always precedes personalization, and personalization is always marked as such.

This is both a compliance stance and, for anyone building with LLMs, the more demanding design problem: sustained usefulness under a non-negotiable constraint.

## Product surface

Two layers.

**Conversational front (chat-first).** Around eleven patient journeys: onboarding with warm-start synthesis, education, inhaler-technique check (computer vision), injectable guide, daily logging, reactive and proactive notifications, appointment preparation, post-appointment sync, the OCS/cortisone burden case, crisis management (with a doubt phase before acute escalation), and a morning briefing.

**Back-office, "Mon espace asthme".** The readable projection of the accumulated record: Identité, Traitements & outils, Clinique, Observance, Ressenti, Ressources, Parcours de soin, Alertes.

<!-- Add 3-4 screenshots here, e.g.:
| Onboarding | Grounded answer + source chips | Crisis triage | Longitudinal record |
|---|---|---|---|
| ![](./docs/screens/onboarding.png) | ![](./docs/screens/chips.png) | ![](./docs/screens/crisis.png) | ![](./docs/screens/record.png) |
-->

## Design principles

- **Provenance over fluency.** Every claim shows its source class.
- **General before personal.** Mechanism first, "for you" second, always marked as such.
- **The guardrail is visible.** When Mo will not cross a line, it says why.
- **The record is the product.** The conversation exists to build the longitudinal view.

## Stack & structure

Static, framework-free clickable prototype: HTML, a shared `app.css`, vanilla JS for navigation. Built to `dist/` and deployed on Netlify from GitHub.

```
.
├── index.html                 # prototype entry point / table of contents
├── app.css                    # shared design system
├── front/                     # conversational journeys (onboarding, crisis, OCS, ...)
├── espace-asthme/             # back-office spaces (clinique, observance, parcours, ...)
├── assets/                    # avatar, icons, source-chip styles
├── dist/                      # production build served by Netlify
└── netlify.toml               # serves dist/
```

<!-- Adjust the tree above to match the actual repository layout. -->

## Current state vs target architecture

| | Built in this prototype | Target architecture |
|---|---|---|
| Interface | full navigable NL interaction model | live LLM dialogue |
| Provenance | typed source chips on every message | retrieval-backed typed-source RAG |
| Agents | journey-specific flows | orchestrated specialist agents |
| Guardrail | MDSW refusals shown in-flow | intent classifier + constrained generation |
| Record | designed longitudinal projection | structured extraction into a real longitudinal store |
| Clinical content | sourced reference scenario (John D.) | validated knowledge base |

## Notice

All patient data is synthetic. This is a research prototype. It is **not a medical device** and is not intended for clinical use.
