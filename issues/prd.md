# Stewardship Sam: Product Requirements Document

HackMIT MVP | GiveCampus | Core question: **Where should I spend Tuesday?**

> Canonical, machine-readable copy of `Stewardship_Sam_PRD.pdf`. The body preserves the PDF's substance and adds stable IDs (SC, SIG, ACT, UX, G, AQ) so issues can cite requirements precisely. Appendices A to C were added during issue breakdown: frozen constants, verified data facts, and a change log. Where an appendix conflicts with the body, the appendix wins.

## ID index

| Prefix | Meaning | Defined in |
| --- | --- | --- |
| SC1 to SC8 | Success criteria | Section 18 |
| SIG1 to SIG6 | Detection signals | Section 7 |
| ACT1 to ACT8 | Recommendation actions | Section 9 |
| UX1 to UX3 | Screens | Section 11 |
| G1 to G6 | Guardrails | Section 17 |
| AQ1 to AQ6 | Ask Sam query patterns | Section 12 |

---

## 1. Product Summary

**One-line description.** Stewardship Sam is a relationship intelligence agent that continuously monitors constituent and community relationships, detects where human attention is needed, explains why, and recommends the appropriate next action.

**Product thesis.** Advancement teams do not only have a prioritization problem. They have a relationship-attention problem. Thousands of constituents generate signals across gifts, interactions, activities, affiliations, events, careers, and fundraising opportunities. A gift officer cannot continuously monitor all of them.

Traditional approaches ask: who is most likely to donate? Sam asks: what relationships need our attention right now, and why?

Sam's constrained action vocabulary is: THANK, FOLLOW UP, RECONNECT, ASSIGN, INVITE, ADVOCATE, ASK, WAIT.

The objective is not to maximize contacts. It is to help fundraisers make more appropriate and meaningful contacts.

## 2. Challenge Alignment

The GiveCampus challenge asks teams to help fundraising teams determine who should be reached out to, and why. It emphasizes judgment about the job: a gift officer has limited time and thousands of people on their list.

Stewardship Sam transforms a large constituent database into a small, explainable queue of relationships requiring attention. Rather than only returning the people with the highest predicted donation probability, Sam can identify relationships needing a thank-you, a promised follow-up, reconnection, assignment, invitation, advocacy opportunity, solicitation, or deliberate pause.

## 3. Problem and Dataset Evidence

| Signal | Dataset evidence (as stated in the PDF) | Interpretation | Likely action |
| --- | --- | --- | --- |
| Stewardship gap | 1,557 recent donors; only 23 have any recorded acknowledgement/stewardship interaction | A recent gift may lack visible stewardship in the available record | THANK |
| Neglected relationship | 193 living constituents with $10K+ lifetime giving; 79 have recorded interaction; 61 assigned | Important relationships may lack ownership or recent human attention | ASSIGN / RECONNECT |
| Broken commitment | 40 interactions have overdue follow-up dates | The institution appears to have created an expectation of follow-up | FOLLOW UP |
| Contact pressure | At least 8 people received 3+ outbound interactions in roughly the final two months | Some relationships may need space | WAIT |
| Community cooling | Alumni Board: ~180 members, 59% ever gave, 9% recent giving, 21% recent interaction | Historically connected community may be cooling | RE-ENGAGE |

**Caveat.** Missing records are not proof an action never occurred. Sam must say "no stewardship interaction is recorded" rather than "this donor was never thanked." Associations between community participation and giving are descriptive, not causal. See Appendix B for figures re-verified against the dataset.

## 4. Product Philosophy

- **Relationships, not rows.** A constituent should be understood through both individual history and institutional context: activities, affiliations, degrees, class year, events, employers, funds, campaigns, gifts, and interactions.
- **Attention, not contact volume.** Sam should not optimize for the number of emails, calls, or solicitations. WAIT is a valid recommendation when a relationship is already receiving sufficient attention.
- **Evidence before recommendation.** Every recommendation must answer: why am I seeing this? The UI should expose observable evidence instead of relying on an opaque relationship score.
- **AI backstage, humans in the relationship.** For the MVP, Sam performs detect, analyze, explain, recommend, prepare. The fundraiser decides whether to act. Sam does not autonomously contact constituents.

## 5. Sociology and Network Foundation

