CREATE TYPE job_status AS ENUM ('pending','done','cancelled');

CREATE TABLE jobs (
    id          UUID PRIMARY KEY,
    job_type    TEXT      NOT NULL,
    payload     JSONB     NOT NULL,
    rrule       TEXT,                 -- NULL when one-shot
    next_run_at TIMESTAMPTZ NOT NULL,
    retries     INT       NOT NULL DEFAULT 0,
    status      job_status NOT NULL DEFAULT 'pending',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX jobs_pending_idx
  ON jobs (status, next_run_at)
  WHERE status = 'pending';
