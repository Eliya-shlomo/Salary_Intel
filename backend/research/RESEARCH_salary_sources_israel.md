# Research: published Israeli tech salary data for calibrating the synthetic dataset

Researched 2026-10-14 (all access dates below are 2026-10-14). Every number in this file was read on a page fetched in this session; nothing comes from memory. Labels used:
**[P]** = what a source states, **[R]** = my own reasoning (including any arithmetic such as annual ÷ 12).

Scope rules followed: individual public pages only (WebSearch + WebFetch), no crawling, no forms, no downloads, no archive/cache workarounds. PDFs were not fetched; they are listed under "Blocked / needs approval". Only aggregates were recorded. Monetary values are ILS; "K" = thousand ILS.

Target statistic: **monthly gross salary in ILS** (p25 / median / p75). **No Israeli source found publishes p25/median/p75 per role × seniority.** Recruiter tables publish *ranges* ("from–to") per experience band, with no stated meaning (not percentiles, not min/max). Only Levels.fyi publishes percentiles, and only as annual total compensation, mostly without role or level splits.

---

## TL;DR

1. **The three usable role × seniority tables are recruiter tables:** GotFriends "טבלת שכר בהייטק 2026" (updated Sep 2026) [S6], Nisha "משכורות הייטק" (data as of April 2026, published 2026-05-28) plus three Nisha role guides from 2026 [S1][S3][S4][S5], and Ethosia's salary-table page (undated) [S12]. JobInfo tables republished on Drushim (dated 2026-01-01) [S15][S16] and AllJobs tables ("2026", no date) [S17] add a fourth and fifth view. All give **ranges, not percentiles**, and none states what the range bounds mean.
2. **GotFriends' 2026 buckets match the proposed ones almost exactly:** "0-2 שנים", "3-5 שנים", "6-10 שנים", "דרג ניהולי" [S6]. Nisha uses 1-2 / 3-5 / 6-10 / management [S1] (its 2026 guides use 0-2 / 3-5 / 6+) [S3][S4]. AllJobs uses 0-2 / 3-5 / 6+ / management [S17]. Ethosia uses 0–1 / 2–4 / 5–8 / 9+ [S12][S14]. JobInfo uses בוגר / 2-3 / 3-5 / מעל 5 / ראש צוות [S15]. **No source has a "10+" non-management bucket except Ethosia (9+).** The staff column of the matrix is therefore mostly missing.
3. **Coverage:** junior, mid and senior cells are **strong** (2+ agreeing recruiter sources) for fullstack, frontend, mobile, data_scientist, data_engineer, qa and (mostly) devops. They are **weak** for backend (sources disagree by up to ~10K), data_analyst, product_manager, architect, and team_lead (bucket meaning unclear). Every staff (10+) cell is weak or missing.
4. **Aggregate anchors:** CBS high-tech average per salaried job was 31,858 for 2024 [S24]. Monthly 2026 values swing from 34,301 (July) to 38,467 (March, a bonus month) [S20][S21]. GotFriends reports 39,810 for 2025 [S10][S11] and 41,722 for experienced (5+ yrs) candidates in H1 2026 [S6][S7]. Ethosia reports 32,500 for 2025 [S13]. These measure different populations, so the gaps are expected.
5. **Big caveats:** (a) recruiter tables reflect placements, which skew toward people who are changing jobs and toward in-demand profiles. (b) "Gross" is stated explicitly only by Nisha, AllJobs, Ethosia MI and CBS-based press. GotFriends, JobInfo and the Ethosia tables do not say. (c) Levels.fyi is annual **total comp incl. stock/bonus**, self-reported and skewed to multinationals, so it runs well above recruiter base ranges. (d) Nisha's pages blend "Israeli market sources" and reuse GotFriends' 39,810 headline, so Nisha is not fully independent of GotFriends [S1][S3][S4].
6. **Secondary data is thin.** No source gives role shares per canonical role. Equity *prevalence* was not found (only volume trends and value). Geography exists only as averages or percent premiums.

---

## Sources and per-source tables

Column legend for every table: *Source role* = as the source names it; *Canon* = my mapping (? = uncertain); *Bucket* = source's own label; *Stat* = statistic type; values are ILS **per month** unless the table says otherwise. Common fields per source are given once above each table (URL, publisher, publication year, period covered, gross/net, bonus/equity, sample, ToS/robots).

### [S1] Nisha (נישה), "משכורות הייטק" salary tables, April 2026

- URL: https://www.nisha.co.il/%d7%9e%d7%a9%d7%9b%d7%95%d7%a8%d7%95%d7%aa-%d7%94%d7%99%d7%99%d7%98%d7%a7/
- Publisher: Nisha (recruitment firm). Author Yevgeny Sini. Published 2026-05-28. Data "as of April 2026" ("טבלאות שכר נישה, אפריל 2026") [P].
- Method [P]: "hundreds of employment contracts" from 2025-2026 and "thousands of recruitment processes". The page calls the figures estimates that vary by company, experience and negotiation. No n per role.
- Gross/net [P]: the headline average and the algorithms table are explicitly "ברוטו לחודש". The other tables say only "₪/חודש" [R: probably gross too, but not stated].
- Bonus/equity: base ranges. The prose mentions options at seed/Series A-B and RSUs and signing bonuses at multinationals as *additional* [P].
- Stat: range ("from–to"), meaning of the bounds not defined.
- Buckets [P]: Junior (1-2 yrs), Mid (3-5), Senior (6-10), Management (labels vary: "Lead / Tech Lead", "TL", "ניהול בכיר").
- ToS/robots: robots.txt allows `/` for `*`. It disallows only `/wp-admin/`, search and job-filter parameter URLs, and `/private-area/`. There are no AI-specific groups. Terms page not fetched.

| Source role | Canon | Junior 1-2 | Mid 3-5 | Senior 6-10 | Management |
|---|---|---|---|---|---|
| Fullstack Developer | fullstack | 20,000-25,000 | 25,000-35,000 | 32,000-45,000 (the intro text says 32-48K) | Lead/Tech Lead 38,000-48,000 → team_lead? |
| Backend Engineer | backend | 20,000-25,000 | 24,000-28,000 | 28,000-35,000 | 35,000-42,000 |
| Front End – React | frontend | 20-25K | 25-32K | 32-40K | 35K+ |
| Front End – Angular | frontend | 15-25K | 25-32K | 32-40K | 35K+ |
| Front End – Vue | frontend | 20-25K | 25-30K | 30-37K | 35K+ |
| Data Scientist | data_scientist | 25-30K | 25-40K | 40-45K | 45-60K |
| Machine Learning Engineer | data_scientist? | 25-30K | 30-35K | 40-65K | 45-70K |
| MLOps Engineer | devops? / data_engineer? | 25-30K | 30-33K | 35-50K | 40-45K |
| Data Engineer | data_engineer | 20,000-25,000 | 25,000-33,000 | 32,000-40,000 | 35,000-45,000 |
| Data Analyst | data_analyst | 15,000-20,000 | 20,000-25,000 | 25,000-30,000 | 28,000-35,000 |
| BI Developer | data_analyst? | 13,000-16,000 | 17,000-22,000 | 24,000-30,000 | 30,000-36,000 |
| Product Manager | product_manager | 13,000-24,000 | 23,000-31,000 | 24,000-30,000 (lower than Mid as published) | 30,000-36,000 |
| QA Team Leader | qa / team_lead? | 25-27K (Junior TL) | 28-30K | 32-38K | 30-38K |
| Automation Team Leader | qa / team_lead? | 28-30K | 30-35K | 35-40K | 38-45K |
| Software Engineer – Java | backend? | 20-25K | 25-35K | 35-45K | 42K+ |
| Software Engineer – Python | backend? | 23-28K | 25-35K | 35-42K | 40K+ |
| Software Engineer – Node.js | backend? | 20-25K | 25-35K | 32-40K | 40K+ |
| Software Engineer – GO | backend? | 25-28K | 30-35K | 40-45K | 45-50K |

Company-type breakdown, Fullstack, 5 years' experience [P]: Pre-Seed/Seed 25-30K + options; Series A-B 28-33K + options; established Israeli company 30-38K; US company with Israeli R&D 35-42K; multinational 38-50K.
Prose [P]: Tel Aviv and Herzliya pay 10%-15% more; Be'er Sheva pays 10%-20% less. Seniority alone explains "only 35%" of pay differences (internal review of contracts). An overall average of "כ-39,810 ₪ ברוטו לחודש" is quoted without a separate source [R: this matches GotFriends' 2025 figure, see S10/S11].
Not covered by this page: mobile, devops, security, architect (only a prose mention of "Microservices Architects" at 45-55K).

