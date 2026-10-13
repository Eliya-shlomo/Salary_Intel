# Salary Intel — command reference

## The two you actually need

```bash
./scripts/up.sh            # bring everything up
./scripts/down.sh          # take everything down (keeps the data)
```

`up.sh` is idempotent — run it as often as you like. It checks Docker, frees
port 6379, builds and starts db + redis + api, waits for `/health`, creates the
tables, and seeds **only if the database is empty**.

### Flags

| command | effect |
|---|---|
| `./scripts/up.sh` | backend stack only |
| `./scripts/up.sh --frontend` | also `npm install` + start Next.js on :3000 |
| `./scripts/up.sh --real` | if seeding, also bulk-ingest the real Facebook posts |
| `./scripts/down.sh` | stop containers, **keep** the postgres volume |
| `./scripts/down.sh --wipe` | also delete the volume — asks you to type DELETE |
| `./scripts/down.sh --restore-redis` | start the local brew redis again |

`SKIP_REDIS_STOP=1 ./scripts/up.sh` leaves your local redis alone.

---

## Everything else

### Health and data

```bash
curl -s http://localhost:8000/health
```

```bash
curl -s -H "X-API-Key: $(grep -m1 '^API_KEY=' .env | cut -d= -f2-)" http://localhost:8000/api/v1/stats
```

### A real query end to end

```bash
curl -s -X POST http://localhost:8000/api/v1/query -H 'Content-Type: application/json' -H "X-API-Key: $(grep -m1 '^API_KEY=' .env | cut -d= -f2-)" -d '{"query":"כמה מרוויח מהנדס תשתיות ענן"}'
```

### The ablation study — run this before the interview

```bash
docker exec salary_intel_api python -m app.ablation_study
```

Fills the two missing rows in the 0.46 → 0.88 table. ~200 OpenAI calls, a few
cents, a few minutes.

### Regenerate the 50 evaluation questions

```bash
docker exec salary_intel_api python -m app.rag.qa_generator
```

Only needed if you wiped the volume — the test cases reference post ids.

### Seeding by hand

```bash
docker exec salary_intel_api python -m app.seed
```

```bash
docker exec salary_intel_api python -m app.seed --real
```

`backend/seed_data.py` does **not** work: it is not copied into the image and it
calls the async `ingest_post` without awaiting it. Use `app.seed` instead.

### Logs

```bash
docker compose logs -f api
```

```bash
docker compose logs --tail=50 db
```

### Shell inside the API container

```bash
docker exec -it salary_intel_api bash
```

### Query the logs table directly

```bash
docker exec -it salary_intel_db psql -U postgres -d salary_intel -c "SELECT query, latency_retrieval, latency_generation, latency_total, tokens_used FROM query_logs ORDER BY created_at DESC LIMIT 10;"
```

### Latency summary — the number behind the 62% claim

```bash
docker exec -it salary_intel_db psql -U postgres -d salary_intel -c "SELECT COUNT(*) n, ROUND(AVG(latency_retrieval)::numeric,2) avg_retrieval, ROUND(AVG(latency_total)::numeric,2) avg_total FROM query_logs WHERE success;"
```

Know the `n` before the interview — you will be asked how many queries the
average is over.

### Frontend on its own

```bash
cd frontend && npm run dev
```

No `.env.local` needed — the fallback key in `lib/api.ts` matches your `.env`.

---

## Danger

```bash
docker compose down -v
```

Deletes the postgres volume and every ingested post.
`generated_test_cases.json` points at those ids, so the ablation study breaks
until you re-seed and regenerate. Use `./scripts/down.sh --wipe` instead — it
makes you confirm.
