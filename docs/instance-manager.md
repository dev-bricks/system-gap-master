# Yard instance lifecycle manager

`yard-instance-manager` is the controlled deployment boundary between a local
`system-gap-master` repository clone and a live shared yard. The yard is not a
Git checkout. Generic templates are built and tested in the clone, then a
saved plan can seed or update only the paths declared in
`system_gap_master/yard_template/YARD_TEMPLATE.json`.

## Ownership model

The template manifest distinguishes four relevant ownership classes:

- `repo`: generic structure or documentation supplied by this repository;
- `instance`: locally curated yard content;
- `host` or `actor`: content written by exactly one host or access path;
- `tool`: a tool-owned lifecycle zone such as `db-transit/<namespace>`.

Files additionally use one of two modes:

- `managed`: a later template version may update the file only when its
  current hash still equals the hash recorded by the previous successful
  operation;
- `seed-once`: create the file when absent, then preserve the instance copy.

Any untracked or locally modified `managed` file blocks the plan. A matching
filename, newer timestamp or host suffix never establishes authority.
Managed files below protected or non-repository-owned directories require an
exact `managed_path_exceptions` entry in the template manifest; a broad glob
cannot silently turn host, message, archive or tool payloads into managed data.

## Read-only inspection

```bash
yard-instance-manager doctor \
  --yard-root /path/to/shared/SYNC

yard-instance-manager inventory \
  --yard-root /path/to/shared/SYNC

yard-instance-manager retention-plan \
  --yard-root /path/to/shared/SYNC \
  --legacy-host-slot laptop --legacy-host-slot workstation
```

`doctor` checks the declared structure, ownership collisions, instance-state
integrity, stale template state, link boundaries and the legacy `_transit`
marker. `inventory` classifies top-level entries without changing them.
`retention-plan` identifies old host artifacts, stale messages, old archives
and flat host slots, but every candidate has `safe_to_apply=false`: reader,
writer, references and acknowledgements must be proven separately.
Repeatable `--legacy-host-slot` values let an older instance expose pre-v1
root-level slots without hard-coding private host names into the public tool.

The legacy `_transit/<publisher>` path is never moved automatically. Its
reader and writer must be identified first, then structured payloads move to
the existing R9 `db-transit/<namespace>` adapter owned by
`sqlite-transit-sync`.

## Plan, upgrade and verify

```bash
yard-instance-manager plan \
  --yard-root /path/to/shared/SYNC \
  --output /host-local/review/yard-plan.json

# Review the JSON. Upgrade refuses a plan with blockers.
yard-instance-manager upgrade \
  --plan /host-local/review/yard-plan.json \
  --state-dir /host-local/system-gap-master-state

# A second plan must contain no create/update actions.
yard-instance-manager plan \
  --yard-root /path/to/shared/SYNC
```

The plan is SHA-256 bound to its content and to the template manifest. Apply
rechecks every source and target hash, rejects symlink, junction and reparse
boundaries, creates local backups before updates, writes an integrity-protected
host-local write-ahead operation journal before its first yard mutation, uses
atomic replacement and writes a
compact `.system-gap-instance.json` state file to the yard. Operational
manifests and backups stay in the host-local state directory outside both the
yard and the repository clone. The packaged template is the default;
`--template-root` selects an explicitly reviewed development template.

The shared state contains a random stable `instance_id`, template hashes and
relative managed paths, but no absolute local yard path. This keeps the state
portable between Windows, macOS and Linux. Its exact pre-plan hash is rebound
before apply. Mutating runs still require one externally coordinated rollout
owner for the yard; the file-sync provider is not a distributed lock service.

## Rollback

```bash
yard-instance-manager rollback \
  --operation-id <hex-operation-id> \
  --yard-root /path/to/shared/SYNC \
  --state-dir /host-local/system-gap-master-state
```

Rollback first verifies the complete operation manifest, every post-upgrade
or already-restored target, every backup and the current instance state. It
sets a journaled `rolling-back` state before mutation and advances the journal
after each record. If a process stops between a file restore and the journal
write, the same command resumes from the observed before/after hashes. Files
created by the operation are removed only when their hashes are unchanged;
updated files and POSIX modes are restored; directories are removed only when
the operation created them and they remain empty. An `applying` journal from a
crashed upgrade can be passed to the same rollback command.

## Boundaries

- The manager never runs `git` inside the yard.
- It never edits undeclared paths, host content, messages, archives or
  `db-transit` payloads.
- It does not provision a new operating system or provider rule files. That
  belongs to an installer or agent bridge; this module only aligns an existing
  multi-system yard.
- A digest detects accidental plan/state corruption; it is not a signature or
  an authorization token. Access control and release approval remain external
  gates.
