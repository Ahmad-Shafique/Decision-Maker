# Phase 3 (Revised): Mobile App with Cloud Backend

**Status:** Ready for Implementation  
**Issue with Previous Plan:** Mobile was querying local FastAPI, not suitable for real mobile use.

---

## Architecture Decision

```
┌─────────────────────────┐      HTTPS      ┌─────────────────────────┐
│     Mobile App          │ ───────────────→│    Cloud Backend        │
│  (React Native/Expo)    │                 │  (Hosted FastAPI)       │
└─────────────────────────┘                 └─────────────────────────┘
                                                      │
                                            ┌─────────┴─────────┐
                                            │   Gemini API      │
                                            │   (Embeddings)    │
                                            └───────────────────┘
```

---

## Backend Hosting

**Choice: Render** (free tier, auto-deploys from GitHub, no Docker needed)

> [!NOTE]
> Render auto-detects Python projects via `requirements.txt`. No Dockerfile required.

---

## Implementation Plan

### Part A: Backend Deployment (Render)

#### 1. Prepare for Deployment

##### [NEW] `render.yaml` (optional but recommended)
```yaml
services:
  - type: web
    name: decision-api
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.interfaces.api:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GEMINI_API_KEY
        sync: false  # Set manually in Render dashboard
      - key: PYTHON_VERSION
        value: "3.11"
```

##### [MODIFY] `src/interfaces/api.py`
- Change host from `127.0.0.1` to `0.0.0.0`
- Read port from `$PORT` environment variable (Render sets this)
- Remove `reload=True` for production
- Add CORS for mobile app

```python
def start():
    port = int(os.environ.get("PORT", 2947))
    uvicorn.run("src.interfaces.api:app", host="0.0.0.0", port=port)
```

#### 2. Deploy Steps
1. Push code to GitHub (public or private repo)
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set environment variables: `GEMINI_API_KEY`
5. Deploy → Get public URL: `https://decision-api.onrender.com`

> [!IMPORTANT]
> Render free tier sleeps after 15 min of inactivity. First request may take ~30s to wake.

---

### Part B: Mobile App Architecture (Flexible Design)

#### Core Principle: Separation of Concerns

```
src/interfaces/mobile/
├── services/           # API layer (easily swappable)
│   ├── api.ts          # HTTP client, base URL config
│   ├── types.ts        # Shared types (match backend models)
│   └── endpoints/
│       ├── analyze.ts      # /analyze endpoint
│       ├── principles.ts   # /principles endpoint
│       └── evolution.ts    # Future: /evolution endpoint
├── hooks/              # Data fetching hooks
│   ├── useAnalyze.ts
│   ├── usePrinciples.ts
│   └── useEvolution.ts     # Future: easy to add
├── screens/
│   ├── AnalyzeScreen.tsx
│   ├── HistoryScreen.tsx
│   └── EvolutionScreen.tsx # Future: plug in easily
└── config/
    └── env.ts          # Environment config (dev/prod URLs)
```

#### Key Files

##### [NEW] `config/env.ts`
```typescript
export const ENV = {
  API_URL: __DEV__ 
    ? 'http://localhost:8000'  // Local dev
    : 'https://decision-api.railway.app',  // Production
};
```

##### [NEW] `services/api.ts`
```typescript
import { ENV } from '../config/env';

class ApiClient {
  private baseUrl = ENV.API_URL;

  async analyze(description: string): Promise<DecisionResult> {
    const res = await fetch(`${this.baseUrl}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    return res.json();
  }

  // Easy to add new endpoints:
  async getEvolution(situationType: string): Promise<EvolutionReport> {
    return fetch(`${this.baseUrl}/evolution/${situationType}`).then(r => r.json());
  }
}

export const api = new ApiClient();
```

##### [NEW] `services/types.ts`
```typescript
// Mirror backend Pydantic models
export interface DecisionResult {
  situation: Situation;
  applicable_principles: PrincipleMatch[];
  triggered_sops: SOP[];
  recommendation: string;
  confidence: number;
  reasoning: string;
  matching_metadata?: MatchingMetadata;
}

// Future additions just add new interfaces:
export interface EvolutionReport {
  situation_type: string;
  analyses: AnalysisReport[];
  trend: TrendData;
}
```

---

## Why This Design is Flexible

| Future Change | How to Integrate |
|---------------|------------------|
| Add `/evolution` endpoint | Add `endpoints/evolution.ts`, create `useEvolution` hook |
| Change backend URL | Update `config/env.ts` only |
| Switch to GraphQL | Replace `services/api.ts`, hooks stay same |
| Add authentication | Add interceptor in `api.ts` |
| Offline support | Add caching layer between hooks and API |

---

## Verification Plan

1. **Backend**: Deploy to Railway, verify `/health` returns 200
2. **Mobile**: Build APK, test against production URL
3. **Integration**: Submit "stepbrother land dispute" scenario, verify principles match

---

## Execution Order

1. ✅ Prepare Dockerfile and deployment config
2. ✅ Deploy backend to Railway/Render
3. Update mobile app with flexible service layer
4. Configure environment switching (dev/prod)
5. Test end-to-end
6. `/post-phase-commit`
