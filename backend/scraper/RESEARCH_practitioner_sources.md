# Research (pass 2): what practitioners report about Facebook group collection

Researched 2026-10-14. This pass covers practitioner sources: GitHub repositories and their issue trackers, PR write-ups, Apify actor pages, tutorials, forum threads and one research paper. The primary sources (Meta terms, help center, law, privacy) are in `RESEARCH_facebook_collection.md` and are not repeated here.

Labels:
- **[multiple sources]**: two or more independent practitioners report it.
- **[single anecdote]**: one report.
- **[relies on evasion – does not transfer]**: the setup used concealment, proxies, account rotation or similar. Its lessons do not apply to a transparent single-account collector.
- **[my reasoning]**: my inference, not something a source states.

Source IDs (P1...) are listed at the end. Years matter here: Facebook changed its markup and its legacy sites between 2021 and 2026, so I give the year for every report.

**Scope rule (same as pass 1).** Many sources rely on stealth, proxies, account farms or cookie transplanting. Those techniques appear below only as category labels, with a note on whether a source's success depended on them. This file contains no instructions for them.

**Coverage gaps.** Reddit was not reachable: its domain is blocked for the search tool, and its JSON API refused the request. Hacker News and Stack Overflow searches found nothing specific to group collection. GitHub issue trackers, PR descriptions and repository code were the richest sources.

---

## TL;DR

