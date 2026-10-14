# Research: international (mainly US) tech salary data, used for ratios only

Researched 2026-10-14 (all pages accessed on that date). Every number below comes from a page read in this session; nothing comes from memory. Labels used:
**[P]** = what a source states, **[R]** = my own reasoning or arithmetic.

Scope rule: this file is used **only for ratios**. It gives (a) role-to-role ratios and (b) experience-step ratios. **US dollar amounts must never be converted into Israeli salaries.** No exchange-rate or percentage conversion is suggested anywhere. ILS numbers come only from Israeli sources (separate research).

Canonical roles: fullstack, backend, frontend, mobile, devops, data_scientist, data_engineer, data_analyst, qa, security, architect, team_lead, product_manager.
Proposed experience buckets: junior 0-2 years, mid 3-5, senior 6-9, staff 10+.

---

## TL;DR

1. **Seven sources gave usable numbers.** These are the Stack Overflow Developer Survey (2024, 2025, 2026), BLS OEWS via the Occupational Outlook Handbook (May 2025), Levels.fyi (live pages and the 2025 report), Robert Half 2027 Salary Guide, Payscale and Built In. **Glassdoor was blocked** (HTTP 403). **Dice 2025** gave only an overall average and one experience figure; its role and experience charts are not in page text (PDF, needs approval). **Hired:** no 2024-2026 edition found.
2. **Role ratios vs backend / software developer (US scope, median or mid-point):**
   - **Data analyst** is the most consistently low: 0.56-0.81 (5 sources).
   - **QA:** 0.74-0.85 (4 sources).
   - **Fullstack:** 0.76-0.94 (5 sources).
   - **Data scientist:** 0.74-1.09 (7 sources).
   - **Data engineer:** 0.81-1.10 (5 sources).
   - **Mobile:** 0.97-1.15 (4 sources).
   - **Frontend** varies most: 0.63-1.00 (5 sources; BLS web developers at 0.68 is an uncertain proxy).
   - **Devops:** 0.77-1.17 (6 sources).
   - **Security:** 0.76-1.05 (5 sources). Levels.fyi splits it into security SWE (1.38) and cybersecurity analyst (0.64).
   - **Architect:** 1.03-1.54 (3 sources).
   - **Product manager:** 0.77-1.18 (4 sources).
   - **Team lead:** no source publishes "team lead". Engineering-manager proxies give 1.13-1.83 (5 sources).
3. **Experience steps differ sharply between base pay and total comp.**
   - **Base pay** per step is about **1.2-1.3x**:
     - Google and Meta level bases: 1.20-1.27 per step;
     - Robert Half low→mid→high tiers: 1.16-1.31.
   - **Payscale** steps between its career bands are smaller, about **1.1-1.25x**: mid-career/early 1.09-1.27, next band/mid 1.02-1.19.
   - **US total comp** at large tech firms is about **1.4-1.7x** per level step:
     - Levels.fyi US SWE 2025: entry→SWE 1.46, SWE→senior 1.38, senior→staff 1.46;
     - Google: 1.43, 1.51, 1.47;
     - Meta: 1.64, 1.49, 1.71.
   - The gap between those two groups is mostly equity. **Do not use total-comp step ratios for Israel without discounting** [R].
4. **Stack Overflow is the only route to Israel-specific data from these sources.**
   - Israel had **297** respondents in 2025 and **600** (1%) in 2024 [S2][S5]. These are country-question counts, not salary answers.
   - The public dataset is on GitHub under ODbL 1.0 (2026 file: 117 MB, Git LFS) [S10][S11].
   - **Needs user approval to download.** With approval, the parent session could compute Israel-only medians (an Israeli source).
5. **Levels.fyi has a public Israel page in ILS** (SWE median total comp, percentiles, 1,914 submissions) [S29]. Pass it to the Israel-sources agent.
6. **Main caveat [R]:** the US premium for frontend, mobile, security-engineering and management roles comes partly from big-tech equity and US market structure. Israeli ratios are likely flatter for equity-heavy roles. Prefer base-pay ratios (BLS, Payscale, Robert Half) for Israel priors.

---

## 1. Stack Overflow Developer Survey

### 1a. 2025 survey [S1][S2][S3]

- **Publisher / year:** Stack Overflow, 2025.
- **Data period:** fielded 2025-05-29 to 2025-06-23 [P][S3]. 49,009 responses used, from 177 countries [P][S3].
- **Salary definition:**
  - [P] Respondents were asked for "total annual compensation (salary, bonuses, and perks, before taxes and deductions)" [S1].
  - Values were converted to USD using exchange rates from 2025-06-25 [S3].
  - **Annual. Total cash comp incl. bonuses and perks.** Equity is not explicitly named.
- **Statistic:** median yearly salary, USD.
- **Sample:** 23,928 global responses for the salary-by-role chart; 5,239 for the US [P][S1]. No per-role n is stated.
- **Experience:** salary by years of experience is shown only as a scatter chart (role median vs average years). No numeric values appear in the page text [P][S1]. No experience ratios are available without the dataset.
- **Experience buckets as published** ("years of professional work experience", 2025): 1 to 5, 6 to 10, 11 to 15, 16 to 20, 21 to 30, 31 to 40, 41 to 50, More than 50 years [P][S2].

**United States, median yearly salary (USD) [P][S1]**

| Role as named | Canonical | Median |
|---|---|---|
| Developer, back-end | backend (reference) | 175,000 |
| Developer, full-stack | fullstack | 138,000 |
| Developer, front-end | frontend | 145,000 |
| Developer, mobile | mobile | 170,000 |
| DevOps engineer or professional | devops | 165,000 |
| Data scientist | data_scientist | 145,000 |
| Data engineer | data_engineer | 150,000 |
| Data or business analyst | data_analyst (includes business analysts, flag) | 100,956 |
| Cybersecurity or InfoSec professional | security | 150,000 |
| Architect, software or solutions | architect | 180,000 |
| Engineering manager | team_lead (proxy, uncertain) | 200,000 |
| Cloud infrastructure engineer | (devops-adjacent, not mapped) | 189,000 |
| AI/ML engineer | (not mapped) | 189,500 |

Product manager and "Developer, QA or test" are **absent** from the US list [P][S1]. Probably they fell under the response threshold [R].

**Global (all respondents), median yearly salary (USD) [P][S1]**

| Role as named | Canonical | Median |
|---|---|---|
| Developer, back-end | backend (reference) | 79,742 |
| Developer, full-stack | fullstack | 72,509 |
| Developer, front-end | frontend | 62,015 |
| Developer, mobile | mobile | 69,609 |
| DevOps engineer or professional | devops | 87,011 |
| Data scientist | data_scientist | 82,910 |
| Data engineer | data_engineer | 81,210 |
| Data or business analyst | data_analyst (flag) | 62,625 |
| Developer, QA or test | qa | 57,442.5 |
| Cybersecurity or InfoSec professional | security | 96,146 |
| Architect, software or solutions | architect | 102,000 |
| Engineering manager | team_lead (proxy, uncertain) | 130,000 |
| Product manager | product_manager | 100,000 |

