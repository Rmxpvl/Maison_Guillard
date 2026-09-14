# S4 — Project Init & Admin Auth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the Maison Guillard monorepo (backend + frontend + local Postgres) and ship a
working admin authentication flow (`POST /api/auth/login` + a login page), matching the plan de
route's Semaine 4 objective: "Initialiser le projet (backend, base de données, squelette
frontend) ; authentification et autorisation administrateur."

**Architecture:** Two independent Node apps in one repo (`backend/`, `frontend/`), no shared
workspace tooling. Backend is Express + Prisma/PostgreSQL exposing a REST API under `/api`;
frontend is a Vite + React SPA that calls it over `fetch`. Postgres runs locally via
docker-compose. Auth is stateless JWT + bcrypt, single admin account, no roles beyond "is admin."

**Tech Stack:** Node.js (LTS, v25.8.1 confirmed locally), Express, Prisma, PostgreSQL 16
(docker-compose), Vitest + Supertest, React 18 + Vite, jsonwebtoken, bcrypt.

**Spec:** `docs/superpowers/specs/2026-09-14-maison-guillard-mvp-design.md`

## Global Constraints

- Node.js LTS as the floor (v25.8.1 confirmed on this machine — do not require a newer minimum).
- Conventional Commits format for every commit (`feat:`, `fix:`, `docs:`, `chore:`, `test:`,
  `refactor:`).
- Work happens on branch `feature/s4-init` (create from `main`); do not commit directly to `main`
  beyond what's already there.
- No secrets committed: `.env` files are gitignored; `.env.example` documents required vars with
  placeholder values only.
- Backend `app.js` must export the Express app WITHOUT calling `.listen()` — `server.js` is the
  only place that listens, so tests can import `app.js` and use Supertest without binding a port.

---

### Task 1: Repo skeleton, docker-compose Postgres, gitignore

**Files:**
- Create: `backend/` (empty dir, populated in Task 2)
- Create: `frontend/` (empty dir, populated in Task 7)
- Create: `docker-compose.yml`
- Create: `.gitignore`
- Create: `README.md`

**Interfaces:**
- Produces: a running Postgres instance reachable at `localhost:5432`, database `maison_guillard`,
  user/password `maison`/`maison_dev_password` — later tasks' `DATABASE_URL` values depend on
  these exact values.

- [ ] **Step 1: Create `.gitignore`**

```gitignore
node_modules/
.env
.env.*
!.env.example
dist/
build/
*.log
.DS_Store
```

- [ ] **Step 2: Create `docker-compose.yml`**

```yaml
services:
  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: maison
      POSTGRES_PASSWORD: maison_dev_password
      POSTGRES_DB: maison_guillard
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U maison -d maison_guillard"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  postgres_data:
```

- [ ] **Step 3: Create root `README.md`**

```markdown
# Maison Guillard

Web app for presenting and selling handmade furniture. See
`docs/superpowers/specs/2026-09-14-maison-guillard-mvp-design.md` for the design and
`docs/superpowers/plans/` for implementation plans.

## Local dev setup

1. `docker compose up -d` — starts Postgres on `localhost:5432`.
2. `cd backend && cp .env.example .env && npm install && npx prisma migrate dev && npm run seed && npm run dev`
3. `cd frontend && npm install && npm run dev`
```

- [ ] **Step 4: Start Postgres and verify it's healthy**

Run: `docker compose up -d && docker compose ps`
Expected: `postgres` service listed with `STATUS` containing `healthy` (wait a few seconds and
re-run `docker compose ps` if it still says `starting`).

- [ ] **Step 5: Create branch and commit**

```bash
git checkout -b feature/s4-init
mkdir -p backend frontend
git add .gitignore docker-compose.yml README.md
git commit -m "chore: scaffold repo skeleton with docker-compose postgres"
```

---

### Task 2: Backend Express skeleton with health check

**Files:**
- Create: `backend/package.json`
- Create: `backend/src/app.js`
- Create: `backend/src/server.js`
- Create: `backend/vitest.config.js`
- Test: `backend/tests/integration/health.test.js`