### [S2] Nisha, "salary-tables/הייטק" page (undated; older edition)

- URL: https://www.nisha.co.il/salary-tables/%D7%94%D7%99%D7%99%D7%98%D7%A7/
- Date [P]: none shown. The body cites "טבלאות שכר הייטק 2024" and the title says "לשנת 2025". [R] Treat it as a 2024/2025 edition, superseded by S1 where the two overlap.
- Gross [P]: a footnote says the figures are gross, by seniority and company size. Stat: range. Buckets: 1-2 / 3-5 / 6-10 / ניהול.
- ToS/robots: same as S1.

| Source role | Canon | 1-2 | 3-5 | 6-10 | ניהול |
|---|---|---|---|---|---|
| Devops | devops | 22K-27K | 30K-35K | 35K-40K | 40K-45K |
| Mobile Developer | mobile | 20K-25K | 25K-32K | 32K-40K | 38K-45K |
| Cyber security | security | 15K-20K | 25K-30K | 30K-35K | 35K+ |
| Software architect | architect | 20K-25K | 25K-35K | 35K-45K | 45K+ |
| QA Engineer | qa | 15K-18K | 20K-25K | 24K-30K | 30K-38K |
| Big data Developer | data_engineer? | 20K-25K | 25K-35K | 35K-45K | 45K+ |
| DevOps team leader | team_lead? / devops | 20K-25K | 30K-35K | 40K+ | 40K+ |

### [S3] Nisha, "שכר DevOps, Cloud ו-SRE" guide, 2026-08-31

- URL: https://www.nisha.co.il/?p=12547
- Method [P]: a "שקלול טווחי שכר ממקורות שוק ישראליים 2026" (blend of Israeli 2026 market sources) plus Nisha estimates. Gross monthly [P]. Buckets [P]: ג'וניור (0-2), מיד (3-5), סניור (6+).

| Source role | Canon | 0-2 | 3-5 | 6+ |
|---|---|---|---|---|
| DevOps Engineer | devops | 16,000-22,000 | 24,000-31,000 | 32,000-40,000 |
| SRE | devops | 18,000-24,000 | 26,000-34,000 | 35,000-45,000 |
| Platform Engineer | devops | 18,000-24,000 | 27,000-35,000 | 36,000-45,000 |
| Cloud Architect | architect? / devops | – | 30,000-38,000 | 38,000-50,000 |
| DevOps Team Lead | team_lead | – | 32,000-38,000 | 38,000-50,000 |

Senior DevOps by employer type [P]: multinational/cloud 38-50K; established Israeli SaaS 33-42K; Series B-C 30-38K; early startup 25-33K; traditional (bank/insurance) 26-35K; integration/outsourcing 24-32K. Internal inconsistency [P]: the intro gives mid 24-32K and senior 33-42K.

### [S4] Nisha, "שכר בסייבר" guide, 2026-08-31

- URL: https://www.nisha.co.il/%D7%9E%D7%93%D7%A8%D7%99%D7%9A-%D7%A9%D7%9B%D7%A8-%D7%91%D7%A1%D7%99%D7%99%D7%91%D7%A8/
- Method/gross: as for S3 (blend of 2026 market sources plus Nisha estimates; gross monthly) [P].

| Source role family | Canon | 0-2 | 3-5 | 6+ |
|---|---|---|---|---|
| Defence & ops (SOC Analyst, implementer, IR) | security | 12,000-17,000 | 17,000-25,000 | 25,000-33,000 |
| Offensive & testing (Pen Tester, Red Team) | security | 16,000-21,000 | 22,000-30,000 | 30,000-42,000 |
| Research & dev (vuln researcher, RE, cyber dev) | security | 18,000-24,000 | 26,000-36,000 | 38,000-55,000 |
| Architecture & management (architect, CISO, GRC) | security / architect? | – | 25,000-35,000 | 35,000-55,000 |

Senior by employer type [P]: global cyber product co. 38-55K; Israeli cyber product co. 32-45K; tech giant security team 35-50K; consulting/integration 25-35K; traditional org 22-33K; public sector 20-30K.
Geography [P]: Gush Dan and Herzliya about +10%-15% over the national average; Be'er Sheva about -10%-20%.

### [S5] Nisha, "טבלת שכר QA ואוטומציה (2025-2026)", 2026-01-23

- URL: https://www.nisha.co.il/טבלת-שכר-qa-ואוטומציה/
- Method [P]: "market estimates, salary surveys, placement-firm data and public sources", 2025-2026. Gross monthly [P]. The buckets are the page's own and are finer than the others.

| Source role | Canon | Bucket [P] | Hi-tech & startups | Traditional cos. |
|---|---|---|---|---|
| Manual QA | qa | 0–1 (Junior) | 10,000–13,000 | 8,000–10,000 |
| Manual QA | qa | 1–2 | 13,000–15,500 | 10,000–12,500 |
| Manual QA | qa | 2–4 (Mid) | 16,000–19,000 | 13,000–16,000 |
| Manual QA | qa | 4–6 (Senior) | 19,000–23,000 | 16,000–19,000 |
| Manual QA | qa | 6–8 | 22,000–25,000 | 18,000–21,000 |
| Manual QA | qa | 8+ (Expert) | 24,000–27,000 | 20,000–23,000 |
| Automation / SDET | qa | 0–1 (Junior) | 17,000–21,000 | 14,000–17,000 |
| Automation / SDET | qa | 1–3 | 22,000–26,000 | 18,000–22,000 |
| Automation / SDET | qa | 3–5 (Mid) | 27,000–32,000 | 23,000–27,000 |
| Automation / SDET | qa | 5–7 (Senior) | 33,000–38,000 | 28,000–33,000 |
| Automation / SDET | qa | 7+ (Tech Lead) | 38,000–44,000 | 32,000–36,000 |
| Automation / SDET | qa / architect? | Expert / Architect | 42,000–50,000 | 35,000–40,000 |

Management [P]: QA Team Lead (0-2 yrs as manager) 24,000–29,000; QA Team Lead (3-6) 28,000–34,000; Automation Team Lead (2+) 34,000–42,000; QA Manager (5+) 38,000–48,000.
Equity [P]: the page gives estimated 4-year grant values in USD by role and company type, for example Automation (Senior) at a Tier-1 giant, RSU $80,000–$140,000. It says equity can add 20%–40% to total comp at large companies. These are Nisha estimates, not survey data.

### [S6] GotFriends, "כמה אני שווה? טבלת שכר בהייטק 2026" (updated September 2026)

- URL: https://www.gotfriends.co.il/%D7%91%D7%9C%D7%95%D7%92%D7%99%D7%9D/high-tech-salary-tables/
- Publisher: GotFriends (recruitment firm). "עודכן לאחרונה: ספטמבר, 2026" [P].
- Method [P]: GotFriends' own placement and recruitment activity. It cites 1,400+ tech placements a year and 1,000+ client companies. The page calls the ranges benchmarks. It does not say whether they are averages or medians.
- Gross/net [P]: **not stated**. Units [P]: thousands ₪ per month. Bonus/equity: not mentioned.
- Buckets [P]: "0-2 שנים" | "3-5 שנים" | "6-10 שנים" | "דרג ניהולי". Some rows have fewer than four values.
- ToS/robots: robots.txt has `User-agent: *` / `Disallow: /jobssalary` only (that path was not accessed). Terms not fetched.

