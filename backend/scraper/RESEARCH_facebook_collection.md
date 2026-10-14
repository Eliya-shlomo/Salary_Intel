# Research: collecting salary posts from one Facebook group with low account risk

Researched 2026-10-14. This is not legal advice. Every claim has a source in brackets (see the Sources list). Labels used:
**[P]** = what a primary source states, **[A]** = practitioner reports (anecdotal, unverified), **[R]** = my own reasoning.

Scope rule: this document does not cover techniques for hiding automation or evading detection (stealth plugins, webdriver overrides, fingerprint or user-agent spoofing, proxy or IP rotation, CAPTCHA solving, account farms). Such techniques exist, and we exclude them by design. Meta's own Automated Data Collection Terms also require collectors to use identifiers "that identify your services" [S2].

---

## TL;DR

1. **Meta forbids what we are doing, with no exception for small scale.** The Terms (s.3.2.3) say "You may not access or collect data from our Products using automated means (without our prior permission)" [S1]. robots.txt disallows `/` for all unlisted agents [S3]. The Automated Data Collection Terms require "express written permission" [S2]. The sanction for a violation is suspension or disabling of the account (s.4.2) [S1]. Nothing we do can make this permitted. We can only make it low-volume, read-only and quick to stop.
2. **Meta names its detection levers, but not its thresholds.** It uses **rate limits** ("the number of times anyone can interact... in a given amount of time"), **data limits** ("more data than they should need to use our products normally"), and **"patterns in activity and behavior... typically associated with automated computer activity"** [S4]. Regulators report that platforms rate-limit "visits per hour or day by one account" and watch "how quickly and aggressively" accounts look at other users [S12]. **Total volume and frequency per account are the levers we control.**
3. **Our collector is detectable as automation by design**, because we do no concealment. We cannot get the risk to zero. The honest goal is a small footprint, fast stopping and no repeat after a warning.
4. **No sanctioned API path exists for a solo developer.** The Groups API was removed from all Graph API versions on 2024-04-22 [S6][S7]. CrowdTangle ended on 2024-08-14 [S9]. Meta Content Library covers public content only and requires an academic or non-profit research affiliation [S8][S10]. Download Your Information covers your own activity, not other members' posts [S11, secondary]. **The realistic legitimate alternative is to ask the group admin and members to submit salaries voluntarily**, for example through an anonymous form that the admin pins.
5. **Legal context (US):** *Meta v. Bright Data* (2024) held that Meta's Terms did not cover **logged-out** scraping of public data. The reasoning was that the Terms aim to stop account holders from "abusing their access" [S13][S14]. Our collection is **logged-in**, which is exactly where the Terms apply. *Meta v. BrandTotal* (2022) found breach of contract for logged-in collection [S15]. *hiQ* shows that the CFAA is weak against public scraping, but contract claims still win [S16][S17]. Our main exposure is contract and account loss, not hacking law.
6. **Privacy (Israel) is the bigger issue for the data itself.** After Amendment 13 (in force since 2025-08-14), "data of special sensitivity" explicitly includes **"Personal data about a person's salary and financial activity"** (s.3, item 10) [S19][S20]. "Identifiable" means identifiable "with reasonable effort, directly or indirectly" [S19]. Salary posts with employer, role and seniority can be identifiable even without a name. De-identification, minimization and short retention of raw files are therefore essential, not optional.
7. **Tighten the draft.** Allow 1 run/day and ≤3/week (now 3/day). Lower the hard max from 100 to 50 posts. Cap **posts examined and scroll steps**, not just matches. Collect incrementally (stop at the first already-seen post). Add a persisted **cooldown after any warning**, a lock against parallel runs, and more warning markers.

---

## Q1. What Meta officially documents

**Terms of Service** (effective 2025-01-01) [S1]
- s.3.2.3 [P]: "You may not access or collect data from our Products using automated means (without our prior permission)".
- s.4.2 [P]: for violations, Meta "may suspend or permanently disable your access to Meta Company Products".

