# World contracts

Status: active — folder index
Last updated: 2026-10-22
Summary: Per-function contracts for the event scheduler and the monitor deletion list.

## Documents

| Document | Summary |
| --- | --- |
| [CEventManager__AddEvent_AtTime](CEventManager__AddEvent_AtTime__0044b370.md) | specimen-bound static scheduler contract plus two retained Level-100 runtime queue envelopes. Two gap-free calls with distinct caller/payload identities inse… |
| [CMonitor__AddDeletionEvent](CMonitor__AddDeletionEvent__00401040.md) | `CMonitor__AddDeletionEvent` at `0x00401040` lazily creates the monitor's deletion set and adds a reader cell at its head; two recordings show the lazy-alloc… |