**Interfaces:**
- Consumes: nothing (first backend code).
- Produces: `app.js` exports `module.exports = app` (an Express instance, no `.listen()` call) —
  every later backend test imports this. `server.js` is the process entrypoint (`node
  src/server.js`), reading `PORT` from env (default `3000`).

- [ ] **Step 1: Init backend package and install dependencies**

```bash
cd backend
npm init -y
npm install express dotenv cors
npm install --save-dev vitest supertest
```

- [ ] **Step 2: Set `backend/package.json` scripts and type**

Edit `backend/package.json` — add/merge these fields:

```json
{
  "type": "commonjs",
  "scripts": {
    "dev": "node src/server.js",
    "test": "vitest run",
    "test:watch": "vitest"
  }
}
```

- [ ] **Step 3: Write the failing test**

```javascript
// backend/tests/integration/health.test.js
const request = require('supertest');
const { describe, it, expect } = require('vitest');
const app = require('../../src/app');

describe('GET /api/health', () => {
  it('returns 200 with status ok', async () => {
    const res = await request(app).get('/api/health');
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ status: 'ok' });
  });
});
```

- [ ] **Step 4: Create `backend/vitest.config.js`**

```javascript
const { defineConfig } = require('vitest/config');

module.exports = defineConfig({
  test: {
    globals: false,
    environment: 'node',
  },
});
```

- [ ] **Step 5: Run test to verify it fails**

Run (from `backend/`): `npm test`
Expected: FAIL — `Cannot find module '../../src/app'`

- [ ] **Step 6: Create `backend/src/app.js`**

```javascript
const express = require('express');
const cors = require('cors');

const app = express();

app.use(cors());
app.use(express.json());

app.get('/api/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

module.exports = app;
```

- [ ] **Step 7: Create `backend/src/server.js`**

```javascript
require('dotenv').config();
const app = require('./app');

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Maison Guillard API listening on port ${PORT}`);
});
```

- [ ] **Step 8: Run test to verify it passes**

Run (from `backend/`): `npm test`
Expected: PASS (1 test)

- [ ] **Step 9: Commit**

```bash
git add backend/package.json backend/package-lock.json backend/src backend/tests backend/vitest.config.js
git commit -m "feat: add express app skeleton with health check endpoint"
```

---

### Task 3: Prisma schema, migration, shared client

**Files:**
- Create: `backend/prisma/schema.prisma`
- Create: `backend/src/lib/prisma.js`
- Create: `backend/.env.example`
- Modify: `backend/package.json` (add `prisma` deps + `postinstall`/`migrate` scripts)

**Interfaces:**
- Consumes: `DATABASE_URL` env var (from `.env`, pointing at the docker-compose Postgres from
  Task 1).
- Produces: `backend/src/lib/prisma.js` exports a singleton `PrismaClient` instance
  (`module.exports = prisma`) — every service in later tasks imports this instead of constructing
  its own client. The `Admin` model (fields: `id`, `email`, `passwordHash`, `createdAt`) is now
  queryable via `prisma.admin.*`.

- [ ] **Step 1: Install Prisma**

```bash
cd backend
npm install @prisma/client
npm install --save-dev prisma
```

- [ ] **Step 2: Create `backend/prisma/schema.prisma`**

```prisma
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

- [ ] **Step 3: Create `backend/.env.example`**

```
DATABASE_URL="postgresql://maison:maison_dev_password@localhost:5432/maison_guillard?schema=public"
JWT_SECRET="replace-with-a-long-random-string"
SEED_ADMIN_EMAIL="admin@maisonguillard.fr"
SEED_ADMIN_PASSWORD="replace-with-a-strong-password"
PORT=3000
```

- [ ] **Step 4: Create local `.env` for development (not committed)**

```bash
cp .env.example .env
```

Edit `backend/.env` and set `JWT_SECRET` to a real random value (e.g. run
`node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"` and paste the output),
and set `SEED_ADMIN_PASSWORD` to a real password you'll use to log in locally.

- [ ] **Step 5: Create `backend/src/lib/prisma.js`**

```javascript
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

module.exports = prisma;
```

- [ ] **Step 6: Run the first migration**

Run (from `backend/`): `npx prisma migrate dev --name init`
Expected: prompts create `prisma/migrations/<timestamp>_init/migration.sql`, applies it to the
`maison_guillard` database, and prints "Your database is now in sync with your schema."