1. **In practitioner reports, volume and request type cause blocks; delay length does not prevent them** [multiple sources, 2021-2023]. Users were blocked with 5-10 s delays [P11], 10 s delays [P13] and 30-60 s random intervals [P12]. Sleeps did not help one user scraping about 20 groups [P6]. The blocks came after roughly 50-100 posts when the scraper also fetched reactions, comments or profiles [P3][P13][P15], or when it used search [P17]. When the same scraper fetched post text only, one user called it "almost unlimited" [P13]. All of these are request-based scrapers from 2021-2023, so the numbers do not transfer to a browser. The pattern does: **read only what the feed already shows, and cap total volume.**
2. **Retrying soon after a block makes things worse** [multiple sources]. Users were re-blocked within about 12 minutes or about 50 posts [P1]. One account went on to a login ban: the correct password was rejected as wrong [P4]. Another got an "account locked" screen with no unlock option on the second occurrence [P7]. Reported durations range from about 1 hour to 2 days for a temporary block [P16][P14][P1]. One person who was only browsing manually waited a few weeks [P43]. A lock needs a manual unlock and sometimes ID verification [P2][P7].
3. **Session continuity is a real safety factor** [multiple sources, 2026]. One project created a fresh browser context on every run, and Facebook treated each run as a new device login. The session died daily until the project switched to a persistent profile [P23 #44]. Another practitioner reported that one manual login in a persistent profile lasted "weeks" [P21]. A third project ran from CI with cookies copied in and an automated re-login. From May to July 2026 it lost its session again and again behind a multi-profile chooser and silent login rejection [P23 #49-#61]. **Never automate login. Never copy cookies to another machine. Never delete the profile.**
4. **The post selector in our draft is probably out of date** [multiple sources, 2026]. Three independent 2026 sources treat `data-ad-rendering-role="story_message"` as the post-body hook and `[role="feed"] > div` as the post unit [P23 selectors][P24][P27]. One source verified this on a live session and found that **`div[role="article"]` on a group feed was a comment, not a post** [P24]. Another found that the group `role="article"` did not wrap the post's real controls [P26]. Our draft keeps only messages that have a `[role="article"]` ancestor, so it could return nothing, or comments.
5. **The Hebrew "See more" text that one practitioner uses is `עוד`, not `ראה עוד`** [single anecdote, May 2026, Hebrew groups] [P21]. The label also follows the account's UI language, not the post's language. One Israeli project's 2025 data contains Hebrew posts that end in "… See more" [P30]. The draft only matches `ראה עוד|See more`.
6. **`mbasic.facebook.com` is gone, and `m.facebook.com` no longer serves the no-JavaScript HTML** [multiple sources]. Scrapers built on them broke between September and November 2024 [P18][P20]. A 2026 project called mbasic "blocked" [P23 #27]. A 2026 test found that mbasic redirects to www [P40]. Do not plan around them.
7. **Chronological sort exists and practitioners treat it as essential for incremental runs** [multiple sources]. Sources include the `?sorting_setting=CHRONOLOGICAL` URL parameter [P8][P22][P41], the "פוסטים חדשים" (New posts) option in the Hebrew UI [P21], and Apify's `CHRONOLOGICAL` option [P34]. Facebook still sometimes serves posts out of order, so the stop rule should be "N consecutive known posts", not "the first known post" [P22 1.0.7].
8. **Silent failure is the most common DIY failure mode** [multiple sources]. Examples:
   - selectors return comments that look like a working scraper [P24];
   - truncated "… See more" text is stored as if complete [P30][P21];
   - a CI run shows green while the account is logged out [P23 #58];
   - feed articles are found but none parse, and nothing is reported [P22 1.1.0];
  - anti-bot responses can be "blocked... silently by returning no content" [P42].

   Count "units seen" against "posts parsed" and fail loudly on any mismatch.
9. **No source reports a quantified, multi-week, problem-free run on a transparent single account in 2023-2026.** The long-running success stories each relied on something we exclude:
   - Igor-Lysk: 24 groups, 6-8 h a night, about 7,100 posts in May 2026 [P21];
   - McGill fbscrape [P33];
   - Apify actors [P34][P35].

   I found **no evidence-based "safe number"** for our setup.

---

## What triggers blocks (practitioner evidence)

| Trigger | Evidence | Year | Label |
|---|---|---|---|
| **Expensive per-post requests: reactions, comments and replies, commenter profiles** | Reactions caused a ban after about 100 posts "regardless if I put a delay"; text alone was "almost unlimited" [P13]. Scraping comments, then the commenters' profiles, over a few days locked the account for "unusual activity" [P7]. Fifty profiles in 6 minutes caused a temporary ban, and 10-15 s delays did not fix it [P15]. 180 friends' posts over 5 h with 90 s sleeps caused a 2-day ban [P14]. The maintainer says comment replies trigger blocks sooner [P16], and pass 1 records the same for #409. | 2021-2023 | [multiple sources] |
| **High total volume in one session** | Blocks came after 100 to 9,000 posts in private groups, on alt accounts too [P5]. A user never got past about 100 days of one profile's history [P9]. The maintainer said 8,000+ posts is "a lot of data" and a human could not read 8,000 posts in 10 minutes [P6]. | 2021-2023 | [multiple sources] |
| **Delays alone do not prevent blocks** | Reports cover 5-10 s [P11], 10 s [P13], 30-60 s [P12], sleeps across about 20 groups [P6], and 3, then 10-15 s [P15]. | 2021-2023 | [multiple sources] |
| **Search** | `get_posts_by_search` was "always temporarily blocked" [P17]. | 2023 | [single anecdote] |
| **Many groups per run** | About 20 groups with `pages=5` caused a temporary block [P6]. In contrast, 24 groups a night ran for weeks [P21], but that run used [relies on evasion – does not transfer]. | 2021 / 2026 | Mixed; not transferable |
| **Re-trying soon after a block** | Blocked again after about 12 minutes and about 50 posts [P1]. After repeated temporary blocks, the login was rejected as "incorrect password" [P4]. The second lock had no unlock option [P7]. | 2022-2023 | [multiple sources] |
| **New-device logins: fresh context per run, cookies copied into CI** | A fresh browser context on every run made each scrape look like a new device login and caused daily `auth_expired` [P23 #44]. Running from CI with seeded cookies led to repeated session invalidation and a multi-profile chooser screen [P23 #55-#61]. A maintainer says the ban is tied to the account (cookies), not the IP, and that public proxy and Tor IPs are "suspicious by default" [P9]. | 2023, 2026 | [multiple sources] |
| **Automated re-login** | One project's automated recovery login was silently rejected and looped on the chooser for weeks [P23 #49-#61]. | 2026 | [single anecdote] |
| **Sudden policy tightening without any change on the user's side** | Several users reported in January 2023 that "almost all users are getting temporarily blocked"; one had scraped "for a few months" before [P1]. | 2023 | [multiple sources] (same thread) |
| **Ordinary fast manual activity** | A user viewing other people's profiles manually got "going too fast", and it lasted weeks. This is a forum report seen only through a search summary; the page timed out [P43]. | ~2022 | [single anecdote], low confidence |
| **Headless vs headed** | **No comparative evidence found.** Headless projects (forage default [P22], rentifier in CI [P23]) and a headed one [P21] all ran. Rentifier's session problems are confounded by CI IPs and cookie seeding. | - | Unverified |
| **Scroll speed / session length** | No source gives a number tied to a block for browser scrolling. Igor-Lysk scrolled every 2 s for hours with 3 parallel tabs [P21], but that setup used [relies on evasion – does not transfer]. | - | Not found |

**Durations and outcomes reported**
- **Temporary block ("You're Temporarily Blocked", "You can't use this feature right now/at the moment"):**
  - about 1 hour (maintainer, 2021) [P16];
  - about 12 minutes before it re-triggered (2023) [P1];
  - "within a few hours" [P7];
  - 2 days [P14];
  - 24-48 h (pass 1, #409).
- The account otherwise kept working: "You could still log in to your account and do other stuff just fine" [P4].
- **Login ban after repeated blocks:** the correct password was reported as wrong [P4] [single anecdote].
- **"Your account has been locked" (unusual activity):**
  - the first lock could be unlocked by the user;
  - the second had no unlock option [P7];
  - with an account farm, one account was permanently lost [P7] (that setup used [relies on evasion – does not transfer]);
  - "Facebook might ask for ID verification" [P2].
- **What people did afterwards:**
  - Most kept going with more delay, more accounts or proxies. These are the wrong lessons for us.
  - The maintainer's own advice was different: make fewer requests (`allow_extra_requests: False`) [P6][P10], and "only iterate... until you see your last recorded post, then abort" [P10]. In other words, collect incrementally.

**Detection strings practitioners use** [multiple sources]. These strings come from the kevinzg detector, quoted in [P4]:
- `you can't use this feature at the moment`
- `you can't use this feature right now`
- `you’re temporarily blocked`

The detector mixes straight `'` and curly `’` apostrophes, so normalize apostrophes before matching [my reasoning]. Rentifier's selectors detect `#login_form, #loginform` and `[href*="/checkpoint/"]` [P23 selectors]. Igor-Lysk treats these as a broken or unavailable page [P21]:
- a login wall;
- "something went wrong";
- "this content isn't available";
- the Hebrew `תוכן זה אינו זמין` ("this content is not available").

---

## What kept accounts safe (transferable to us)

1. **Persistent profile, one manual login, same machine** [multiple sources, 2026]. Igor-Lysk: "One manual login, then weeks" [P21]. Rentifier: a persistent context fixed the daily session loss [P23 #44]. Forage separates `login` (manual) from `scrape` [P22]. *Caveat:* Igor-Lysk also used concealment, so his "weeks" cannot be credited to the profile alone. Our draft already uses a persistent profile with manual login.
2. **Read the feed only. Do not open permalinks, comments, reactions or profiles** [multiple sources]. Request type was the strongest block predictor in the kevinzg reports [P7][P13][P15][P16]. Our draft already reads feed text only. Igor-Lysk's "catch-up" pass revisits post URLs to recover truncated text [P21]. That pass is exactly the extra traffic to avoid.
3. **Incremental collection: stop at already-seen posts** [multiple sources]:
   - the kevinzg maintainer [P10];
   - Igor-Lysk's "DB_HIT" early exit made "nightly runs cheap" [P21];
   - rentifier's second run returned 0 new posts [P23 #32];
   - forage stops after 5 consecutive old posts [P22].

   Pass 1 already recommends this.
4. **Chronological sort, verified before relying on order** [multiple sources]. Igor-Lysk skips a group when the sort cannot be verified (`SORT_REQUIRED`) [P21]. Forage requests chronological order through the URL [P22].
5. **Stop on the first warning, and do not retry the same day** [multiple sources, by negative example]. Every quick-retry report escalated [P1][P4][P7]. This supports pass 1's 7-day and 30-day cooldowns.
6. **Never automate login, and stop when the session ends** [single anecdote, strong]. Rentifier's two months of auto-login fixes [P23 #49-#61] show the trap. Forage simply raises "Not logged in or session expired" and exits [P22]. Our draft already waits for the user to log in.
7. **One tab, one group** [my reasoning, supported by negative examples]. The reports of trouble at about 20 groups [P6] and the parallel-tab setups [P21] are the opposite of what we want.
8. **Be identifiable to the group** [single anecdote]. The one academic collector identified herself to the admins when joining. Her paper reports no block, but it also gives no volume or block data, so this is weak evidence [P36].

**Volumes reported to run for weeks without problems**

| Setup | Volume | Conditions | Transfers? |
|---|---|---|---|
| Igor-Lysk FB_scrapper (May 2026) [P21] | 24 groups, about 7,100 raw posts across the apartment hunt, 6-8 h a night, "weeks of unattended scraping" | Headed persistent Chrome profile, 3 parallel tabs, 2 s scrolls, plus an automation-flag concealment launch argument | **No.** [relies on evasion – does not transfer], and the scale is far above ours |
| kevinzg user cabunda (until Jan 2023) [P1] | "scraping for a few months" | Request-based scraping of m.facebook.com, which no longer exists | **No.** The method is gone |
| Rentifier (Mar 2026) [P23 #32] | 10 posts from 3 groups in about 30 s; cron in CI | Cookie-seeded headless runs in CI, multiple accounts | **No.** [relies on evasion – does not transfer]. It also later lost sessions repeatedly |
| Dedecek Gertz (research, ~2021-2022) [P36] | All posts and comments of several migrant groups; volume not stated | Selenium logged into the researcher's own account; identified to admins | Partly. It is the closest to our setup, but gives no volume or block data |
| Forage (2026) [P22] | No volume claims | Manual login, saved storage state, headless default, 2 s delay | Unknown |

**Bottom line:** no practitioner number tells us what is safe for a transparent account [my reasoning]. Pass 1's conservative numbers rest on reasoning, not on measured evidence, and nothing here contradicts them.

---

## Lessons that do NOT transfer (rely on evasion)

These are category labels only. "Success depended?" says whether the source's reported success needed the technique.

| Category | Seen in | Success depended? |
|---|---|---|
| Automation-flag concealment via browser launch arguments | Igor-Lysk [P21] | Unknown, so we cannot credit his "weeks" to anything else |
| Anti-detect browser plus account pool with rotation after N scrolls | McGill fbscrape [P33] | Yes, by design ("to avoid detection") |
| Residential or rotating proxies | Apify actors [P34][P35]; iankalvin/Crawlbase [P37]; Thunderbit audit [P39]; passivebot comment [P38] | Yes. Apify says "no risk of IP blocking" because of proxies |
| Account farms / multi-account cookie rotation | kevinzg #936, #310, #1017 [P7][P5][P3]; rentifier [P23]; McGill [P33] | Yes. They switched accounts when one was blocked |
| Cookie export / transplant to cloud, CI or third parties | Apify cookie actors [P35]; rentifier CI [P23]; udsey auto-fill login [P31] | Partly. Rentifier shows this route breaks sessions |
| User-agent or header spoofing to get legacy HTML | kevinzg #1113 comments [P18]; moda20 "mbasicHeaders" [P20] | Yes, and the legacy HTML is now gone anyway |
| Scripted credential entry designed to pass bot checks | rentifier #57 [P23] | Yes, and it was still unreliable |
| Fingerprint variation (random viewport) | forage [P22] | Unknown; mild |
| Replaying Facebook's private GraphQL API (`doc_id`, tokens) | rentifier #27/#28 [P23]; McGill [P33] | Yes. Out of scope: it is a private API, not page reading |
| "Human-like" mouse drift and random scrolling as anti-bot measures | S-T-R-A-N-G-E-R fb_rent_scraper [P32]; forage [P22] | Unknown. Framed as avoiding bot detection |

---

## DOM and robustness lessons

**Locating the post body (2026)**
- `[data-ad-rendering-role="story_message"]` is the post-body hook in current markup [multiple sources]:
  - rentifier, "validated against live Facebook DOM (2026-03-03)" [P23 selectors];
  - opencue, verified on a live logged-in group feed, 2026-08 [P24];
  - FeedWriter, 2026-10 [P27];
  - olter-tn includes it first [P25].
- Fallbacks: `[data-ad-preview="message"]` and `[data-ad-comet-preview="message"]` [P23][P25][P22]. Igor-Lysk still used `data-ad-preview="message"` successfully on Hebrew groups in May 2026 [P21]. **Use story_message first and keep both fallbacks.**
- **Post unit:** `[role="feed"] > div`. The first child is the sort widget [P23 selectors][P24].
- **Do not anchor on `role="article"`** [multiple sources, but conflicting]:
  - Opencue: on a group feed, `div[role="article"]` had `aria-label` "Comment by … 12 minutes ago". The first version "returned three comments… and looked like a working scraper" [P24].
  - Page-auto: the group `role="article"` does not wrap the post's real controls, so it moved its post selector off `role=article` [P26].
  - Forage still uses `[role="feed"] [role="article"]`, but filters out comments by `aria-label^="Comment by"` [P22].
  - On the News Feed (not a group), one 2026-09 report found no `[role="feed"]` root at all, with posts detected only as `div[role="article"]` [P45].
  - Conclusion [my reasoning]: Facebook may serve both variants (A/B testing), so code must handle posts with and without an article wrapper.
- **Class names** are build-generated and rotate [multiple sources] [P24][P39][P28]. Avoid them. olter-tn still carries some as a last fallback [P25].
- **Read only the message node, never the whole card** [multiple sources]. If you fall back to the card, the author, buttons, comments and suggested posts leak into the text [P27]. `[data-ad-rendering-role="meta"]` contains "anti-scraping decoy text", and some text runs carry invisible joiner characters [P24]. Use rendered `innerText` (our draft does), not `textContent` [my reasoning; forage uses textContent].

**"See more"**
- Hebrew label: `עוד` exact match. Igor-Lysk's click set is `{'Ещё','See more','See More','עוד'}`, and his truncation regex is `(?:Ещё|See\s+more|עוד|подробнее)\s*$` [P21] [single anecdote, 2026].
- I found no source confirming `ראה עוד` or `הצג עוד` in the current UI. The label depends on the account's UI language: Domica's Hebrew posts were captured with "… See more" [P30].
- Scope the clicks to the post. Forage clicks "See more" only when `control.closest('[role=article]') === root` [P22]. Igor-Lysk limits clicks to the viewport ±800 px, at most 20 per scroll [P21]. Our draft locates "See more" inside the message element, which is already well scoped.
- Expansion does not always succeed [multiple sources]:
  - Igor-Lysk needed a separate catch-up pass for posts that stayed truncated [P21];
  - forage flags `content_truncated` [P22];
  - Domica's sample data stored truncated text [P30].

  **Detect a trailing truncation marker and flag or skip the post.** Never store it as complete text.

**Feed behaviour**
- In 2026 the group feed was not reported as virtualized away. Igor-Lysk had to remove old articles himself, because the DOM grew to "multi-GB" and crashed Chrome on long runs [P21] [single anecdote]. At our scale of 150 posts or fewer, this is not a concern [my reasoning].
- Wait for new feed children after a scroll instead of sleeping blindly. Forage made this change in 2026-01, and its count of posts found in a 24-hour window went from 10 to 57 [P22].
- Expect element handles to go stale. Forage moved permalink work to a separate page "to avoid invalidating cached feed element handles" [P22].

**Sort order**
- `?sorting_setting=CHRONOLOGICAL` exists on desktop:
  - a 2020 Chrome extension adds it after observing that Facebook's own sort change sets this parameter [P41];
  - a June 2026 Firefox add-on does the same [P41];
  - forage adds it, 2026-06 [P22];
  - Apify lists `CHRONOLOGICAL` [P34];
  - kevinzg #935 (2022) confirmed it on desktop but not on mobile [P8].
- Whether Facebook honours it consistently is **not verified**. Forage still saw out-of-order posts [P22]. Practical rule: check the visible sort label ("New posts" / `פוסטים חדשים`) [P21].

**Timestamps**
- The permalink and the absolute date live in the timestamp link, which Facebook "renders lazily on hover". The hit rate was 1-3/10 without hover and 4/10 with a real hover [P24].
- Forage reads the link's `aria-label` or text instead of hovering, because hovering adds about 1 s per post [P22].
- One practitioner tried rebuilding permalinks from other IDs and got "a *different author's post*" [P24].
- For us [my reasoning]: we do not need timestamps (pass 1 says day granularity at most), so we skip this fragile area. Use `collected_at`.

**Deduplication**
- Use content-based dedup, not permalinks [multiple sources]:
  - thanh2004nguyen went from 98% to 100% success after switching to content-based dedup [P29];
  - opencue dedups on author+text because permalinks are unreliable [P24];
  - Igor-Lysk normalizes text and URL and dedups again after reloads [P21].
- Hidden characters break naive hashing [P24]. For Hebrew text, also strip bidi marks [my reasoning].

**mbasic / m.facebook.com status**
- The no-JS mobile HTML stopped working for scrapers around 2024-09-24 [P18]. "mbasic is gone" (moda20, 2024-11/12) [P20].
- Forage removed its mbasic parsers in 2026-06 ("the mbasic site was discontinued") [P22]. Rentifier called mbasic "blocked" in 2026-03 [P23 #27].
- On 2026-09-19, mbasic redirected to www, and m.facebook.com redirected to www from a desktop browser [P40].
- Risk profile: unusual user agents or headers are needed to get legacy HTML. That counts as spoofing, which we exclude, and the HTML is gone anyway [P18][P20].

**Detecting comments vs posts**
- Comments are `role="article"` elements with `aria-label` starting "Comment by", or "Reply by" for replies [P22][P24][P25].
- The Hebrew aria-label text is **not verified**. Any message element whose closest `role=article` is a descendant of the post unit is a comment [my reasoning].

---

## Non-automated alternatives

| Alternative | Practitioner evidence | Notes |
|---|---|---|
| **Admin cooperation + pinned anonymous form** | No practitioner report found. Pass 1 recommends it. | Still the strongest route [my reasoning]. |
| **Paste UI: user copies posts into our `/submit`** | Domica (Israeli rentals, 2025-08) built a "parsing/pasting posts" PoC UI [P30]. | Zero automation footprint. The backend already has `POST /api/v1/posts`. |
| **User-clicked "scan current page" extension** | Domica's extension popup has "סרוק דף נוכחי" ("scan current page"), with the user starting the scan [P30]. Chrome Web Store tools offer user-clicked export [P44]. | Third-party extensions can see your session. Meta has sued extension makers over data harvesting (HN 2020 [P46]). If we do this, write our own minimal extension; never install a third-party scraper extension [my reasoning]. It is still automated collection under the Terms, but with a much smaller behavioural footprint, because the user scrolls. |
| **Saved page (user scrolls, then "Save page as") and offline parsing** | No practitioner report found. Forage parses saved JSON offline and tests selectors on saved, network-blocked HTML pages [P22]. | [my reasoning] The parser can be the same code. No automated browsing touches Facebook. |
| **Researcher's own account, identified to admins** | Dedecek Gertz identified herself to admins when joining [P36]. She notes that Facebook "prohibits scrapping, but not manual data collection". | Supports the admin route. |
| **Paid services (Apify etc.)** | Public groups only when logged out [P34]; cookie-based actors cover private groups [P35]. | [relies on evasion – does not transfer] (proxies). They also hand your session to a third party. |

---

## Comparison with RESEARCH_facebook_collection.md recommendations

**Agrees**
- Volume and repetition drive blocks more than pause length (pass 1 Q5c). Strongly confirmed by many independent kevinzg reports [P6][P11][P12][P13][P15].
- Read-only, feed-only, with no comments, profiles or permalinks. Confirmed: extra request types were the main triggers [P7][P13][P15][P16].
- Incremental collection is the biggest single reduction. Confirmed by the maintainer [P10] and by three 2026 projects [P21][P22][P23].
- Avoid search [P17]. Use one group, no parallel sessions, no re-login, the same machine [P6][P23].
- Stop at the first warning, with long cooldowns. Supported: quick retries escalated into a login ban or a lock [P1][P4][P7]. Practitioners report blocks lifting in hours, but re-triggering just as fast. The 7-day cooldown is conservative and justified.
- No safe number exists. Confirmed: no transparent-setup quantification was found.

**Disagrees / needs revision**
- **Pass 1, change #8 ("article count that drops to zero" as a block signal):** posts may not be `role="article"` in 2026 [P24][P26]. Use a count of `[role="feed"] > div` or story_message elements instead.
- **Hebrew strings:** pass 1 left them as unverified guesses, and the draft uses `ראה עוד`. Practitioner evidence points to `עוד` for See more [P21], `פוסטים חדשים` for the sort [P21], and `תוכן זה אינו זמין` for unavailable content [P21]. All are single-source and need a live check.
- **Proposed text markers:** `"you can't use this feature"` uses a straight apostrophe, but Facebook's text may use the curly `’` [P4]. Normalize before matching.

**Adds**
- Session continuity and new-device logins as a lever [P23 #44].
- Automated login as a trap [P23].
- Silent-failure diagnostics [P22][P23][P24].
- Truncated-text and duplicate pitfalls [P21][P24][P29][P30].
- Chronological URL parameter [P8][P22][P41].
- mbasic/m.facebook are dead [P18][P20][P40].

---

## Concrete changes to recommend for backend/scraper/*.py

These are recommendations only. No code was edited.

`browser.py`
1. **`MESSAGE_SELECTOR`:** put `[data-ad-rendering-role="story_message"]` first and keep the two `data-ad-preview` fallbacks [P23][P24][P27].
2. **`READ_MESSAGES_JS`:** stop requiring a `[role="article"]` ancestor. Instead:
   - iterate `[role="feed"] > div` units and skip the sort widget;
   - take the outermost message element in each unit;
   - drop any message whose nearest `[role="article"]` sits inside the unit, or has a "Comment by" / "Reply by" aria-label. Those are comments [P22][P24].

   This yields one post per unit and reads only the message node. If no `[role="feed"]` exists [P45], fall back to message elements directly, and report that the fallback was used in the run diagnostics.
3. **`SEE_MORE_SELECTOR`:** match `^(See more|עוד|ראה עוד|הצג עוד)$`. The first two have practitioner evidence; the last two are guesses to verify. Document that the label follows the account's UI language [P21][P30].
4. **Truncation:** after expansion, if the text still ends with `…`, `See more` or `עוד`, return it with `truncated=True`. Do not fingerprint it or keep it. Let a later pass in the same run retry once [P21][P22][P30].

`filters.py`

5. **`fingerprint()`:** before hashing, apply NFC normalization and strip zero-width and bidi characters (U+200B-U+200F, U+202A-U+202E, U+2060-U+2069, U+FEFF). Also remove a trailing truncation marker [P24][my reasoning].
6. **`block_reason()`:** normalize `’` to `'`, then add markers:
   - temporary block: `you can't use this feature right now`, `you can't use this feature at the moment` [P4];
   - no access: `this content isn't available`, `תוכן זה אינו זמין` [P21];
   - session ended: a login form present (`#login_form`, `#loginform`), or the multi-profile chooser text "Use another profile" / "Remove profiles from this browser" [P23].

   On a "session ended" outcome, tell the user to log in manually next time. Never retry the login.

`collect_facebook.py`

7. **Empty-pass stop is keyed to the wrong signal.** `empty_passes` counts passes with no new *salary* post. In a general group, that stops early, and it also cannot tell "feed ended" apart from "no salary posts". Count new posts *examined* (any new fingerprint) for the stop rule. Keep salary matching separate [my reasoning; forage separates `no_new_posts` from limits, P22].
8. **Diagnostics, so failures are loud** [P22][P23 #58][P24]. Record these in the run log:
   - feed units seen;
   - messages parsed;
   - truncated;
   - duplicates;
   - comments skipped;
   - stop reason.

   If units > 0 and parsed == 0, the outcome is "selectors broken" (distinct from "no salary posts") and the exit code is non-zero.
9. **Feed-gone signal:** replace pass 1's `role="article"` count with a count of `[role="feed"] > div` / story_message elements [P24][P26].
10. **Sort:** append `?sorting_setting=CHRONOLOGICAL` to the group URL. In the Enter prompt, ask the user to confirm that the feed shows "New posts" / `פוסטים חדשים`. If the run can read the sort label and it is not chronological, refuse incremental stopping [P8][P21][P22][P41].
11. **Incremental stop:** stop after 5 consecutive already-seen fingerprints, not on the first one. Pinned posts and out-of-order posts make a first-hit rule wrong [P22].
12. **Keep, and document why:**
    - persistent profile;
    - manual login;
    - the user's own machine and network;
    - no profile deletion ("delete the profile folder" advice [P21] creates a new-device login [P23 #44]);
    - no cookie export;
    - single tab;
    - no launch arguments or init scripts that change how the browser identifies itself. Several tutorials and repos add such arguments [P21]; we must not.
13. **Pacing:** keep `human_pause`. Do not raise volume because of it: evidence says delays do not protect [P11][P12][P13]. The caps on posts examined and scroll steps (pass 1, #3) are the real guard.

---

## Unverified / open

- The Hebrew UI strings `עוד` (See more), `פוסטים חדשים` (New posts) and `תוכן זה אינו זמין` each come from one practitioner (2026). The Hebrew strings for the block and lock screens and for the comment aria-labels were **not found anywhere**.
- Whether `role="article"` currently wraps posts, comments or both on our group. Sources conflict [P22] vs [P24][P26]. Inspect our group's live markup once with DevTools before the first run.
- Whether `?sorting_setting=CHRONOLOGICAL` is honoured consistently [P22].
- Headless vs headed as a block factor: no comparative evidence.
- Whether "See more" expansion triggers a network request in current markup (it matters for the expansion cap): unknown.
- Block thresholds for browser-based feed reading in 2023-2026: **no report found**. All numeric block reports are request-based (kevinzg, 2021-2023).
- Reddit threads (r/webscraping and others) could not be accessed. Their reports are missing from this pass.
- The elektroda forum report of a "going too fast" block from manual profile viewing lasting weeks [P43] was seen only through a search summary. The page timed out.
- Igor-Lysk's README does not mention any block. Absence of a report is not evidence of no blocks.

---

## Sources

GitHub issue numbers refer to `kevinzg/facebook-scraper` unless stated otherwise.

- P1 #956 "Users getting temporarily blocked" (2023-01): https://github.com/kevinzg/facebook-scraper/issues/956
- P2 #1028 "TemporarilyBanned" (2023-06/07): https://github.com/kevinzg/facebook-scraper/issues/1028
- P3 #1017 "How to not get 'You're Temporarily Blocked'" (2023-05): https://github.com/kevinzg/facebook-scraper/issues/1017
- P4 #1056 "gets 'Temporarily banned' but Firefox is working" (2023-09/10): https://github.com/kevinzg/facebook-scraper/issues/1056
- P5 #310 "Unable to collect posts beyond a certain number due to Temporary Block" (2021-06): https://github.com/kevinzg/facebook-scraper/issues/310
- P6 #550 "banned from facebook" (2021-11): https://github.com/kevinzg/facebook-scraper/issues/550
- P7 #936 "Your account has been locked" (2022-12/2023-01): https://github.com/kevinzg/facebook-scraper/issues/936
- P8 #935 "sort group feeds chronologically (?sorting_setting=CHRONOLOGICAL)" (2022-12 to 2023-10): https://github.com/kevinzg/facebook-scraper/issues/935
- P9 #1011 "7 years of posts without getting banned" (2023-05): https://github.com/kevinzg/facebook-scraper/issues/1011
- P10 #362 "Tips & advice for regular scraping" (2021-06): https://github.com/kevinzg/facebook-scraper/issues/362
- P11 #1047 "about delay to avoid getting banned" (2023-08): https://github.com/kevinzg/facebook-scraper/issues/1047
- P12 #1033 "resume from where i got banned" (2023-06): https://github.com/kevinzg/facebook-scraper/issues/1033
- P13 #986 "Temporary Banned when getting reactions" (2023-03): https://github.com/kevinzg/facebook-scraper/issues/986
- P14 #548 "Temporarily banned...friends scraper" (2021-11): https://github.com/kevinzg/facebook-scraper/issues/548
- P15 #542 "get_profiles is reason to getting banned" (2021-11): https://github.com/kevinzg/facebook-scraper/issues/542
- P16 #281 "About temporary ban on extracting comments" (2021-05): https://github.com/kevinzg/facebook-scraper/issues/281
- P17 #1081 "Temporarily Blocked Issue" with search (2023-12): https://github.com/kevinzg/facebook-scraper/issues/1081
- P18 #1113 "get_posts_by_search: No raw posts" (m.facebook.com no-JS gone, 2024-09/10): https://github.com/kevinzg/facebook-scraper/issues/1113 ; also #1119 (2024-10): https://github.com/kevinzg/facebook-scraper/issues/1119 ; #1130 (2025-10 to 2026-09): https://github.com/kevinzg/facebook-scraper/issues/1130
- P20 moda20/facebook-scraper #73 "mbasic is no longer working" (2024-11), #75 "mbasic is gone" (2024-11/12), #66 (2024-09/10): https://github.com/moda20/facebook-scraper/issues/75 ; https://github.com/moda20/facebook-scraper/issues/73 ; https://github.com/moda20/facebook-scraper/issues/66
- P21 Igor-Lysk/FB_scrapper (README "Lessons learned", `facebook_apartments.py`, `catchup.py`; May 2026, Tel Aviv Hebrew/Russian groups): https://github.com/Igor-Lysk/FB_scrapper
- P22 jwmoss/forage (README, `docs/capabilities.md`, CHANGELOG 1.0.4-2.2.0, `scraper.py`, `parser.py`; 2026-01 to 2026-10): https://github.com/jwmoss/forage
- P23 oricho123/rentifier (Israeli rentals). PRs #26-#28 (mbasic, then GraphQL, 2026-03), #32 (Playwright migration), #43, #44 (persistent context), #49-#61 (session and login incidents, 2026-05 to 2026-07), and `packages/connectors/src/facebook/selectors.ts`: https://github.com/oricho123/rentifier/pull/44 ; https://github.com/oricho123/rentifier/pull/58 ; https://github.com/oricho123/rentifier/pull/32 ; https://github.com/oricho123/rentifier/blob/main/packages/connectors/src/facebook/selectors.ts
- P24 opencue/agenticbrowser #38 "facebook site pack — verified against a live session" (2026-08): https://github.com/opencue/agenticbrowser/pull/38
- P25 olter-tn/garment-leads `garment_leads/selectors.py`, `cadence.py` (2024-2026): https://github.com/olter-tn/garment-leads
- P26 meyecarpenter23842/page-auto #248 (2026-09): https://github.com/meyecarpenter23842/page-auto/pull/248
- P27 anlvdt/FeedWriter #2 "extract story_message body instead of whole post card" (2026-10): https://github.com/anlvdt/FeedWriter/pull/2
- P28 aitkn/xtil #53 (2026-02): https://github.com/aitkn/xtil/pull/53
- P29 thanh2004nguyen/facebook-group-scraper (2025-06): https://github.com/thanh2004nguyen/facebook-group-scraper
- P30 EtanHey/domica-admin #49 "scrape-facebook groups chrome extension" (2025-08), with sample data `public/facebook-posts-2025-07-27.json`: https://github.com/EtanHey/domica-admin/pull/49
- P31 udsey/fb-rental-scanner (2026): https://github.com/udsey/fb-rental-scanner
- P32 S-T-R-A-N-G-E-R/fb_rent_scraper (2026-04): https://github.com/S-T-R-A-N-G-E-R/fb_rent_scraper
- P33 MEOMcGill/fbscrape (README, 2026): https://github.com/MEOMcGill/fbscrape
- P34 Apify, Facebook Groups Scraper (official): https://apify.com/apify/facebook-groups-scraper
- P35 Apify cookie-based actors: https://apify.com/swerve/fb-group-scraper ; https://apify.com/curious_coder/facebook-group-member-scraper
- P36 Dedecek Gertz, "Collecting migrants' Facebook posts: Accounting for ethical measures in a text-as-data approach", Frontiers in Sociology (2023), doi 10.3389/fsoc.2022.932908: https://pmc.ncbi.nlm.nih.gov/articles/PMC9868646/ (read via Europe PMC full text)
- P37 iankalvin, "Scraping Facebook Groups using Python…" DEV Community (2020, edited 2023): https://dev.to/iankalvin/scraping-facebook-groups-using-python-avoid-getting-blocked-with-proxycrawl-456a
- P38 passivebot/facebook-marketplace-scraper #1 "Getting blocked" (2023-2024): https://github.com/passivebot/facebook-marketplace-scraper/issues/1
- P39 Thunderbit, "Facebook Scraper GitHub: What Still Works and What Doesn't" (updated 2026-08-05; secondary audit): https://thunderbit.com/blog/facebook-scraper-github-guide
- P40 Techdows, Basic Facebook (mbasic) status table, tested 2026-09-19, page dated 2026-10-03: https://techdows.com/?p=13376
- P41 johnbryan/fbGroupsExtension (2020-2021): https://github.com/johnbryan/fbGroupsExtension ; KronoFeed Firefox add-on (v1.1.0, 2026-06-27): https://addons.mozilla.org/en-US/firefox/addon/kronofeed/
- P42 Make Community, "How to get the new posts from a facebook group if I'm not an admin" (2025-12): https://community.make.com/t/how-to-get-the-new-posts-from-a-facebook-group-if-im-not-an-admin-public-and-private-groups/99808
- P43 [low confidence, seen through a search summary only] elektroda forum, "going too fast" while viewing profiles: https://www.elektroda.com/rtvforum/topic3898585.html
- P44 Chrome Web Store, user-clicked export extensions (listing only, not evaluated): https://chromewebstore.google.com/detail/amlggiobnpdaadmoimbcambmmminkono
- P45 Artificial-Sweetener/facebook-clean-my-feeds #16 (2026-09, News Feed: `feedRoot: null`, posts detected as `div[role="article"]`): https://github.com/Artificial-Sweetener/facebook-clean-my-feeds/issues/16
- P46 Hacker News, "Facebook sues two Chrome extension makers for scraping user data" (2020): https://news.ycombinator.com/item?id=24661891
