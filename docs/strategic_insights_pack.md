# Strategic Insight Pack — Methylation Interpretation Assistant

This pack converts the current MVP materials into actionable product strategy artifacts for both consumer and clinician contexts.

## Source Basis Used
- `docs/one_pager.md`
- `docs/risk_register.md`
- `docs/demo_script.md (90 seconds)`
- `README.md`

---

## METHYL-1 — Extract Strategic Insights

### 1) ICP split is not optional; the product already serves two intent modes
- **Insight:** The user base naturally separates into (a) consumers needing readability and (b) practitioners needing triage-ready summaries.
- **Evidence:** Target users are explicitly listed as non-technical users and wellness practitioners, with PM stakeholders as tertiary.
- **Decision it informs:** Build dual output tracks now: “Consumer Summary” and “Clinician Prep Notes,” each with different language and uncertainty framing.
- **Risk if wrong:** A single blended output will satisfy neither audience: too technical for consumers, too soft for practitioners.
- **Next validation step:** 10-user split test (5 consumers, 5 practitioners) comparing single-template vs role-specific templates on comprehension and confidence.

### 2) Safety positioning should be framed as “decision support,” never “interpretation certainty”
- **Insight:** The product's strongest defensible claim is data structuring + screening support, not biological or clinical conclusion.
- **Evidence:** Out-of-scope excludes diagnosis/treatment; risk register flags “interpreted as medical advice” as high impact.
- **Decision it informs:** Product copy, CTA labels, and export headers should avoid causal/diagnostic phrasing and enforce uncertainty language.
- **Risk if wrong:** Regulatory exposure, user harm from overreach, and trust erosion if outputs are mistaken for prescriptions.
- **Next validation step:** Compliance + clinical SME redline review of every user-facing claim before demo day.

### 3) Workflow value hinges on reliability in messy-input handling, not model sophistication
- **Insight:** The current MVP’s moat is robust ingest/QC and transparent cleaning behavior.
- **Evidence:** One-pager and demo script emphasize schema mapping, non-numeric coercion, dropped-row warnings, and export artifacts.
- **Decision it informs:** Prioritize “upload success rate + explainability of cleaning” over adding advanced inference features.
- **Risk if wrong:** Users churn at first upload failure; advanced features never get seen.
- **Next validation step:** Instrument funnel metrics for upload, mapping completion, successful normalization, and first export.

### 4) Threshold-based flags need guardrails to prevent false certainty
- **Insight:** A flexible threshold is useful but dangerous without context, defaults, and caveats.
- **Evidence:** Risk register names threshold misuse as a known source of misleading flags.
- **Decision it informs:** Add threshold rationale text, benchmark presets, confidence badges, and “what this does/doesn't mean” microcopy.
- **Risk if wrong:** Users over-index on arbitrary cutoffs and take inappropriate health actions.
- **Next validation step:** A/B test contextualized threshold UI versus plain slider; measure misinterpretation in post-task survey.

