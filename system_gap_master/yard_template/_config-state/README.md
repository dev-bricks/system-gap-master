# Configuration-state showroom

Copy `examples/config-state.providers.example.json` to a host-local private
path outside this synced directory, replace the placeholder paths and keys
with an explicit allowlist, and keep `DEVIATIONS.md` under review. The snapshot
script never walks a provider directory: it reads only the configured files
and keys.

From the repository root, run this on each machine using its own slot name:

```text
python scripts/config_snapshot.py all \
  --state-dir /path/to/SYNC/_config-state \
  --config /path/to/private/system-gap-master/providers.json \
  --slot YOUR-HOST
```

Generated snapshots and `CONFIG-STATE.md` are disposable derived state. Keep
the rationale here, but keep the provider table, credentials, and live database
files outside the yard. The script rejects a provider table inside (or
redirected into) `--state-dir`.