### 1b. 2024 survey [S4][S5]

- **Publisher / year:** Stack Overflow, 2024.
- **Salary definition:** same question wording, "total annual compensation (salary, bonuses, and perks...)". USD median, annual [P][S4].
- **Sample:** 22,677 global compensation responses; 4,496 US [P][S4].
- **Experience buckets as published** ("years of professional coding experience"): Less than 1 year, 1 to 4, 5 to 9, 10 to 14, 15 to 19, 20 to 24, ... More than 50 years [P][S5]. There is no salary-by-experience table in text [P][S4].

**United States, median (USD) [P][S4]** (role labels are abbreviated on the page)

| Role as named | Canonical | Median |
|---|---|---|
| Back-end | backend (reference) | 170,000 |
| Full-stack | fullstack | 130,000 |
| Front-end | frontend | 135,000 |
| Mobile | mobile | 185,000 |
| DevOps specialist | devops | 145,000 |
| Data sci. or ML specialist | data_scientist (includes ML, flag) | 159,000 |
| Data engineer | data_engineer | 150,000 |
| Data/Biz | data_analyst (flag) | 100,000 |
| QA | qa | 130,000 |
| Security pro. | security | 130,000 |
| Manager | team_lead (proxy, uncertain) | 192,500 |

Architect and product manager are absent from the 2024 US list.

**Global median (USD) [P][S4]:**

| Role as named | Canonical | Median |
|---|---|---|
| Back-end | backend (reference) | 67,227 |
| Full-stack | fullstack | 63,332.5 |
| Front-end | frontend | 48,787 |
| Mobile | mobile | 54,340 |
| DevOps specialist | devops | 72,611 |
| Data sci. or ML specialist | data_scientist (flag) | 73,036 |
| Data engineer | data_engineer | 76,153.5 |
| Data/Biz | data_analyst (flag) | 54,507 |
| QA | qa | 54,178 |
| Security pro. | security | 78,995 |
| Manager | team_lead (proxy, uncertain) | 115,999.5 |
| Product manager | product_manager | 80,000 |

### 1c. 2026 survey (released 2026-10-06) [S6][S7][S8][S9]

- **Publisher / year:** Stack Overflow, 2026.
- **Data period:** fielded 2026-06-23 to 2026-08-05. 30,903 valid responses, from 169 countries [P][S9].
- **Salary definition:** same "total annual compensation" wording, USD [P][S8].
- **Data cleaning:** rows with multiple quality flags are excluded (very low or high values, country outliers, and similar) [P][S9].
- **Global chart:** n = 12,040, and it includes only roles with 100+ responses [P][S8].
- **US:** only an overall US median of **154,000** (n = 2,885) is in the page text. **No US-by-role values** [P][S8].
- QA, security and product manager have no salary line in 2026. They appear only in role counts [P][S8].
- The experience chart gives each role's *average years* (for example back-end 14.5, front-end 11.8), not a salary curve [P][S8].

**Global median (USD) [P][S8]**

| Role as named | Canonical | n | Median |
|---|---|---|---|
| Developer, back-end | backend (reference) | 1,922 | 85,296 |
| Developer, full-stack | fullstack | 3,761 | 79,610 |
| Developer, front-end | frontend | 441 | 70,320 |
| Developer, mobile | mobile | 346 | 84,277 |
| DevOps engineer or professional | devops | 307 | 85,096 |
| Data scientist | data_scientist | 155 | 90,982 |
| Data engineer | data_engineer | 233 | 90,000 |
| Data or business analyst | data_analyst (flag) | 119 | 67,161 |
| Architect, software or solutions | architect | 1,023 | 102,355 |
| Engineering manager | team_lead (proxy, uncertain) | 378 | 133,263 |
| Software engineer | (generic) | 105 | 101,218 |

### 1d. Public dataset and Israel

- **Israel respondents (country question):**
  - 2025: "Israel 297 0.8%" out of 35,369 answering [P][S2].
  - 2024: Israel 600 (1%) [P][S5].
  - 2026: no per-country count was found in the pages I read [S9].
- [R] Only about half of all respondents answered compensation (48.8% in 2025 [S1]). So **Israeli salary answers in 2025 are probably in the low hundreds or fewer**. This is a rough reasoning estimate and needs a check against the data.
- **Country field:** the results pages break respondents down by country [S2][S5], so the data has a country variable [R]. I did not read the schema itself. The 2026 `survey_results_schema.csv` is 91.7 KB and stored in Git LFS, so viewing it means downloading it [P][S11].
- **Files:**
  - 2025: `results.csv`, `schema.csv`, `survey.pdf` in https://github.com/StackExchange/Survey/tree/main/packages/archive/2025 [P][S10].
  - 2026: `survey_results_public.csv` (**117 MB, Git LFS**) and `survey_results_schema.csv` in https://github.com/StackExchange/Survey/tree/main/packages/archive/2026 [P][S10][S11].
  - 2024: https://github.com/StackExchange/Survey/tree/main/packages/archive/2024 [P][S10].
- **Format:** CSV [P][S10][S11].
- **License:** "Survey data licensed under ODbL 1.0, contents under DbCL 1.0" [P][S9][S10].
- **Status: needs user approval to download.** With approval, the parent session could compute Israel-only medians by role and experience. That result would count as an Israeli source, but its small n should be reported.
- **Terms/robots:** survey.stackoverflow.co/robots.txt has `User-agent: *` / `Allow: /`, and it explicitly allows ClaudeBot and Claude-User [P][S12]. ODbL permits reuse with attribution and share-alike [P][S10].

---

## 2. U.S. Bureau of Labor Statistics, OEWS May 2025 (via the Occupational Outlook Handbook) [S13]-[S24]

- **Publisher / year:** BLS. The data is May 2025; the OEWS tables index was last modified 2026-05-15 [P][S22].
- **Wage definition:**
  - [P] Wages are "straight-time, gross pay, exclusive of premium pay" [S23].
  - **Included:** base rate, commissions, production bonuses and similar items.
  - **Excluded:** overtime, non-production and year-end bonuses, profit-sharing and stock bonuses [P][S23].
  - So this is **annual, close to base pay**.
- **Scope:** wage and salary workers in nonfarm establishments; excludes the self-employed [P][S23].
- **Experience:** **OEWS has no experience dimension.** The FAQ says it cannot account for experience [P][S23].
- **Percentiles actually read:** 10th, 50th and 90th, from the OOH pay sections. **The 25th and 75th were not readable.**
  - The OEWS occupation pages (`/oes/current/oes151252.htm`, `/oes/2025/may/oes151252.htm`) returned the tables index or unrelated page content when fetched.
  - The May 2025 national HTML table sits at data.bls.gov in a JavaScript app.
  - The XLSX (`oesm25nat.zip`) is a download, so it **needs user approval** [P][S22].
