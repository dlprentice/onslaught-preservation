# Where the retail game depends on real time

Status: active — controlled runtime observations of replay determinism
Date: 2026-11-06
Last updated: 2026-11-06 (first version)
Summary: the places where the retail executable lets real time, or the PC's state, change what it does, measured by
replaying recorded input under a fixed-step clock, with what removes each one. With all of them removed, the original
repeats itself exactly, with sound and movies on and at 30, 60 and 144 steps a second.
Evidence: MEASURED — replays of recorded input in the specimen below, compared run against run; INFERRED — how
particle emission turns small time differences into different random draws; UNKNOWN — other graphics hardware,
drivers and Windows versions.
Specimen: `BEA.exe`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` (Steam retail).

## Setup

Every observation here comes from the unmodified game code. A proxy DLL, loaded in place of the game's `zlib.dll`,
installs a test harness; none of its rebuilt functions were active for these runs. The harness is public:
[battle-engine-aquila-rebuild, `src/bea/platform/test_harness.cpp`](https://github.com/deten/battle-engine-aquila-rebuild/blob/54154fcb6d14d07bca58dc194d508f799a7c4b01/src/bea/platform/test_harness.cpp),
and the switch names below are its environment variables.

- **Fixed-step clock** (`BEA_FIXEDSTEP`): the game's `QueryPerformanceCounter` and `timeGetTime` imports return the
  number of presented frames times a fixed step (1/60 s unless stated), plus a tiny step per read so that a wait loop
  inside one frame still ends.
- **Recorded input:** a person's play is recorded as window messages by frame and DirectInput mouse states by read,
  and replayed into the same windowed game (640x480 back buffer, `-forcewindowed -skipfmv -nosound` unless stated).
- **What is compared:** the outcome and the game clock it happened at (the event manager's time), and every 10 frames
  the player Battle Engine's position and the main thread's C runtime random state.

The run logs are the contributor's own and are not published.

## What follows real time, and what removes it

| What depends on real time | Where | Observed with it | What removes it | Observed without it |
| --- | --- | --- | --- | --- |
| Background streaming jobs | `CWaitingThread::StartAsync` (0x528d50) hands a job to the worker `CWaitingThread::ThreadProc` (0x528b60) and the main thread carries on; when the result lands depends on real time | A recording of level 521 won at 247 s and its replay died at 231 s; replays also changed with the machine's load | `BEA_SYNCJOBS`: the main thread waits until the job is done | Recordings replay exactly; recordings made this way are the basis of every other row |
| Sound | Mission scripts wait for a voice line to end, and streams refill, through DirectSound buffer status and play position, which run on the sound card's clock | With sound on, level 211 ended between 190 and 198 s from run to run | `BEA_SOUNDCLOCK`: each secondary buffer's play position and playing state are computed from game time (its size, byte rate, Play, Stop, SetCurrentPosition, SetFrequency); the sound is still heard | Level 211 ended at 174.8 s in four runs out of four; other levels repeated exactly |
| Movies | `CDXFrontEndVideo::NextFrame` (0x541d30) asks Bink's `BinkWait` whether the next frame is due, and Bink answers from real time; `CDXFrontEndVideo::Open` (0x5412e0) opens the file on the streaming worker | The front end's background video stood at a different frame in every run | `BEA_VIDEOCLOCK`: frame *k* of a video is due *k* / frame rate after its first `BinkWait`; the start-up movies, which play outside the frame loop, get their next frame when asked three times at one game time. With `BEA_SYNCJOBS` | Two runs of the original matched every screenshot in 42 of 47 menu tours; three of the other runs were cut short by a lost display, and two differed (see open questions) |
| Clock reads from several threads | The game's sound and streaming threads read the same clock as the main thread | With one count of clock reads for the whole process, a career session recorded at normal speed parted from its fast replay at play frame 890: the random state first, the Battle Engine's position from frame 7,060. The draws there come from the particle code (`CParticleManager::AllocateParticle`, 0x4cb5c0, called from `CPDEmitter`, `CPDSimpleSprite` and `CPDTrail` methods), 400 to 500 draws in a burst every third frame | `BEA_FPSCLOCK`: each thread's reads are counted separately | A new career session recorded this way replayed exactly in two runs, all 1,103 checkpoints (11,020 play frames) |
| The active keyboard layout | The Controller Options page names keys through Windows, in the active layout | With a Norwegian layout active, Space showed as "MELLOMROM" and two menu tours' screenshots differed from their references | The US English layout loaded for the game process only | The tours matched again |

### Notes on the clock rows

- **The frame-rate meter is a reader, not a leak, under a fixed clock.** `CFrameTimer::Frame` (0x423720) measures
  the frame rate from `QueryPerformanceCounter`, and `CPCPlatform::GetFPS` (0x515950) returns it to
  `CGame::DrawGameStuff` (0x4714c0), `CMessageBox::RenderBattleLinePulse` (0x4b82b0), `CMessageLog::Render` (0x4b93f0)
  and `CLevelBriefingLog::Render` (0x48f620) (static call sites). In normal play it follows the machine's real frame
  rate. Under the fixed clock it can only differ through the per-read step. Pinning it to 30, 60 or 120 frames a second
  left the career-session parting at frame 890 unchanged, so it is not the cause of that parting.
- **The parting needed real-time play.** The same session replayed twice at full speed matches itself; it only parts
  from the person's playthrough, which ran at normal speed while the other threads read the clock many more times per
  frame.

## A measurement pitfall

Reading the win/lose state from another thread, even every millisecond, reads it late: a replay at full speed runs
thousands of frames a second. Two runs of level 600 with no input, at a 1/30 s step, had identical positions and random states
throughout, yet their outcome times differed by up to 0.55 s. Taking the frame and clock of the state change on the
game thread, at `Present`, gives the same time in every run (64.2 s, four runs out of four).

With the rows above removed and the outcome taken at its frame, 12 levels, AI-only and recorded, ended at the same
game time in the original and in the contributor's rebuild at 1/30 and 1/144 s steps. By this repository's evidence
rules that agreement supports, but does not prove, that the original repeats itself at those steps; level 600 is the one
measured on the original alone.

## Open questions

- **Which particle systems turn time into a different count, and is it the same effect as their count following the
  camera?** The cheapest check: count `CParticleManager::AllocateParticle` calls per frame in two replays of one
  session, one with a shared and one with per-thread read counts, and find the first frame and emitter that differ.
- **Two menu tours with movies on differed between two runs of the original:** `fe_video_fsaa` at one frame, and the
  whole-session tour `sess_win`. The first may be multisampling edge noise at polygon edges, which already varies by up
  to 90 pixels between runs; the second was recorded before per-thread read counts and may be the clock-read row.
- **Other hardware.** Every observation here is from one PC: Windows 11 and an NVIDIA RTX 5080.
