# The organizational contract

What a domain and the organization exchange, as JSON Schema (draft 2020-12). It assumes no language, framework, storage or transport: a domain written in TypeScript over PostgreSQL and one written in Python over files implement the same three documents.

| Schema | Direction | What it is |
|---|---|---|
| [`signal.schema.json`](signal.schema.json) | domain → organization | Something that already happened |
| [`capability-manifest.schema.json`](capability-manifest.schema.json) | domain → organization | What a domain can achieve, never how |
| [`intent.schema.json`](intent.schema.json) | organization → domain | A desired outcome and its constraints |

The organization reports its own decisions as signals too, under the domain id `bionic`.

Contract version: **0.1**. The meaning of each field is in [docs/m0-model.md](../docs/m0-model.md) and [docs/m1-model.md](../docs/m1-model.md). The `bionic` package is one implementation, and its tests validate everything it produces against these schemas.