- [ ] **Step 7: Verify the table exists**

Run: `npx prisma studio` (opens a browser UI) — or non-interactively:
`docker compose exec postgres psql -U maison -d maison_guillard -c '\d "Admin"'`
Expected: shows the `Admin` table with columns `id, email, passwordHash, createdAt`.
Close/stop Prisma Studio (Ctrl+C) before continuing.

- [ ] **Step 8: Commit**

```bash
git add backend/prisma backend/src/lib backend/.env.example backend/package.json backend/package-lock.json
git commit -m "feat: add prisma schema with Admin model and initial migration"
```

---

### Task 4: AuthService (unit tests, Prisma mocked)

**Files:**
- Create: `backend/src/services/auth.service.js`
- Test: `backend/tests/unit/auth.service.test.js`
- Modify: `backend/package.json` (add `bcrypt`, `jsonwebtoken`)

**Interfaces:**
- Consumes: `backend/src/lib/prisma.js` (mocked in this task's tests).
- Produces: `AuthService.hashPassword(plain: string): Promise<string>`,
  `AuthService.verifyPassword(plain: string, hash: string): Promise<boolean>`,
  `AuthService.login(email: string, password: string): Promise<{ token: string }>` (throws
  `InvalidCredentialsError` on bad email/password), `AuthService.verifyToken(token: string):
  { sub: number, email: string }` (throws on invalid/expired token). Task 5's route and
  middleware call these exact names.

- [ ] **Step 1: Install auth dependencies**

```bash
cd backend
npm install bcrypt jsonwebtoken
```

- [ ] **Step 2: Write the failing tests**

```javascript
// backend/tests/unit/auth.service.test.js
const { describe, it, expect, vi, beforeEach } = require('vitest');

vi.mock('../../src/lib/prisma', () => ({
  __esModule: true,
  default: undefined,
  admin: {
    findUnique: vi.fn(),
  },
}));

const prisma = require('../../src/lib/prisma');
const AuthService = require('../../src/services/auth.service');

describe('AuthService.hashPassword / verifyPassword', () => {
  it('hashes a password and verifies it back', async () => {
    const hash = await AuthService.hashPassword('correct horse battery staple');
    expect(hash).not.toBe('correct horse battery staple');
    const ok = await AuthService.verifyPassword('correct horse battery staple', hash);
    expect(ok).toBe(true);
  });

  it('rejects the wrong password', async () => {
    const hash = await AuthService.hashPassword('right-password');
    const ok = await AuthService.verifyPassword('wrong-password', hash);
    expect(ok).toBe(false);
  });
});

describe('AuthService.login', () => {
  beforeEach(() => {
    prisma.admin.findUnique.mockReset();
    process.env.JWT_SECRET = 'test-secret';
  });

  it('returns a token for valid credentials', async () => {
    const passwordHash = await AuthService.hashPassword('good-password');
    prisma.admin.findUnique.mockResolvedValue({
      id: 1,
      email: 'admin@test.com',
      passwordHash,
    });

    const result = await AuthService.login('admin@test.com', 'good-password');

    expect(result).toHaveProperty('token');
    expect(typeof result.token).toBe('string');
  });

  it('throws InvalidCredentialsError for unknown email', async () => {
    prisma.admin.findUnique.mockResolvedValue(null);

    await expect(AuthService.login('nobody@test.com', 'whatever')).rejects.toThrow(
      AuthService.InvalidCredentialsError
    );
  });

  it('throws InvalidCredentialsError for wrong password', async () => {
    const passwordHash = await AuthService.hashPassword('good-password');
    prisma.admin.findUnique.mockResolvedValue({
      id: 1,
      email: 'admin@test.com',
      passwordHash,
    });

    await expect(AuthService.login('admin@test.com', 'bad-password')).rejects.toThrow(
      AuthService.InvalidCredentialsError
    );
  });
});

describe('AuthService.verifyToken', () => {
  beforeEach(() => {
    process.env.JWT_SECRET = 'test-secret';
  });

  it('decodes a token produced by login', async () => {
    const passwordHash = await AuthService.hashPassword('good-password');
    prisma.admin.findUnique.mockResolvedValue({
      id: 42,
      email: 'admin@test.com',
      passwordHash,
    });
    const { token } = await AuthService.login('admin@test.com', 'good-password');

    const decoded = AuthService.verifyToken(token);

    expect(decoded.sub).toBe(42);
    expect(decoded.email).toBe('admin@test.com');
  });

  it('throws on a garbage token', () => {
    expect(() => AuthService.verifyToken('not-a-real-token')).toThrow();
  });
});
```

- [ ] **Step 3: Run tests to verify they fail**

Run (from `backend/`): `npm test`
Expected: FAIL — `Cannot find module '../../src/services/auth.service'`

- [ ] **Step 4: Create `backend/src/services/auth.service.js`**

```javascript
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const prisma = require('../lib/prisma');

const SALT_ROUNDS = 10;
const TOKEN_EXPIRY = '8h';

class InvalidCredentialsError extends Error {
  constructor() {
    super('Invalid email or password');
    this.name = 'InvalidCredentialsError';
  }
}

async function hashPassword(plain) {
  return bcrypt.hash(plain, SALT_ROUNDS);
}

async function verifyPassword(plain, hash) {
  return bcrypt.compare(plain, hash);
}

async function login(email, password) {
  const admin = await prisma.admin.findUnique({ where: { email } });
  if (!admin) {
    throw new InvalidCredentialsError();
  }

  const passwordMatches = await verifyPassword(password, admin.passwordHash);
  if (!passwordMatches) {
    throw new InvalidCredentialsError();
  }

  const token = jwt.sign({ sub: admin.id, email: admin.email }, process.env.JWT_SECRET, {
    expiresIn: TOKEN_EXPIRY,
  });

  return { token };
}

function verifyToken(token) {
  return jwt.verify(token, process.env.JWT_SECRET);
}

module.exports = {
  hashPassword,
  verifyPassword,
  login,
  verifyToken,
  InvalidCredentialsError,
};
```

- [ ] **Step 5: Run tests to verify they pass**

Run (from `backend/`): `npm test`
Expected: PASS (all `auth.service.test.js` + previous `health.test.js` tests green)

- [ ] **Step 6: Commit**

```bash
git add backend/src/services backend/tests/unit backend/package.json backend/package-lock.json
git commit -m "feat: add AuthService with bcrypt hashing and JWT issuing"
```

---

### Task 5: `requireAdmin` middleware + `POST /api/auth/login` route (integration tests, real test DB)

**Files:**
- Create: `backend/src/middleware/requireAdmin.js`
- Create: `backend/src/controllers/auth.controller.js`
- Create: `backend/src/routes/auth.routes.js`
- Modify: `backend/src/app.js` (mount the auth router)
- Test: `backend/tests/integration/auth.routes.test.js`
- Modify: `backend/.env.example`, `backend/.env` (add `TEST_DATABASE_URL`)
- Modify: `backend/package.json` (add `pretest` DB reset script)

**Interfaces:**
- Consumes: `AuthService.login`, `AuthService.verifyToken`, `AuthService.InvalidCredentialsError`
  from Task 4; `prisma` from Task 3.
- Produces: `requireAdmin` Express middleware (attaches `req.admin = { sub, email }` or responds
  `401 { error: 'Unauthorized' }`) — later tasks (product/order/quote admin routes in S5+) mount
  this on protected routes. Route `POST /api/auth/login` mounted at `/api/auth/login`.

- [ ] **Step 1: Add a separate test database URL**

Edit `backend/.env.example`, add:

```
TEST_DATABASE_URL="postgresql://maison:maison_dev_password@localhost:5432/maison_guillard_test?schema=public"
```

Edit `backend/.env` and add the same line (with real values matching your local Postgres).

- [ ] **Step 2: Create the test database and apply migrations to it**

```bash
docker compose exec postgres psql -U maison -d maison_guillard -c "CREATE DATABASE maison_guillard_test;"
cd backend
DATABASE_URL="$TEST_DATABASE_URL" npx prisma migrate deploy
```

On Windows PowerShell use instead: `$env:DATABASE_URL=$env:TEST_DATABASE_URL; npx prisma migrate deploy`
(or read `TEST_DATABASE_URL` from `.env` manually and pass it inline — any shell works as long as
`DATABASE_URL` points at `maison_guillard_test` for this one command).

- [ ] **Step 3: Write the failing tests**

```javascript
// backend/tests/integration/auth.routes.test.js
const request = require('supertest');
const { describe, it, expect, beforeAll, afterAll, beforeEach } = require('vitest');

process.env.DATABASE_URL = process.env.TEST_DATABASE_URL;

const app = require('../../src/app');
const prisma = require('../../src/lib/prisma');
const AuthService = require('../../src/services/auth.service');

describe('POST /api/auth/login', () => {
  beforeAll(async () => {
    await prisma.admin.deleteMany();
    const passwordHash = await AuthService.hashPassword('test-password-123');
    await prisma.admin.create({
      data: { email: 'admin@test.com', passwordHash },
    });
  });

  afterAll(async () => {
    await prisma.admin.deleteMany();
    await prisma.$disconnect();
  });

  it('returns 200 and a token for valid credentials', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'admin@test.com', motDePasse: 'test-password-123' });

    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('token');
  });

  it('returns 401 for a wrong password', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'admin@test.com', motDePasse: 'wrong-password' });

    expect(res.status).toBe(401);
  });

  it('returns 401 for an unknown email', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'nobody@test.com', motDePasse: 'whatever' });

    expect(res.status).toBe(401);
  });

  it('returns 400 when motDePasse is missing', async () => {
    const res = await request(app).post('/api/auth/login').send({ email: 'admin@test.com' });

    expect(res.status).toBe(400);
  });
});

describe('requireAdmin middleware (via a protected test route)', () => {
  it('rejects requests with no Authorization header', async () => {
    const res = await request(app).get('/api/health/protected-check');
    expect(res.status).toBe(401);
  });

  it('accepts requests with a valid token', async () => {
    const loginRes = await request(app)
      .post('/api/auth/login')
      .send({ email: 'admin@test.com', motDePasse: 'test-password-123' });
    const { token } = loginRes.body;

    const res = await request(app)
      .get('/api/health/protected-check')
      .set('Authorization', `Bearer ${token}`);

    expect(res.status).toBe(200);
  });
});
```

> Note: `beforeAll` re-creates the one admin fixture the first `describe` block needs; the second
> block's `it('accepts...')` logs in again against that same fixture, so test order within this
> file must stay as written (both blocks share the DB state seeded in the first `beforeAll`).

- [ ] **Step 4: Run tests to verify they fail**

Run (from `backend/`): `npm test`
Expected: FAIL — `Cannot find module '../../src/routes/auth.routes'` and `404` on
`/api/health/protected-check` (route doesn't exist yet).

- [ ] **Step 5: Create `backend/src/middleware/requireAdmin.js`**

```javascript
const AuthService = require('../services/auth.service');

function requireAdmin(req, res, next) {
  const header = req.headers.authorization || '';
  const [scheme, token] = header.split(' ');

  if (scheme !== 'Bearer' || !token) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    req.admin = AuthService.verifyToken(token);
    return next();
  } catch (err) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
}

module.exports = requireAdmin;
```

- [ ] **Step 6: Create `backend/src/controllers/auth.controller.js`**

```javascript
const AuthService = require('../services/auth.service');

async function login(req, res) {
  const { email, motDePasse } = req.body;

  if (!email || !motDePasse) {
    return res.status(400).json({ error: 'email et motDePasse sont requis' });
  }

  try {
    const { token } = await AuthService.login(email, motDePasse);
    return res.status(200).json({ token });
  } catch (err) {
    if (err instanceof AuthService.InvalidCredentialsError) {
      return res.status(401).json({ error: 'Identifiants invalides' });
    }
    throw err;
  }
}

module.exports = { login };
```

- [ ] **Step 7: Create `backend/src/routes/auth.routes.js`**

```javascript
const express = require('express');
const authController = require('../controllers/auth.controller');

const router = express.Router();

router.post('/login', authController.login);

module.exports = router;
```

- [ ] **Step 8: Mount the router and a protected test route in `backend/src/app.js`**

```javascript
const express = require('express');
const cors = require('cors');
const authRoutes = require('./routes/auth.routes');
const requireAdmin = require('./middleware/requireAdmin');

const app = express();

app.use(cors());
app.use(express.json());

app.get('/api/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// Exercises requireAdmin end-to-end; also useful during S5+ manual testing.
app.get('/api/health/protected-check', requireAdmin, (req, res) => {
  res.status(200).json({ status: 'ok', admin: req.admin.email });
});

app.use('/api/auth', authRoutes);

module.exports = app;
```

- [ ] **Step 9: Run tests to verify they pass**

Run (from `backend/`): `npm test`
Expected: PASS (all tests across all three test files green)

- [ ] **Step 10: Commit**

```bash
git add backend/src backend/tests backend/.env.example
git commit -m "feat: add POST /api/auth/login route and requireAdmin middleware"
```

---

### Task 6: Admin seed script

**Files:**
- Create: `backend/prisma/seed.js`
- Modify: `backend/package.json` (add `"seed"` script and `prisma.seed` config)

**Interfaces:**
- Consumes: `AuthService.hashPassword` (Task 4), `prisma` (Task 3), `SEED_ADMIN_EMAIL` /
  `SEED_ADMIN_PASSWORD` env vars (Task 3's `.env.example`).
- Produces: one `Admin` row in the dev database, usable to log in from the frontend in Task 7.

- [ ] **Step 1: Create `backend/prisma/seed.js`**

```javascript
require('dotenv').config();
const prisma = require('../src/lib/prisma');
const AuthService = require('../src/services/auth.service');

async function main() {
  const email = process.env.SEED_ADMIN_EMAIL;
  const password = process.env.SEED_ADMIN_PASSWORD;

  if (!email || !password) {
    throw new Error('SEED_ADMIN_EMAIL and SEED_ADMIN_PASSWORD must be set in .env');
  }

  const existing = await prisma.admin.findUnique({ where: { email } });
  if (existing) {
    console.log(`Admin ${email} already exists, skipping.`);
    return;
  }

  const passwordHash = await AuthService.hashPassword(password);
  await prisma.admin.create({ data: { email, passwordHash } });
  console.log(`Created admin account for ${email}.`);
}

main()
  .catch((err) => {
    console.error(err);
    process.exitCode = 1;
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
```

- [ ] **Step 2: Add the `seed` script to `backend/package.json`**

```json
{
  "scripts": {
    "seed": "node prisma/seed.js"
  }
}
```

- [ ] **Step 3: Run the seed script against the dev database**

Run (from `backend/`): `npm run seed`
Expected: `Created admin account for <SEED_ADMIN_EMAIL>.`

- [ ] **Step 4: Verify manually with curl**

Run: `curl -X POST http://localhost:3000/api/auth/login -H "Content-Type: application/json" -d "{\"email\":\"<SEED_ADMIN_EMAIL>\",\"motDePasse\":\"<SEED_ADMIN_PASSWORD>\"}"`
(start the server first in another terminal: `npm run dev`, from `backend/`)
Expected: JSON response with a `token` field.

- [ ] **Step 5: Commit**

```bash
git add backend/prisma/seed.js backend/package.json
git commit -m "feat: add admin account seed script"
```

---

### Task 7: Frontend Vite/React skeleton with admin login page

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/.env.example`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/App.jsx`
- Create: `frontend/src/context/AuthContext.jsx`
- Create: `frontend/src/api/auth.js`
- Create: `frontend/src/pages/admin/PageLoginAdmin.jsx`

**Interfaces:**
- Consumes: backend `POST /api/auth/login` (Task 5), read from `import.meta.env.VITE_API_URL`.
- Produces: `AuthContext` exposing `{ token, isAuthenticated, login(email, password), logout() }`
  — S5's `DashboardAdmin` and protected admin routes will wrap themselves in this context and read
  `isAuthenticated` / call `logout()`.

- [ ] **Step 1: Scaffold the Vite React app**

```bash
cd frontend
npm create vite@latest . -- --template react
npm install
```

- [ ] **Step 2: Create `frontend/.env.example`**

```
VITE_API_URL=http://localhost:3000/api
```

Copy it: `cp .env.example .env`

- [ ] **Step 3: Create `frontend/src/api/auth.js`**

```javascript
const API_URL = import.meta.env.VITE_API_URL;

export async function loginRequest(email, motDePasse) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, motDePasse }),
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.error || 'Échec de la connexion');
  }

  return data.token;
}
```

- [ ] **Step 4: Create `frontend/src/context/AuthContext.jsx`**

```jsx
import { createContext, useContext, useState, useCallback } from 'react';
import { loginRequest } from '../api/auth';

const AuthContext = createContext(null);
const STORAGE_KEY = 'maison_guillard_admin_token';

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(STORAGE_KEY));

  const login = useCallback(async (email, password) => {
    const newToken = await loginRequest(email, password);
    localStorage.setItem(STORAGE_KEY, newToken);
    setToken(newToken);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setToken(null);
  }, []);

  const value = {
    token,
    isAuthenticated: Boolean(token),
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}
```

- [ ] **Step 5: Create `frontend/src/pages/admin/PageLoginAdmin.jsx`**

```jsx
import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';

export function PageLoginAdmin() {
  const { login, isAuthenticated, logout } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isAuthenticated) {
    return (
      <div>
        <p>Connecté en tant qu'administrateur.</p>
        <button onClick={logout}>Se déconnecter</button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>Connexion administrateur</h1>
      <label>
        Email
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </label>
      <label>
        Mot de passe
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </label>
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Connexion...' : 'Se connecter'}
      </button>
    </form>
  );
}
```

- [ ] **Step 6: Wire it up in `frontend/src/App.jsx`**

```jsx
import { AuthProvider } from './context/AuthContext';
import { PageLoginAdmin } from './pages/admin/PageLoginAdmin';

export default function App() {
  return (
    <AuthProvider>
      <PageLoginAdmin />
    </AuthProvider>
  );
}
```

- [ ] **Step 7: Manual verification**

With the backend running (`npm run dev` in `backend/`, Postgres up, admin seeded from Task 6),
run (from `frontend/`): `npm run dev`, open the printed local URL, submit the login form with the
seeded admin's email/password.
Expected: form replaced by "Connecté en tant qu'administrateur." with a working "Se déconnecter"
button. Submitting wrong credentials shows the error message inline instead.

- [ ] **Step 8: Commit**

```bash
git add frontend
git commit -m "feat: add vite react skeleton with admin login page and auth context"
```

---

### Task 8: Wire remaining docs and merge to `dev`

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: nothing new.
- Produces: nothing consumed by later tasks — this is the wrap-up task for S4.

- [ ] **Step 1: Update root `README.md` with the actual commands verified in Tasks 1-7**

```markdown
# Maison Guillard

Web app for presenting and selling handmade furniture. See
`docs/superpowers/specs/2026-09-14-maison-guillard-mvp-design.md` for the design and
`docs/superpowers/plans/` for implementation plans.

## Local dev setup

1. `docker compose up -d` — starts Postgres on `localhost:5432`.
2. Backend:
   ```
   cd backend
   cp .env.example .env   # then edit JWT_SECRET, SEED_ADMIN_EMAIL, SEED_ADMIN_PASSWORD
   npm install
   npx prisma migrate dev
   npm run seed
   npm run dev             # API on http://localhost:3000
   ```
3. Frontend:
   ```
   cd frontend
   cp .env.example .env
   npm install
   npm run dev              # opens on http://localhost:5173 (or similar)
   ```

## Tests

`cd backend && npm test` — unit tests (mocked Prisma) + integration tests (real Postgres test
database, see `TEST_DATABASE_URL` in `backend/.env`).
```

- [ ] **Step 2: Run the full backend test suite one last time**

Run (from `backend/`): `npm test`
Expected: PASS, all tests.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: finalize S4 local dev setup instructions"
```

- [ ] **Step 4: Merge into `dev`**

```bash
git checkout -b dev 2>/dev/null || git checkout dev
git merge --no-ff feature/s4-init -m "merge: S4 project init and admin auth"
git checkout main
```

Leave the merge to `main` for the weekly checkpoint per the doc technique's SCM strategy (`dev` →
`main` only at week's end / milestones, never a direct commit) — do not merge `dev` into `main` as
part of this task.