- **Embeddedness.** Constituents are embedded in institutional communities rather than existing as isolated donor rows. Their connection to the institution may include teams, clubs, departments, class cohorts, alumni groups, events, workplaces, geographic communities, and causes.
- **Social capital.** Financial contribution is only one form of institutional value. Someone may give relatively little while spanning multiple communities. That may make INVITE or ADVOCATE more appropriate than ASK.
- **Weak ties and brokerage.** Network structure can reveal people who span otherwise separated institutional contexts. Sam may identify a constituent as a potential connector based on observed community overlap, but must not infer friendship or social influence that the dataset does not establish.
- **Micro and meso levels.** At the micro level, Sam asks what an individual relationship needs. At the meso level, Sam asks what is happening to a community's relationship with the institution and which observed institutional connectors may help a fundraiser understand or re-engage that community.

## 6. Graph Data Model

Node types: Constituent; Activity / Affiliation; Degree / Major / Class Year; Event; Employer; Fund / Campaign.

Example edge types: Person participated_in Activity; Person affiliated_with Organization; Person studied Major; Person graduated_in Class Year; Person attended Event; Person works_at Employer; Person donated_to Fund; Person donated_via Campaign.

Interactions and gifts additionally provide temporal relationship events. An edge represents an observed institutional relationship or shared context, not necessarily a direct social relationship between two constituents.

## 7. Core Detection Engine

### SIG1: Stewardship Gap

Question: did someone recently give without subsequent stewardship appearing in the available relationship record?

```
IF received gift is recent
AND no subsequent acknowledgement/stewardship interaction is recorded
THEN surface Stewardship Gap -> THANK
```

Example: Valerie Kaur gave $25,000 on Feb. 4. No subsequent stewardship interaction is recorded. Phone contact is unavailable. Sam recommends a personal thank-you via an allowed channel.

### SIG2: Broken Commitment

Question: did the institution indicate it would follow up but apparently fail to do so?

```
IF interaction.follow_up_date < current date
AND no subsequent interaction resolves the follow-up
THEN Broken Commitment -> FOLLOW UP
```

These should generally rank highly because an explicit expectation already exists. The resolution rule is frozen in Appendix A.

### SIG3: Neglected Relationship

Question: does an established relationship appear to lack sufficient human attention?

- Meaningful historical giving or engagement
- Long interaction gap
- No assigned fundraiser
- Previous opportunities or repeated institutional involvement

Typical recommendations: ASSIGN or RECONNECT. ASK should only appear when additional context supports solicitation.

### SIG4: Relationship Change

Question: has something changed that creates an appropriate reason to reconnect?

- Career change
- Recent event attendance
- New gift
- Changed affiliation
- New fundraising opportunity

A career change is contextual evidence for reconnection, not automatic evidence of increased wealth or capacity.

### SIG5: Contact Pressure

Question: are we interacting with someone too frequently?

```
IF recent contact count exceeds threshold
OR proposed channel violates a restriction
OR another interaction is already scheduled
THEN WAIT
```

WAIT demonstrates judgment: a highly engaged or high-capacity constituent should not automatically receive more outreach.

### SIG6: Community Cooling

Question: are institutional communities showing weakening recent connection relative to their historical relationship?

- Historical giving rate
- Recent giving rate
- Historical and recent event participation
- Interaction recency
- Stewardship coverage
- Assignment coverage
- Member count

For a cooling community, Sam may recommend INVITE, RECONNECT, or ADVOCATE before another broad solicitation. The detection rule is frozen in Appendix A.

## 8. Community Connector Analysis

Connector analysis supports Community Cooling (SIG6) rather than serving as a separate alert category. MVP techniques can include membership overlap, degree centrality, and betweenness centrality.

Good language: "Sarah spans three relevant institutional communities." Avoid unsupported claims such as "Sarah is highly influential." (See G5.)

## 9. Recommendation Vocabulary

| ID | Action | Meaning |
| --- | --- | --- |
| ACT1 | THANK | Steward a recent contribution |
| ACT2 | FOLLOW UP | Fulfill an existing commitment |
| ACT3 | RECONNECT | Restore an inactive relationship |
| ACT4 | ASSIGN | Give the relationship a human owner |
| ACT5 | INVITE | Create a non-solicitation engagement opportunity |
| ACT6 | ADVOCATE | Consider constituent for community participation |
| ACT7 | ASK | Consider solicitation |
| ACT8 | WAIT | Deliberately avoid additional outreach |

## 10. Prioritization

Detection alone does not answer where a fundraiser should spend Tuesday. Sam therefore creates a priority queue using transparent factors rather than presenting a magic score.

