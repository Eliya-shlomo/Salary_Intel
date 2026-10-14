# Research summary: salary sources behind the synthetic dataset

Researched 2026-10-14. This file joins two detailed research files and records the decisions taken from them:

- [`RESEARCH_salary_sources_israel.md`](RESEARCH_salary_sources_israel.md): Israeli sources, the only source of ILS numbers (S1–S30).
- [`RESEARCH_salary_sources_international.md`](RESEARCH_salary_sources_international.md): US and global sources, used **only for ratios** (S1–S40).

Labels: **[P]** = what a source states, **[R]** = reasoning or a decision.

Spot check [P]: the GotFriends table (IL-S6), three Nisha pages (IL-S1, IL-S2, IL-S3, IL-S4) and both JobInfo tables (IL-S15, IL-S16) were re-read in the main session after the research agent finished. Every value used in `salary_reference.json` matched the page.

---

## TL;DR

1. **No Israeli source publishes p25 / median / p75 by role and seniority** [P]. Recruiters publish "from–to" ranges per experience band and never say what the bounds mean.
2. **Three recruiter publishers carry the table:** GotFriends (Sep 2026), Nisha (2025–2026 pages) and JobInfo (Jan 2026). Each one's buckets line up with junior 0-2 / mid 3-5 / senior 6-10.
3. **Every ILS number in the dataset is derived by code from published ranges**, by a fixed rule (below). The ranges are stored in [`app/ingestion/salary_reference.json`](../app/ingestion/salary_reference.json) as each source printed them, and `python -m app.ingestion.salary_reference` prints the derived table.
4. **Everything that is not a salary is an assumption** and is marked `"assumption": true` in the JSON: role mix, bucket mix, post styles, gross-vs-unstated share, cities and the equity share. No source was found for any of them.
5. **US data was used as a cross-check only.** The Israeli experience steps (about 1.2–1.4× per bucket) sit close to US base-pay steps (1.16–1.31×). Some role ratios do not match (see "Cross-check").

---

## Decisions [R]

| Decision | Choice | Why |
|---|---|---|
| Buckets | junior 0-2, mid 3-5, senior 6-10 | GotFriends uses exactly these, and Nisha uses 1-2 / 3-5 / 6-10. No source has a non-management 10+ bucket except Ethosia's undated 9+, so there is no staff bucket. |
| What a range means | read as the source's p25–p75 | Nothing published settles it. p25–p75 is the narrower reading, so the generated spread is conservative. |
| Combining sources | one range per publisher (rows averaged), then p25 = median of lows, p75 = median of highs, median = median of midpoints | Medians stop one outlying publisher from moving the cell. Collapsing per publisher stops Nisha's four pages from counting four times. |
| Confidence | high = 3+ publishers within 15%; medium = 2+ within 25%; low otherwise, or when a row's mapping is uncertain | Computed in code from the data, not chosen per cell. |
| Basis | monthly gross base, ILS | Nisha says gross [P]. GotFriends and JobInfo do not say, and are treated as gross by Israeli convention. |
| Net posts | not generated | Turning gross into net needs a tax model we do not have. Inventing one would add numbers with no source. |
| `qa` | manual and automation rows averaged per publisher | The canonical role merges both, and their pay differs by about 1.5–2× [P]. This is a 50/50 mix assumption. |
| `team_lead`, `architect` | senior only (architect also mid), low confidence | These are roles reached after years of experience. The sources' bucket columns may mean years in the role. |

### Included and excluded

