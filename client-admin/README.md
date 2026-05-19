# Admin Client (`client-admin`)

Next.js admin dashboard for Drone4Dengue. This app is used for operations workflows such as user management, drone management, weather monitoring, dengue data operations, and reporting.

## Prerequisites

- Node.js 18+ and npm
- `server-api` running locally (usually `http://localhost:4000`)

## 1) Install dependencies

```bash
cd client-admin
npm install
```

## 2) Configure environment

Create `.env.local` (or copy from `env.example`):

```env
NEXT_PUBLIC_API_URL=http://localhost:4000
```

Optional keys in `env.example` (`UPLOADTHING_SECRET`, `UPLOADTHING_APP_ID`) are only needed if your local flow uses UploadThing integration.

## 3) Run locally

```bash
npm run dev
```

Open `http://localhost:3000`.

## Build and test commands

- `npm run dev` - start development server
- `npm run build` - create production build
- `npm run start` - run production build
- `npm run lint` - run lint checks

## Local verification checklist

1. Confirm login/signup flows can reach API.
2. Open pages that fetch backend data (users, drone management, weather, data management).
3. Verify no API URL mismatch (`NEXT_PUBLIC_API_URL` must point to your `server-api`).

# Drone4Dengue Admin Web Portal (client-admin)

Next.js **15** admin dashboard (App Router, TypeScript) for managing users, drones, dengue data, reports, and weather-related views. UI uses Tailwind CSS, Radix primitives, and maps (Leaflet / MapLibre) where applicable.

## Prerequisites

- Node.js 18+
- Running [server-api](../server-api/) (default `http://localhost:4000`)

## Setup

1. Install dependencies:

   ```bash
   cd client-admin
   npm install
   ```

2. Environment — create `.env.local` (or copy from your team’s template):

   ```env
   NEXT_PUBLIC_API_URL=http://localhost:4000
   ```

   The app reads the REST API base URL from `NEXT_PUBLIC_API_URL` (see `src/lib/api.ts` and feature pages). Do not commit secrets; production URLs belong in hosting env vars or `.env.production` that stays out of git.

3. Development server:

   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000).

## Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Next.js dev server |
| `npm run build` | Production build |
| `npm run start` | Start production server (after `build`) |
| `npm run lint` | Run ESLint |

## Documentation

- [Root README](../README.md) — repository overview
- [Setup guide](../docs/setup-guide.md) — full stack
- [API specification](../docs/api-spec.md)