| Source role | Canon | 0-2 | 3-5 | 6-10 | ניהולי |
|---|---|---|---|---|---|
| Full Stack Developer | fullstack | 20-26 | 27-37 | 34-45 | 40-50 |
| Backend Developer | backend | 22-27 | 30-37 | 35-45 | 42-55 |
| Node JS Developer | backend? | 20-25 | 27-37 | 33-44 | 40-50 |
| Python Developer | backend? | 20-26 | 28-40 | 34-45 | 42-50 |
| JAVA Developer | backend? | 22-27 | 30-37 | 38-45 | 40-50 |
| GO Developer | backend? | 20-26 | 27-38 | 33-45 | 42-52 |
| Frontend Developer | frontend | 22-27 | 27-37 | 35-45 | 42-55 |
| מפתח REACT | frontend | 24-29 | 28-38 | 36-47 | 44-57 |
| Angular Developer | frontend | 22-27 | 26-36 | 35-45 | 42-55 |
| Mobile Developer | mobile | 20-25 | 26-33 | 32-40 | 38-45 |
| iOS Developer | mobile | 22-27 | 26-33 | 32-40 | 38-45 |
| Android Developer | mobile | 20-25 | 26-33 | 32-40 | 38-45 |
| ראש צוות מובייל | team_lead (mobile) | 25-39 | 30-35 | 35-40 | 40-47 |
| שכר DevOps Engineer | devops | 25-30 | 32-38 | 35-45 | 40-55 |
| ראש צוות DevOps | team_lead (devops) | 40-50 (bucket not specified) | | | |
| שכר Data scientist | data_scientist | 22-35 | 28-45 | 40-55 | 40-60 |
| Machine Learning Engineer | data_scientist? | 22-35 | 28-45 | 40-55 | 40-55 |
| שכר Data Engineer | data_engineer | 20-25 | 27-37 | 33-43 | 40-50 |
| שכר Big Data Developer | data_engineer? | 25-30 | 32-40 | 40-50 | 42-52 |
| שכר Data Analyst | data_analyst | 20-25 | 25-30 | 28-32 | 30-40 |
| Product Analyst | data_analyst? | 20-25 | 25-30 | 28-32 | 30-40 |
| שכר מפתח BI | data_analyst? | 20-25 | 25-27 | 28-32 | 32-42 |
| שכר בתחום ה QA | qa | 12-15 | 15-25 | 23-30 | – |
| שכר מפתח אוטומציה | qa | 18-25 | 25-33 | 33-38 | – |
| שכר ראש צוות QA | qa / team_lead | 18-20 | 20-25 | 25-30 | 30-35 |
| ראש צוות אוטומציה | qa / team_lead | 30-40 | 35-40 | 35-45 | – |
| Security Analyst | security | 18-20 | 20-30 | 30-40 | 35-50 |
| SOC Analyst | security | 15-20 | 20-25 | 25-30 | 30-40 |
| Security Researcher | security | 20-25 | 25-30 | 35-48 | 60-100 |
| שכר מומחה אבטחת מידע | security | 20-25 | 25-30 | 35-48 | 60-100 |
| Incident Response | security | 25-30 | 30-35 | 35-40 | 40-60 |
| שכר Malware Analyst | security | 20-28 | 28-35 | 30-40 | 40-50 |
| שכר ארכיטקט תוכנה | architect | 35-40 | 40-43 | 43-45 | 45-52 |
| Solution Architect | architect? | 20-25 | 25-35 | 32-38 | 38-48 |
| שכר ראש צוות פיתוח | team_lead | 35-40 | 40-44 | 43-45 | 45-55 |
| שכר מנהל מוצר | product_manager | 23-29 | 28-35 | 33-45 | 40-60 |
| שכר בוגר/ת מצטיין/ת | (graduate, any) | 18-28 (bucket not specified) | | | |

[R] For team_lead and architect, the 0-2 column cannot mean 0-2 years of total experience. It is probably years in the role. Treat it as unclear.

H1 2026 averages printed on the same page (₪/month, "experienced, 5+ years" context; gross not stated) [P]:

| Group | Canon | Bucket | 2025 avg | H1 2026 avg |
|---|---|---|---|---|
| Experienced candidates, all | (all tech) | 5+ | 39,810 | 41,722 |
| Security Research | security | 5+ | – | 57,643 |
| Algorithm Engineer | data_scientist? | 5+ | – | 47,273 |
| AI Engineer | data_scientist? | 5+ | – | 45,286 |
| C++ | backend? | 5+ | – | 43,897 |
| Python | backend? | 5+ | – | 42,031 |
| Node.js | backend? | 5+ | – | 38,075 |
| Product Manager | product_manager | 5+ | 39,189 | 42,543 |
| Data Analyst | data_analyst | 5+ | 27,112 | 31,000 |
| QA/Automation | qa | 5+ | 24,000 | 32,000 |

### [S7] Funder.co.il, GotFriends H1 2026 data (2026-07-07)

- URL: https://www.funder.co.il/article/204883
- Republishes GotFriends' H1 2026 data. Stat: average. Monthly [P]. Gross not stated. Period: H1 2026 vs 2025. No sample or method given.

| Group | Canon | Bucket | Value |
|---|---|---|---|
| Senior candidates | (all) | over 5 yrs | 41,722 (2025: 39,810) |
| Security Research | security | not specified | 57,643 |
| Algorithm Engineer | data_scientist? | not specified | 47,273 |
| AI Engineer | data_scientist? | not specified | 45,286 |
| C/C++ developers | backend? | not specified | ~42,600 |
| Ex-tech-unit developers | (all) | 6 yrs | 40,800 |

Geography (average) [P]: Sharon 44,000; Petah Tikva 43,083; Tel Aviv 42,461 (2025: 40,256). In 2025 Tel Aviv was ~3.3% above the rest of the country.
Hybrid [P]: 48% of roles offer 2 remote days, 31% one day, 12% none, ~0.4% fully remote.

### [S8] Bizportal, H1 2026 market roundup (2026-08-01)

- URL: https://www.bizportal.co.il/career/news/article/20037516
- Source [P]: unnamed "placement and staffing firms", job-posting data and recruiter reports. The page calls the figures estimates. Monthly averages, gross not stated.
- Values [P]: cyber researchers ~56,500; algorithm engineers ~46,300; AI engineers ~44,400; seniors 5+ yrs ~40,900 (2025 ~39,000); C/C++ ~41,750. Geography: Sharon ~43,100; Petah Tikva ~42,200; Tel Aviv ~41,600 (2025 ~39,500).
- [R] Close to, but not identical with, the GotFriends numbers in S6/S7. It is probably derived from them with different rounding, or from a different cut. I count it as **not independent** of S6/S7.

### [S9] Walla Finance, GotFriends Q1 2025 (2025-04-20)

- URL: https://finance.walla.co.il/item/3743450
- GotFriends Q1 2025 vs 2024. Monthly averages. Gross not stated [P]. Method: not described beyond ~2,000 candidates recruited per year [P].

| Role | Canon | Bucket | Q1 2025 | 2024 |
|---|---|---|---|---|
| Senior tech roles | (all) | 5+ yrs | 38,183 | 37,071 |
| Development managers / team leads | team_lead | not specified | 51,258 | 46,815 |
| C/C++ programmers | backend? | not specified | 43,218 | 39,242 |
| Product managers | product_manager | not specified | 41,525 | 37,878 |
| Information security researchers | security | not specified | 47,204 | 45,012 |
| Algorithm engineers | data_scientist? | not specified | 45,259 | 43,118 |
| Python programmers | backend? | not specified | 43,689 | 41,044 |
| Data analysts | data_analyst | not specified | 27,430 | 26,375 |
| Outstanding graduates | (junior, any) | graduate | 17,500 | – |

Gender [P]: average monthly salary men 40,657, women 37,647. Placement share by field (Q1 2025 open positions) [P]: Security 29%, AI 15%, Fintech 13%, Ad-Tech 9%. These are fields (industries), not roles.
Also read: Bizportal's version of the same release (https://www.bizportal.co.il/career/news/article/20015996, 2025-04-20) confirms 38,183 / 37,071 and the field shares.

### [S10] ICE, GotFriends 2025 full year (2026-01-06) and [S11] Maariv, same data (2026-01-06)

- URLs: https://www.ice.co.il/career/news/article/1098829 ; https://www.maariv.co.il/economy/israel/article-1269829
- GotFriends 2025 vs 2024. Averages. Neither page states monthly or gross [P] (S6 shows these are monthly figures).

| Group | Canon | Bucket | 2025 avg | Source |
|---|---|---|---|---|
| All tech workers | (all) | – | 39,810 (2024: 37,071, +7.4%) | S10, S11 |
| AI specialists (GenAI, LLM, RAG, NLP) | data_scientist? | – | ~43,212 | S11 |
| Dev group managers / dev managers / team leads | team_lead | – | 56,646 (+21%) | S11 |
| Developers from IDF tech units | (all) | ~6 yrs | 40,400 | S11 |
| RAG / GenAI specialists | data_scientist? | – | 45,000–46,000 (range) | S11 |
| Data specialists with Airflow | data_engineer? | – | ~44,500 | S11 |

Gender [P]: men ~40,657, women ~37,647. The gap fell from 11% (2024) to 7.4% (2025). Both articles also say the gap is "about 2,600", which does not match their own averages (difference 3,010).
Geography [P]: Tel Aviv average is 3.3% above outside the metro area (S11).

### [S12] Ethosia (אתוסיה), "טבלאות וסקרי שכר" page (undated)

