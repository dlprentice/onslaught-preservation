# CCareer__GetGradeForWorld

Status: active function note
Last updated: 2026-10-22 (research-campaign records removed)
Summary: `GRADE` (earlier `CCareer__GetGradeForWorld`) at `0x0041c330`: the letter grade for one world.

> Address: 0x0041c330 | Source: `references/Onslaught/Career.cpp`
>
> **This function is `GRADE`** (2026-09-29: the byte-matching decompilation compiles Stuart's `GRADE` in Career.cpp to this body). Earlier analysis called it `CCareer_T3_0041c330`.
> This page keeps its old title so existing references still resolve.

## Name demotion — 2026-08-17

The 2026-08-17 anchor audit
(`name-cohort-promotion-manifest-2026-08-17.tsv` (archived research record, not published))
found no `CCareer` type descriptor anywhere in the shipped image and no vtable
owning this VA, so the descriptive name lost its structural support and was
replaced by a neutral placeholder rather than by a second invented label.

Read that for exactly what it is. The audit graded *names* against RTTI and
vtable anchors; it did not open the body and it did not look at
`references/Onslaught/Career.cpp`. What it withdraws is the claim that the
image proves this address belongs to a class called `CCareer` and to a method
called `GetGradeForWorld`. What it leaves untouched is everything below, which
rests on the source correspondence and on the byte-level reading — a different
axis of evidence that this audit did not measure. `CCareer` has never had an
RTTI anchor here.

## Status
- **Verified vs Source:** Yes (source-equivalent helper; retail ABI differs) —
  unaffected by the demotion above, which measured RTTI anchors and not source
  correspondence

## Purpose
Get letter grade (S/A/B/C/D/E) for specific level. Retrieves the mRanking value from a node and converts it to a display grade.

## Signature

Retail takes a pointer to an output grade byte and the world number, writes the grade into the
output byte and returns that pointer. Stuart's source declares the same helper as
`CGrade GRADE(int world_num)`, returning the grade by value.

## Grade Calculation
From source code (Career.cpp:1178-1195):
```cpp
if (f == 1.f) c = 'S';
else if (f <= 0.f) c = 'E';
else c = 'D' - floor(f * 4);
```

| Grade | Float Range |
|-------|-------------|
| S | 1.0 exactly |
| A | 0.75-0.99 |
| B | 0.5-0.74 |
| C | 0.25-0.49 |
| D | 0.01-0.24 |
| E | <= 0.0 |

## Notes
- Retail helper writes one grade byte into `out_grade` and returns `out_grade`
- Source-equivalent role matches `GRADE(int world_num)` (returns `CGrade` by value)
- Used by mission select screen for grade display

## Related Functions
- [CCareer__GetGradeFromRanking](CCareer__GetGradeFromRanking.md) - Core conversion logic
- CCareer__GetNodeFromWorld (in the decompilation notes, not yet published) - Gets node to read ranking from