| Dimension | Example evidence |
| --- | --- |
| Urgency | Overdue promised follow-up, recent significant gift, upcoming event |
| Relationship history | Historical giving, repeated engagement, event participation |
| Attention deficit | No assignment, no recent interaction, no recorded stewardship |
| Community context | Member of cooling community, overlaps multiple institutional contexts |
| Contact pressure | Recent outreach suppresses unnecessary additional contact |

Internal ranking values may exist, but the UI should emphasize the evidence that caused a relationship to surface.

## 11. Primary UX

Sam is an internal advancement-team product. There is no donor-facing Sam interface in the MVP.

Core navigation: Today, Relationship, Community, with Ask Sam persistent across the experience.

### UX1: Today

Purpose: answer "Where does my attention matter today?" The homepage presents a prioritized work queue with action labels, concise evidence, and drill-down links.

Example mock:

```
STEWARDSHIP SAM                                   Ask Sam...

Good morning, Maya.
14 relationships need your attention today.
3 Follow-ups | 7 Stewardship | 1 Community | 3 Reconnect

Isaac Chen            FOLLOW UP
  Replied to cultivation email
  Follow-up promised May 15 · overdue           [View relationship]

Valerie Kaur          THANK
  $25,000 gift · Feb 4
  No subsequent stewardship interaction recorded [View relationship]

Alumni Board          RE-ENGAGE
  59% historical giving -> 9% recent giving
  21% recently engaged                           [Explore community]
```

Requirements: prioritize signals, identify the action category, show 1 to 3 evidence points, distinguish people from communities, support dismissal, and allow drill-down. (Note: the Isaac Chen mock does not match the data; see Appendix B.)

### UX2: Relationship View

Purpose: answer "Why does this person's relationship need attention?"

- Header: name, class/year, relevant affiliations, location if available, assigned fundraiser, recommended action
- Why Sam surfaced this: concise evidence card
- Relationship timeline: gifts, interactions, events, career changes, and key moments
- Community context: visible institutional memberships
- Action controls: prepare action or dismiss

The screen should feel like a relationship narrative, not a propensity-score dashboard.

### UX3: Community View

Purpose: answer "What is happening to this community?" This is the signature visualization.

- Community header with member count and historical/recent engagement metrics
- Interactive network visualization
- Potential connectors based on observed overlap
- Sam explanation of why the community surfaced
- Actions such as Explore Members and Plan Engagement

The graph should support a decision rather than serve as the homepage. Sam performs the analysis first; the visualization lets the fundraiser inspect the evidence.

## 12. Ask Sam

Natural language is an interface into the system, not the entire product. The ideal behavior is: natural language, then structured query, then UI change plus explanation.

| ID | Query |
| --- | --- |
| AQ1 | Who have we promised to follow up with? |
| AQ2 | Show major donors without an assigned officer. |
| AQ3 | Which communities are losing engagement? |
| AQ4 | Who shouldn't I contact today? |
| AQ5 | Why did Valerie surface? |
| AQ6 | Show Boston alumni connected to athletics. |

Pipeline: natural-language intent extraction, structured query, relationship/graph engine results, UI update plus explanation.

## 13. AI vs Deterministic Responsibilities

| LLM / AI | Deterministic data + graph logic |
| --- | --- |
| Interpret natural-language questions | Gift totals and dates |
| Generate evidence-grounded explanations | Contact counts and assignment status |
| Extract structured information from notes | Overdue follow-ups and stewardship detection |
| Summarize relationship timelines | Community metrics and graph construction |
| Translate analysis into understandable language | Centrality, contact-policy rules, ranking features |

The LLM should not be asked to inspect the raw dataset and guess who is important. Analytical code computes evidence; the LLM helps the fundraiser interrogate and understand it.

## 14. Technical Architecture

```
GIVECAMPUS DATA
  -> DATA NORMALIZATION
  -> Relationship Engine (temporal signals, follow-ups, stewardship, contact pressure)
  -> Graph Engine (communities, overlap, centrality, connectors)
  -> SIGNAL ENGINE
  -> PRIORITY + POLICY ENGINE
  -> OPENAI (query interpretation + grounded explanation)
  -> STEWARDSHIP SAM UI (Today / Relationship / Community)
```

Hackathon implementation can use relational data or DataFrames, NetworkX for graph analysis, a FastAPI backend, OpenAI for query interpretation and explanations, React/Next.js for UI, and a graph visualization library such as Cytoscape, D3, or React Flow. A dedicated graph database is not required for the MVP.