- The FAQ notes that from May 2025, OEWS publishes values for some percentiles that used to be top-coded [P][S23].
- **Terms/robots:** /ooh/ and /oes/ are not disallowed in bls.gov/robots.txt [P][S24]. [R] BLS data is US federal government work and is generally in the public domain; I did not read a BLS copyright page.

| Occupation as named (SOC per brief) | Canonical | p10 | Median | p90 | Source |
|---|---|---|---|---|---|
| Software developers (15-1252) | backend/fullstack/mobile reference | 82,460 | **135,980** | 214,670 | [S13] |
| Software quality assurance analysts and testers (15-1253) | qa | 61,440 | 104,300 | 167,010 | [S13] |
| Web developers (15-1254) | frontend (uncertain; includes non-engineering web roles) | 48,100 | 92,650 | 162,290 | [S14] |
| Web and digital interface designers | (not mapped) | 53,750 | 104,000 | 201,550 | [S14] |
| Data scientists (15-2051) | data_scientist | 67,240 | 120,230 | 199,130 | [S15] |
| Information security analysts (15-1212) | security | 75,090 | 129,180 | 199,850 | [S16] |
| Database architects (15-1243) | architect / data_engineer (uncertain) | 86,240 | 139,500 | 204,000 | [S17] |
| Database administrators | (not mapped) | 60,230 | 104,620 | 163,320 | [S17] |
| Computer network architects (15-1241) | architect (uncertain; network, not software) | 79,900 | 134,050 | 202,680 | [S18] |
| Computer and information systems managers (11-3021) | team_lead (proxy, uncertain; includes IT directors/CTOs) | 107,550 | 175,140 | 297,510 | [S19] |
| Network and computer systems administrators | devops (weak proxy) | 62,640 | 99,130 | 155,050 | [S20] |
| Computer programmers | (not mapped) | 57,710 | 100,390 | 160,460 | [S21] |

All values are annual, in USD, for May 2025. Employment counts were not read for these pages. The OOH says computer and information systems managers typically need "5 years or more" of related work experience [P][S19].

---

## 3. Levels.fyi [S25]-[S30]

- **Publisher:** Levels.fyi.
- **Compensation definition:** "median total yearly compensation including salary, stock, and bonuses" [P][S25]. **Total comp, annual, including equity.**
- **Data:** live pages, all "last updated 10/14/2026". They are self-reported submissions.

### 3a. End-of-year 2025 report [S25]

- Calendar year 2025, 245K+ data points, 47K of them from the United States [P].
- **Software Engineer median TC by level**, under the "U.S. Compensation Trends" section. The table caption itself does not say "US-only" [P].
- **Levels as named:** Entry Level Engineer **155K**; Software Engineer **226K**; Senior Engineer **312K**; Staff Engineer **457K**; Principal Engineer **551K** (2025) [P].
- **Year bounds:** the report gives no years-of-experience range for these levels [R].
- The 2025 US regional report gives a national SWE median TC of **192,500** (47K data points, December 2025) [P][S26].

### 3b. US title pages, all levels, median TC (USD) [S27]

| Title as named | Canonical | p25 | Median | p75 | p90 | n |
|---|---|---|---|---|---|---|
| Backend Software Engineer | backend (reference) | 148K | **195,700** | 267K | 346K | n/s |
| Software Engineer (all) | generic | 138K | 197,000 | 283K | 390K | 47,782 |
| Frontend Software Engineer | frontend | 135K | 196,000 | 264K | 340K | n/s |
| Full-Stack Software Engineer | fullstack | 124K | 173,340 | 240K | 324K | n/s |
| Mobile Software Engineer | mobile | 167K | 224,600 | 275K | 376K | n/s |
| DevOps Engineer | devops | 120K | 153,000 | 189K | 226K | n/s |
| Data Scientist | data_scientist | 135K | 180,000 | 251K | 340K | 3,342 |
| Data Engineer | data_engineer | 117K | 159,000 | 225K | 315K | n/s |
| Data Analyst | data_analyst | 85K | 110,000 | 145K | 188K | 1,027 |
| Quality Assurance (QA) Software Engineer | qa | 108K | 144,000 | 200K | 261K | n/s |
| Security Software Engineer | security (engineering variant) | 190K | 270,000 | 384K | 497K | n/s |
| Cybersecurity Analyst | security (analyst variant) | 95K | 125,000 | 183K | 230K | 509 |
| Solution Architect | architect (uncertain; solution ≠ software architect) | 170K | 218,000 | 280K | 350K | 1,213 |
| Software Engineering Manager | team_lead (proxy, uncertain) | 240K | 359,000 | 508K | 663K | 3,177 |
| Product Manager | product_manager | 169K | 230,000 | 330K | 450K | 4,979 |

n/s = not stated on the page.

### 3c. Company level pages, Software Engineer, United States [S28]

The tables are headed "Average Compensation By Level", but each page's FAQ calls the figures medians, so **the statistic is unclear** [P]. Levels are company-specific. The pages give no year ranges.

| Company | Level as named | Total | Base |
|---|---|---|---|
| Google | L3 SWE II (Entry Level) | 210K | 155K |
| Google | L4 SWE III | 301K | 191K |
| Google | L5 Senior SWE | 454K | 234K |
| Google | L6 Staff SWE | 667K | 285K |
| Meta | E3 (Entry Level) | 187K | 146K |
| Meta | E4 | 307K | 186K |
| Meta | E5 | 458K | 224K |
| Meta | E6 | 785K | 273K |
| Microsoft | 59 SDE (Entry Level) | 165K | 128K |
| Microsoft | 61 SDE II | 202K | 158K |

The Microsoft levels above 62 were collapsed on the page and not read.

### 3d. Israel page (for the Israel-sources agent) [S29]

https://www.levels.fyi/t/software-engineer/locations/israel
- **Currency:** ILS.
- **Software Engineer, all levels, total comp:** median ₪449,171; p25 ₪339K; p75 ₪559K; p90 ₪709K.
- **n:** 1,914.
- It also shows city medians (Tel Aviv, Petach Tikva, Ramat Gan) [P].
- **Includes equity.** No level breakdown was shown.

### 3e. Terms and robots

- **robots.txt** [P][S30]:
  - The wildcard user agent is `Allow: /`. Claude-User is explicitly allowed.
  - Compensation pages are closed to AI *training* crawlers.
  - The file requests attribution with a link to the canonical URL when quoting figures.
