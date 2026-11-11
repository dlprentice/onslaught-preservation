# MSL Mission Scripting Language

Status: active — the `.msl` language reference: syntax conventions and corpus observations, not runtime proof
Last updated: 2026-11-11 (callback timing and PostEvent timing point to the runtime page; earlier: 2026-11-06 corpus checks, unchecked text labelled)
Summary: the `.msl` mission language's conventions, command families and examples, with corpus observations labelled as such.

**Battle Engine Aquila** uses a custom `.msl` mission language for objectives,
AI, events, messages, cutscenes, and level outcomes. The maintainer's local
reference corpus, which holds hundreds of loose scripts, is not published and
cannot be checked from this repository. Per-level details are in
[level-inventory.md](../level-inventory.md) and the public tables; this document
keeps the reusable language conventions and examples.

The retail binary contains the MissionScript/IScript interpreter and command
registry described by the
[static contract](missionscript-iscript-static-contract.md).
That static evidence does not yet prove whether retail selects loose or packed
scripts, nor the visible or gameplay effect of a command. The project has no
active MSL compiler, interpreter, or proven live loose-script override.

## File Structure

Most MSL scripts follow a common structure, but blocks like `vars` and some `#include`s are optional and vary by level:

```msl
// Script comments use C-style double-slash

// ******************************************************************************
// Debug directives (commented out in release)
// debug show_asm ;
// debug show_tab ;
// debug do_trace ;
// debug show_tree ;

// ******************************************************************************
// Header files
#include data\MissionScripts\onsldef.msl      // Master definitions
#include data\MissionScripts\text\text.stf    // Global text strings (optional)
#include data\MissionScripts\Level100\text.stf // Level-specific text (optional)

// ******************************************************************************
// Variables
vars
    thing   player;
    int     count = 0;
    float   health;
    bool    completed = FALSE;
    position pos1;
end_vars

// Function definitions follow...
```

## Data Types

| Type | Description | Example |
|------|-------------|---------|
| `int` | Integer | `int count = 0;` |
| `float` | Floating point | `float health = 100.0;` |
| `bool` | Boolean | `bool active = TRUE;` / `FALSE` |
| `thing` | Game object reference | `thing player;` |
| `position` | 3D coordinate | `position pos1;` |

**Notes:**
- Variables can be declared in a `vars` / `end_vars` block (most scripts have one; some omit it, and the level scripts of levels 010 and 020 declare theirs in an `attributes` block, see [level-inventory.md](../level-inventory.md))
- Variables can have default values
- `thing` is a reference type pointing to game objects

## Special Functions (Lifecycle Callbacks)

