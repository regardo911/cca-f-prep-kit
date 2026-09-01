# Widget Service

## Deployment

The service deploys to Fly.io from the `main` branch. A push to `main` triggers
the `deploy` workflow, which builds the container, runs the migration check
against a throwaway Postgres, and promotes the new machine group one region at
a time — `iad` first, then `fra`, then `syd`. Each region has to report healthy
on `/healthz` for ninety seconds before the next one starts. A full rollout
takes about eleven minutes. Deploys are blocked between 16:00 and 20:00 UTC on
weekdays, which is when the European checkout traffic peaks.

## Rollback

Rollback is a redeploy of the previous image, not a revert commit. Run
`fly deploy --image <previous-sha>` against the affected region only; the other
regions keep serving. The previous three images stay in the registry for
fourteen days, so anything older than two weeks has to be rebuilt from the tag.
Database migrations are the exception: they are forward-only, so a rollback
past a migration boundary needs the compensating migration in
`migrations/down/` applied by hand first. The on-call runbook has the decision
tree for that case.