- URL: https://ethosia.co.il/%d7%98%d7%91%d7%9c%d7%90%d7%95%d7%aa-%d7%a9%d7%9b%d7%a8/
- Publisher: Ethosia research unit [P]. **No date, no units, no gross/net, no average/median statement** [P]. [R] Values are evidently thousands of ₪ per month. The year is unknown, so treat this as weaker than dated sources.
- Buckets [P]: professional tier 0–1 / 2–4 / 5–8 / 9+. The management tier (1–4 / 5–8 / 9+) has **no role labels** in the page text, so it is unusable.
- ToS/robots: robots.txt as fetched contained only a SemrushBot crawl-delay group, with no `*` rules. Terms not fetched.

| Source role | Canon | 0–1 | 2–4 | 5–8 | 9+ |
|---|---|---|---|---|---|
| Java | backend? | 22–27 | 28–34 | 35–45 | 45–55 |
| C# / .Net | backend? | 22–27 | 28–34 | 35–45 | 45–55 |
| Python | backend? | 22–27 | 28–34 | 35–45 | 45–55 |
| Web Developer | fullstack? / frontend? | 17–21 | 22–24 | 25–29 | 30–32 |
| PHP / Frontend (HTML/CSS) | frontend | 15–20 | 21–25 | 31–39 | 34–39 |
| Mobile App Developer | mobile | 18–23 | 24–30 | 31–37 | 38–45 |
| Software Architect | architect | – | 38–45 | 46–50 | 51–55 |
| Manual QA | qa | 13–16 | 17–21 | 22–26 | 27–32 |
| Automation | qa | 16–21 | 22–30 | 31–38 | 39–48 |
| BI Specialist | data_analyst? | 16–20 | 21–26 | 27–32 | 33–42 |
| Info Security | security | 18–23 | 24–32 | 33–45 | 46–55 |
| Product Manager (marketing table) | product_manager | 19–23 | 24–32 | 33–42 | 43–55 |

### [S13] Ethosia, annual report "דו״ח אתוסיה 2025" (2025-12-24)

- URL: https://ethosia.co.il/report-2025-2026/
- Method [P]: not stated (research division, ongoing salary surveys). ₪, but monthly/gross not stated [P]. [R] The magnitudes imply monthly figures.
- Stat [P]: average for candidates with **5 years' experience**, 2024 → 2025.

| Source role | Canon | Bucket | 2024 | 2025 |
|---|---|---|---|---|
| Industry average (all) | (all) | – | 29,900 | 32,500 |
| Server-side development | backend | 5 yrs | 33,000 | 35,000 |
| Full Stack | fullstack | 5 yrs | 30,500 | 31,400 |
| Client-side development | frontend | 5 yrs | 26,000 | 28,000 |
| Mobile app development | mobile | 5 yrs | 28,500 | 30,000 |
| Automation testing | qa | 5 yrs | 17,800 | 18,500 |
| Project management | (not canonical) | 5 yrs | 25,500 | 25,000 |
| IT | (not canonical) | 5 yrs | 25,000 | 26,000 |
| Executives | (not canonical) | 5 yrs | 52,000 | 52,000 |

Peak salaries "about 54,500" for AI and data engineering roles [P].
Employment [P]: high-tech employees 417,000 (Dec 2024) → 409,000 (Dec 2025); about 63% of employees are in technical roles; women about one-third of the workforce; open positions 9,200 → 11,500. Access: open page, no gate.

### [S14] Ethosia Market Intelligence, July 2026 (defense-tech and advanced systems sector only)

- URL: https://ethosia.co.il/ethosia-market-intelligence-2026/ (2026-07-30)
- Method [P]: Brightsource Data Analytics profiles (June 2026), public data, and Ethosia internal recruitment data from the last 12 months. **Base monthly gross**, thousands ₪, mid-2026 [P].
- [R] This covers **defense-tech only**, so it is not representative of the general market. Use it as a cross-check only.

| Source role | Canon | 0-1 | 2-4 | 5-8 | 9+ | Manager |
|---|---|---|---|---|---|---|
| Software Engineer | backend?/fullstack? | 22-27 | 28-32 | 33-42 | 43-55 | 56-68 |
| C4I / Cyber Engineer | security? | 24-28 | 29-36 | 37-48 | 49-62 | 63-78 |
| Systems Architect | architect? | — | — | 38-52 | 53-66 | 67-80 |
| Quality Engineer | qa? | 18-21 | 22-26 | 27-33 | 34-42 | 43-52 |

Role share in this sector [P]: Software Engineer = 46% of the talent pool and 28.3% of open positions. Geography of talent [P]: Center 23.6%, Tel Aviv 21.3%, Haifa 14.3%, South 7.2%, Jerusalem 3.9% (the North value is printed as "90%", an evident typo).

### [S15] Drushim, "טבלאות שכר 2026 תוכנה - SOFTWARE" (JobInfo data), 2026-01-01

- URL: https://www.drushim.co.il/article/107
- Data [P]: "נתוני השכר נמסרו באדיבות חברת ההשמה Jobinfo". Units: thousands ₪ [P]. Gross/net and monthly not stated [P]. No method or sample.
- Buckets [P]: בוגר | 2-3 שנים | 3-5 שנים | מעל 5 שנים | ראש צוות.
- [R] Several rows are printed with inverted ranges, which suggests a carelessly maintained table. The publication date may be a re-stamp of older data.
- ToS/robots: drushim robots.txt allows `/` for `*`; only some `/api/` paths are disallowed. Terms not fetched.

| Source role | Canon | בוגר | 2-3 | 3-5 | מעל 5 | ראש צוות |
|---|---|---|---|---|---|---|
| מפתח/ת Fullstack | fullstack | 20-21 | 25-28 | 30-34 | 35-40 | 40-42 |
| מפתח/ת python | backend? | 20-21 | 26-28 | 30-34 | 35-40 | 40-42 |
| מתכנת Java | backend? | 19-21 | 26-28 | 30-34 | 35-40 | 40-42 |
| מפתח/ת מובייל | mobile | 19-21 | 24-26 | 30-34 | 35-40 | 40-42 |
| בדיקות (QA) | qa | 14-16 | 16-18 | "20-18" (as printed) | "26-22" (as printed) | 28-30 |
| מהנדס/ת אוטומציה | qa | 18-20 | 20-24 | 24-27 | 32-35 | 35-37 |
| מנהל/ת מוצר | product_manager | - | 21-24 | 25-28 | 28-30 | 30-35 |
| אבטחת מידע malware | security | 18-20 | 20-22 | 22-25 | 25-27 | 28-30 |
| Data Security Expert | security | (blank) | 18-20 | 21-23 | 25-28 | 28-32 |

### [S16] Drushim, "טבלאות שכר - הייטק כללי / תשתיות / מערכות מידע" (JobInfo), 2026-01-01

- URL: https://www.drushim.co.il/article/117/
- Same source and caveats as S15 [P]. "הנתונים מעודכנים לשנת 2026".

| Source role | Canon | בוגר | 2-3 | 3-5 | מעל 5 | ראש צוות |
|---|---|---|---|---|---|---|
| DevOps | devops | - | 25-28 | 30-32 | 35-40 | 40-42 |
| אנאליסט (IS table, no בוגר column) | data_analyst? | n/a | 11-15 | 15-18 | 18-22 | 23-29 |
| BI (IS table) | data_analyst? | n/a | 14-18 | 19-22 | 22-25 | 26-30 |

### [S17] AllJobs, "טבלאות שכר 2026" (high-tech/software tables)

- URL: https://www.alljobs.co.il/User/SalaryCompound/SalarySurvey.aspx (a preview of the same table is at https://www.alljobs.co.il/Partners/Hitech/HitechIndex.aspx)
- Method [P]: "weighted data from the AllJobs site". **Monthly gross, thousands ₪. Excludes** car, shifts, pension, **bonuses and equity**. Full-time employees only. The ranges "are averages". The table is "updated regularly"; no explicit update date [P].
- Buckets [P]: "0-2 שנות ניסיון", "3-5 שנות ניסיון", "6 + שנות ניסיון", "ניהולי / בכיר".
- ToS/robots: robots.txt does not disallow `/User/SalaryCompound/` or `/Partners/Hitech`. Terms not fetched.