**Automated Data Collection Terms** (effective 2024-10-07) [S2]
- [P]: "You will not engage in Automated Data Collection without first obtaining Meta's express written permission". That permission goes through a formal authorization process. The definition covers any "automated or programmatic tools", so a Playwright script qualifies.
- [P]: the collector must comply with robots.txt. Collectors must "only use IP addresses, user-agent strings, and other identifiers that identify your services". Meta may enforce "with or without notice".
- [R]: in practice this is a regime for search engines and similar crawlers. A personal account has no realistic route to this permission.

**robots.txt** [S3]
- [P]: the header says "Collection of data on Facebook through automated means is prohibited unless you have express written permission". It has `User-agent: *` / `Disallow: /`.

**Anti-scraping publications**
- "How We Combat Scraping" (Mike Clark, 2021-04-15) [S4] [P] describes:
  - an External Data Misuse team of 100+ people;
  - rate limits and data limits as the "first" defense;
  - detection of behavior "typically associated with automated computer activity";
  - enforcement through disabling accounts, cease-and-desist letters and lawsuits.
- The post refuses to give "a roadmap to scrapers", so **no numeric thresholds are published anywhere** [P][S4].
- Meta sued scrapers in 2022, including Ekrem Ateş for using automated Instagram accounts. It also described taking enforcement actions such as "revoking his access" [S5].

**Community Standards** [S21][S22]
- Account Integrity [P]: lists "Creating or using an account... through automated means, such as scripting (unless... through authorized routes...)". The stated response is that Meta "may request additional information about an account to ascertain ownership and/or permissible activity". This is what a checkpoint or identity verification looks like from the user's side [R].
- Spam [P]: targets activity done "either manually or automatically, at very high frequencies". It also says Meta "may place restrictions on accounts that are acting at lower frequencies" when other signals are present.

**Help Center** [S23][S24][S25]
- Account lock [P]: "If we see unusual activity on your account, we might lock it for security". You unlock it by following on-screen steps, and Meta may ask you to confirm your identity.
- Sharing block [P]: triggers include having "Posted a lot in a short amount of time". Facebook says it cannot lift a block early.
- Suspension [P]: you can appeal within 180 days, depending on region. Without an appeal, the account is permanently disabled.
- Meta has no official help page that defines "You're temporarily blocked" or "going too fast" thresholds for *viewing*. I could only find third-party pages, so this is unverified.
- Account Status (in Settings/Accounts Center) shows current restrictions and their duration [P][S26].

**Behaviors Meta itself names as triggers:**
- interaction rate per time window;
- data volume beyond normal use;
- automation-typical behavior patterns;
- very high frequency;
- doing a lot in a short time;
- "unusual activity";
- using an account through scripting.

Regulators add per-account visits per hour or day, and how aggressively an account looks at other users [S12].

---

## Q2. Sanctioned alternatives