- **Terms page** (https://www.levels.fyi/legal/terms): **blocked: HTTP 403**, so it was not read.

---

## 4. Glassdoor (US)

- **Blocked: HTTP 403** on the public salary page https://www.glassdoor.com/Salaries/backend-developer-salary-SRCH_KO0,17.htm. No numbers were recorded and no workaround was attempted [S31].
- **robots.txt** [P][S31]:
  - `/Salaries/` is not disallowed for `*`.
  - ClaudeBot, GPTBot and others are restricted to `/blog/`, `/Award/`, `/About/` and `/employers/`.
- **Terms of Use:** not read.

---

## 5. Dice Tech Salary Report

- **Latest edition:** the **2025 report**, which covers 2024 salaries. I found no 2026 edition [S32][S33].
- **Data:** 2024 Dice Salary Survey, fielded 2024-08-30 to 2024-11-06, with 2,835 completed US surveys [P][S32].
- **Statistic:** "average" (mean, per its weighting note). **Base vs total is not stated** [P][S32][S33].
- **Figures in page text** [P][S32][S33]:
  - overall average 2024: **112,521**;
  - "more than 15 years" of experience: **133,047**;
  - average bonus: 14,194.
  - For entry level (2 years or less) and mid-career (3-5 years), only year-over-year changes are given, not dollar values.
  - Role values are in charts and are not in the text.
- **No ratios are computable** from the page text.
- **PDF:** the page offers a "Download the PDF" link (https://dice.com/recruiting/ebooks/dice-tech-salary-report). **Needs user approval to download.**
- **robots.txt:** `/technologists/ebooks/` and `/recruiting/ebooks/` are not disallowed [P][S34].

---

## 6. Robert Half 2027 Salary Guide (US) [S35]-[S37]

- **Edition:** the 2027 Salary Guide, the latest. The page is © 2026 [P][S35].
- **Method** [P][S35]:
  - figures come from compensation of professionals Robert Half placed, validated against Textkernel job-posting data;
  - they are **starting salaries** for someone new to a role or company;
  - bonuses and merit increases are excluded.
  - **So this is starting base pay, annual.**
- **Tiers:** the guide gives Low / Mid / High tiers, not years and not labeled percentiles [P][S36]:
  - Low: newer to the role or limited experience.
  - Mid: moderate experience; meets most requirements.
  - High: extensive experience and advanced skills.
- **Mapping [R]:** low ≈ junior, mid ≈ mid, high ≈ senior. This is uncertain because the tiers measure experience *in the role*.

| Title as named | Canonical | Low | Mid | High |
|---|---|---|---|---|
| Software Engineer | backend/generic (reference) | 111,500 | **146,250** | 179,000 |
| DevOps Engineer | devops | 119,500 | 148,750 | 177,250 |
| Data Scientist | data_scientist | 123,750 | 158,750 | 186,750 |
| Data Engineer | data_engineer | 130,500 | 160,500 | 185,500 |
| Data Analyst | data_analyst | 96,250 | 118,500 | 138,500 |
| Cybersecurity Engineer | security | 120,750 | 148,500 | 194,750 |
| Product Manager | product_manager (uncertain; may not be a software-product role) | 95,250 | 122,250 | 142,250 |

- **Pages without values:** full-stack, front-end, mobile applications developer, QA engineer, solutions architect, software developer and information security analyst pages exist, but showed no values in the page text.
- **robots.txt:** `/us/en/job-details/` is not disallowed. Only `/us/en/insights/salary-guide/details/*` is [P][S37].

---

## 7. Payscale (US) [S38][S39]

- **Statistic:** average base salary, with the median shown as well. Pages were updated May-Jul 2026 and are self-reported profiles [P].
- **Experience section** [P]:
  - It is "Pay by Experience Level", expressed as a % above or below a reference.
  - The text defines **Entry Level as "less than 1 year"** and **Early Career as "1-4 years"**. The dollar figures there are "average total compensation (includes tips, bonus, and overtime pay)".
  - Mid Career, Late Career and Experienced year ranges are **not defined on the pages I read**. Search snippets suggested 5-9, 10-19 and 20+, but **those are unverified** [S38].
  - The page lists the items as Entry, Early, Mid, Late, Experienced. The fetch tool noted that the links for "Late Career" and "Experienced" look swapped. **The 4th and 5th bands are therefore ambiguous.**
- [R] The % values appear to be relative to the job's median base. For Software Engineer: 84,370 / 0.86 ≈ 98.1K and 94,966 / 0.97 ≈ 97.9K, which matches the 98.2K average base.

| Title as named | Canonical | Avg base | p10 / median / p90 | n | Entry | Early | Mid | 4th | 5th |
|---|---|---|---|---|---|---|---|---|---|
| Software Engineer | reference | **98,200** | 72k / 98k / 142k | 25,510 | -14% | -3% | +12% | +24% | +31% |
| Software Developer | generic | 83,355 | 60k / 83k / 120k | 8,013 | -15% | -4% | +13% | +28% | +34% |
| Full Stack Software Developer | fullstack | 92,320 | 62k / 92k / 128k | 1,436 | -23% | -7% | +9% | +26% | +29% |
| Front End Developer / Engineer | frontend | 89,372 | 59k / 89k / 133k | 1,908 | -22% | -3% | +10% | +13% | +12% |
| Mobile Applications Developer | mobile | 98,636 | 70k / 99k / 152k | **121** | -33% | -4% | +13% | +34% | +48% |
| Development Operations (DevOps) Engineer | devops | 114,777 | 77k / 115k / 163k | 1,745 | -29% | -12% | +9% | +25% | +29% |
| Data Scientist | data_scientist | 103,820 | 73k / 104k / 145k | 5,600 | -14% | -2% | +14% | +23% | +38% |
| Data Engineer | data_engineer | 100,094 | 71k / 100k / 142k | 3,649 | -20% | -6% | +16% | +28% | +34% |
| Data Analyst | data_analyst | 70,643 | 51k / 71k / 95k | 11,864 | -10% | -1% | +12% | +14% | +17% |
| Quality Assurance (QA) Engineer | qa | 83,066 | 63k / 83k / 112k | 3,146 | -18% | -6% | +8% | +15% | +18% |
| Security Engineer | security | 103,272 | 74k / 103k / 149k | 1,257 | -26% | -6% | +6% | +20% | +19% |
| Software Architect | architect | 150,967 | 106k / 151k / 190k | 943 | -46% | -27% | -7% | +1% | +6% |
| Software Engineering Manager | team_lead (proxy, uncertain) | 155,526 | 115k / 156k / 194k | 1,746 | -19% | -10% | -2% | +2% | +3% |
| Product Manager, Software | product_manager | 112,517 | 79k / 113k / 149k | 3,929 | -22% | -7% | +6% | +14% | +26% |

- The Back End Developer page returned 404, so **Software Engineer is the reference**.
- Absolute pay levels sit well below the other sources: the SWE median base is 98k vs 135,980 at BLS. [R] Likely causes are self-selection and a broad title mix. Ratios are less affected than levels.
- **robots.txt:** `/research/` is not disallowed for `*`, and no AI bots are named [P][S39]. Terms of Use: not read.

---

## 8. Built In (US) [S40]

- **Pages:** 2026 pages, built from anonymous self-reported salaries. **n is not stated** [P].
- **Statistics reported:** average base, average additional cash, average total comp, median, and averages for "<1 year" and "7+ years" of experience.
- The pages show only those two experience buckets.

| Title as named | Canonical | Avg base | Median | Avg total | <1 yr | 7+ yrs |
|---|---|---|---|---|---|---|
| Back End Developer | backend (reference) | **173,388** | 183,000 | 223,712 | 125,500 | 201,375 |
| Front End Developer | frontend | 110,010 | 101,000 | 121,493 | 78,957 | 135,476 |
| Full Stack Developer | fullstack | 162,772 | 170,000 | 179,533 | 106,000 | 174,485 |
| DevOps Engineer | devops | 133,817 | 125,000 | 150,355 | 84,510 | 149,162 |
| Data Scientist | data_scientist | 128,067 | 120,000 | 145,852 | 95,903 | 159,035 |
| Product Manager | product_manager | 133,231 | 125,000 | 152,462 | 105,724 | 144,318 |

- [R] Built In's backend figure looks high relative to every other source (avg additional cash 50,324). This depresses all Built In role ratios. **Treat them as low-confidence.**
- **robots.txt:** `/salaries/` is not disallowed for `*`. GPTBot, OAI-SearchBot, ChatGPT-User and PerplexityBot are explicitly allowed on salaries [P][S40].

---

## 9. Hired

- **Not found for 2024-2026.** One web search surfaced only third-party coverage of the 2022 and 2023 "State of Software Engineers" reports. I read no Hired page, so no figures are recorded.

---

## 10. Derived role ratios (role median ÷ backend / software-developer median) [R]

All of these are [R] arithmetic on the [P] values above. Codes: **B** = base-pay-like, **TC** = total comp including equity, **TCash** = total cash (bonus/perks, equity not named). **G** = global, mixed countries, so composition is confounded.

| Role | SO25 US (TCash) | SO24 US (TCash) | BLS May25 (B) | Levels.fyi US (TC) | Robert Half 27 mid (B, starting) | Payscale avg (B) | Built In avg (B) | SO25 G | SO24 G | SO26 G |
|---|---|---|---|---|---|---|---|---|---|---|
| reference | back-end 175,000 | back-end 170,000 | software devs 135,980 | backend SWE 195,700 | software eng 146,250 | software eng 98,200 | back-end 173,388 | 79,742 | 67,227 | 85,296 |
| fullstack | 0.79 | 0.76 | n/a | 0.89 | n/a | 0.94 | 0.94 | 0.91 | 0.94 | 0.93 |
| frontend | 0.83 | 0.79 | 0.68 (web devs, uncertain) | 1.00 | n/a | 0.91 | 0.63 | 0.78 | 0.73 | 0.82 |
| mobile | 0.97 | 1.09 | n/a | 1.15 | n/a | 1.00 (n=121) | n/a | 0.87 | 0.81 | 0.99 |
| devops | 0.94 | 0.85 | 0.73 (net/sys admins, weak) | 0.78 | 1.02 | 1.17 | 0.77 | 1.09 | 1.08 | 1.00 |
| data_scientist | 0.83 | 0.94 | 0.88 | 0.92 | 1.09 | 1.06 | 0.74 | 1.04 | 1.09 | 1.07 |
| data_engineer | 0.86 | 0.88 | 1.03 (DB architects, uncertain) | 0.81 | 1.10 | 1.02 | n/a | 1.02 | 1.13 | 1.06 |
| data_analyst | 0.58 | 0.59 | n/a | 0.56 | 0.81 | 0.72 | n/a | 0.79 | 0.81 | 0.79 |
| qa | n/a | 0.76 | 0.77 | 0.74 | n/a | 0.85 | n/a | 0.72 | 0.81 | n/a |
| security | 0.86 | 0.76 | 0.95 | 1.38 (sec SWE) / 0.64 (analyst) | 1.02 | 1.05 | n/a | 1.21 | 1.18 | n/a |
| architect | 1.03 | n/a | 1.03 (DB arch) / 0.99 (network arch), uncertain | 1.11 (solution arch) | n/a | 1.54 | n/a | 1.28 | n/a | 1.20 |
| team_lead (EM proxy) | 1.14 | 1.13 | 1.29 (CIS managers) | 1.83 | n/a | 1.58 | n/a | 1.63 | 1.73 | 1.56 |
| product_manager | n/a | n/a | n/a | 1.18 | 0.84 (uncertain) | 1.15 | 0.77 | 1.25 | 1.19 | n/a |

Two other ratios against the same reference: Levels.fyi all-SWE / backend = 197,000 / 195,700 = 1.01, and Payscale software developer / software engineer = 0.85.

Example working:
- SO25 US fullstack: 138,000 / 175,000 = 0.789 → 0.79.
- BLS QA: 104,300 / 135,980 = 0.767 → 0.77.
- Levels.fyi mobile: 224,600 / 195,700 = 1.148 → 1.15.

[R] Notes on the table:
- **Equity:** the Levels.fyi ratios (TC) carry equity. That inflates roles concentrated at big tech: mobile, security SWE, engineering manager, PM.
- **Global SO ratios** mix countries. Roles over-represented in high-pay countries (security, architect, managers) look higher, and frontend and mobile look lower. **Do not use the global ratios as US or Israel ratios.**
- **Architect:** Payscale's 1.54 compares a senior-only title to an all-levels reference, so it partly measures seniority, not role.

---

## 11. Derived experience ratios [R]

| Source | Pay type | Levels or bands as published | Step 1 (≈ mid/junior) | Step 2 (≈ senior/mid) | Step 3 (≈ staff/senior) |
|---|---|---|---|---|---|
| Levels.fyi 2025 report, US SWE [S25] | TC (equity) | Entry → Software Engineer → Senior → Staff (→ Principal) | 226/155 = **1.46** | 312/226 = **1.38** | 457/312 = **1.46** (Principal/Staff 551/457 = 1.21) |
| Levels.fyi Google, US SWE [S28] | TC | L3 → L4 → L5 → L6 | 301/210 = 1.43 | 454/301 = 1.51 | 667/454 = 1.47 |
| Levels.fyi Google, US SWE [S28] | **Base** | L3 → L4 → L5 → L6 | 191/155 = **1.23** | 234/191 = **1.23** | 285/234 = **1.22** |
| Levels.fyi Meta, US SWE [S28] | TC | E3 → E4 → E5 → E6 | 307/187 = 1.64 | 458/307 = 1.49 | 785/458 = 1.71 |
| Levels.fyi Meta, US SWE [S28] | **Base** | E3 → E4 → E5 → E6 | 186/146 = **1.27** | 224/186 = **1.20** | 273/224 = **1.22** |
| Levels.fyi Microsoft, US SWE [S28] | TC / base | 59 → 61 only | 202/165 = 1.22 (base 158/128 = 1.23) | n/a | n/a |
| Robert Half 2027, Software Engineer [S36] | Base (starting) | Low → Mid → High (experience tiers, no years) | 146,250/111,500 = **1.31** | 179,000/146,250 = **1.22** | n/a |
| Robert Half 2027, 6 other roles [S36] | Base (starting) | Low → Mid → High | 1.23-1.28 | 1.16-1.31 | n/a |
| Payscale Software Engineer [S38] | Base-referenced % (total cash in the $ text) | Entry <1 → Early 1-4 → Mid → 4th → 5th | Early/Entry 0.97/0.86 = 1.13 | Mid/Early 1.12/0.97 = **1.15** | 4th/Mid 1.24/1.12 = **1.11** (5th/Mid = 1.17) |
| Payscale, 14 titles [S38] | same | same | Early/Entry 1.10-1.43 | Mid/Early 1.09-1.27 | 4th/Mid 1.02-1.19 (5th/Mid 1.02-1.31) |
| Built In, 6 titles [S40] | Avg (base, probably) | "<1 year" vs "7+ years" only | span 7+/<1: backend 1.60, frontend 1.72, fullstack 1.65, devops 1.77, data scientist 1.66, PM 1.37 | | |
| SO 2024/2025/2026 | TCash | n/a | not in page text (dataset needed) | | |
| BLS OEWS | B | none | **no experience dimension** | | |
| Dice 2025 | mean | ≤2 / 3-5 / >15 years | only YoY %, no $ by bucket except >15 years | | |

Payscale per-title Mid/Early ratios [R]:

| Title | Ratio |
|---|---|
| Software Developer | 1.18 |
| Full Stack Software Developer | 1.17 |
| Front End Developer / Engineer | 1.13 |
| Mobile Applications Developer | 1.18 |
| DevOps Engineer | 1.24 |
| Data Scientist | 1.16 |
| Data Engineer | 1.23 |
| Data Analyst | 1.13 |
| QA Engineer | 1.15 |
| Security Engineer | 1.13 |
| Software Architect | 1.27 |
| Software Engineering Manager | 1.09 |
| Product Manager, Software | 1.14 |

Robert Half per-role ratios [R]:

| Role | Mid/Low | High/Mid |
|---|---|---|
| DevOps Engineer | 1.24 | 1.19 |
| Data Engineer | 1.23 | 1.16 |
| Data Analyst | 1.23 | 1.17 |
| Data Scientist | 1.28 | 1.18 |
| Cybersecurity Engineer | 1.23 | 1.31 |
| Product Manager | 1.28 | 1.16 |

Mapping to the proposed buckets is uncertain [R]:
- Levels.fyi levels have no published years in the pages I read.
- Robert Half tiers measure experience in the role.
- Payscale "Early 1-4" straddles our junior (0-2) and mid (3-5). Its Mid Career band is undefined on the pages I read (5-9 is unverified), which would be roughly our senior. The 4th and 5th bands are ambiguous because of the label/link swap.

---

## 12. Ratio summary (US-scope sources only; global SO excluded) [R]

| Canonical role | Ratio range vs backend / software developer | # sources | Notes |
|---|---|---|---|
| backend | 1.00 (reference) | — | Levels.fyi backend ≈ all SWE (0.99) |
| fullstack | 0.76-0.94 | 5 (SO25, SO24, Levels.fyi, Payscale, Built In) | consistently a little below backend |
| frontend | 0.63-1.00 | 5 (+ BLS web devs 0.68, uncertain proxy) | widest spread; Levels.fyi TC at parity, Built In lowest |
| mobile | 0.97-1.15 | 4 (SO25, SO24, Levels.fyi, Payscale) | TC source highest |
| devops | 0.77-1.17 | 6 (SO25, SO24, Levels.fyi, RH, Payscale, Built In) | BLS net/sys admin 0.73 excluded (weak proxy) |
| data_scientist | 0.74-1.09 | 7 | base sources ≥ 0.88 except Built In |
| data_engineer | 0.81-1.10 | 5 (SO25, SO24, Levels.fyi, RH, Payscale) | BLS DB architects 1.03 excluded (uncertain) |
| data_analyst | 0.56-0.81 | 5 | lowest-paid technical role in every source |
| qa | 0.74-0.85 | 4 (SO24, BLS, Levels.fyi, Payscale) | tight range |
| security | 0.76-1.05 | 5 (SO25, SO24, BLS, RH, Payscale) | Levels.fyi splits: security SWE 1.38 (TC) vs cybersecurity analyst 0.64 |
| architect | 1.03-1.54 | 3 (SO25, Levels.fyi solution arch, Payscale) | BLS DB/network architects 0.99-1.03 are different jobs; Payscale value includes seniority |
| team_lead | 1.13-1.83 (EM proxies only) | 5 (SO25, SO24, BLS CIS mgrs, Levels.fyi, Payscale) | **no source publishes "team lead"**; low end (SO, base) more plausible for a TL |
| product_manager | 0.77-1.18 | 4 (Levels.fyi, RH, Payscale, Built In) | RH title may not be software-specific |

## 13. Experience-curve summary [R]

| Step | Base-pay sources | Total-comp sources (equity-inflated) | Note |
|---|---|---|---|
| junior → mid | 1.23-1.31 (Google/Meta/MSFT base, RH low→mid); Payscale early/entry 1.10-1.43 | 1.22-1.64 (Levels.fyi report 1.46; Google 1.43; Meta 1.64; MSFT 1.22) | Payscale entry (<1 yr) is narrower than our junior |
| mid → senior | 1.16-1.31 (RH mid→high, Google/Meta base 1.20-1.23); Payscale Mid/Early 1.09-1.27 | 1.38-1.51 | |
| senior → staff | 1.22 (Google/Meta base); Payscale band 4/Mid 1.02-1.19 | 1.46-1.71 | Payscale bands ambiguous; RH has no 4th tier |
| junior (<1 yr) → 7+ yrs span | Built In 1.37-1.77 | — | two buckets only |

[R] For an Israeli prior, the defensible range is roughly 1.15-1.3 per step on base pay, and flatter for senior → staff. Total-comp steps of 1.4-1.7 reflect US big-tech equity refresh grants.

---

## 14. Caveats: why US ratios may not transfer to Israel [R]

- **Equity weight differs.** US big-tech total comp at senior and staff level is up to about half stock (Google L6 base 285K vs TC 667K [S28]). Israeli salary posts are typically monthly gross base. Use base-pay ratios, not TC ratios.
- **Market structure.** The US role premiums reflect US labor supply. Examples: mobile above backend in Levels.fyi and SO24 US; security engineering above both. Israel's market (many cyber firms, large R&D centers of multinationals, heavy backend/infra demand) may rank security and devops differently.
- **Title semantics.** Some titles mean different things in Israel and the US:
  - "Team lead" in Israel is usually a hands-on manager of a small team, which is not the same as a US engineering manager. The EM proxies (especially the Levels.fyi 1.83) likely overstate a TL premium.
  - "Architect" in Israel is often a senior-IC title.
  - "QA" in Israel often means manual QA, while US "QA software engineer" is closer to SDET.
- **Experience buckets do not line up.** No US source publishes our buckets (0-2, 3-5, 6-9, 10+). Levels are company-defined, Robert Half tiers are qualitative, and Payscale bands are 1-4 / 5-9(?) / 10-19(?). Bucket-level ratios are approximate.
- **Self-selection.** Levels.fyi skews to big-tech, high-pay respondents. Payscale and Built In are self-reported with unknown n per bucket. SO respondents skew to engaged developers. Built In's backend figure looks like an outlier.
- **Global SO medians are confounded by country mix.** A role looks "well paid" globally if its practitioners are concentrated in rich countries. Use US-only or (with approval) Israel-only SO cuts.
- **Statistic mismatch.** Sources mix medians (SO, BLS, Levels.fyi titles), averages (Payscale avg base, Built In, Dice), "average or median" (Levels.fyi company pages) and starting-salary midpoints (Robert Half). Ratios within one source are more reliable than ratios across sources.
- **Time.** The data spans 2024 (SO24, Dice) to 2026/2027 (Levels.fyi live, Payscale 2026, Robert Half 2027 projections). Ratios move slowly, but AI-related titles are shifting fast.

---

## 15. Blocked / needs approval

| Item | Status | URL |
|---|---|---|
| Glassdoor salary pages | **blocked: HTTP 403** | https://www.glassdoor.com/Salaries/backend-developer-salary-SRCH_KO0,17.htm |
| Glassdoor Terms of Use | not read | — |
| Levels.fyi Terms | **blocked: HTTP 403** | https://www.levels.fyi/legal/terms |
| SO survey public dataset 2024 / 2025 / 2026 (CSV, ODbL 1.0; 2026 file 117 MB, Git LFS) | **needs user approval to download** | https://github.com/StackExchange/Survey/tree/main/packages/archive/2026 (and /2025, /2024) |
| SO 2026 schema CSV (91.7 KB, Git LFS; needed to confirm column names such as country and compensation) | **needs user approval to download** | https://github.com/StackExchange/Survey/blob/main/packages/archive/2026/survey_results_schema.csv |
| SO 2026 archive README | HTTP 503 at fetch time | https://github.com/StackExchange/Survey/blob/main/packages/archive/2026/README.md |
| BLS OEWS May 2025 national XLSX (gives p25/p75 and employment) | **needs user approval to download** | https://www.bls.gov/oes/special-requests/oesm25nat.zip |
| BLS OEWS occupation HTML pages | fetch returned index or unrelated content; national HTML is a JS app at data.bls.gov | https://www.bls.gov/oes/current/oes151252.htm |
| Dice 2025 Tech Salary Report PDF (role and experience charts) | **needs user approval to download** | https://dice.com/recruiting/ebooks/dice-tech-salary-report |
| Robert Half full-stack / front-end / mobile / QA / solutions architect / software developer / info-sec analyst values | not in page text (no workaround tried) | https://www.roberthalf.com/us/en/job-details/full-stack-developer (etc.) |
| Levels.fyi Microsoft levels 63+, Google L7+, Meta E7+ | collapsed on page; not read | [S28] |

---

## 16. Open questions

1. Should the parent session download the SO 2025 (and 2026) CSV to compute Israel-only medians by DevType and experience? Expect small n: 297 Israeli respondents in 2025, and fewer with salary. Report n per cell and suppress cells under a threshold.
2. Does the 2026 SO dataset contain an Israel country value, and how many Israeli rows have compensation? This is unverified without the schema and data.
3. Payscale band definitions beyond "Early Career 1-4 years" (Mid 5-9? Experienced 10-19? Late 20+?), and the apparent Late/Experienced label swap. Not confirmed on any page read.
4. Do Levels.fyi levels publish typical years of experience, which would map L3/L4/L5/L6 onto our buckets? Not found on the pages read.
5. BLS p25/p75 for the listed occupations need the XLSX (approval) or a readable data.bls.gov page.
6. Is Robert Half's "Product Manager" a software-product role? The page does not say.
7. Should team_lead get its own prior? No source publishes it. Options: a senior-IC × small premium, or wait for Israeli data.
8. Is the Built In backend figure (avg base 173,388; median 183,000) an outlier? Its n is not published.

---

## Sources

All accessed 2026-10-14.

- S1 Stack Overflow Developer Survey 2025, Work: https://survey.stackoverflow.co/2025/work
- S2 Stack Overflow Developer Survey 2025, Developers (country and experience): https://survey.stackoverflow.co/2025/developers
- S3 Stack Overflow Developer Survey 2025, Methodology: https://survey.stackoverflow.co/2025/methodology
- S4 Stack Overflow Developer Survey 2024, Work: https://survey.stackoverflow.co/2024/work
- S5 Stack Overflow Developer Survey 2024, Developer Profile: https://survey.stackoverflow.co/2024/developer-profile
- S6 Stack Overflow blog, "The results of the 2026 Developer Survey are here!" (2026-10-06): https://stackoverflow.blog/2026/10/06/the-results-of-the-2026-developer-survey-are-here/
- S7 Stack Overflow Developer Survey 2026, home and Work: https://survey.stackoverflow.co/2026/ ; https://survey.stackoverflow.co/2026/work
- S8 Stack Overflow Developer Survey 2026, Work full data (compensation): https://survey.stackoverflow.co/2026/work/data
- S9 Stack Overflow Developer Survey 2026, Methodology: https://survey.stackoverflow.co/2026/methodology
- S10 Stack Overflow survey data landing page, and GitHub archive folders: https://survey.stackoverflow.co/ ; https://github.com/StackExchange/Survey/tree/main/packages/archive/2024 ; https://github.com/StackExchange/Survey/tree/main/packages/archive/2025 ; https://github.com/StackExchange/Survey/tree/main/packages/archive/2026 ; ODbL 1.0: https://opendatacommons.org/licenses/odbl/1-0/
- S11 GitHub file pages (metadata only): https://github.com/StackExchange/Survey/blob/main/packages/archive/2026/survey_results_schema.csv ; https://github.com/StackExchange/Survey/blob/main/packages/archive/2026/survey_results_public.csv
- S12 survey.stackoverflow.co robots.txt: https://survey.stackoverflow.co/robots.txt
- S13 BLS OOH, Software Developers, Quality Assurance Analysts, and Testers (Pay): https://www.bls.gov/ooh/computer-and-information-technology/software-developers.htm
- S14 BLS OOH, Web Developers and Digital Designers: https://www.bls.gov/ooh/computer-and-information-technology/web-developers.htm
- S15 BLS OOH, Data Scientists: https://www.bls.gov/ooh/math/data-scientists.htm
- S16 BLS OOH, Information Security Analysts: https://www.bls.gov/ooh/computer-and-information-technology/information-security-analysts.htm
- S17 BLS OOH, Database Administrators and Architects: https://www.bls.gov/ooh/computer-and-information-technology/database-administrators.htm
- S18 BLS OOH, Computer Network Architects: https://www.bls.gov/ooh/computer-and-information-technology/computer-network-architects.htm
- S19 BLS OOH, Computer and Information Systems Managers: https://www.bls.gov/ooh/management/computer-and-information-systems-managers.htm
- S20 BLS OOH, Network and Computer Systems Administrators: https://www.bls.gov/ooh/computer-and-information-technology/network-and-computer-systems-administrators.htm
- S21 BLS OOH, Computer Programmers: https://www.bls.gov/ooh/computer-and-information-technology/computer-programmers.htm
- S22 BLS OEWS data tables index (May 2025; last modified 2026-05-15): https://www.bls.gov/oes/current/oes_nat.htm ; https://www.bls.gov/oes/2025/may/oes_nat.htm
- S23 BLS OEWS FAQ and overview: https://www.bls.gov/oes/oes_ques.htm ; https://www.bls.gov/oes/oes_emp.htm
- S24 bls.gov robots.txt: https://www.bls.gov/robots.txt
- S25 Levels.fyi End of Year Pay Report 2025: https://www.levels.fyi/2025/
- S26 Levels.fyi 2025 US Regional report: https://www.levels.fyi/reports/2025-us-regional.html
- S27 Levels.fyi US title pages:
  - Software Engineer: https://www.levels.fyi/t/software-engineer/locations/united-states
  - Backend: https://www.levels.fyi/t/software-engineer/title/backend-software-engineer/locations/united-states
  - Frontend: https://www.levels.fyi/t/software-engineer/title/frontend-software-engineer/locations/united-states
  - Full-stack: https://www.levels.fyi/t/software-engineer/title/full-stack-software-engineer/locations/united-states
  - Mobile: https://www.levels.fyi/t/software-engineer/title/mobile-software-engineer/locations/united-states
  - DevOps: https://www.levels.fyi/t/software-engineer/title/devops-engineer/locations/united-states
  - Security SWE: https://www.levels.fyi/t/software-engineer/title/security-software-engineer/locations/united-states
  - Data engineer: https://www.levels.fyi/t/software-engineer/title/data-engineer/locations/united-states
  - QA: https://www.levels.fyi/t/software-engineer/title/quality-assurance-(qa)-software-engineer/locations/united-states
  - Product manager: https://www.levels.fyi/t/product-manager/locations/united-states
  - Data scientist: https://www.levels.fyi/t/data-scientist/locations/united-states
  - Data analyst: https://www.levels.fyi/t/data-analyst/locations/united-states
  - Solution architect: https://www.levels.fyi/t/solution-architect/locations/united-states
  - Cybersecurity analyst: https://www.levels.fyi/t/security-analyst/locations/united-states
  - Engineering manager: https://www.levels.fyi/t/software-engineering-manager/locations/united-states
  - Title index: https://www.levels.fyi/t
- S28 Levels.fyi company level pages (US): https://www.levels.fyi/companies/google/salaries/software-engineer ; https://www.levels.fyi/companies/meta/salaries/software-engineer ; https://www.levels.fyi/companies/microsoft/salaries/software-engineer
- S29 Levels.fyi Software Engineer, Israel (ILS): https://www.levels.fyi/t/software-engineer/locations/israel
- S30 Levels.fyi robots.txt: https://www.levels.fyi/robots.txt ; Terms (403): https://www.levels.fyi/legal/terms
- S31 Glassdoor salary page (403): https://www.glassdoor.com/Salaries/backend-developer-salary-SRCH_KO0,17.htm ; robots.txt: https://www.glassdoor.com/robots.txt
- S32 Dice Tech Salary Report 2025 (recruiting page): https://dice.com/recruiting/ebooks/dice-tech-salary-report
- S33 Dice Tech Salary Report 2025 (technologists eBook, salary trends chapter): https://dice.com/technologists/ebooks/tech-salary-report/ ; https://dice.com/technologists/ebooks/tech-salary-report/salary-trends.html
- S34 dice.com robots.txt: https://www.dice.com/robots.txt
- S35 Robert Half 2027 Salary Guide: https://www.roberthalf.com/us/en/insights/salary-guide ; Technology: https://www.roberthalf.com/us/en/insights/salary-guide/technology ; 2027 technology salary trends: https://www.roberthalf.com/us/en/insights/research/technology-salary-trends
- S36 Robert Half US job-details pages: https://www.roberthalf.com/us/en/job-details/software-engineer ; https://www.roberthalf.com/us/en/job-details/devops-engineer ; https://www.roberthalf.com/us/en/job-details/data-engineer ; https://www.roberthalf.com/us/en/job-details/data-analyst ; https://www.roberthalf.com/us/en/job-details/data-scientist ; https://www.roberthalf.com/us/en/job-details/cybersecurity-engineer ; https://www.roberthalf.com/us/en/job-details/product-manager
- S37 roberthalf.com robots.txt: https://www.roberthalf.com/robots.txt
- S38 Payscale US job pages:
  - Software Engineer: https://www.payscale.com/research/US/Job=Software_Engineer/Salary
  - Software Developer: https://www.payscale.com/research/US/Job=Software_Developer/Salary
  - Full Stack: https://www.payscale.com/research/US/Job=Full_Stack_Software_Developer/Salary
  - Front End: https://www.payscale.com/research/US/Job=Front_End_Developer_%2F_Engineer/Salary
  - Mobile: https://www.payscale.com/research/US/Job=Mobile_Applications_Developer/Salary
  - DevOps: https://www.payscale.com/research/US/Job=Development_Operations_(DevOps)_Engineer/Salary
  - Data Scientist: https://www.payscale.com/research/US/Job=Data_Scientist/Salary
  - Data Engineer: https://www.payscale.com/research/US/Job=Data_Engineer/Salary
  - Data Analyst: https://www.payscale.com/research/US/Job=Data_Analyst/Salary
  - QA: https://www.payscale.com/research/US/Job=Quality_Assurance_(QA)_Engineer/Salary
  - Security: https://www.payscale.com/research/US/Job=Security_Engineer/Salary
  - Architect: https://www.payscale.com/research/US/Job=Software_Architect/Salary
  - Engineering Manager: https://www.payscale.com/research/US/Job=Software_Engineering_Manager/Salary
  - Product Manager: https://www.payscale.com/research/US/Job=Product_Manager%2C_Software/Salary
  - Band-definition check: https://www.payscale.com/research/US/Job=Management_Consultant/Salary/285d670c/Late-Career
- S39 payscale.com robots.txt: https://www.payscale.com/robots.txt
- S40 Built In US salary pages:
  - Back end: https://builtin.com/salaries/us/back-end-developer
  - Front end: https://builtin.com/salaries/us/front-end-developer
  - Full stack: https://builtin.com/salaries/us/full-stack-developer
  - DevOps: https://builtin.com/salaries/us/devops-engineer
  - Data scientist: https://builtin.com/salaries/us/data-scientist
  - Product manager: https://builtin.com/salaries/us/product-manager
  - robots.txt: https://builtin.com/robots.txt