The corpus defines these callbacks by name. When the engine raises each one, and what raises it, is read from the decompilation in [mission script runtime](script-runtime-events-and-waits.md#the-built-in-events) (static evidence; no capture of the call times). The comments below give the intended use, not a measured call time:

```msl
init()
{
    // Called when the script is first loaded
    // Use for setup, initial objectives, component assignment
}

started_dying()
{
    // Called when the attached entity begins its death sequence
    PostEvent("Engine Died");
}

died()
{
    // Called when the attached entity is fully destroyed
}

hit(otherThing)
{
    // Called when colliding with another game object
    if(otherThing.IsA(THING_TYPE_BATTLE_ENGINE))
    {
        // Player touched this object
    }
}
```

## Event System

Events are the core mechanism for mission scripting. They can be triggered by the game engine or posted from other scripts.

### Defining Event Handlers

```msl
event("Event Name")
{
    // Code executed when this event fires
}
```

### Posting Events

```msl
PostEvent("Event Name");  // Schedule the event for the next frame (see the runtime page)
```

### Reserved/Built-in Events

| Event | Trigger |
|-------|---------|
| `"game playing"` | Posted when the opening pan ends and the game enters its playing state (see [level 100 construction order](../level100-construction-order.md)) |
| `"Reached [Zone Name]"` | Named in two level 100 scripts in the corpus; what posts it is not runtime-verified |

### Example Event Chain

```msl
event("game playing")
{
    PostEvent("Start Timer");
}

event("Start Timer")
{
    while(timer > 0)
    {
        timer = timer - 1;
        Pause(1);
    }
    PostEvent("Timer Complete");
}
```

## Control Structures

### Conditionals

```msl
if (condition)
{
    // code
}
else if (condition2)
{
    // code
}
else
{
    // code
}
```

### Switch Statement

```msl
switch(variable)
{
    case 0:
    {
        // code
    }
    case 1:
    {
        // code
    }
}
```

### Loops

```msl
// While loop
while(condition)
{
    // code
}

// Infinite loop pattern
while(1 == 1)
{
    // code
    Pause(0.05);  // Always pause to avoid freezing
}

// For loop
for(n = 1; n <= 23; n = n + 1)
{
    // code
}
```

### Special Control: `do_once`

Executes contained code only once, even if the surrounding block runs multiple times:

```msl
while(1 == 1)
{
    if(health <= 5.0)
    {
        do_once
        {
            PostEvent("Critical Health Warning");
        }
    }
    Pause(0.1);
}
```

## Core Functions Reference

### Mission Outcome Functions

```msl
LevelWon();                                    // Player wins the mission
LevelLostString(TEXT_CONSTANT);               // Player loses with message

// Objective tracking
PrimaryObjectiveFailed(number, TEXT_CONSTANT);
PrimaryObjectiveComplete(number, TEXT_CONSTANT);
SecondaryObjectiveFailed(number, TEXT_CONSTANT);
SecondaryObjectiveComplete(number, TEXT_CONSTANT);
```

### Object Reference Functions

```msl
player = GetPlayer(1);                         // Get player 1's Battle Engine
thing = GetThingRef("Object Name");            // Get object by level editor name
component = GetComponent(index);               // Get component by index (for complex objects)
```

### Player/Entity Control

```msl
// Activation
player.Activate();
player.Deactivate();       // Freezes player, used during tutorials/cutscenes
player.Shutdown();         // Remove from game entirely

// Weapons
player.EnableWeapon("Mech Twin Vulcan Cannon");
player.DisableWeapon("Pulse Cannon Pod");
player.EnableFlightMode();
player.DisableFlightMode();

// Health/State
health = player.GetHealth();
player.SetHealth(value);
player.SetVulnerable(TRUE);   // Can take damage
player.SetVulnerable(FALSE);  // Invincible

// Objectives
thing.SetObjective();      // Mark as objective (shows on HUD)
thing.UnsetObjective();

// AI
SetAIState(AI_OFF);        // Disable AI
SetAIState(AI_ON);         // Enable AI
SetAIState(AI_NORMAL);     // Normal behavior
SetAIState(AI_DEFENSIVE);  // Defensive stance
```

### Spawning

```msl
// Spawn from a spawner
thing.SpawnThing("Unit Type", "Spawner Name", count, "New Object Name");

// Example
GetThingRef("Airfield").SpawnThing("Air Trainer", "SpawnerB", 1, "AirTrainer");
```

### Distance and Position

```msl
dist = thing1.GetDistToObj(thing2);            // Distance between objects
pos = CreatePosition(x, y, z);                 // Create 3D position
thing.Teleport(position);                      // Move to position
thing.TeleportOrientation(yaw, pitch, roll);   // Set rotation
```

### Movement and Pathfinding

```msl
FollowWaypointWait("Waypoint Path Name");      // Follow path, wait until complete
Attack(target);                                // Attack a target
```

### Messages and Dialog

```msl
// Play character dialog (non-blocking)
PlayCharMessage(P_TATIANA, MESSAGE_CONSTANT, delay);

// Play and wait for completion
PlayCharMessageWait(P_TATIANA, MESSAGE_CONSTANT, delay);

// Priority versions: PlayPCharMessage takes a script-supplied numeric argument; whether it sets priority or interrupts is not established (see the command registry)
PlayPCharMessage(P_KRAMER, MESSAGE_CONSTANT, delay, priority);
PlayPCharMessageWait(P_KRAMER, MESSAGE_CONSTANT, delay, priority);

// Help messages (tutorial prompts)
AddHelpMessage(HELP_FIRE);
AddHelpMessage(HELP_TRANSFORM);
```

**Character Constants (P_*):**

| Constant | Character |
|----------|-----------|
| `P_TATIANA` | Tatiana (mission control) |
| `P_KRAMER` | Commander Kramer |
| `P_RADAR` | Radar operator |
| `P_TECHNICIAN` | Technician |
| `P_COMMANDER` | Generic commander |
| `P_TROOPER` | Infantry trooper |
| `P_FORSETI_PILOT` | Forseti pilot |
| `P_SURT` | Surt (enemy) |
| `P_CARVER` | Carver |
| `P_SIMMONS` | Simmons |

### HUD Control

```msl
HighlightHudPart(HUD_COMPASS);    // Flash HUD element
UnHighlightHudPart(HUD_COMPASS);  // Stop flashing

// HUD part constants
// HUD_HEALTH_BAR, HUD_ENERGY_BAR, HUD_COMPASS
// HUD_BATTLE_LINE_MAP, HUD_RADAR, HUD_CURRENT_WEAPON
```

### Variables and UI Display

```msl
// Initialize a display variable
InitVariable(TEXT_CONSTANT, VARIABLE_TYPE);

// Update displayed value
SetVariable(TEXT_CONSTANT, value, threshold);

// Remove from display
ShutdownVariable(TEXT_CONSTANT);

// Variable types:
// VARIABLE_NUMBER                  - Simple number
// VARIABLE_NUMBER_AND_THRESHOLD   - Number with target/threshold
// VARIABLE_TIMER                   - Countdown timer
// VARIABLE_PERCENTAGE              - Percentage
// VARIABLE_PERCENTAGE_AND_THRESHOLD - Percentage with threshold (levels 621 and 622 use it)
// VARIABLE_TIME                    - Elapsed time display
```

The exact current registry places `HighlightHudPart`, `UnHighlightHudPart`,
`InitVariable`, `SetVariable`, and `ShutdownVariable` at rows 34, 35, 76, 77,
and 78; see the
`144-entry native registry` (archived research record, not published).
Those bindings and these authored examples do not by themselves prove visible
HUD output or rebuild parity.

### Timing

```msl
Pause(seconds);           // Wait for duration (float)
GameTime();               // Get elapsed game time in seconds
```

### Animation

```msl
PlayAnimation("animation_name", looped, wait);
PlayAnimationWait("animation_name", looped, wait);  // Block until complete
```

### Score and Career

```msl
AddScore(points);         // Add to mission score (can be negative)

// Tech slots (persistent career flags)
GetSlot(SLOT_CONSTANT)          // Returns TRUE/FALSE
SetSlot(SLOT_CONSTANT, TRUE);   // Set for current session only
SetSlotSave(SLOT_CONSTANT, TRUE); // Set and persist to save file

// Goodies (unlockables)
state = GetGoodieState(goodie_id);
SetGoodieState(goodie_id, GOODIE_NEW);

// Goodie states: GOODIE_UNKNOWN, GOODIE_INSTRUCTIONS, GOODIE_NEW, GOODIE_OLD
```

### Unit Counting and Battle Line

```msl
count = GetNumUnits(BEHAVIOUR_TYPE, ALLEGIANCE);
ratio = GetRatioBattleLineNodes(ALLEGIANCE);

// Behaviour types: GROUND_UNIT_BEHAVIOUR, FIGHTER_UNIT_BEHAVIOUR,
//                  BOMBER_UNIT_BEHAVIOUR, MECH_UNIT_BEHAVIOUR, etc.

// Allegiances: FRIENDLY_ALLIGENCE, ENEMY_ALLIGENCE, NEUTRAL_ALLEGIANCE
// Note: "ALLIGENCE" is a typo preserved from the original code
```

### Random Numbers

```msl
random = GetFloatRand();      // Returns 0.0 to 1.0
message = Rand(3);            // Returns 0, 1, or 2
```

### Type Checking

```msl
if(otherThing.IsA(THING_TYPE_BATTLE_ENGINE))
{
    // It's the player's mech
}

if(Exists(thing))
{
    // Object exists and hasn't been destroyed
}
```

### Special Functions

```msl
// Submarines
thing.Dive();          // Submerge
thing.Surface();       // Surface

// Script assignment
thing.SetScript("ScriptName");        // Assign behavior script
thing.SetSpawnScript("ScriptName");   // Set script for spawned units

// Debug
Print(variable);       // Output to debug console
Print("message");      // Output string

// Allegiance
SetAllegiance(ENEMY_ALLIGENCE);
SetAllegiance(FRIENDLY_ALLIGENCE);
```

Bare calls such as `Dive()` and `GetHealth()` appear in entity scripts in the corpus (for example the submarine and Fenrir scripts), where they refer to the script's own entity; `thing.Dive()` names its receiver. This is a corpus pattern, not a runtime-verified rule.

### Camera Control

```msl
Goto3PointPanCamera(target, pos1, pos2, pos3, duration);
SpawnEscapePod();      // Spawn player escape pod (for death cutscenes)
```

## Master Definitions (onsldef.msl)

The `onsldef.msl` file contains all shared constants:

### AI States

```msl
#define AI_ON           0
#define AI_OFF          1
#define AI_NORMAL       2
#define AI_DEFENSIVE    3
#define AI_ONF          4
```

### Thing Types (for IsA checks)

```msl
#define THING_TYPE_NONE             0
#define THING_TYPE_THING            1
#define THING_TYPE_ACTOR            2
#define THING_TYPE_AMMUNITION       4
#define THING_TYPE_BATTLE_ENGINE    8      // Player's mech
#define THING_TYPE_UNIT             16
#define THING_TYPE_STATIONARY       32
#define THING_TYPE_ANIMAL           64
#define THING_TYPE_MESH_COLLISION   128
#define THING_TYPE_BUILDING         256
#define THING_TYPE_GROUND_UNIT      512
#define THING_TYPE_AIR_UNIT         1024
#define THING_TYPE_MECH             2049
#define THING_TYPE_TANK             4096
#define THING_TYPE_NAMED_MESH       8192
#define THING_TYPE_INFANTRY         16384
#define THING_TYPE_NAVAL            32768
#define THING_TYPE_CUTSCENE         65536
#define THING_TYPE_VEHICLE          131072
#define THING_TYPE_EMPLACEMENT      262144
#define THING_TYPE_COMPONENT        524288
#define THING_TYPE_CAN_BE_WALKED_ON 1048576
#define THING_TYPE_CAN_DESTROY_TREES 2097152
```

### Behavior Types

```msl
#define MECH_UNIT_BEHAVIOUR                     0
#define NULL_BEHAVIOUR                          1
#define GROUND_UNIT_BEHAVIOUR                   2
#define INFANTRY_UNIT_BEHAVIOUR                 3
#define TURRET_UNIT_BEHAVIOUR                   4
#define BOAT_UNIT_BEHAVIOUR                     5
#define CARRIER_UNIT_BEHAVIOUR                  6
#define BUILDING_UNIT_BEHAVIOUR                 7
#define FIGHTER_UNIT_BEHAVIOUR                  8
#define BOMBER_UNIT_BEHAVIOUR                   9
#define GROUND_ATTACK_AIRCRAFT_UNIT_BEHAVIOUR   10
#define JEEP_UNIT_BEHAVIOUR                     11
#define DROPSHIP_UNIT_BEHAVIOUR                 12
#define MINE_UNIT_BEHAVIOUR                     13
#define HIVEBOSS_UNIT_BEHAVIOUR                 14
#define SUBMARINE_UNIT_BEHAVIOUR                15
#define DIVE_BOMBER_UNIT_BEHAVIOUR              16
#define THUNDERHEAD_UNIT_BEHAVIOUR              17
#define CARVER_UNIT_BEHAVIOUR                   18
#define GILLM_UNIT_BEHAVIOUR                    19
#define SENTINEL_UNIT_BEHAVIOUR                 20
#define WWARSPITE_UNIT_BEHAVIOUR                21
#define FENRIR_UNIT_BEHAVIOUR                   22
#define WARSPITE_DOME_UNIT_BEHAVIOUR            23
#define POD_UNIT_BEHAVIOUR                      24
#define SIMPLE_BUILDING_UNIT_BEHAVIOUR          25
```

### Allegiances

```msl
#define FRIENDLY_ALLIGENCE     0    // Note: typo preserved from original
#define ENEMY_ALLIGENCE        1
#define NEUTRAL_ALLEGIANCE     2    // Spelled correctly here
```

### HUD Parts

```msl
#define HUD_HEALTH_BAR         0
#define HUD_ENERGY_BAR         1
#define HUD_COMPASS            2
#define HUD_BATTLE_LINE_MAP    3
#define HUD_RADAR              4
#define HUD_CURRENT_WEAPON     5
```

### Variable Display Types

```msl
#define VARIABLE_NUMBER                    1
#define VARIABLE_NUMBER_AND_THRESHOLD      2
#define VARIABLE_TIMER                     3
#define VARIABLE_PERCENTAGE                4
#define VARIABLE_PERCENTAGE_AND_THRESHOLD  5
#define VARIABLE_TIME                      6
```

### Goodie States

```msl
#define GOODIE_UNKNOWN       0
#define GOODIE_INSTRUCTIONS  1
#define GOODIE_NEW           2
#define GOODIE_OLD           3
```

### Tech Slots (Career Flags)

```msl
// Fenrir component destruction tracking (level 731)
#define SLOT_F_731_TURRET_1      1
#define SLOT_F_731_TURRET_2      2
// ... through SLOT_F_731_FRONTDOOR_30 (30)

// Fenrir component destruction tracking (level 732)
#define SLOT_F_732_TURRET_1      31
// ... through SLOT_F_732_FRONTDOOR_30 (60)

// Mission branching flags
#define SLOT_500_ROCKET          61   // Player chose rocket path in level 500
#define SLOT_500_SUB             62   // Player chose submarine path in level 500

// Tutorial progress flags
#define SLOT_TUTORIAL_1          63
#define SLOT_TUTORIAL_2          64
#define SLOT_TUTORIAL_3          65
#define SLOT_TUTORIAL_4          66
```

Corpus observation, not runtime-verified: in the level 731 and 732 folders, only `Fenrir.msl` calls SetSlot. Level 731's script calls `SetSlot(n, ...)` for components 1-23 (slots 1-23), and level 732's calls `SetSlot(n + 29, ...)` (slots 30-52). The level 741 and 742 `Fenrir.msl` scripts read `GetSlot(n + 29)` for components 1-23, the slots level 732 sets. The labels above number the 732 block from 31, one more than `n + 29` gives for component 1.

## Text String Files (.stf)

Text strings are defined in `.stf` files (String Table File) and referenced by constants:

```c
// Example from text.stf (auto-generated by TextConvert.cpp)
#define _100_OBJECTIVE_1    110325434
#define P_TATIANA           1508464
#define HELP_FIRE           1197607
```

Many levels have their own `text.stf` for mission-specific strings, but some levels omit it or leave it empty.

## Mission Structure Patterns

### Tutorial Mission (level100)

```msl
init()
{
    // Set up objectives as initially failed
    PrimaryObjectiveFailed(1, _100_OBJECTIVE_1);

    // Check if tutorial section was already completed
    if(GetSlot(SLOT_TUTORIAL_1) == FALSE)
    {
        player.Deactivate();           // Freeze player
        PlayCharMessageWait(...);      // Show instructions
        HighlightHudPart(HUD_COMPASS); // Flash UI element
        PlayCharMessageWait(...);
        UnHighlightHudPart(HUD_COMPASS);
    }

    player.Activate();
    SetSlotSave(SLOT_TUTORIAL_1, TRUE);  // Mark complete (persists to save)
}
```

### Branching Mission (level500)

```msl
event("game playing")
{
    // Reset branching flags
    SetSlot(61, FALSE);  // SLOT_500_ROCKET
    SetSlot(62, FALSE);  // SLOT_500_SUB

    // ... mission logic ...
}

event("Rocket Died")
{
    SetSlot(61, TRUE);   // Player destroyed rocket, unlocks rocket path
}

event("Submarine Destroyed")
{
    SetSlot(62, TRUE);   // Player destroyed sub, unlocks sub path
}
```

The shipped level 500 scripts set these flags with `SetSlot`, the session-only call described under [Score and Career](#score-and-career). The career keeps tech slots in the saved career ([career system](../../engine/source/gameplay/career-system.md)); whether a session-only flag reaches that saved copy is not checked here.

### Defense Mission (level311)

The script is in the level 311 folder, but its text constants use the 312 text IDs (`_312_...`), as [level-inventory.md](../level-inventory.md) pairs 311 with 312.

```msl
init()
{
    // Track defense objectives
    InitVariable(_312_FORSETI_BUILDING, VARIABLE_NUMBER_AND_THRESHOLD);
    SetVariable(_312_FORSETI_BUILDING, ForsetiBuilding, building_fail);
}

event("ForsetiBuildingDies")
{
    ForsetiBuilding = ForsetiBuilding - 1;
    SetVariable(_312_FORSETI_BUILDING, ForsetiBuilding, building_fail);

    if(ForsetiBuilding <= building_fail)
    {
        LevelLostString(_312_2_MANY_BUILDINGS);
    }
}
```

### Racing Mission (level901)

Simplified: the lap and win logic are not copied from the shipped script. The goodie threshold follows the shipped `LapMonitor.msl` in the level 901 folder, which sets goodie 68 for a time under 2,900 ticks (under 2,750 with a different message); see [level-inventory.md](../level-inventory.md#race-5).

```msl
init()
{
    InitVariable(_A2_LAP, VARIABLE_NUMBER);
    InitVariable(_A2_LAP_TIME, VARIABLE_TIME);
    InitVariable(_A2_BEST_LAP, VARIABLE_TIME);
}

event("Start Line")
{
    lap = lap + 1;
    SetVariable(_A2_LAP, lap, 0);

    if(lap == 4)
    {
        PostEvent("Race Complete");
    }
}

event("Race Complete")
{
    if(raceTime < 2900)
    {
        // Goodie 68 for a time under 2,900 ticks (shipped threshold)
        if(GetGoodieState(68) < GOODIE_NEW)
        {
            SetGoodieState(68, GOODIE_NEW);
        }
    }
    LevelWon();
}
```

### Boss Fight (level741/742 - Fenrir)

```msl
// Fenrir.msl - Complex multi-component boss
init()
{
    // Check which components were destroyed in previous attempts
    for(n = 1; n <= 23; n = n + 1)
    {
        if(GetSlot(n + 29) == TRUE)
        {
            GetComponent(n).Shutdown();
        }
    }

    // Assign behavior scripts to components
    component = GetComponent(1);
    component.SetScript("Turret");

    component = GetComponent(12);
    component.SetScript("PlaneLauncher");
    component.SetSpawnScript("Fighter");
}

event("game playing")
{
    SetAIState(AI_OFF);
    PostEvent("check health");
    FollowWaypointWait("fenrir");  // Boss follows path
}

event("check health")
{
    while(1 == 1)
    {
        health = GetHealth();
        if(health <= 0.0)
        {
            do_once
            {
                PostEvent("Fenrir Down");
            }
        }
        Pause(0.05);
    }
}
```

## Interesting Findings

### Debug Directives

732 of the 733 `.msl` files in the corpus contain these commented-out directives (all but `onsldef.msl`, the definitions file; a corpus count, not a runtime fact):

```msl
// debug show_asm ;    // Show compiled assembly
// debug show_tab ;    // Show symbol table
// debug do_trace ;    // Execution tracing
// debug show_tree ;   // Show parse tree
```

These suggest the MSL compiler outputs to a bytecode/ASM format.

### Typos Preserved from Original Code

- `ALLIGENCE` instead of `ALLEGIANCE` (in `FRIENDLY_ALLIGENCE`, `ENEMY_ALLIGENCE`)
- `TK_INFANTY` in kill tracking enum (missing R)
- These are preserved for compatibility with the game engine

### Player Health Monitoring Pattern

Scripts commonly monitor player health with percentage-based thresholds:

```msl
playerHelpHealth = player.GetHealth() * 0.8;    // 80% of the health when this line runs
playerAbortHealth = player.GetHealth() * 0.4;   // 40% of the health when this line runs

while(...)
{
    if(player.GetHealth() < playerAbortHealth)
    {
        do_once
        {
            PostEvent("Abort Mission");
            AddScore(-50);  // Penalty for aborting (see Negative Scores)
        }
    }
}
```

### Negative Scores as Penalties

The corpus passes negative values to AddScore. Level 100's script passes -10, -20 and -50 once each, and 50 appears in ten scripts (corpus observation, not runtime-verified). Level 100's Reached Target Zone 3 poll reads -20 as the help penalty and -50 as the abort penalty ([level 100 final drone wave](../level100-final-drone-wave.md)); the meaning of -10 and of the 50 calls is not established:

```msl
AddScore(-10);   // Level 100 Evade Failed handler; meaning not established
AddScore(-20);   // Help penalty in level 100 (see the drone wave document)
AddScore(-50);   // Abort penalty in level 100 (see the drone wave document)
AddScore(50);    // Passed in ten scripts; meaning not established
```

### Submarine Behavior

The submarine script in level 512 (`Sub.msl`) has a Northwest event that dives, teleports and surfaces. The abridged copy below is a corpus observation, not runtime-verified:

```msl
event("Northwest")
{
    Dive();
    PostEvent("Dive");
    Pause(45.0);
    Teleport(NW);
    TeleportOrientation(-127, 0, 0);
    Surface();
}
```

### Weather System (Commented Out)

Weather effects exist but are often commented out:

```msl
init()
{
//  SetRainDensity(1);
//  SetLightningDensity(0.01);
}
```

### Mission 500 Branching Logic

Level 500 (Split second) is the major branching point in the campaign:

```msl
// Player can either:
// 1. Destroy the rocket (SLOT_500_ROCKET = 61)
// 2. Destroy the submarine (SLOT_500_SUB = 62)

// These flags affect which missions are available next
SetSlot(61, TRUE);  // After destroying rocket
SetSlot(62, TRUE);  // After destroying submarine
```

Flag 62 (submarine) opens world 511 and flag 61 (rocket) opens world 512 ([career links](../../saves/career-links.md), link indices 46 and 47). The submarine's teleport script is in level 512 (see Submarine Behavior), and the level 500 folder's `Submarine.msl` sets flag 62.

### Component-Based Destruction

Complex vehicles like the Fenrir use indexed components:

```msl
// Components 1-10: Turrets
// Component 11: Main gun
// Components 12-17: Plane launchers
// Components 18-23: Bomb bays
// Components 24-27: Engines
// Components 28 and 29: back doors (BackDoor in level 741; BackDoorTop and BackDoorBot in level 742)
// Component 32: front door (FrontDoor); components 30 and 31 are not referenced in the level 741 or 742 scripts

for(n = 1; n <= 23; n = n + 1)
{
    if(GetSlot(n + 29) == TRUE)  // Check if destroyed in previous mission
    {
        GetComponent(n).Shutdown();
    }
}
```

The loop covers components 1-23 only and has no comment, so these scripts never shut down the engines (24-27) or the doors (28, 29, 32); they do not say why.

### Cutscene Camera System

The current registry places `CreatePosition`, `Goto3PointPanCamera`, and
`Goto4PointPanCamera` at rows 66, 114, and 115. The retained [VM schema](missionscript-vm-datatype-opcode-schema.v1.json) lists
the `CPositionDataType` vtable; runtime camera switching and
visible output remain separate proof.

Death/victory cutscenes use a 3-point pan camera:

```msl
event("Player Lost")
{
    SpawnEscapePod();
    // Positions relative to Fenrir (note: -z is up)
    pos1 = CreatePosition(-80.0, 20.0, -30.0);
    pos2 = CreatePosition(0.0, 40.0, 60.0);
    pos3 = CreatePosition(100.0, 20.0, 40.0);

    Goto3PointPanCamera(GetThingRef("Fenrir"), pos1, pos2, pos3, 15.0);
    Pause(8.5);
    LevelLostString(_J2_742_STILL_INSIDE);
}
```

## File Organization

Directory casing varies by level (`Level###` vs `level###`). Preserve the on-disk casing when referencing files.

```
MissionScripts/
  onsldef.msl              # Master definitions
  text/
    text.stf               # Global text strings (huge file)
  level100/                # Tutorial
    LevelScript.msl        # Main script
    text.stf               # Level text (may be empty)
    TankFactory.msl        # Entity scripts
    Hangar.msl
  level500/                # Branching mission
    Level500script.msl
    Submarine.msl
    rocketbase.msl
    text.stf
  level741/                # Fenrir fight (part 1)
    Level741script.msl
    Fenrir.msl
    Engine.msl
    Turret.msl
    cutscene.msl
    Cutscene_Won.msl
    Cutscene_Lost.msl
    hack.msl               # Door unlock trigger
  level901/                # Racing checkpoints (single player)
    LapMonitor.msl
    LapTimer.msl
    Checkpoint1.msl
    ...
```

## Summary

The MSL language is a purpose-built scripting system for Battle Engine Aquila that provides:

- Event-driven architecture with string-named events
- Full game object control (spawning, AI, health, weapons)
- Objective tracking and scoring
- HUD manipulation
- Career save integration (slots, goodies)
- Cutscene camera control
- Component-based entity systems

The language syntax is C-like but with game-specific constructs like `do_once`, `thing` references, and the `vars`/`end_vars` block. Debug features suggest it compiles to bytecode.