| Option | Status | Realistic for us? |
|---|---|---|
| Graph API Groups API | Deprecated in v19 (2024-01-23). It applies to all versions from **2024-04-22**, including `publish_to_groups`, `groups_access_member_info` and the ability to install apps on groups [P][S6][S7]. | **No.** It is gone. |
| Download Your Information | Exports *your* data, including your own group posts and comments [S11, secondary; Meta's page did not render]. | **No.** It does not include others' posts. |
| Meta Content Library + API | Covers public posts from Pages, **public** groups and events. You need an academic or non-profit research affiliation. Applications go through ICPSR, there are no fees, and only aggregate outputs may be published [P][S8][S10]. Private groups are not mentioned. | **No** for a solo developer without an institution. |
| CrowdTangle | Shut down on **2024-08-14**. Meta points to Content Library instead [P][S9]. | No. |
| Group admin export of posts | I found no official Meta feature for exporting members' posts. Page Insights export exists for Pages, not groups [unverified; S27]. | Unverified, probably no. |
| **Ask the admin and members** | Needs no Meta permission. Example: the admin pins a post linking to an anonymous form (Google Form or our own `/submit` page) that asks only for role, seniority, salary and city. | **Yes. This is the most legitimate route.** It also creates real consent (Israeli law s.11 notice, s.2(9) purpose) [R]. |

[R] Recommendation: approach the admin before the first automated run, whatever else you decide. Even with collection, admin approval plus a pinned notice lowers the chance that members report you, and it addresses consent and purpose. It does not make collection compliant with Meta's Terms.

---

## Q3. Legal context (not legal advice)

- ***Meta v. Bright Data*, N.D. Cal. No. 3:23-cv-00077-EMC, order of 2024-01-23 (Judge Chen)** [S13][S14]:
  - Summary judgment went to Bright Data on breach of contract.
  - "Bright Data did not 'use' Facebook and Instagram when it engaged in public logged-off scraping".
  - The Terms exist "to prevent account holders who have privileges and access to Meta services from abusing their access".
  - The court found no evidence of scraping data that was available only when logged in.
  - Meta then dismissed the remaining claims and waived appeal (around 2024-02-23) [S18].
- ***Meta v. BrandTotal*, N.D. Cal. No. 3:20-cv-07182 (May 2022)** [S15]:
  - Meta won summary judgment on **breach of contract** for logged-in collection.
  - BrandTotal won on the CFAA claim, for access to non-password-protected pages.
  - The case then settled.
- ***hiQ v. LinkedIn*** [S16][S17]:
  - The 9th Circuit (2022) held that scraping public pages is unlikely to be "without authorization" under the CFAA.
  - In Nov 2022 the district court found that hiQ **breached the User Agreement**, including through fake accounts.
  - The case ended in a consent judgment: $500k, a permanent injunction, and deletion of the data.
- **What this means for us** [R]:
  - We log in with our own account to read a group. That is the scenario the Terms clearly cover.
  - The realistic consequences, in order of likelihood:
    1. a temporary block, checkpoint or disabled account;
    2. a cease-and-desist letter;
    3. a lawsuit. This is very unlikely at our scale; Meta's lawsuits target commercial or large-scale scrapers [S5].
  - The CFAA is a weak theory against an authorized member reading content they can already see. The contract claim is not weak.
  - Israel's Computers Law, 1995 was **not researched**. Whether breaching the Terms affects "authorized access" under Israeli law is an open question.

---

## Q4. Privacy

**Israel: Privacy Protection Law 1981, after Amendment 13** (in force 2025-08-14) [S19][S20]
- "Personal data" covers anyone identifiable "with reasonable effort, directly or indirectly", including by data about "economic... status" [P][S19].
- **"Data of special sensitivity" includes (10) "Personal data about a person's salary and financial activity"** [P][S19].
- s.2(9): "Using, or passing on to another, information on a person's private affairs for a purpose other than for which it was given" is an infringement. s.5 makes a willful infringement under 2(9) a criminal offence [P][S19].
- s.8(b): process data only for the database's lawful purpose. s.8(d): do not process data collected in violation of any law that regulates data processing [P][S19].
- s.11: a request for data must state its purpose, the controller and the data subject's rights [P][S19].
- PPA opinion on data minimization (2021, published for public hearing) [P][S28]:
  - Collecting excess data is in itself an infringement.
  - Purpose limitation rests on ss.2(9) and 8(b).
- The "database" definition excludes collections "for personal use that is not for business purposes" [P][S19].
  - [R] A public portfolio site is probably not "personal use", so assume the law applies.
- Israel's PPA co-signed the 2024 GPA **Concluding Joint Statement on Data Scraping** [P][S12]:
  - "Personal information that is publicly accessible is subject to data protection and privacy laws in most jurisdictions."
  - Contractual terms alone cannot make scraping lawful.

**EU GDPR (context)**
- [R] The GDPR likely does not apply directly to an Israeli developer reading an Israeli group, because of the Art. 3(2) targeting/monitoring test [S29]. Its principles are still the benchmark the Israeli reform follows [S20].
- Relevant articles [S29]:
  - Art. 5(1)(b) purpose limitation;
  - Art. 5(1)(c) minimization;
  - Art. 5(1)(e) storage limitation;
  - Art. 14, the duty to inform people whose data was not collected from them;
  - Recital 26: anonymous data is outside the GDPR.
- CNIL on scraping (2025 sheet) [P][S30]:
  - Define collection criteria in advance.
  - Delete irrelevant data.
  - Respect sites that object via robots.txt or CAPTCHAs.
  - Limit collection to data "accessible to any user who is not registered". Exclude data "published on social networks for private use".
- Dutch AP (2024) [S31]: scraping by private parties is "almost never" allowed. This view is contested.

**Private vs public group** [R]
- In a **private** group, members reasonably expect only fellow members to read their posts. Under CNIL's logic it is not "freely accessible" data, and AoIR ethics guidance treats closed venues as needing more consent [S32].
- That makes admin permission and a member notice much more important for a private group.
- If the group is private, the strongest position is: admin approval, a pinned notice, and storing only de-identified extracted fields.

**Implications** [R]
- Treat raw post text as special-sensitivity data until it is de-identified.
- Names are not the only identifiers. Employer + exact title + years + city can identify a person.
- Store extracted fields, not verbatim text, in the DB if possible. Never keep `author`.
- Delete `scraper/output/*.jsonl` after ingestion.
- Publish only aggregates with a minimum group size, for example n≥5 per cell.

---

## Q5. Practical practice for the collector

**(a) What primary sources state**
- Meta limits interactions per time and data per person [S4].
- Platforms rate-limit per-account visits per hour/day and limit access on "unusual activity" [S12].
- Doing "a lot in a short amount of time" triggers blocks, and Facebook will not lift them early [S24].
- Unusual activity can lock the account behind identity confirmation [S23].
- Scripted use can trigger a request for more information [S21].
- Meta publishes no numbers.

**(b) Practitioner reports [A] (kevinzg/facebook-scraper issue #409, 2021, request-based scraper, logged in)** [S33]
- Users got temporary bans even with delays, after about 100 posts.
- They were blocked again after waiting only 10 minutes.
- Bans lasted "24-48+ hours" after repeated bot-like behavior.
- Some request types, such as comment replies and friend lists, were "more sensitive".
- The maintainer advised staying under one request per second.
- Old and not directly comparable to a real browser, but the pattern holds: **volume and repetition trigger blocks, and retrying soon after a block makes it worse.**
- I found no reliable report of a "safe" daily number.

**(c) My reasoning [R]**

*Volume*
- The main risk drivers are **total items viewed per day/week**, **session frequency** and **repeating after a warning**. Pause length within a session matters less than these.
- `max_posts` counts only *salary matches*. In a general group, reaching 100 matches may mean scrolling through many hundreds of posts. **The cap must be on posts examined and scroll steps.**
- Incremental collection is the biggest single reduction. Remember fingerprints across runs, then stop when the feed reaches posts already seen. After the first run, each run reads only new posts.

*Behaving like a normal reader*
- Keep it read-only: no likes, comments, joins, profile visits, comment threads or messages. The draft already complies.
- Use the group's own feed, which the user opens and sorts manually. Avoid **group search**: every query is an extra request pattern, and many queries are unlike ordinary use. At most one search per run, typed by the user.
- Run while the user is at the computer and supervising (manual launch, visible window). This is about being able to see and react to warnings, not about appearing human.
- Use the same machine and network the user normally uses for Facebook. New logins from new places are a documented lock trigger [S23][S34].

*What not to do*
- parallel sessions;
- scheduled or cron runs;
- headless mode, because nobody would see warnings;
- frequent logouts or re-logins, or deleting the profile;
- new or secondary accounts;
- more than one group;
- re-running the same day to "catch up";
- retrying after any warning.

*Warning states* [R] (exact Meta strings not officially documented; verify against the live UI)
- URL contains `/checkpoint`, `/login`, `/recover`, `two_step_verification`, `/authentication` or `captcha`.
- Page text contains:
  - "temporarily blocked", "you can't use this feature", "going too fast", "misusing this feature";
  - "unusual activity", "suspicious activity", "account has been locked", "we suspended your account";
  - "confirm your identity", "automated", "security check", "confirm you're human";
  - the Hebrew equivalents. **Hebrew strings are unverified; capture them if they ever appear.**
- Also treat a **feed that suddenly disappears** as a warning: zero `role="article"` elements after it had posts.

---

## Recommended practice for our collector (checklist)

Numbers are [R], chosen well under anything reported as triggering. Meta publishes no safe limits.

- [ ] **Before the first run:** message the group admin. Explain the project, that only de-identified salary facts are stored, and how to opt out. Ask the admin to pin a notice or an anonymous form. If the admin says no, do not collect.
- [ ] **Scope:** one group, one account (the user's real, long-standing one), one machine, read-only.
- [ ] **Frequency:** ≤1 run/day, ≤3 runs/week, ≥24 h between runs. No runs on consecutive days in the first two weeks.
- [ ] **Per run:**
  - default 25 salary posts, hard max **50**;
  - **≤150 posts examined**;
  - **≤60 scroll steps**;
  - ≤10 minutes;
  - ≤30 "See more" expansions.
- [ ] **Pacing:** keep a 4–9 s random pause before and after each scroll, which is about 4–7 scrolls/min. Never go faster.
- [ ] **Incremental:** persist seen fingerprints. Stop after 5 consecutive already-seen posts. For history beyond about two weeks, use the admin/form route instead of deep scrolling.
- [ ] **Stop rule:** at the first warning marker, stop immediately, close the browser, save what was collected, and record the reason.
- [ ] **Cooldown after a temporary block or a "going too fast" type message:**
  - no runs for **7 days**, and the user browses Facebook normally in the meantime;
  - then halve all limits permanently.
- [ ] **Checkpoint, identity confirmation or lock:**
  - the user resolves it manually;
  - no automation for **30 days**;
  - a second event of any kind ends automated collection permanently, and we switch to the form/admin route.
- [ ] **Check Account Status** in Settings before each run. If any restriction is active, do not run.
- [ ] **Data:**
  - store text only, with regex redaction, then the LLM name stripping. The DB keeps extracted fields only;
  - delete raw JSONL within 7 days of ingestion;
  - no author, profile link, comments, images or timestamps finer than a day;
  - publish aggregates with n≥5.

---

## Changes to the current draft (recommendations only, code not edited)

`backend/scraper/collect_facebook.py`
1. Lower `HARD_MAX_POSTS` from 100 to **50**. Keep `DEFAULT_MAX_POSTS = 25`.
2. Change `MAX_RUNS_PER_DAY = 3` to **1**. Add `MAX_RUNS_PER_WEEK = 3` and `MIN_HOURS_BETWEEN_RUNS = 24`.
3. Add `MAX_POSTS_EXAMINED = 150` (count every new fingerprint, salary or not) and `MAX_SCROLL_STEPS = 60`. Stop on whichever limit comes first.
4. Fix `record_run()`. It overwrites the file with only today's key, so a weekly cap and cooldown history are impossible. Store a list of `{started_at, outcome, posts, examined}` instead.
5. Add a **cooldown**. On any `stopped: possible block` outcome, write `cooldown_until` to the runs file: +7 days for a temporary block, +30 days for checkpoint, login or lock URLs. Refuse to start until it has passed, and print why. After the second block event in the history, refuse permanently unless the user passes an explicit override.
6. Add a **lock file** (e.g. `~/.salary-intel/fb.lock`) so two runs cannot overlap. Refuse to start if the persistent profile is already in use.
7. **Incremental mode:** persist fingerprints (e.g. `~/.salary-intel/fb-seen.json`), and stop after 5 consecutive known posts. Also add the outcome "stopped: reached already-collected posts".
8. Treat an article count that drops to zero, after previously being above zero, as a block signal.
9. Keep `headless=False`, the manual login, `channel="chrome"` and the persistent profile. Do not add any launch flags or init scripts that change how the browser identifies itself.

`backend/scraper/browser.py`
10. Add a run-level counter so the expansions in `expand_see_more` are capped at about **30 per run**, not just 5 per pass. Optionally expand only posts whose visible preview already matches `SALARY_HINT_RE`.

`backend/scraper/filters.py`
11. Extend `BLOCK_URL_MARKERS` with `"two_step_verification"` and `"/authentication"`.
12. Extend `BLOCK_TEXT_MARKERS` with:
    - "you can't use this feature", "going too fast", "misusing this feature";
    - "suspicious activity", "account has been locked", "we suspended your account";
    - "confirm your identity", "automated behavior".
    - Add Hebrew equivalents after you see them in the real UI; today's Hebrew strings are unverified guesses.
    - These checks stay deliberately over-sensitive, since a false stop costs little.

Process / data
13. After `send_posts` succeeds, delete or move the JSONL. Add `--delete-after-send`.
14. Document in the README that this collector is used only with the admin's knowledge, and describe the opt-out path.

---

## Open questions / unverified

- Meta's numeric rate or data limits for *viewing* group feeds are not published [S4], and **no safe number exists in any primary source**.
- I found no official Meta help article defining the "You're temporarily blocked / going too fast" message or its duration. Help Center pages mostly would not render for fetching. The exact Hebrew UI strings for warnings are also unverified.
- Whether group admins can export members' posts natively: no official source found.
- What Download Your Information contains was confirmed only from secondary sources.
- Israel's Computers Law, 1995 and whether a Terms breach affects "authorized access": not researched.
- How s.2(9) applies to reusing salary posts that members shared voluntarily in a group: not settled. Ask a privacy lawyer if the project goes public.
- Whether the "personal use" database exclusion could cover a non-commercial portfolio project: unclear.
- The anecdotal report from kevinzg (2021) concerns a request-based scraper and may not reflect current browser-based behavior.

---

## Sources

- S1 Facebook Terms of Service (en_US, effective 2025-01-01): https://www.facebook.com/legal/terms/update?locale=en_US (also https://www.facebook.com/terms.php)
- S2 Meta Automated Data Collection Terms: https://www.facebook.com/apps/site_scraping_tos_terms.php
- S3 Facebook robots.txt: https://www.facebook.com/robots.txt
- S4 Meta, "How We Combat Scraping" (2021-04-15): https://about.fb.com/news/2021/04/how-we-combat-scraping/
- S5 Meta, "Taking Action Against Scraping for Hire" (2022-07): https://about.fb.com/news/2022/07/actions-against-scraping-for-hire/
- S6 Graph API v19.0 changelog: https://developers.facebook.com/docs/graph-api/changelog/version19.0/
- S7 Meta dev blog, Graph API v19 (2024-01-23): https://developers.facebook.com/blog/post/2024/01/23/introducing-facebook-graph-and-marketing-api-v19/
- S8 Meta Content Library overview: https://transparency.meta.com/researchtools/meta-content-library
- S9 Meta CrowdTangle page: https://transparency.meta.com/researchtools/other-data-catalogue/crowdtangle/
- S10 Content Library API – Get access: https://developers.secure.facebook.com/docs/content-library-api/get-access ; ICPSR SOMAR: https://www.icpsr.umich.edu/sites/somar/meta-content-library
- S11 Download Your Information (secondary): https://www.getsafeonline.org/personal/articles/your-information-facebook ; https://www.pandasecurity.com/en/mediacenter/how-to-download-your-personal-data-from-facebook-a-step-by-step-guide/
- S12 GPA Concluding Joint Statement on Data Scraping (2024-10-28, incl. Israel PPA): https://www.priv.gc.ca/en/opc-news/speeches-and-statements/2024/js-dc_20241028/
- S13 Farella Braun + Martel on *Meta v. Bright Data*: https://www.fbm.com/post/102kqw7/
- S14 Quinn Emanuel client alert: https://www.quinnemanuel.com/the-firm/news-events/client-alert-what-does-the-meta-v-bright-data-summary-judgment-ruling-mean-for-web-scraping/
- S15 *Meta v. BrandTotal* coverage: https://www.courthousenews.com/judge-rules-brandtotals-data-harvesting-violates-metas-terms-of-use-and-anti-hacking-laws/ ; https://techcrunch.com/2022/10/03/meta-settles-lawsuit-for-significant-sum-against-businesses-scraping-facebook-and-instagram-data/
- S16 Proskauer on *hiQ* (Nov 2022): https://newmedialaw.proskauer.com/2022/11/11/court-finds-hiq-breached-linkedins-terms-prohibiting-scraping-but-in-mixed-ruling-declines-to-grant-summary-judgment-to-either-party-as-to-certain-key-issues/
- S17 ZwillGen, "hiQ v. LinkedIn Wrapped Up": https://www.zwillgen.com/alternative-data/hiq-v-linkedin-wrapped-up-web-scraping-lessons-learned/ ; Privacy World on consent judgment: https://www.privacyworld.blog/2022/12/linkedins-data-scraping-battle-with-hiq-labs-ends-with-proposed-judgment/
- S18 Eric Goldman blog on Meta dropping Bright Data suit: https://blog.ericgoldman.org/archives/2024/02/facebook-drops-anti-scraping-lawsuit-against-bright-data-guest-blog-post.htm ; TechCrunch: https://techcrunch.com/2024/02/26/meta-drops-lawsuit-against-web-scraping-firm-bright-data-that-sold-millions-of-instagram-records
- S19 Privacy Protection Law 5741-1981, unofficial English translation "Updated After Amendment 13" (gov.il; Hebrew is official): https://www.gov.il/BlobFolder/legalinfo/legislation/en/Protection-of-Privacy-Law57411981unofficialtranslatioup.pdf
- S20 Pearl Cohen, Amendment 13 takes effect (2025-08-14): https://www.pearlcohen.com/israel-significant-amendment-to-the-privacy-law-takes-effect/
- S21 Meta Community Standards – Account Integrity: https://transparency.meta.com/policies/community-standards/account-integrity/
- S22 Meta Community Standards – Spam: https://transparency.meta.com/policies/community-standards/spam/
- S23 Facebook Help – Unlock your account: https://www.facebook.com/help/669497174142663
- S24 Facebook Help – Blocked from sharing: https://www.facebook.com/help/986265348145792
- S25 Facebook Help – Account suspended or disabled: https://www.facebook.com/help/103873106370583
- S26 Meta Transparency – Restricting accounts / Account Status: https://transparency.meta.com/enforcement/taking-action/restricting-accounts/
- S27 (No official source found for group post export; search noted only Page Insights export via third parties.)
- S28 PPA opinion on Data Minimization (2021): https://www.gov.il/BlobFolder/rfp/data_minimization_public_hearing/en/PPA%20Opinion%20on%20Data%20Minimization%20-%20English%20Translation.pdf
- S29 GDPR (Regulation (EU) 2016/679): https://eur-lex.europa.eu/eli/reg/2016/679/oj ; EU adequacy review reconfirming Israel (2024-01-15), via Hunton: https://www.hunton.com/privacy-and-cybersecurity-law-blog/european-commission-reviews-and-reaffirms-adequacy-decisions-for-11-jurisdictions
- S30 CNIL, legitimate interest focus sheet on web scraping: https://www.cnil.fr/en/legal-basis-legitimate-interests-focus-sheet-measures-implement-case-data-collection-web-scraping
- S31 Dutch AP scraping guidance (2024), via IAPP: https://iapp.org/news/a/netherlands-dpa-issues-guidance-against-web-scraping ; Pinsent Masons: https://www.pinsentmasons.com/out-law/news/dutch-web-scraping-guidance-warn-businesses-gdpr-breach-risk
- S32 AoIR Internet Research Ethics 3.0: https://aoir.org/reports/ethics3.pdf ; Loughborough summary: https://www.lboro.ac.uk/internal/research-ethics-integrity/research-ethics/guidance-investigators/socialmedia
- S33 [Anecdotal] kevinzg/facebook-scraper issue #409: https://github.com/kevinzg/facebook-scraper/issues/409
- S34 [Secondary] reports that new device or location logins trigger locks: https://forums.tomsguide.com/threads/your-account-has-been-temporarily-locked-we%E2%80%99ve-detected-suspicious-activity-on-your-facebook-account-and-have-temporarily-lo.204964/