## 15. Optional Voice Layer

Voice is secondary. If implemented, a speech layer can support fundraiser-side queries such as "Who needs my attention today?" or capture post-call notes.

Example voice note: "Sarah isn't ready to give again. She's interested in the Boston alumni event, prefers texts, and I told her I'd follow up in November."

Sam can extract structured relationship memory: Interest = Boston alumni events; Communication preference = Text; Solicitation status = Not currently interested; Follow-up = November.

This creates a feedback loop: data, Sam insight, human conversation, voice note, structured relationship memory, better future insight.

## 16. Human-in-the-Loop Boundary

| Sam may | Sam may not autonomously |
| --- | --- |
| Monitor, detect, prioritize | Solicit a donor |
| Explain and recommend | Send donor-facing messages |
| Draft or prepare actions | Call constituents |
| Filter and visualize | Alter assignments or create commitments |

Donor-facing actions require fundraiser confirmation in the MVP.

## 17. Guardrails

- **G1.** Explicit contact restrictions override recommendations.
- **G2.** Recent interaction/contact pressure can suppress unnecessary recommendations.
- **G3.** Existing fundraiser ownership should be surfaced before suggesting action.
- **G4.** Missing data must be represented as missing, not converted into certainty.
- **G5.** Community overlap cannot be described as friendship or influence without evidence.
- **G6.** Career changes provide contextual reasons to reconnect, not automatic conclusions about wealth or donation capacity.

## 18. Success Criteria

- **SC1.** A fundraiser opens Sam and immediately sees where attention may be needed.
- **SC2.** They understand why each relationship surfaced.
- **SC3.** They can identify an appropriate next action.
- **SC4.** They can inspect a person's relationship history and institutional context.
- **SC5.** They can explore a community experiencing changing engagement.
- **SC6.** They can identify potential connectors based on observed institutional overlap.
- **SC7.** They can query the underlying data using natural language.
- **SC8.** Sam can deliberately recommend WAIT when additional outreach is inappropriate.

Demo UX goal: a judge should understand any recommendation within roughly 30 seconds without needing the team to explain the algorithm verbally.

## 19. MVP Scope

**Must build**

- Today Queue with at least Stewardship Gap, Broken Commitment, Neglected Relationship, and Contact Pressure
- Relationship View with evidence, timeline, communities, and recommendation
- Community View for at least one real community with historical/recent metrics and network visualization
- Ask Sam with several working query patterns backed by real data
- Explainability for every recommendation

**Should build**

- All six signal detectors
- Career-change detection
- Community cooling across explicit communities
- Interactive graph and connector analysis
- Filters and action preparation
- Optional fundraiser-side voice queries or post-call note extraction

**Stretch**

- Algorithmic community detection
- More sophisticated temporal community-health modeling
- Graph embeddings
- Learning from fundraiser acceptance/rejection
- Institution-specific thresholds
- Portfolio-level analytics

## 20. Explicit Non-Goals

Replacement CRM; generic chatbot over CSVs; email-writing product; autonomous robocaller; wealth-scoring engine; donor-likelihood leaderboard; mass outreach system; replacement for existing GiveCampus research/event/outreach agents; opaque relationship score.

## 21. Position in the GiveCampus AI Ecosystem

Sam's role is continuous relationship monitoring. Existing tools can discover prospects, research individuals, prepare fundraisers for events, or execute outreach. Sam asks a different question: where are relationships falling through the cracks, and where does human attention matter? Sam can eventually hand recommendations into existing GiveCampus workflows rather than replacing them.

## 22. Why Sam Is an Agent

Observe, detect, prioritize, check context, recommend, explain, human acts, observe outcome, repeat.

Sam's job description: make sure important institutional relationships do not quietly fall through the cracks.

## 23. Demo Narrative

1. Open Today: "GiveCampus gave us a database of nearly 20,000 people who care about a school. A fundraiser cannot pay attention to 20,000 relationships at once."
2. Broken promise: open the overdue follow-up. Action: FOLLOW UP. (The PDF names Isaac Chen; Appendix B replaces this with Nia Chen and uses Isaac as the control.)
3. Stewardship: open Valerie. Show a recent $25,000 gift with no subsequent stewardship interaction recorded. Action: THANK.
4. Restraint: open Kieran. Show heavy recent outbound contact. Action: WAIT. Explain that Sam is not trying to maximize outreach.
5. Community: ask "Which communities are we losing touch with?" Open Alumni Board and show the network, declining recent engagement, and potential connectors.
6. Close on Today: "Fundraising isn't just about finding the next donor. It's about tending the relationships you already have."