### 5) RAG should be introduced only when citation quality gating is operational
- **Insight:** RAG can increase perceived intelligence, but only if retrieval quality and citation grounding are strict.
- **Evidence:** Risk register already anticipates hallucination controls (citations, constrained templates, “I don't know”). README lists future RAG placeholders.
- **Decision it informs:** Gate RAG behind citation completeness and abstention behavior before exposing to end users.
- **Risk if wrong:** Confidently wrong health claims create outsized safety and legal risk.
- **Next validation step:** Build a 30-case evaluation set where every generated claim must map to source citation or abstain.

---

## METHYL-2 — 5-Step Build Plan for Demo-Ready MVP (RAG + UI)

### Step 1: Ingest + QC Hardening
- **Deliverable:** Reliable upload pipeline with schema detection, mapping UX, coercion logs, and QC summary panel.
- **Owner role:** Eng + Data.
- **KPI:** Upload success rate; % files parsed without manual file edits.
- **Quick win:** Add explicit “rows dropped and why” table.
- **Definition of Done:** 90% success on internal messy-file test set and clear user-readable QC output.

### Step 2: Evidence-Scoped Annotation Layer
- **Deliverable:** Annotation module that links flagged patterns to evidence snippets (rule-based first, RAG optional behind flag).
- **Owner role:** Data + Clinical SME.
- **KPI:** Citation coverage (% claims with source); annotation precision proxy on test set.
- **Quick win:** Start with 10 high-confidence, manually vetted evidence cards.
- **Definition of Done:** Every surfaced claim has citation metadata and confidence tier (High/Med/Low).

### Step 3: Insight Composer with Uncertainty UX
- **Deliverable:** Structured insight output with claim, confidence, caveats, and “questions for clinician.”
- **Owner role:** PM + Clinical SME + Compliance.
- **KPI:** User comprehension score; % users correctly identifying non-diagnostic nature.
- **Quick win:** Add fixed disclaimer block and non-medical language lint check in templates.
- **Definition of Done:** Role-based outputs (consumer/practitioner) pass compliance review and comprehension testing.

### Step 4: Action Plan + “Do Next” Recommendations
- **Deliverable:** Safe action options (monitoring, discuss with clinician, lifestyle tracking) without medical prescriptions.
- **Owner role:** PM + Clinical SME.
- **KPI:** Time-to-insight; % users who can state next step in <60 seconds.
- **Quick win:** Generate a one-click “discussion brief” export.
- **Definition of Done:** Action section includes bounded options, caveats, and escalation trigger language.

### Step 5: Evaluation Harness + Demo Instrumentation
- **Deliverable:** Lightweight eval suite and analytics events for upload→insight funnel.
- **Owner role:** Eng + PM + Compliance.
- **KPI:** Citation quality, abstention rate on unsupported claims, end-to-end completion time.
- **Quick win:** Add event logging for each workflow stage and failed-state reasons.
- **Definition of Done:** 90-second demo reliably runs with measurable KPIs and documented risk controls.

---

## METHYL-3 — Hidden Assumptions

1. **Assumption:** Rule-based flags reflect meaningful biological signals.
   - **Why it matters:** Core product value depends on relevance.
   - **How it fails:** Statistical artifacts are treated as insight.
   - **Harm/risk:** User anxiety or false reassurance.
   - **Guardrail + test:** Require minimum evidence threshold and reviewer checks against known reference cases.

2. **Assumption:** Insights generalize across populations and assay contexts.
   - **Why it matters:** Users vary by age, ancestry, platform, and health context.
   - **How it fails:** Same pattern means different things across cohorts.
   - **Harm/risk:** Biased or invalid guidance.
   - **Guardrail + test:** Add cohort applicability tags and holdout tests across demographic strata.

3. **Assumption:** Confounders are negligible for MVP interpretation.
   - **Why it matters:** Methylation is highly context-sensitive.
   - **How it fails:** Medication/lifestyle/comorbidity effects are ignored.
   - **Harm/risk:** Misattribution of cause and poor decisions.
   - **Guardrail + test:** Add confounder intake checklist and “insufficient context” abstention when missing.

4. **Assumption:** Users will treat recommendations as educational, not prescriptive.
   - **Why it matters:** Real behavior determines safety outcomes.
   - **How it fails:** Users act directly without clinician consultation.
   - **Harm/risk:** Unsafe self-management.
   - **Guardrail + test:** Force “discuss with clinician” callout and test user interpretation in scenario-based studies.

5. **Assumption:** Citation presence equals trustworthiness.
   - **Why it matters:** Poor citations can still mislead.
   - **How it fails:** Irrelevant or weak evidence is cited superficially.
   - **Harm/risk:** False confidence in weak claims.
   - **Guardrail + test:** Citation quality rubric (relevance, recency, evidence tier) and periodic audit.

---

## METHYL-4 — Compare Opposing Views

### Shared ground
- Better data readability helps both consumers and clinicians.
- Uncertainty must be explicit.
- Product should avoid diagnostic/treatment claims.

### Core disagreements
- **Optimist view:** Personalized insights drive engagement and behavior change even with partial evidence.
- **Conservative view:** Partial evidence is precisely why outputs should be tightly bounded and sometimes withheld.

### Context where each is right
- **Optimism is right when:** Goal is habit formation, journaling, trend awareness, and clinician conversation prep.
- **Conservatism is right when:** Users may take irreversible actions or when evidence/confounder context is weak.

### Combined safety + usefulness policy
- **Will claim:** “We organize methylation data, highlight patterns, and provide evidence-linked discussion prompts.”
- **Will not claim:** “We diagnose conditions, predict treatment response, or prescribe interventions.”
- **Operational rule:** If evidence quality is low or context is missing, default to abstain + explain uncertainty + suggest professional follow-up.

---

## METHYL-5 — Distill for Role: Compliance/Legal

### 3 takeaways they care about
1. Product currently aligns best as educational decision support.
2. Main legal risk is user overinterpretation of non-diagnostic outputs.
3. Future RAG must be constrained by citation and abstention controls.

### 3 questions they’ll ask
1. Which exact claims appear in UI, exports, and marketing?
2. What guardrails prevent prescriptive/clinical language?
3. How are sensitive uploads handled, stored, and logged?

### 3 decisions they need to make
1. Approve or reject claim taxonomy (allowed vs prohibited claims).
2. Define mandatory disclaimer placement and wording.
3. Set release gate criteria for AI-generated outputs.

### Inputs needed from them
- Claim policy matrix.
- Jurisdiction-specific wording requirements.
- Required privacy disclosures and retention policy.

### Red lines / disclaimers they require
- No diagnosis, treatment, or supplement prescription language.
- Clear educational-use disclaimer on every insight surface.
- Mandatory clinician-consultation language for potentially high-risk outputs.

---

## METHYL-6 — Reusable Interpretation Framework

### Stage 1: Upload
- **Inputs:** User file (CSV/TSV/TXT), optional metadata.
- **Outputs:** Parsed dataset preview + schema status.
- **Confidence scoring:** High if required fields present and parse clean.
- **Citation requirements:** N/A (operational stage).

### Stage 2: QC
- **Inputs:** Parsed table.
- **Outputs:** Quality report (missingness, coercions, dropped rows, range checks).
- **Confidence scoring:** High/Med/Low based on data completeness and validity.
- **Citation requirements:** Cite QC rules/version used.

### Stage 3: Annotation
- **Inputs:** QC-passed records.
- **Outputs:** Annotated features/flags with evidence links.
- **Confidence scoring:** Based on evidence tier + context match.
- **Citation requirements:** Source for each annotation claim.

### Stage 4: Evidence Ranking
- **Inputs:** Candidate claims and references.
- **Outputs:** Ranked evidence set (tiered strength).
- **Confidence scoring:** High (systematic/consensus), Med (cohort/replicated), Low (exploratory).
- **Citation requirements:** Study type, year, and relevance note.

### Stage 5: Insight
- **Inputs:** Ranked evidence + user context.
- **Outputs:** Structured insights with caveats.
- **Confidence scoring:** Minimum of data quality score and evidence score.
- **Citation requirements:** Every factual claim must map to at least one ranked source.

### Stage 6: Action Options
- **Inputs:** Insights and risk policy.
- **Outputs:** Safe next steps (monitor, discuss, track) and escalation guidance.
- **Confidence scoring:** High only for low-risk process advice; otherwise Med/Low.
- **Citation requirements:** Cite policy/risk logic used for recommendation category.

### Stage 7: Follow-up Tracking
- **Inputs:** Prior report, user notes, repeat uploads.
- **Outputs:** Trend summary and unresolved questions.
- **Confidence scoring:** Based on longitudinal consistency and data quality.
- **Citation requirements:** Cite prior report IDs and date-stamped evidence context.

### Reusable Insight Card Template
- **Claim:**
- **Why it surfaced:**
- **Evidence (with citations):**
- **Evidence tier:**
- **Confidence (H/M/L):**
- **What this does *not* mean:**
- **Action options (non-prescriptive):**
- **Questions to discuss with clinician:**
- **Caveats / confounders considered:**
- **Review date / follow-up trigger:**

---

## METHYL-7 — Contrarian but Credible Takeaways

1. Better QC UX may improve health outcomes more than better models.
   - **What would change my mind:** If model upgrades beat QC upgrades on comprehension and safe action metrics.
   - **Experiment:** 2x2 test (basic/advanced model × basic/advanced QC UX).

2. Citation volume can decrease trust if users cannot interpret evidence quality.
   - **What would change my mind:** If more citations consistently raise comprehension and appropriate confidence.
   - **Experiment:** Compare 1 high-quality citation vs 5 mixed citations with user trust surveys.

3. “Abstain” responses may increase long-term retention more than always-on answers.
   - **What would change my mind:** If abstention correlates with churn and lower trust.
   - **Experiment:** Randomize abstention style and track 30-day return + NPS.

4. Role-specific reports are likely higher leverage than personalization algorithms.
   - **What would change my mind:** If algorithmic personalization outperforms role templates on decision quality.
   - **Experiment:** Role-template arm vs personalization arm with standardized tasks.

5. Most perceived value comes from “what to do next,” not molecular detail depth.
   - **What would change my mind:** If deeper molecular detail improves action quality.
   - **Experiment:** Action-focused report vs detail-heavy report; measure next-step clarity.

6. Threshold sliders can create false precision unless uncertainty is co-displayed.
   - **What would change my mind:** If plain thresholds do not increase overconfidence.
   - **Experiment:** Slider-only vs slider+uncertainty annotations; assess confidence calibration.

7. Compliance-first language can improve, not reduce, conversion in health contexts.
   - **What would change my mind:** If stricter language harms engagement without safety gains.
   - **Experiment:** Compliance-first copy vs growth copy; compare completion and misuse proxies.

---

## METHYL-8 — Leverage Points

### Leverage Point 1: Uncertainty UX blocks
- **Small action:** Add a fixed “Confidence + Caveats” block to every insight.
- **Why it compounds:** Trains users to interpret outputs probabilistically.
- **KPI moved:** User comprehension and misuse reduction.
- **7-day validation experiment:** Launch to 20 users and measure correct interpretation rate before/after.

### Leverage Point 2: Citation grounding minimums
- **Small action:** Require at least one high-relevance citation or explicit abstain.
- **Why it compounds:** Prevents unsupported claims from entering user flow.
- **KPI moved:** Citation quality and trust calibration.
- **7-day validation experiment:** Audit 50 generated insights for citation pass rate and reviewer agreement.

### Leverage Point 3: One-click “Do Next” brief
- **Small action:** Add export section: “3 safe next steps + 3 clinician questions.”
- **Why it compounds:** Converts passive reading into productive follow-up behavior.
- **KPI moved:** Time-to-insight and actionability score.
- **7-day validation experiment:** Measure export usage and self-reported next-step clarity.