| Source role | Canon | 0-2 | 3-5 | 6+ | ניהולי/בכיר |
|---|---|---|---|---|---|
| מהנדס תוכנה | backend?/fullstack? | 10-20 | 15-25 | 20-30 | 20-32 |
| תוכניתן JAVA | backend? | 13-18 | 17-24 | 23-28 | 26-33 |
| BackEnd (listed in the hardware table) | backend? | 17-20 | 19-27 | 24-33 | 28-35 |
| מתכנת WEB (internet table) | frontend?/fullstack? | 8-15 | 10-20 | 12-25 | 20-30 |
| QA תוכנה | qa | 6-13 | 8-16 | 11-22 | 17-31 |
| מומחה אבטחת מידע | security | 8-14 | 12-21 | 17-25 | 20-30 |
| מהנדס אבטחת מידע | security | 11-14 | 15-19 | 20-26 | 26-30 |
| מנהל מוצר- תוכנה | product_manager | 15-20 | 20-25 | 25-32 | (blank) |
| ארכיטקסט מערכת (hardware table) | architect? | 16-22 | 21-27 | 26-33 | 22-36 |

Not present on AllJobs [P]: fullstack, frontend, mobile, devops, data scientist, data engineer, data analyst, team lead.
[R] AllJobs runs systematically **lower** than every recruiter table, by 5-10K at mid and senior levels. A plausible reason is that it weights listings across all employer types, including non-tech companies and services firms.

### [S18] Levels.fyi, Israel location pages (live, "last updated 10/14/2026")

- URLs:
  - SWE all levels: https://www.levels.fyi/t/software-engineer/locations/israel
  - SWE entry: https://www.levels.fyi/t/software-engineer/levels/entry-level/locations/israel
  - SWE senior: https://www.levels.fyi/t/software-engineer/levels/senior/locations/israel
  - Data Scientist: https://www.levels.fyi/t/data-scientist/locations/israel
  - Product Manager: https://www.levels.fyi/t/product-manager/locations/israel
  - The `mid-level` and `staff` slugs returned 404. Level pages have no years-of-experience definition [P]. The entry-level filter includes "internship" and "entry" [P].
