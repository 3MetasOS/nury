# Standards page: text for the app footer

Page-ready text for hack-artisans. Source and evidence: `documents/STANDARDS_ALIGNMENT.md` (read it for sources and the full gap list). Written 2026-10-07 by hack-ninja. Quoted standards are verbatim and must not be edited or humanized. Everything else is plain prose.

Suggested page title: **Standards**. Suggested footer link text: **Case management standards**.

---

## Intro

Nury is informed by case-management and trauma-informed practice. It gathers the facts, makes a plan, leaves every decision to the pastor and saves a record.

It is a drafting aid. It is not a professional case-management system, and it does not make the pastor a case manager. No standards body has reviewed, approved or endorsed Nury. This page says where Nury lines up with the standards, where it only partly does, and where it does not.

## How to read this page

- **Informed by** or **aligned with** means Nury does something that serves the standard's intent. It does not mean Nury meets the standard.
- Nury gives legal information and drafts. The pastor decides. Nury does not give advice, advocate or predict.
- Evidence names a feature you can open in the app, or a file in the repository.

## The NASW standards: what Nury does

The National Association of Social Workers published *NASW Standards for Social Work Case Management* in 2013. We read the full text. The standards bind social workers, not Nury and not pastors. We use them as a yardstick.

| Standard (NASW 2013) | What Nury does | What it does not do | Evidence |
|---|---|---|---|
| 1 Ethics and Values | A safety floor in code: no advice, no outcome predictions, no claim to be a pastor, lawyer or doctor. A disclaimer on every output. No send path. The pastor approves every stage. | Nury does not adhere to the NASW Code of Ethics. That code binds social workers. | Disclaimer on every output; approval gates |
| 2 Qualifications | Nothing. Nury is not a professional and says so on every output. | The pastor's own training is outside Nury. | Disclaimer on every output |
| 3 Knowledge | Vetted sources only: a reviewed rights file, an official list, approved hospital sources. Every point is cited. | No attorney or other professional has reviewed the sources. | Citation chips; `code/playbooks/*/sources/` |
| 4 Cultural and Linguistic Competence | Family output in Spanish or English. A language check blocks mixed-language drafts. | One language pair. No native-speaker review. The pastor's screens are English only. | Family-language output |
| 5 Assessment | The triage stage: situation, people, place, language, urgency with a reason, and three missing facts. | It does not capture the family's goals or strengths. No ongoing assessment. | Stage 1, Triage |
| 6 Service Planning, Implementation, and Monitoring | A five-stage plan and a next-steps map with four lanes (tonight, this week, questions open, who to call). Versions v1 to v2. The pastor can record what happened and a result. | No case status, follow-up date or measurable objectives. No check on what the family did. | Next-steps map; "What happened?" updates |
| 7 Advocacy and Leadership | Nothing, by design. Nury gives legal information only and never advocates. It lists official and church contacts. | This is a decision, not a gap. | Attorney resources stage |
| 8 Interdisciplinary and Interorganizational Collaboration | The pastor's church network and the official Department of Justice list, labeled, never ranked or endorsed. | One pastor's own contacts only. No shared cases, teams or roles. | Network page; "listed does not mean recommended" |
| 9 Practice Evaluation and Improvement | Four evaluation layers, scorecards and judge validation. | That evaluates the tool, not any case. Nothing tracks whether a family was helped. | Evaluation layers |
| 10 Record Keeping | A saved case of approved text only, a zip export, versions, an audit log with reason categories only, and tokens in place of names. | No case status, follow-up date or closing note. No log of who opened a case. No sign-in, no separation between churches and no encryption at rest, so the standard's word "secured" is not met. | Case page; audit view |
| 11 Workload Sustainability | Not applicable. | It is an organization's duty. | n/a |
| 12 Professional Development and Competence | Not applicable. | It is an individual's duty. | n/a |

### Quoted from the NASW standards

> "The social work case manager shall adhere to and promote the ethics and values of the social work profession, using the NASW Code of Ethics as a guide to ethical decision making in case management practice." (Standard 1)

> "...shall provide and facilitate access to culturally and linguistically appropriate services..." (Standard 4)

> "...shall engage clients... in an ongoing information-gathering and decision-making process to help clients identify their goals, strengths, and challenges." (Standard 5)

> "...shall document all case management activities in the appropriate client record in a timely manner. Social work documentation shall be recorded on paper or electronically and shall be prepared, completed, secured, maintained, and disclosed in accordance with regulatory, legislative, statutory, and organizational requirements." (Standard 10)

Source: NASW, *NASW Standards for Social Work Case Management*, 2013. Copyright National Association of Social Workers. Read from the copy at https://ovcsupport.org/wp-content/uploads/2019/06/standards-case-management.pdf.

## The six case-management functions and the five stages

The NASW document names six core functions: "engagement with clients", "assessment of client priorities, strengths, and challenges", "development and implementation of a care plan", "monitoring of service delivery", "evaluation of outcomes" and "closure (including termination or transition follow-up)".