## 24. Core Product Loop

Observe (what changed?), detect (where is attention needed?), understand (why does it matter?), decide (THANK, FOLLOW UP, RECONNECT, ASSIGN, INVITE, ADVOCATE, ASK, WAIT), human acts, record outcome, observe again.

## 25. North-Star Principle

Stewardship Sam should never make a fundraiser contact more people simply because AI makes contact cheaper. It should help them identify the smaller number of relationships where thoughtful human attention matters most.

---

# Appendix A: Frozen implementation constants (added)

All thresholds live in one configuration module and are imported everywhere. No slice may hard-code them. Values are defaults chosen to be explainable and verifiable against the dataset; they can be tuned later but must change in one place.

**Population and dates**

| Constant | Value | Notes |
| --- | --- | --- |
| `AS_OF_DATE` | 2026-08-31 | "Today" for every calculation. It is the latest date in the dataset. Never use the system clock. |
| Population | `entity_type = individual`, `deceased = false` | Organizations are excluded from queues and community metrics. |
| Received gift | `gifts.status = paid` and `gift_type != recurring_parent` | Recurring parents are commitments, not cash. Installments count. |
| Date comparisons | Calendar-date granularity | An interaction on the same date as a gift or follow-up date counts as on or after it. |

**Signal windows and thresholds**

| Constant | Value | Used by |
| --- | --- | --- |
| `RECENT_GIFT_WINDOW_DAYS` | 365 | SIG1: a gift is recent if it is within 365 days of `AS_OF_DATE`. |
| `STEWARDSHIP_PURPOSES` | `acknowledgement`, `stewardship` | SIG1: interaction purposes that count as stewardship. |
| `CONTACT_PRESSURE_WINDOW_DAYS` | 60 | SIG5 |
| `CONTACT_PRESSURE_MIN_OUTBOUND` | 3 | SIG5: 3 or more outbound interactions in the window triggers WAIT. |
| `RECENT_CONTACT_SUPPRESSION_DAYS` | 14 | G2: any outbound interaction in the last 14 days suppresses new THANK, RECONNECT, INVITE, and ASK recommendations. It does not suppress an overdue FOLLOW UP. |
| `MAJOR_DONOR_LIFETIME_USD` | 10,000 | SIG3, AQ2 |
| `LONG_INTERACTION_GAP_DAYS` | 730 | SIG3: no recorded interaction within 730 days (or ever). |
| `RELATIONSHIP_CHANGE_WINDOW_DAYS` | 180 | SIG4: a career change, event attendance, new gift, or changed affiliation is "recent" within 180 days. |
| `RECENT_GIVING_WINDOW_DAYS` | 365 | SIG6 |
| `RECENT_ENGAGEMENT_WINDOW_DAYS` | 730 | SIG6: recent engagement rate is the share of members with at least one recorded interaction (any type, direction, or outcome) in the window. Event participation is reported separately. |
| `TODAY_QUEUE_MAX_ITEMS` | 15 | UX1 |
| `COMMUNITY_GRAPH_MAX_NODES` | 150 | UX3 visualization cap |

**SIG2 resolution rule (frozen).** An interaction with a `follow_up_date` on or before `AS_OF_DATE` creates a due commitment. The commitment is *resolved* when a subsequent interaction with that constituent occurs on or after the promised follow-up date, or when the source data explicitly indicates the commitment was completed or cancelled. This dataset has no completed/cancelled field, so only the first clause applies; the implementation must leave a documented hook for the second. When resolution cannot be established, Sam says "No subsequent follow-up is recorded." Follow-up dates after `AS_OF_DATE` are upcoming, not broken.

**SIG3 rule (frozen).** Surface when the person is in the population, has lifetime received giving of at least `MAJOR_DONOR_LIFETIME_USD`, has no recorded interaction within `LONG_INTERACTION_GAP_DAYS` (or ever), and is either unassigned or assigned to an inactive staff member (treated as unassigned). Recommend ASSIGN if unassigned, RECONNECT if assigned. ASK is never produced by SIG3 alone (G1, G3).

