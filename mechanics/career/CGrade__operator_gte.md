# CGrade__operator_gte

Status: active function note
Last updated: 2026-10-22 (research-campaign records removed)
Summary: `CGrade::operator >=` at `0x00420ac0`: S beats every grade, otherwise letters compare alphabetically.

> Address: `0x00420ac0`
>
> Source: `references/Onslaught/Career.h` line 35 (`CGrade::operator >=`)

## Status
- **Verified vs Source:** Yes

## Signature

A member function on the left-hand grade that takes the right-hand grade letter as a `char` and returns a boolean.

## Behavior (source-parity)
Equivalent to Stuart's inline operator:
```cpp
if (grade == 'S') return TRUE;
if (right.grade == 'S') return FALSE;
return grade <= right.grade;
```

Interpretation:
- Treats `S` as strictly highest.
- Otherwise grade letters are compared lexicographically (`A` better than `B`, etc.).
- Used as "left grade is at least as good as right grade."

## Notes
- Called many times inside `CCareer__UpdateGoodieStates` to evaluate grade-gated goodies.

## Related
- CGrade__ctor_char (in the decompilation notes, not yet published)
- [CCareer__UpdateGoodieStates](../../saves/by-function/CCareer__UpdateGoodieStates.md)
