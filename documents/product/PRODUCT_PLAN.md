# Nury: from hackathon tool to a product a church can use

Draft 2026-10-08 by hack-sensei, for Juan to decide. Part 1 is what to change in the app you see. Part 2 is what a church needs that the hackathon build does not have. Part 3 is a proposed order.
Facts below come from the current app (`code/app/static/`) and the facts table (`documents/product/ALIGNMENT_AUDIT.md`).

## Part 1. The app: what only makes sense at a hackathon

| # | What it is today | Why it is hackathon-only | Product change |
|---|---|---|---|
| 1 | Footer block "For judges and reviewers": How this was built, Observability, Self-improvement, What did not work, Economics, The pattern, Standards we use | Written for judges. A pastor does not need it, and it shows internal numbers. | Move to a "Trust" or "How Nury works" area, one page, plain words. The long pages go to a public docs site. |
| 2 | Footer text about Claude Sonnet 4.6, "20 named rules", Jev, Scripture sources | Technical detail, in a pastor's footer | One short line: "Checked before you see it. Nothing is sent unless you send it." Link to Trust. |
| 3 | "Recorded run" banner, replay mode, "Demo with a saved example", "Use the sample intake", "Try a sample" | Exists because judges had no Gloo key | Remove from the product. Keep a "Practice case" for training, labeled as practice, saved apart from real cases. |
| 4 | Checkbox "Demo: show a rejected-and-regenerated draft" | A stage trick for the demo | Remove from the pastor UI. Keep it as a developer flag. |
| 5 | Network page banner "Fictional demo contacts" and the demo network | Fake contacts | A real, empty network the church fills in. A guided "add your first contacts" start. |
| 6 | "Run your own case" page: "connect a Gloo key" | The pastor must not handle API keys | Remove. The church signs in and uses the service. The key lives on the server. |
| 7 | About page with the memorial and "Built to grow"; "Built in Boulder... Hackathon" provenance line | Story for judges | Product About: who it is for, what it does, what it does not do, the limits, who built it, contact. Memorial stays as a private choice of Juan. |
| 8 | Build log page, Observability, Self-improvement pages inside the app | Internal | Admin area for the church's tech contact, or removed. |
| 9 | Case header "Mode: Recorded run", "Your name" field on the case | Hackathon artifacts | Mode shows only for practice. Prepared-by comes from the signed-in user. |
| 10 | Home: "A family needs help" banner, handwritten notes (many) | Demo storytelling; some are good guidance | Keep the best two or three as first-use hints that fade after use. Remove the rest. |
| 11 | Only two crises live; two "Coming soon" cards | Fine, but "Coming soon" cards read as unfinished | Show only live crises; a quiet "Request a crisis type" link. |
| 12 | English UI only, Spanish output for families | Hackathon scope | Add a Spanish UI for pastors; then more family languages. |

## Part 2. What a church needs that we do not have

1. **Sign-in and accounts.** Today there is no login. A product needs church accounts, roles (pastor, assistant, admin) and a way to invite people.
2. **Hosting and storage.** Cases are plain local files. A product needs a hosted service, encrypted storage, backups, and a delete-my-data path.
3. **Privacy and legal.** Family details are sensitive. Needs a privacy policy, terms, data retention rules, a clear statement on what is stored, and legal review on the "legal information" line per state. Hospital cases touch health privacy rules; get advice before storing them.
4. **Real vetting of sources.** The rights brief uses a vetted source file we assembled. A product needs an owner for that content, a review by attorneys, an update schedule, and a visible "last reviewed" date.
5. **The network.** The church's own contacts need an easy editor, a verification step, and a clear label that Nury never endorses anyone.
6. **Reliability.** Model outages, rate limits and cost spikes. Needs monitoring, alerts, fallbacks, and a budget per church.
7. **Support.** A way to report a bad draft, a human to answer, and a feedback loop that reaches the rules.
8. **Learning loop.** Built but off. Turn on only with a pastor-approval screen, a record of every change, and a rollback.
9. **Model and vendor risk.** Claude through Gloo, Jev from TypeSafe. Get commercial terms for both and a plan if either changes.
10. **Pricing and distribution.** Who pays (church, denomination, network), per seat or per case, and a pilot with two or three pastors before any launch.
11. **Accessibility and mobile.** A pastor will use a phone at night. Test with real phones, large text, and low light.
12. **Evidence.** No real pastor has used Nury. The first product milestone is a small pilot and an honest report, including human ratings of warmth and accuracy.

## Part 3. Proposed order

- **Phase 0 (this week): decide.** Pick a first customer type (single church, denomination, or a legal-aid partner), a pilot size, and a hosting plan.
- **Phase 1 (2 to 3 weeks): clean the app.** Items 1 to 12 above. No new features. This makes the app look like a product.
- **Phase 2 (4 to 6 weeks): make it safe to host.** Accounts, hosted storage with encryption, privacy policy, error monitoring, delete path.
- **Phase 3 (pilot): 3 pastors, 4 weeks.** Real use, weekly check-ins, human review of every draft for the first 50 cases, written results.
- **Phase 4: offer.** Pricing, a one-page offer, and a public docs site that holds the "how it was built" material.

## Decisions I need from Juan
1. First customer type and whether the pilot is with churches you know.
2. Keep the judge pages as a public docs site, or retire them.
3. Hosting direction (managed cloud, or on your own infrastructure).
4. Who owns the legal source file and the attorney review.
5. Whether Phase 1 starts now, and who builds it (a new developer agent).