| Source | Used for cells | Reason |
|---|---|---|
| GotFriends table 2026 (IL-S6) | yes | Dated Sep 2026, own placements, all 13 roles, matching buckets |
| Nisha 2026 tables and guides (IL-S1, S3, S4) | yes | Dated 2026, says gross. One publisher with IL-S2. |
| Nisha 2025 table (IL-S2) | yes, only for mobile, qa, architect | The 2026 pages do not cover those roles |
| JobInfo via Drushim (IL-S15, S16) | yes | Dated 2026-01-01. The "2-3" column is skipped because it straddles junior and mid. |
| Ethosia tables (IL-S12) | no | Undated, buckets offset by a year (0-1 / 2-4 / 5-8) |
| AllJobs (IL-S17) | no | Undated, excludes bonuses, runs 5–10K below every recruiter |
| Levels.fyi Israel (IL-S18) | no | Annual total comp including stock, skewed to multinationals |
| Payscale Israel (IL-S19) | no | n=144, implausible p10 |
| CBS, Innovation Authority, GotFriends and Ethosia averages | no, cross-check only | All roles together; different populations |
| Rows the research mapped with "?" (e.g. "Python Developer" → backend) | no | The mapping to a canonical role is a guess |

---

## Derived table (monthly gross ILS)

Output of `python -m app.ingestion.salary_reference` on 2026-10-14:

```text
role             bucket      p25  median     p75  pubs  conf    sources
architect        mid      32,500  35,800  39,000     2  low     IL-S2, IL-S6
architect        senior   39,000  42,000  45,000     2  low     IL-S2, IL-S6
backend          junior   21,000  23,500  26,000     2  medium  IL-S1, IL-S6
backend          mid      27,000  29,800  32,500     2  low     IL-S1, IL-S6
backend          senior   31,500  35,800  40,000     2  medium  IL-S1, IL-S6
data_analyst     junior   17,500  20,000  22,500     2  medium  IL-S1, IL-S6
data_analyst     mid      22,500  25,000  27,500     2  medium  IL-S1, IL-S6
data_analyst     senior   26,500  28,800  31,000     2  medium  IL-S1, IL-S6
data_engineer    junior   20,000  22,500  25,000     2  medium  IL-S1, IL-S6
data_engineer    mid      26,000  30,500  35,000     2  medium  IL-S1, IL-S6
data_engineer    senior   32,500  37,000  41,500     2  medium  IL-S1, IL-S6
data_scientist   junior   23,500  28,000  32,500     2  medium  IL-S1, IL-S6
data_scientist   mid      26,500  34,500  42,500     2  medium  IL-S1, IL-S6
data_scientist   senior   40,000  45,000  50,000     2  medium  IL-S1, IL-S6
devops           junior   20,500  23,200  26,000     2  low     IL-S3, IL-S6
devops           mid      30,000  31,000  32,000     3  medium  IL-S16, IL-S3, IL-S6
devops           senior   35,000  37,500  40,000     3  high    IL-S16, IL-S3, IL-S6
frontend         junior   20,200  23,100  26,000     2  medium  IL-S1, IL-S6
frontend         mid      26,000  30,100  34,200     2  medium  IL-S1, IL-S6
frontend         senior   33,200  37,600  42,000     2  medium  IL-S1, IL-S6
fullstack        junior   20,000  22,500  25,000     3  high    IL-S1, IL-S15, IL-S6
fullstack        mid      27,000  32,000  35,000     3  high    IL-S1, IL-S15, IL-S6
fullstack        senior   34,000  38,500  45,000     3  high    IL-S1, IL-S15, IL-S6
mobile           junior   20,000  22,500  25,000     3  high    IL-S15, IL-S2, IL-S6
mobile           mid      26,000  29,500  33,000     3  high    IL-S15, IL-S2, IL-S6
mobile           senior   32,000  36,000  40,000     3  high    IL-S15, IL-S2, IL-S6
product_manager  junior   18,000  22,200  26,500     2  low     IL-S1, IL-S6
product_manager  mid      25,000  27,000  31,000     3  medium  IL-S1, IL-S15, IL-S6
product_manager  senior   28,000  29,000  30,000     3  low     IL-S1, IL-S15, IL-S6
qa               junior   15,000  17,000  18,000     3  high    IL-S15, IL-S2, IL-S6
qa               mid      20,000  22,500  25,000     3  high    IL-S15, IL-S2, IL-S6
qa               senior   27,000  28,800  30,500     3  high    IL-S15, IL-S2, IL-S6
security         junior   17,700  20,200  22,800     2  medium  IL-S4, IL-S6
security         mid      21,700  26,000  30,000     3  medium  IL-S15, IL-S4, IL-S6
security         senior   31,000  37,200  43,300     3  low     IL-S15, IL-S4, IL-S6
team_lead        senior   40,000  43,000  45,000     3  low     IL-S1, IL-S15, IL-S6
```

