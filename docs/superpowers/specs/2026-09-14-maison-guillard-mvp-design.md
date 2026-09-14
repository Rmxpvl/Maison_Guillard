# Maison Guillard — MVP Design (condensed from project documentation)

> Source documents (authoritative, out-of-repo): `Documentation/Maison-Guillard-MVP.pdf`,
> `Documentation/Maison-Guillard-Doc-Technique.pdf`, `Documentation/Maison-Guillard-Plan-de-route.pdf`
> (in the parent `Maison_guillard/` folder). This file condenses the parts needed to plan and
> implement Semaine 4 (project init: backend, DB, frontend skeleton, admin auth) and stays valid
> for later weeks (S5-S9).

## Product summary

Maison Guillard: web app for an artisan furniture maker to present and sell handmade furniture
(tables, chairs, stools, lamps). Two public flows: direct purchase (cart → order) and quote
request (form → artisan follow-up). One admin (the artisan) manages the catalog via a protected
back-office. No customer accounts in the MVP (guest checkout / guest quote requests).

## Stack

- **Frontend:** React + Vite (JS or TS — pick one and stay consistent; plan below uses plain JS
  for speed, matching the "solo dev, 9-week window" constraint).
- **Backend:** Node.js + Express, REST API under `/api`.
- **Database:** PostgreSQL via Prisma ORM.
- **Auth:** JWT (stateless) + bcrypt password hashing. Single admin account, no roles/permissions
  system beyond "is admin."
- **Media:** Cloudinary for product photos (backend stores only the returned URL). Out of scope
  for S4 — introduced when product CRUD is built (S5).
- **Local dev DB:** docker-compose running Postgres, so `docker compose up -d` gives a working DB
  without installing Postgres natively.

## Repository layout (monorepo, two independent apps — no workspaces needed for MVP scope)

```
Maison_Guillard/
├── backend/
│   ├── src/
│   │   ├── app.js              # Express app factory (no .listen() — for testability)
│   │   ├── server.js           # entrypoint: imports app, calls .listen()
│   │   ├── routes/
│   │   │   └── auth.routes.js
│   │   ├── controllers/
│   │   │   └── auth.controller.js
│   │   ├── services/
│   │   │   └── auth.service.js
│   │   ├── middleware/
│   │   │   └── requireAdmin.js
│   │   └── lib/
│   │       └── prisma.js       # shared PrismaClient instance
│   ├── prisma/
│   │   ├── schema.prisma
│   │   └── seed.js
│   ├── tests/
│   │   ├── unit/auth.service.test.js
│   │   └── integration/auth.routes.test.js
│   ├── .env.example
│   ├── package.json
│   └── vitest.config.js
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── context/AuthContext.jsx
│   │   ├── api/auth.js
│   │   └── pages/admin/PageLoginAdmin.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml           # postgres service for local dev
├── docs/superpowers/{specs,plans}/
└── .gitignore
```

Full catalog/order/quote schema, all REST endpoints, and the complete frontend component tree are
specified in `Maison-Guillard-Doc-Technique.pdf` §04-07 and are implemented incrementally in later
weeks (S5+). This spec only locks in what S4 needs.

## Database schema — S4 slice

Only the `Admin` table is needed this week. Later weeks add `Categorie`, `Produit`, `Photo`,
`Commande`, `LigneCommande`, `Devis` per the doc technique's ERD (page 7 of that PDF).

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Admin {
  id           Int      @id @default(autoincrement())
  email        String   @unique
  passwordHash String
  createdAt    DateTime @default(now())
}
```

## Auth design

- `AuthService.hashPassword(plain)` → bcrypt hash (10 salt rounds).
- `AuthService.verifyPassword(plain, hash)` → bool.
- `AuthService.login(email, password)` → looks up Admin by email, verifies password, returns a
  signed JWT (`{ sub: admin.id, email }`, secret from `process.env.JWT_SECRET`, expiry `8h`) or
  throws `InvalidCredentialsError`.
- `AuthService.verifyToken(token)` → decoded payload or throws.
- `requireAdmin` Express middleware: reads `Authorization: Bearer <token>`, verifies via
  `AuthService.verifyToken`, attaches `req.admin = payload` or responds `401`.
- Endpoint: `POST /api/auth/login` — body `{ email, motDePasse }` → `200 { token }` / `401`.
- Seed script creates one admin account from `SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD` env vars
  (never hardcode a password in source).

## Frontend — S4 slice

- Vite React app, no router library yet needed for a single page — add `react-router-dom` when S6
  introduces multiple public pages. For S4: a single `PageLoginAdmin` form that posts to
  `/api/auth/login`, stores the token via `AuthContext` (in-memory + `localStorage`), and shows
  "connecté" on success.
- `AuthContext` exposes `{ token, login(email, password), logout(), isAuthenticated }`.
- `api/auth.js` wraps `fetch` to `VITE_API_URL + '/auth/login'`.

## Testing strategy — S4 slice

- **Unit (Vitest):** `AuthService` methods, with Prisma mocked (no real DB hit) — hashing,
  password verification, token verify/expiry, invalid-credentials path.
- **Integration (Supertest + Vitest):** `POST /api/auth/login` against a real test database
  (separate `DATABASE_URL` for tests, reset between runs via `prisma migrate reset` in a
  pretest script or a truncate helper) — covers 200 and 401 paths end-to-end.
- No frontend test framework introduced yet for S4 (doc technique doesn't mandate frontend unit
  tests; manual parcours testing is the stated strategy — see doc technique §08).

## Out of scope for this plan (S4)

Product/category/photo/order/quote CRUD, Cloudinary integration, cart, public catalog pages,
`react-router-dom` multi-page routing. These land in S5-S8 per the plan de route and get their own
plans building on this one.

## Global constraints carried into the plan

- Node.js LTS (use whatever `node -v` reports locally as the floor; no specific version pinned by
  the source docs).
- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`) per doc
  technique §08.
- Branch model: `main` / `dev` / `feature/<task>` — for solo work in this session, commit directly
  on a `feature/s4-init` branch and note the merge-to-`dev` step at the end (per doc technique's
  SCM strategy, merges to `main` only from `dev`).
- No secrets committed: `.env` gitignored, `.env.example` documents required vars without values.
