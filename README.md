# URL Shortener — FastAPI + PostgreSQL + Redis

A production-ready URL shortener service built with **FastAPI**, **PostgreSQL**, and **Redis**, fully containerized with Docker.

---

## 1. Setup Instructions

### Prerequisites

* [Docker](https://docs.docker.com/get-docker/) installed
* [Docker Compose](https://docs.docker.com/compose/install/) installed

### Steps

```bash
# Clone the repository
git clone https://github.com/smgusain24/urlShortner.git
cd urlShortner

# Copy environment variables template
cp .env.example .env

# Start services
docker compose up --build
```

Your application will be available at: **[http://localhost:8000](http://localhost:8000)**

---

## 2. What is a URL Shortener?

A URL shortener takes a long URL and maps it to a shorter, unique code (e.g., `http://sho.rt/abc123`). This is useful for:

* Easier sharing
* Tracking link usage
* Preventing link breakage in messages

**Basic Workflow:**

1. User enters a long URL.
2. Service stores it in the database and generate a unique code (Base62 encoding of the ID).
3. When the short link is visited, user is redirected to the original URL.

---

## 3. System Design & Back-of-the-Envelope Estimates

**Assumptions:**

* 100M total short links
* Average URL length: 100 bytes
* Storage: \~10 GB for URLs + indexes
* 80% of traffic hits 20% of URLs → optimize for read performance

**Core Components:**

* **FastAPI** → API layer
* **PostgreSQL** → primary data store
* **Redis** → cache hot URLs with LRU eviction

**Performance Goals:**

* Read latency (cache hit): <5ms
* Write latency: <50ms
* Scale horizontally with more app servers

---

## 4. Scaling Strategies

* **Caching:** Redis for the most frequently accessed links. We can use Pareto's principle here. 80% of read traffic is for 20% of data.
* **Indexes:** Ensure `code` and `normalized_url` are indexed.
* **Load Balancing:** Multiple FastAPI app servers behind a load balancer.
* **Sharding:** Split URLs across multiple Postgres instances for large datasets.

---

## 5. Environment Variables

Example `.env.example`:

```
DATABASE_URL=postgresql://postgres:password@db:5432/shortner
REDIS_URL=redis://redis:6379/0
BASE_URL=http://localhost:8000
```

---

## 6. Running Queries on PostgreSQL

```bash
docker exec -it urlshortener_db psql -U postgres -d shortner
```

Use SQL here to inspect or alter your schema.
