# Frontend — pathologist review MVP

Web UI for the slide classifier: a pathologist opens a whole-slide image, sends it to the model and
sees the predicted class (non-tumour, adenocarcinoma/LUAD, squamous/LUSC), the model identifier, the
number of tiles analysed and any preprocessing quality warnings.

Vite + React + TypeScript, Zustand for state, OpenSeadragon for the slide viewer.

```
frontend/
├── src/
│   ├── api/contracts/inference.ts   prediction.json + job API types and runtime validation
│   ├── api/adapters/                mockAdapter (fixtures) · httpAdapter (model service)
│   ├── features/analysis/labels.ts  class names and quality-warning wording (only place)
│   ├── features/viewer/             OpenSeadragon viewer, zoom controls, minimap
│   └── styles/tokens.css            design tokens
├── tools/convert-slides/            .svs → Deep Zoom tiles for the viewer
└── tools/stub-model-server/         stdlib reference server for the job API
```

## Run

```sh
cd frontend
npm install
# put sample .svs files in frontend/sample-slides/, then once:
uv run tools/convert-slides/convert.py
npm run dev                          # http://localhost:5173, mock inference by default
```

`/kitchen-sink` shows every UI primitive and every analysis-panel state.

## Talking to the model service

```sh
cp .env.example .env.local           # VITE_INFERENCE_MODE=http, VITE_API_BASE_URL=http://localhost:8000
```

The UI submits a job and polls it:

- `POST /jobs` — multipart field `slide` (the `.svs`), optional `case_id` → `202 { job_id, status }`
- `GET /jobs/{id}` → `{ job_id, status: queued|running|done|failed, progress?, stage?, result?, error? }`
- `DELETE /jobs/{id}` — optional cancel

When `status` is `done`, `result` is the model's `prediction.json` (success or `{status:"error", reason}`),
typed and validated in `src/api/contracts/inference.ts`. The service must allow CORS from the UI origin.
`tools/stub-model-server/server.py` implements this API without a model, for local testing.

## Checks

```sh
npm run check                        # tsc --noEmit · oxlint · vite build
```