Coverage: 36 of 39 cells (13 roles × 3 buckets). Missing: architect junior, team_lead junior and mid, by decision. 10 cells are high confidence, 18 medium, 8 low.

---

## Cross-check against US ratios [R]

The ratios below are computed from the derived table, with backend = 1.00 in each bucket. The US ranges come from the international file (base pay or median, US only).

| Role | Israel (junior / mid / senior) | US range | Reading |
|---|---|---|---|
| data_analyst | 0.85 / 0.84 / 0.80 | 0.56–0.81 | Consistent |
| qa | 0.72 / 0.76 / 0.80 | 0.74–0.85 | Consistent |
| mobile | 0.96 / 0.99 / 1.01 | 0.97–1.15 | Consistent |
| devops | 0.99 / 1.04 / 1.05 | 0.77–1.17 | Consistent |
| data_engineer | 0.96 / 1.02 / 1.03 | 0.81–1.10 | Consistent |
| security | 0.86 / 0.87 / 1.04 | 0.76–1.05 | Consistent |
| architect | – / 1.20 / 1.17 | 1.03–1.54 | Consistent |
| team_lead | – / – / 1.20 | 1.13–1.83 (engineering manager proxy) | Consistent with the low end |
| product_manager | 0.94 / 0.91 / 0.81 | 0.77–1.18 | Consistent, but the mid→senior step is only 1.07 |
| fullstack | 0.96 / 1.07 / 1.08 | 0.76–0.94 | **Above the US range** |
| frontend | 0.98 / 1.01 / 1.05 | 0.63–1.00 | Slightly above |
| data_scientist | 1.19 / 1.16 / 1.26 | 0.74–1.09 | **Above the US range** |

Experience steps per bucket in the Israeli table are 1.07–1.43×, mostly 1.2–1.35×. US base-pay steps are 1.16–1.31× [international file].

**What the mismatches probably mean:**

- **Backend is the likely problem, not fullstack.** Nisha's "Backend Engineer" row (24-28K mid, 28-35K senior) sits below Nisha's own Java and Python rows in the same publication [P, IL-S1]. With only two publishers, it pulls the backend cell down, so every ratio against backend goes up.
- **Product manager senior is flat because of Nisha.** Nisha prints senior PM (24-30K) at or below mid (23-31K). The research flags this as a probable data-entry error. The median rule keeps it in, because the rule does not choose between sources.
- **Data scientist above backend is plausible in Israel** [R]. GotFriends' H1 2026 averages put algorithm and AI engineers above Python and Node developers. US data-science medians include many analyst-like roles.

These are open questions for the user (below), not silent fixes.

---

## Open questions

1. **Backend:** add the JobInfo "Python" and "Java" rows as backend observations? They are clearly backend languages, but the inclusion rule excludes "?" mappings. Adding them raises backend mid and senior, and gives backend a third publisher.
2. **Product manager senior:** keep Nisha's row as published, or drop it as a probable error? Either choice should be recorded in the JSON.
3. **Downloads that need approval:** the Stack Overflow 2024–2026 datasets (Israel-only medians; small samples), the CBS Table 7 PDF, and four Innovation Authority PDFs (possible role shares). None were downloaded.
4. **10+ years:** posts with 11+ years are not generated. Add a bucket later only if a source covers it.

---

## Sources

The full source lists, with URLs and terms-of-use notes, are in the two detailed files. The IDs used in the JSON (`IL-S1`, `IL-S2`, `IL-S3`, `IL-S4`, `IL-S6`, `IL-S15`, `IL-S16`) are the Israeli file's S-numbers with an `IL-` prefix.
