# Local multiplayer evidence boundary

Status: retail local split-screen path evidenced; original-binary online play not established by this contract
Last updated: 2026-10-30 (retail multiplayer scope and CE release navigation clarified)
Summary: what supports the retail local split-screen path, and the limits of original-binary evidence for online play.

This contract describes the retail game's bounded local multiplayer path and
the limits of the original-binary evidence. It does not add netcode, patch
networking into the retail executable, or prove online play.

Onslaught CE is a separate native-source port. Its [README](https://github.com/dlprentice/onslaught-ce#readme)
describes what is currently available to players; experimental network work
alone does not establish a released online feature.

## Retail anchors

| Area | Bounded evidence |
| --- | --- |
| Runtime level gate | Source `game.cpp` and retail `0x004725d0 CGame__IsMultiplayer` agree on a current-level predicate of `850..899`. |
| Frontend selection | Source frontend routing selects multiplayer pages for `850..879`; that narrower menu range must not be generalized to every runtime-multiplayer level. |
| World mode | Retail `0x0050d7d0 CWorld__IsMultiplayerMode` accepts world mode `1` or `2`. The matching source body is absent, so this remains retail-static/call-site evidence. |
| Player count | The pinned source sets two players after a multiplayer world load and one otherwise. No retained evidence establishes active P3/P4 retail gameplay. |
| Controllers | Source startup assigns player 0 and player 1 controller ports, including a same-port fallback. Retail controller mapping remains a separate static anchor. |
| Views | Source defines two viewpoints and a two-player split-screen render path. Retail render anchors include `CGame__Render`, `CEngine__SetNumViewpoints`, and `CEngine__SetViewpoint`. |
| Outcome flow | Source contains multiplayer win, death, respawn, and player-number handoff paths; static identity alone does not prove every runtime outcome. |

Stuart's pinned source is a naming and control-flow reference, not proof of the
Steam binary. The listed retail addresses provide bounded corroboration only.

## Retired toolkit behavior

The Windowed & Mods page of the retired WinUI app could select a local split-screen launch preset for an
app-owned game copy. It used `-skipfmv -level 850` and the same required
windowed compatibility base as other copies. The installed game and
original `BEA.exe` remained read-only source material.

The preset did not expose Host, Join, invitation, matchmaking, relay, or
public-network actions, and the app said online multiplayer was
not ready. The readiness service of the retired AppCore editor (Onslaught-Career-Editor [`4ac3c9ae`](https://github.com/dlprentice/Onslaught-Career-Editor/tree/4ac3c9ae32d97c1293858c49bf9cc485eb814f28), the last commit that has it) reported source-level checks only;
passing those commands was not runtime or network proof.

Controlled copied-target observations established bounded launch, exact-process
ownership, source safety, managed stop, and selected P1/P2 input-to-state/frame
correlations. They did not establish improved control feel, a physical gamepad
path, deterministic synchronization, multi-host play, active P3/P4 gameplay,
or gameplay parity. Raw logs, frames, executable copies, and input captures stay
outside Git.

## Requirements for any online claim

An online surface remains blocked until separately reviewed evidence covers at
least:

- two real hosts with explicit process and runtime-host identity;
- session/auth/invitation and disconnect/reconnect ownership;
- bounded input delivery and host/relay authority;
- cleanup, rollback, source safety, and installed-game non-mutation;
- measured gameplay outcomes rather than metadata-only participant slots; and
- clear failure and recovery behavior in the user-facing app.

None of those requirements was satisfied by the retired WinUI app's split-screen preset,
source inspection, same-host helpers, VM-only metadata, or a rebuild that agrees
with itself.

## Claim boundary

This file records the retired WinUI app's local split-screen label and its explicit
online non-claim. It does not prove native retail netcode, LAN/public matchmaking,
more than two active retail players, control quality, exact layouts, visual
parity, or rebuild parity. Current corrected function names are those of the
decompilation notes (not yet published).