- Stat [P]: **annual total compensation** in ₪ (median, p25, p75, p90). Self-reported, reviewed before publication. Total comp normally includes base + stock + bonus; the pages break comp down that way, but the headline label is just "Total Comp".
- ToS/robots: robots.txt has `User-agent: *` / `Allow: /`. User-initiated agents (Claude-User etc.) are allowed. Training crawlers (ClaudeBot, GPTBot, …) are disallowed except a few paths. The terms page (https://www.levels.fyi/terms) returned **403**, so it was not read.

| Page | Canon | Level | n | p25 /yr | Median /yr | p75 /yr | p90 /yr | Median ÷12 [R] |
|---|---|---|---|---|---|---|---|---|
| Software Engineer | fullstack/backend/frontend? (generic SWE) | all | 1,914 | 339K | 449,171 | 559K | 709K | ≈37,431 (p25 ≈28,250; p75 ≈46,583) |
| Software Engineer | generic SWE | Entry (incl. intern) | 128 | 175K | 261,422 | 315K | 418K | ≈21,785 (p25 ≈14,583; p75 ≈26,250) |
| Software Engineer | generic SWE | Senior | 916 | 452K | 537,820 | 660K | 835K | ≈44,818 (p25 ≈37,667; p75 ≈55,000) |
| Data Scientist | data_scientist | all | 78 | 394K | 471,063 | 537K | 628K | ≈39,255 |
| Product Manager | product_manager | all | 161 | 388K | 468,076 | 558K | 741K | ≈39,006 |

City medians (annual total comp) [P]. SWE: Petach Tikva 509,325; Tel Aviv 491,512; Ramat Gan 392,846. Data Scientist: Haifa 449,717; Jerusalem 440,884; Tel Aviv 439,938. PM: Herzliyya 471,752; Tel Aviv 460,220; Jerusalem 416,374.
[R] The ÷12 figures are monthly *total comp*, not monthly gross base. They are not comparable with the recruiter ranges without removing stock and bonus.

### [S19] Payscale, Software Engineer – Israel

- URL: https://www.payscale.com/research/IL/Job=Software_Engineer/Salary (last updated 2026-07-02 [P])
- Stat [P]: annual base salary: average ₪229,839, median ₪230k, p10 ₪10k, p90 ₪462k. n = 144 profiles. Average total comp by experience: entry (<1 yr) ₪221,726 (n=25); early career (1–4 yrs) ₪250,700 (n=80). Mid, experienced and late career showed no values in the fetched text.
- [R] Monthly equivalents: median base ≈19,167; entry ≈18,477; early career ≈20,892. The p10 of ₪10k/yr is implausible for a full-time engineer. This is a small, low-quality sample, so use it only as a sanity floor.
- ToS/robots: robots.txt does not disallow `/research/`. Terms not fetched.

### [S20]–[S25] Israel CBS (הלמ"ס), high-tech average wage per salaried job, via press

CBS release pages for these months were not found as HTML. The CBS tables are PDFs (see Blocked). The figures below are as reported by the press, attributed to CBS.
- Definition [P]: average wage **per salaried job** (not per person) in the CBS "high-tech" sector, current prices, monthly. It covers all employees of high-tech companies, not only developers. [S25] labels the whole-economy figure "ברוטו". [S21] attributes the March spikes to annual bonuses and grants [P], so **bonuses are included in the month they are paid**.
- ToS/robots: cbs.gov.il robots.txt disallows only SharePoint system paths; `/he/mediarelease/` is not disallowed. Terms not fetched.

| ID | URL | Pub. date | Period | Value (₪/month, high-tech avg per salaried job) | Notes |
|---|---|---|---|---|---|
| S20 | https://www.calcalistech.com/ctechnews/article/cysn2t0w7 | 2026-10-05 | Jul 2026 | 34,301 (Jun 2026: 36,584; Jul 2025: 33,520) | Programming & computer consultancy 36,052 (218,000+ workers, 55% of high-tech); scientific R&D 37,578 (46,400 workers); high-tech = 9.3% of salaried jobs |
| S21 | https://www.calcalistech.com/ctechnews/article/emfdd1msa | 2026-06-04 | Mar 2026 | 38,467 (record; Mar 2025: 36,884; Feb 2026: 35,619) | Programming 40,117; scientific R&D 39,866; 396,000 high-tech jobs |
| S22 | http://www.calcalistech.com/ctechnews/article/y8o8kvcer | 2026-08-04 | May 2026 | 35,760 (Apr 2026: 34,870; May 2025: 31,459) | +13.7% YoY |
| S23 | https://finance.walla.co.il/item/3858394 | 2026-08-04 | May 2026 | 35,760 | 397.1K high-tech jobs = 9.5% of salaried jobs |
| S24 | https://finance.walla.co.il/item/3731717 | 2025-03-04 | **Year 2024** | **31,858** (2023: 29,826) | 400.6K jobs, 10% of salaried jobs |
| S25 | https://www.bizportal.co.il/general/news/article/20021200 | 2025-09-04 | Jun 2025 | 32,774 | Whole-economy figure explicitly "ברוטו" |

Also read: Maariv https://www.maariv.co.il/economy/israel/article-1352120 (2026-08-04) gives the whole-economy May 2026 average of 14,263 (gross) and says high-tech is 9.5% of jobs. Its headline "48,666" figure is not explained in the body, so I did not use it.

### [S26] Israel Innovation Authority, 2025 High-Tech Employment Status Report, via Maariv (2025-04-07)

- URL: https://www.maariv.co.il/economy/israel/article-1186406 (the IIA page itself returned 403; see Blocked)
- [P] 2024 average high-tech salary 32.3K ₪, 2.8× the national average. High-tech employment 391K in 2024 (-1.2%), ~11.4% of total employment. The R&D share of high-tech employees rose from 37% (2012) to about 50% (2024).

### [S27] Israel Innovation Authority, 2026 High-Tech Status Report, via AHK (page dated 2026-05-31)

- URL: https://israel.ahk.de/en/news/israeli-high-tech-2025-record-exports-and-exits-but-first-decline-in-r-d-employees-in-a-decade
- [P] About 400,000 high-tech employees in 2025 (11.4% of all employees). First decline in R&D headcount in ten years. 62% of employees of private Israeli tech companies were based in Israel (69% in 2019). **No salary figures on this page.**

### [S28] Globes English, Ethosia 2023 survey (2024-01-25), historical only

- URL: https://en.globes.co.il/en/article-1001468626
- [P] Average tech salary 30,800 (2023), 30,000 (2022), 29,100 (2021). Senior managers' average 54,100/month (2023). Averages only; gross not stated; no sample given.

### [S29] Globes English, altshare options study (2025-01-12) and [S30] Globes English, options value (2026-04-26)

- URLs: https://en.globes.co.il/en/article-1001499150 ; https://en.globes.co.il/en/article-1001540937
- S29 [P]: number of options distributed by tech companies in 2024 down 76% since 2021. Over 31 million options in 2024, about half the 2023 number. altshare says it controls 40% of Israel's options market. The study measures volume, not prevalence.
- S30 [P]: nearly NIS 150 billion in in-the-money options and blocked shares held by Israeli employees at end-2025 (Bank Hapoalim strategist). The share of employees holding options is **not stated**.

### Pages read but not used for numbers

- Bizportal, 2026-01-19 (https://www.bizportal.co.il/career/news/article/20026286): mixes US survey data, AI-prompt examples and unsourced FAQ figures, with internal inconsistencies. **Not used.**
- INN "המדריך המלא לשכר בהייטק" (https://www.inn.co.il/news/688035, 2026-01-19): labelled "תוכן שיווקי" (sponsored). It links to JobInfo and gives no salary figures.
- Drushim index (https://www.drushim.co.il/article/87/): only links to the tables in S15 and S16.
- CBS media release index (https://www.cbs.gov.il/he/mediarelease/Pages/default.aspx): no wage releases were listed at the time of access.
- Ethosia and GotFriends home pages: used only to find the salary pages.

---

## Secondary data

**Role share of the workforce or job postings**
- No source gives shares for the canonical roles (backend vs frontend vs devops, etc.). **Not found.**
- Partial:
  - CBS sub-sector: "programming and computer consultancy" = 55% of high-tech employees, July 2026 [S20].
  - R&D ≈ 50% of high-tech employees in 2024 [S26].
  - About 63% of employees are in technical roles [S13].
  - In defense-tech, Software Engineer is 46% of talent and 28.3% of open positions [S14].
  - GotFriends Q1 2025 open positions by *field*: Security 29%, AI 15%, Fintech 13%, Ad-Tech 9% [S9].

**Equity/options prevalence**
- The share of employees with equity: **not found.**
- What exists:
  - option volume trend, -76% from 2021 to 2024 [S29];
  - aggregate value, ~NIS 150b at end-2025 [S30];
  - Nisha *estimates* of grant sizes by role and company type, and "equity can add 20%–40%" at large companies [S5];
  - Nisha's fullstack ranges at seed and Series A-B are marked "+ options" [S1].

**Geography**
- GotFriends H1 2026 averages: Sharon 44,000; Petah Tikva 43,083; Tel Aviv 42,461 [S7]. Bizportal's ~43,100 / ~42,200 / ~41,600 [S8] are probably the same data.
- Nisha: Tel Aviv/Herzliya +10-15%; Be'er Sheva -10-20% [S1][S4].
- Levels.fyi city medians, annual total comp [S18]:
  - SWE: Petach Tikva > Tel Aviv > Ramat Gan.
  - Data Scientist: Haifa ≈ Jerusalem ≈ Tel Aviv.
  - PM: Herzliyya > Tel Aviv > Jerusalem.
- Haifa, Jerusalem and Be'er Sheva SWE figures: **not found** as numbers, except Nisha's percentage for Be'er Sheva.

**Gender**
- GotFriends 2025 averages: men ~40,657, women ~37,647 [S9][S10][S11]. The stated gap ("~2,600", 7.4%) is internally inconsistent.
- Ethosia: women are about one-third of the workforce [S13].
- Not by role.

**Company stage**
- Nisha only:
  - fullstack at 5 yrs by company type [S1];
  - senior DevOps by employer type [S3];
  - senior cyber by employer type [S4];
  - QA by sector [S5].
- All are Nisha estimates.

---

## 1. Coverage matrix (canonical role × proposed bucket)

Bucket mapping [R]: junior 0-2 ← (Nisha 1-2, GotFriends 0-2, AllJobs 0-2, Ethosia 0–1 (+part of 2–4), JobInfo בוגר/2-3). Mid 3-5 ← (Nisha 3-5, GotFriends 3-5, AllJobs 3-5, Ethosia 2–4, JobInfo 3-5, Ethosia annual "5 yrs"). Senior 6-9 ← (Nisha 6-10/6+, GotFriends 6-10, AllJobs 6+, Ethosia 5–8, JobInfo מעל 5). Staff 10+ ← (Ethosia 9+ only; management columns are *not* mapped here).
Grades: **strong** = 2+ independent publishers that broadly agree; **weak** = 1 source, or sources disagree, or the bucket fit is poor; **missing** = no usable number. Nisha pages S1-S5 count as one publisher. S7, S8, S9, S10 and S11 count as GotFriends (S6). S15 and S16 are JobInfo.

| Canon | Junior 0-2 | Mid 3-5 | Senior 6-9 | Staff 10+ |
|---|---|---|---|---|
| fullstack | **strong**: S1, S6, S15 (20-26K) | **strong**: S1, S6, S15, S13 (25-37K; Ethosia 5-yr avg 31,400) | **strong**: S1, S6, S15 (32-45K) | **missing** (only Lead/management columns) |
| backend | **strong**: S1, S6, S17 BackEnd; Ethosia language rows S12 (≈20-27K) | **weak**: disagree. S1 24-28K, S6 30-37K, S17 19-27K, S13 5-yr avg 35,000 | **weak**: disagree. S1 28-35K, S6 35-45K, S17 24-33K, S12 (Java/Python 5–8) 35-45K | **weak**: S12 language rows 9+ 45-55K (mapping uncertain) |
| frontend | **strong**: S1, S6 (20-29K). S12 PHP/Frontend 15-20 is lower | **strong**: S1, S6, S13 (25-38K; Ethosia 5-yr avg 28,000) | **strong**: S1, S6, S12 (31-47K) | **weak**: S12 only (34–39K) |
| mobile | **strong**: S2, S6, S15, S12 (18-26K) | **strong**: S2, S6, S15, S12, S13 (24-34K) | **strong**: S2, S6, S15, S12 (31-40K) | **weak**: S12 only (38–45K) |
| devops | **weak**: disagree. S3 16-22K, S2 22-27K, S6 25-30K, S16 (2-3 yrs) 25-28K | **strong**: S6, S16 agree (30-38K); S3 lower (24-31K) | **strong**: S2, S3, S6, S16 (32-45K) | **missing** |
| data_scientist | **strong**: S1, S6 (22-35K) | **strong**: S1, S6 (25-45K, wide) | **strong**: S1, S6 (40-55K) | **missing** (S18 all-levels only) |
| data_engineer | **strong**: S1, S6 (20-25K) | **strong**: S1, S6 (25-37K) | **strong**: S1, S6 (32-43K) | **missing** |
| data_analyst | **weak**: S1 15-20K vs S6 20-25K; S16 "אנאליסט" (IS) 11-15K | **weak**: S1 20-25K, S6 25-30K, S16 15-18K | **weak**: S1 25-30K, S6 28-32K agree; S16 18-22K lower; GotFriends 5+ avg 27,112-31,000 | **missing** |
| qa (manual + automation) | **strong**: S5, S6, S12, S15, S2 (manual ~10-16K; automation ~16-26K). S17 6-13K is an outlier | **strong**: S5, S6, S12, S15 (manual 15-25K; automation 22-33K) | **strong**: S5, S6, S12 (manual 19-30K; automation 31-38K) | **weak**: S12 9+ (manual 27–32K; automation 39–48K), S5 8+/7+ (manual 24-27K; automation 38-44K) |
| security | **strong** but heterogeneous: S4, S6, S12, S15 (≈12-25K by sub-family); S17 lower | **strong** (heterogeneous): S4, S6, S12, S15 (≈17-36K) | **strong** (heterogeneous): S4, S6, S12 (≈25-55K) | **weak**: S12 9+ 46–55K only |
| architect | **missing** (not a junior role; S6 "0-2" column is not total experience) | **weak**: S6 40-43K, S12 (2–4) 38–45K vs S2 25-35K | **weak**: S6 43-45K, S12 46–50K vs S2 35-45K | **weak**: S12 9+ 51–55K only |
| team_lead | **missing** (not meaningful) | **weak**: bucket meaning unclear. S6 TL rows; S3 DevOps TL 32-38K | **weak**: S1 Lead 38-48K, S6 43-45K, S15 ראש צוות 40-42K; GotFriends TL avg 51,258 (Q1 2025) / 56,646 (2025) | **weak**: management columns only |
| product_manager | **weak**: spread 13-29K. S1 13-24K, S6 23-29K, S12 19-23K, S17 15-20K, S15 (2-3) 21-24K | **strong**: S1, S6, S12, S15 (23-35K); S17 lower | **weak**: S1 24-30K vs S6 33-45K, S12 33-42K; GotFriends 5+ avg 42,543 | **weak**: S12 9+ 43–55K only |

Generic "software engineer" cross-checks that do not map to one canonical role: S18 (Levels.fyi, all/entry/senior total comp), S19 (Payscale), S14 (defense-tech SWE), S17 "מהנדס תוכנה".

---

## 2. Disagreements (shown, not resolved)

1. **QA/automation at ~5 years.**
   - Ethosia: "automation testing" 5-yr average 18,500 for 2025 [S13].
   - GotFriends: "QA/Automation" 5+ average 32,000 for H1 2026, and 24,000 for 2025 [S6].
   - Nisha: automation 5-7 yrs 33-38K in hi-tech [S5]. Ethosia's own table: automation 5–8 is 31–38 [S12].
   - [R] Possible reasons:
     - Ethosia's report figure may describe test roles broadly, including manual testers;
     - the report and the table are not consistent with each other;
     - year differences.
   - The 18,500 sits close to manual-QA levels.
2. **Backend mid/senior.**
   - Nisha Backend Engineer: 24-28K (3-5) and 28-35K (6-10) [S1].
   - GotFriends Backend: 30-37K and 35-45K [S6].
   - Ethosia: server-side 5-yr average 35,000 [S13].
   - AllJobs BackEnd (in its hardware table): 19-27K and 24-33K [S17].
   - [R] The Nisha row sits oddly below Nisha's own Java/Python rows (25-35K / 35-45K) in the same publication. AllJobs is consistently low (see 3).
3. **AllJobs vs recruiters in general.**
   - AllJobs is lower in almost every row: "מהנדס תוכנה" 0-2 = 10-20K, QA 0-2 = 6-13K [S17].
   - [R] Possible reasons:
     - its base is weighted site data across all employer types;
     - it explicitly excludes bonuses and equity;
     - its update date is unknown.
   - Recruiter tables reflect placements into tech companies.
4. **DevOps junior.**
   - Nisha 2026 guide: 16-22K (0-2) [S3]. Nisha older table: 22-27K (1-2) [S2].
   - GotFriends: 25-30K (0-2) [S6]. JobInfo: 25-28K (2-3) [S16].
   - [R] The different bucket starts (0 vs 1-2 vs 2-3) explain part of this. Nisha's 2026 guide is a blend of "market sources", not placements.
5. **Overall averages.**

   | Figure | Value | Source |
   |---|---|---|
   | CBS 2024 annual | 31,858 | [S24] |
   | Innovation Authority 2024 | 32.3K | [S26] |
   | Ethosia 2024 / 2025 | 29,900 / 32,500 | [S13] |
   | GotFriends 2024 / 2025 / H1 2026 (5+) | 37,071 / 39,810 / 41,722 | [S6][S10] |
   | CBS monthly 2026 | 34,301–38,467 | [S20][S21] |

   [R] Reasons:
   - CBS covers every employee of high-tech firms (incl. non-tech staff), per job, with bonuses in the month paid.
   - GotFriends covers placed or experienced candidates.
   - Ethosia's population and statistic are not described.
6. **GotFriends H1 2026 as reported in different places.**
   - C/C++: ~42,600 on Funder [S7] vs 43,897 on GotFriends' own page [S6].
   - Bizportal [S8] shows ~40,900 / ~56,500 / Tel Aviv ~41,600, vs GotFriends 41,722 / 57,643 / Tel Aviv 42,461.
   - [R] Probably rounding or different data cuts. GotFriends' own page should take precedence.
7. **Levels.fyi vs recruiter ranges.**
   - Levels SWE senior median: 537,820/yr total comp, ≈44.8K/month [R] [S18]. That is at or above the top of the recruiter senior ranges (S1 32-45K, S6 34-45K).
   - [R] Reasons: total comp includes stock and bonus; self-reported; skewed to multinationals (Meta, Google and Apple medians ~880-900K/yr appear on the same page).
8. **Payscale vs everything.** Median base ₪230k/yr ≈ 19.2K/month [R] [S19]. That is far below recruiter mid-level ranges. n=144 and the p10 of ₪10k signal poor data quality.
9. **Product manager seniority curve.**
   - Nisha prints Senior (24-30K) at or below Mid (23-31K) [S1].
   - GotFriends: 33-45K senior; 5+ average 42,543 [S6].
   - Ethosia: 33–42 (5–8) [S12].
   - [R] The Nisha senior row looks like a data-entry error.
10. **Gender gap (GotFriends 2025).** The stated "~2,600" does not match its own averages (40,657 − 37,647 = 3,010) [S10][S11].
11. **Geography direction.**
    - GotFriends (H1 2026): Sharon and Petah Tikva **above** Tel Aviv [S7].
    - Nisha: Tel Aviv/Herzliya +10-15% vs other areas [S1][S4].
    - [R] Not necessarily a contradiction: "Sharon" includes Herzliya, and Nisha compares against the whole country, not against Petah Tikva.

---

## 3. Gross vs net

| Source | What it says | Unclear |
|---|---|---|
| Nisha S1 | Gross monthly stated for the headline and the algorithms table; other tables say only "₪/חודש" | Whether every table is gross (probably) |
| Nisha S2–S5 | Gross monthly stated | Range meaning; mix of "market sources" and estimates |
| GotFriends S6 | Monthly, thousands ₪; **gross/net not stated** | Gross assumed by convention [R], not confirmed; average vs median not stated |
| GotFriends via press S7–S11 | Averages; gross not stated | Same |
| Ethosia tables S12 | **No units, no gross/net, no date** | Everything except the numbers |
| Ethosia annual S13 | ₪ averages for 5-yr candidates; monthly/gross not stated | Basis |
| Ethosia MI S14 | **Base monthly gross**, explicit | Defense-tech only |
| JobInfo/Drushim S15–S16 | Thousands ₪; gross/net and monthly not stated | Basis; real data year |
| AllJobs S17 | **Monthly gross, excludes bonuses and equity**, explicit | Update date; sample |
| Levels.fyi S18 | Annual total comp (base + stock + bonus) | Not comparable to monthly base without decomposition |
| Payscale S19 | Annual base (headline); total pay by experience | Quality |
| CBS via press S20–S25 | Average per salaried job, monthly, gross (S25 states "ברוטו"), bonuses included in the month paid | Annual 2025 average not found; CBS PDF tables not read |

[R] None of the Israeli recruiter tables say whether "salary" includes the employer's pension/severance contributions or a car allowance. Israeli convention ("שכר ברוטו") usually excludes the employer side, but no source states this except AllJobs, which excludes them explicitly.

---

## 4. Blocked / needs approval

| Item | URL | Status |
|---|---|---|
| Innovation Authority press pages (2026 report; 2025 employment report; Women in High-Tech 2026) | https://innovationisrael.org.il/en/press_release/israeli-high-tech-report-2026/ ; https://innovationisrael.org.il/en/press_release/2025-high-tech-employment-status-report/ ; https://innovationisrael.org.il/en/report_year/women-in-high-tech-2026/ | **blocked: HTTP 403** |
| IIA "סקר כוח אדם בהייטק 2026" (Aug 2026), PDF | https://innovationisrael.org.il/wp-content/uploads/2026/08/סקר-כוח-אדם-בהייטק-2026.pdf | **needs user approval to download** (size not shown) |
| IIA "Annual Report The State of High Tech 2026" (Hebrew), PDF | https://innovationisrael.org.il/wp-content/uploads/2026/05/Annual-Report-The-State-of-High-Tech-2026Heb.pdf | **needs user approval to download** (size not shown) |
| IIA High-Tech Employment Report (English, Apr 2025), PDF | https://innovationisrael.org.il/en/wp-content/uploads/sites/3/2025/04/Innovation-Authority-High-Tech-Employment-Report-English-Final.pdf | **needs user approval to download** (size not shown) |
| IIA Women in High Tech 2026 (Hebrew), PDF | https://innovationisrael.org.il/wp-content/uploads/2026/03/%D7%AA%D7%9E%D7%95%D7%A0%D7%AA-%D7%9E%D7%A6%D7%91-2026-%D7%A0%D7%A9%D7%99%D7%9D-%D7%91%D7%94%D7%99%D7%99%D7%98%D7%A7-1.pdf | **needs user approval to download** (size not shown) |
| CBS Table 7, high-tech jobs and wages (Jan 2026 release), PDF | https://www.cbs.gov.il/he/mediarelease/DocLib/2026/003/26_26_003t7.pdf | **needs user approval to download**; this is the primary source for the CBS figures quoted via the press |
| Glassdoor Israel salaries | https://www.glassdoor.com/Salaries/israel-software-engineer-salary-SRCH_IL.0,6_IN119_KO7,24.htm | **blocked: HTTP 403**. robots.txt allows most `/Salaries/` for `*` but disallows everything for ClaudeBot/GPTBot |
| Levels.fyi Terms of Use | https://www.levels.fyi/terms | **blocked: HTTP 403** (robots.txt read instead) |
| Levels.fyi mid-level and staff Israel pages | …/levels/mid-level/locations/israel ; …/levels/staff/locations/israel | not found (404; slug guesses) |
| Indeed Israel salaries | https://il.indeed.com/career/software-engineer/salaries | not found (404) |
| GotFriends `/jobssalary` | (path disallowed in robots.txt) | not accessed, by rule |

**Not found** (searched, no current edition located):
- SQLink, Matrix/Experis (the only Experis Israel survey found was 2018 press), Adam Milo, Elad, Manpower: no public 2024-2026 salary tables found.
- TheMarker: no salary-survey article found.
- Geektime: no salary survey found.
- Start-Up Nation Central: no 2025/2026 human-capital report found.
- Hibob/Comeet: no public Israel compensation report found.
- Ethosia: no dated 2026 general-market role table found. Only the undated table page [S12], the Dec 2025 report [S13] and the defense-tech MI [S14].

Terms of Use pages were not fetched for Nisha, GotFriends, Ethosia, Drushim, AllJobs, Payscale or the press sites. Only robots.txt was checked (summaries in each source block above; calcalistech.com robots.txt does not disallow `/ctechnews/`).

---

## 5. Open questions for the user

1. **Buckets:** GotFriends' 0-2 / 3-5 / 6-10 / management fits the proposal best, but no source has a non-management 10+ bucket except Ethosia's 9+. Do you want to keep "staff 10+" (and fill it from Ethosia 9+ only, or extrapolate), or merge it into senior (6+)?
2. **What a range means:** sources publish "from–to" without defining it. Should the synthetic generator treat a range as roughly p25–p75, or as p10–p90? This choice changes the spread a lot. Nothing published settles it.
3. **Which source should anchor each role?** Possible rule: the GotFriends 2026 table as the primary anchor (dated Sep 2026, covers all 13 roles and matches the buckets), with Nisha and Ethosia as cross-checks. Or average the recruiter midpoints?
4. **Base vs total comp:** should the synthetic posts be base salary only (recruiter tables, AllJobs), or should some fraction mention total comp/RSUs at Levels.fyi-like levels (multinationals)?
5. **Gross assumption:** GotFriends, JobInfo and the Ethosia tables do not say "gross". OK to treat them as gross by Israeli convention?
6. **Approve PDF downloads?** The IIA 2026 State of High-Tech report and the 2026 manpower survey may contain occupation shares and wage data. CBS Table 7 would let us cite CBS directly instead of via the press. See Blocked.
7. **Defense-tech (S14) and AllJobs (S17):** include them as low-weight signals, or exclude them as non-representative (defense) or likely stale/low (AllJobs)?
8. **QA split:** our canonical `qa` merges manual QA and automation, whose pay differs by ~1.5-2× at the same seniority [S5][S6][S12]. Should the generator model a manual/automation mix inside `qa`?
9. **Team lead and architect:** these are roles *after* years of experience. Should they be generated only in senior/staff buckets?

---

## Sources

- S1 Nisha, "משכורות הייטק" (2026-05-28, data Apr 2026): https://www.nisha.co.il/%d7%9e%d7%a9%d7%9b%d7%95%d7%a8%d7%95%d7%aa-%d7%94%d7%99%d7%99%d7%98%d7%a7/
- S2 Nisha, salary tables "הייטק" (undated, 2024/2025 edition): https://www.nisha.co.il/salary-tables/%D7%94%D7%99%D7%99%D7%98%D7%A7/
- S3 Nisha, DevOps/Cloud/SRE salary guide (2026-08-31): https://www.nisha.co.il/?p=12547
- S4 Nisha, cyber salary guide (2026-08-31): https://www.nisha.co.il/%D7%9E%D7%93%D7%A8%D7%99%D7%9A-%D7%A9%D7%9B%D7%A8-%D7%91%D7%A1%D7%99%D7%99%D7%91%D7%A8/
- S5 Nisha, QA and automation salary table (2026-01-23): https://www.nisha.co.il/טבלת-שכר-qa-ואוטומציה/
- S6 GotFriends, "טבלת שכר בהייטק 2026" (updated Sep 2026): https://www.gotfriends.co.il/%D7%91%D7%9C%D7%95%D7%92%D7%99%D7%9D/high-tech-salary-tables/
- S7 Funder, GotFriends H1 2026 (2026-07-07): https://www.funder.co.il/article/204883
- S8 Bizportal, H1 2026 salary roundup (2026-08-01): https://www.bizportal.co.il/career/news/article/20037516
- S9 Walla Finance, GotFriends Q1 2025 (2025-04-20): https://finance.walla.co.il/item/3743450 ; also Bizportal (2025-04-20): https://www.bizportal.co.il/career/news/article/20015996
- S10 ICE, GotFriends 2025 (2026-01-06): https://www.ice.co.il/career/news/article/1098829
- S11 Maariv, GotFriends 2025 (2026-01-06): https://www.maariv.co.il/economy/israel/article-1269829
- S12 Ethosia, salary tables page (undated): https://ethosia.co.il/%d7%98%d7%91%d7%9c%d7%90%d7%95%d7%aa-%d7%a9%d7%9b%d7%a8/
- S13 Ethosia, annual report 2025 (2025-12-24): https://ethosia.co.il/report-2025-2026/
- S14 Ethosia Market Intelligence, defense-tech (2026-07-30): https://ethosia.co.il/ethosia-market-intelligence-2026/
- S15 Drushim / JobInfo, software salary table 2026 (2026-01-01): https://www.drushim.co.il/article/107
- S16 Drushim / JobInfo, infrastructure / IS salary table (2026-01-01): https://www.drushim.co.il/article/117/
- S17 AllJobs, salary tables 2026: https://www.alljobs.co.il/User/SalaryCompound/SalarySurvey.aspx ; preview: https://www.alljobs.co.il/Partners/Hitech/HitechIndex.aspx
- S18 Levels.fyi Israel pages: https://www.levels.fyi/t/software-engineer/locations/israel ; https://www.levels.fyi/t/software-engineer/levels/entry-level/locations/israel ; https://www.levels.fyi/t/software-engineer/levels/senior/locations/israel ; https://www.levels.fyi/t/data-scientist/locations/israel ; https://www.levels.fyi/t/product-manager/locations/israel ; robots: https://www.levels.fyi/robots.txt
- S19 Payscale, Software Engineer Israel: https://www.payscale.com/research/IL/Job=Software_Engineer/Salary
- S20 CTech (Calcalist), CBS July 2026 data (2026-10-05): https://www.calcalistech.com/ctechnews/article/cysn2t0w7
- S21 CTech, CBS March 2026 data (2026-06-04): https://www.calcalistech.com/ctechnews/article/emfdd1msa
- S22 CTech, CBS May 2026 data (2026-08-04): http://www.calcalistech.com/ctechnews/article/y8o8kvcer
- S23 Walla Finance, CBS May/June 2026 (2026-08-04): https://finance.walla.co.il/item/3858394
- S24 Walla Finance, CBS annual 2024 (2025-03-04): https://finance.walla.co.il/item/3731717
- S25 Bizportal, CBS June 2025 (2025-09-04): https://www.bizportal.co.il/general/news/article/20021200
- S26 Maariv, IIA 2025 employment report (2025-04-07): https://www.maariv.co.il/economy/israel/article-1186406
- S27 AHK Israel, IIA 2026 High-Tech Status Report (2026-05-31): https://israel.ahk.de/en/news/israeli-high-tech-2025-record-exports-and-exits-but-first-decline-in-r-d-employees-in-a-decade
- S28 Globes English, Ethosia 2023 salaries (2024-01-25): https://en.globes.co.il/en/article-1001468626
- S29 Globes English, altshare options study (2025-01-12): https://en.globes.co.il/en/article-1001499150
- S30 Globes English, NIS 150b options (2026-04-26): https://en.globes.co.il/en/article-1001540937
- Context (read, not cited for numbers): Maariv CBS May 2026 (https://www.maariv.co.il/economy/israel/article-1352120); Bizportal 2026-01-19 (https://www.bizportal.co.il/career/news/article/20026286); INN sponsored guide (https://www.inn.co.il/news/688035); Drushim index (https://www.drushim.co.il/article/87/)
- robots.txt checked: nisha.co.il, gotfriends.co.il, ethosia.co.il, drushim.co.il, alljobs.co.il, levels.fyi, payscale.com, glassdoor.com, cbs.gov.il, calcalistech.com