| Function | Where it lives in Nury | How far it goes |
|---|---|---|
| Engagement | Stage 5, the pastoral message, and the pastor's own call. | Partly. The pastor engages the family. Nury only drafts a message and never speaks to the family. |
| Assessment | Stage 1, Triage. | Partly. Facts and urgency, yes. The family's goals and strengths, no. |
| Care plan | Stages 2, 3 and 4 (rights brief, attorney resources, checklist) and the next-steps map. | Yes, as a draft plan for the pastor to approve or edit. |
| Monitoring | The "What happened?" update form on a case. | Partly. The pastor records a step, a result and a note. There is no status and no follow-up date. |
| Evaluation of outcomes | A result label on each update. | Barely. Nury does not track whether the family was helped. |
| Closure | Not built. | No. There is no way to close a case with a note yet. |

## Trauma-informed practice

SAMHSA defines a trauma-informed program as one that "realizes the widespread impact of trauma and understands potential paths for recovery; recognizes the signs and symptoms of trauma in clients, families, staff, and others involved with the system; and responds by fully integrating knowledge about trauma into policies, procedures, and practices, while seeking to actively resist retraumatization." (SAMHSA, Trauma-Informed Approaches and Programs.)

| Principle (as SAMHSA lists them) | What Nury does | What it does not do |
|---|---|---|
| Safety | No send path. Names, phones, addresses and IDs become tokens before a request goes to the model. A leak test of 90 checks per playbook found none. | No sign-in, no encryption at rest, and one shared pool of cases. Data safety is partial. |
| Trustworthiness and Transparency | Approval gates, an audit view, citations, "Nury is an AI assistant" on every output, "listed does not mean recommended", and Jev and the AI voice disclosed. | |
| Peer support | The church network holds contacts the pastor has vetted. | No peer support for pastors or families. |
| Collaboration and Mutuality | The pastor edits every stage. | The family is never in the loop. The pastor mediates. |
| Empowerment, Voice and Choice | The pastor decides at each gate. The family's language is respected. | The family's own wishes are not recorded as such. |

SAMHSA's own page lists five principles. Some secondary sources name a sixth, cultural, historical and gender issues. We did not find it on SAMHSA's page. Nury has a humanitarian, non-political frame and Spanish output, and no cultural review of its drafts.

## Psychological first aid

The WHO describes psychological first aid as "humane, supportive and practical help to fellow human beings suffering serious crisis events" and "a framework for supporting people in ways that respect their dignity, culture and abilities." Look, listen and link is a common summary of the model, but we found it in a secondary source, not in the WHO page.

Nury helps with the "link" part: official and church contacts, hotlines, a checklist and a plain-language brief. The pastor does the listening. Nury does not listen to anyone, and it does not offer coping information or stabilization. Those are person-to-person acts.

## Confidentiality in pastoral care

Norms vary by tradition and by state law. We found no national standard that covers every pastor. One example is the code of the American Association of Pastoral Counselors, quoted by Duane R. Bidwell in *Sightings* (University of Chicago Divinity School, 2004): "We do not disclose client confidences to anyone, except: as mandated by law; to prevent a clear and immediate danger to someone; in the course of civil, criminal or disciplinary action arising from the counseling where the pastoral counselor is a defendant; for purposes of supervision or consultation..." That is a counselor code, not a rule for every pastor.

What Nury does: a pastor's private note on a contact never reaches a model or a family message. Tokens hide direct identifiers. There is no send path, so Nury cannot share anything by accident. A short consent and confidentiality note is in the app.

What Nury does not do: it does not state the limits (danger, mandated reporting) that the pastor remains responsible for, beyond that note. The pastor can still paste a copy anywhere. Nobody has reviewed the note against a standard. There is no access log and no sign-in.

## What we could not verify

- **CMSA.** The Case Management Society of America publishes *Standards of Practice for Case Management* (2022). The standards are behind a membership, and we did not pay or sign in. We read only the public page. We do not map Nury to any CMSA standard.
- **Look, listen, link and the eight core actions** are from a secondary source. We could not open the WHO guide's PDF or read NCTSN's list from NCTSN itself.
- **SAMHSA's sixth principle** is named in secondary sources only.
- **The AAPC code** is read through Bidwell's article, not from AAPC.
- **A DHS faith-community toolkit** was named in a search summary. We did not open it.

## The gaps we know

1. Case status and a follow-up date. Only a follow-up flag exists.
2. Closing a case, with a note.
3. Outcome tracking beyond a per-update label.
4. A record of who opened a case. Without sign-in it could say only when.
5. Sign-in, separation between churches and encryption at rest.
6. The family's own goals and strengths are not captured.
7. No native-speaker review of the Spanish, and no professional review of the sources.

## Closing line for the page

Nury is informed by these standards. It is not compliant with them, and nobody has certified it. Tested on synthetic families only. No real pastor has used Nury.