**SIG6 rule (frozen).** Communities are activities (`activities.activity_name`) with at least `COMMUNITY_MIN_MEMBERS` = 60 eligible members. For each, compute the historical giving rate (share of members with at least one received gift ever) and the recent giving rate (share with a received gift within `RECENT_GIVING_WINDOW_DAYS`). A community is *cooling* when its historical giving rate is at or above the median across eligible communities and its recent-to-historical giving ratio is at or below the 25th percentile across eligible communities. Recent interaction rate, event participation, stewardship coverage, and assignment coverage are reported as supporting evidence, not as gates. Initial action rule: RECONNECT by default; INVITE when an upcoming event exists; ADVOCATE only once connector analysis can name at least one connector.

**Language rules (from G4, G5, G6).** Say "no stewardship interaction is recorded", never "was never thanked". Say "spans N communities", never "influential" or "friends with". Describe career changes as a reason to reconnect, never as evidence of wealth or capacity.

# Appendix B: Verified data facts and demo cast (added)

Computed against the provided dataset with the constants above. Tests should reproduce these values or document why they differ.

| Item | Verified value |
| --- | --- |
| Individuals with a recent received gift | 1,530 (the PDF's 1,557 includes organizations) |
| Of those, with no stewardship interaction on or after the gift | 1,508 |
| Living individuals with lifetime giving of $10,000 or more | 191 |
| Of those, no interaction within 730 days or ever | 116 |
| Of those, also unassigned | 101 |
| Interactions with a follow-up date due by `AS_OF_DATE` | 40 |
| Of those, unresolved under the SIG2 rule | 1 (Nia Chen) |
| People with 3 or more outbound interactions in the last 60 days | 8 |
| Communities with at least 60 eligible members | 79 |
| Cooling communities under the SIG6 rule | 12, including Alumni Board |
| Alumni Board (individuals, non-deceased) | 180 members; 58.9% ever gave; 8.9% gave in the last 365 days; 20.6% had an interaction in the last 730 days |

**Demo cast**

| Person | Role in demo | Facts |
| --- | --- | --- |
| Valerie Kaur (constituent 2669) | THANK | One-time gift of $25,000 on 2026-02-04. No interactions on record at all. Phone status `do_not_call`; email deliverable, so the allowed channel is email. Assigned to staff 1. |
| Nia Chen (constituent 14456) | FOLLOW UP (positive example) | Outbound call on 2026-03-15, purpose solicitation, outcome no_response, follow-up date 2026-05-01. No later interaction. Assigned to staff 1. Phone available; email inactive. |
| Isaac Chen (constituent 2548) | Control example: commitment kept | Email reply on 2026-03-18 with follow-up date 2026-05-15. A meeting occurred on 2026-05-15 (meeting_booked), followed by contacts on 2026-06-13 and 2026-07-22. A further follow-up dated 2026-12-01 is upcoming, not overdue. Assigned to staff 4. Email and phone status missing. Sam must NOT surface Isaac as a broken commitment. |
| Kieran Kaur (constituent 12022) | WAIT | 5 outbound stewardship interactions between 2026-07-28 and 2026-08-19 (call, email, call, email, meeting), all with outcome gift_received. Assigned to staff 5. Email deliverable; phone available. |
| Alumni Board | Community | See table above. Surfaces as cooling under the SIG6 rule. |

# Appendix C: Changes from the PDF (added)

1. Stable IDs added (SC, SIG, ACT, UX, G, AQ). AQ IDs are new; they label the six example questions in Section 12.
2. SIG2 resolution rule locked (Appendix A). Under it the data supports one broken commitment, not 40. The PDF's Today mock and demo narrative use Isaac Chen; the data shows his commitment was kept. Nia Chen is the positive example and Isaac is the control.
3. SIG6 detection rule locked (Appendix A). A simple "lowest recent interaction rate" rule does not surface Alumni Board (20.6% against a cutoff of about 18%). The giving-decay rule operationalizes the PDF's own "59% ever gave, 9% recent" framing and does surface it.
4. The Today mock labels the community item RE-ENGAGE, which is not in the constrained vocabulary (Section 9). Implement it as RECONNECT, INVITE, or ADVOCATE per the SIG6 action rule; RE-ENGAGE may remain as a display group heading only.
5. Today is a team-level queue with an optional officer filter. "Maya" is a configurable demo persona, not a staff record. Cast members belong to different officers.
6. The dataset has no phone numbers, no street addresses, no text-message interactions, and event data covering only September 2025 to June 2026. Sam must show these as missing or limited (G4).
7. Counts in Section 3 were computed on all constituents; Appendix B gives individuals-only values.
8. Contact-restriction flags are a current snapshot, so some historical outreach appears to conflict with them. That is a data caveat, not evidence of a violation.
