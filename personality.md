# Personality
Each character has a set of personality scores that inform their behavior on and off campaign.

*Personality scores (0.01-1.0):*
  - Primary scores:
    - Sociable: Tendency to communicate with others and attempt to maintain relationships.
    - Patient (vs volatile): Tendency to stay calm and keep with a plan. Also affects their ability to engage with new knowledge off the battlefield.
    - Pensive (vs Impulsive): Tendency to act without planning.
  - Secondary scores (informing roleplay):
    - Cooperative: Tendency to communicate plans with others, and to take other's plans into account.
    - Assertive: Tendency to take charge and attempt to convince others to follow an established plan (granted that they trust the plan).
    - Violent: Tendency to take violent options over non-violent.
    - Open (vs secretive): Tendency to share information with others.

On the battlefield personality scores are mostly boiled down into 3 mechanical scores:

*Mechanical scores:*
  - Initiative: The speed with which the character can act in battle.
  - Cogitation: The amount of time that the character can spend planning each turn.
  - Communication: The amount of time that the character can spend communicating plans or information to others.

In addition, each character has a set of knowledge scores that modify their ability to use their mechanical scores.

*Knowledge scores (0.01-1.0):*
  - Learning: Skill att looking up and digesting information. Not used in battle, but affects long-term projects. Learned by studying or tutoring by others.
  - Logic: Skill at analyzing a situation, reducing overall cogitation costs and allows for longer plans.
  - Tactics: Skill at organizing their allies and recognizing their enemies plans. Reduces cogitation costs for allies' actions and improves chances of identifying enemy plans.
  - Oration: Skill at communicating clearly and intentionaly (reduces overall communication costs)
  - Weapon skill (for each weapon type): Skill with the given weapon type, improving effectiveness with and slightly reducing cogitation costs for the weapon type. Obtained through practice, affected by physical scores.
  - Weapon knowledge (for each weapon type): Kowledge about the weapon type, slightly improving effectiveness and reduces cogitation costs for weapon type. Obtained through study.
  - Thaumaturgy (Magic skill): Practical knowledge of magic, improving effectiveness, reducing cognitive costs and slightly improving chance to identify plans with magic in them.
  - Arcana (Magic knowledge): General knowledge of magic, sligtly improving effectiveness, reducing cognitive costs and improving chance to identify plans with magic in them.
  - Bestiary (for each enemy type): General knowledge about an enemy type, improving effectiveness against it, reducing cognitive costs and improves chances of identifying plans.
  - Character (for each character, friend or foe): Knowledge about an individual, reduces cognitive costs and improves chances of identifying plans.

Knowledge scores may also inform a characters actions in their off-time.

## Personality Scores
Personality scores represent personality dynamics that range from extreme absence to extreme dominance e.g.:
  - Sociable: 0.0: Automaton   -> Anti-social (0.1) -> Loner (0.25)     -> Average (0.5) -> Cooperative (0.75) -> Co-Dependent (1.0)  -> 1.0+: "Hive mind"
  - Patient:  0.0: Instinctive -> Volatile (0.1)    -> Mercurial (0.25) -> Average (0.5) -> Consistent (0.75)  -> Hard-line (1.0)     -> 1.0+: "Programmed"
  - Pensive:  0.0: Instinctive -> Arbitrary (0.1)   -> Impulsive (0.25) -> Average (0.5) -> Sober (0.75)       -> Wistful (1.0)       -> 1.0+: Over-thinking

They do not dictate the characters behavior, but inform how they tend to act: A low-social character can still interact with and even be co-dependent on another character, they just tend to be less likely to.

A few practical examples:
 - A highly "Sociable" character is likely to accept the plan of another character (if it is someone they trust), where-as a low "Sociable" character is more likely to reject the plan.
 - A highly "Patient" character is more likely to stick with an accepted plan even as they lose trust in it or the character that sugested it, a less "Patient" character is more likely to create their own.
 - A highly "Pensive" character tends to take longer to formulate a plan (hence the effect in Initiative), and is more likely to create their own plan if they do not trust the accepted plan (or the character that suggested it). A less "Pensive" character is more likely to accept a plan that's longer than the accepted plan, provided that they trust the character that made it.

These tendencies inform how they tend to operate in a fight, and so forms a modifier to their Mechanical scores.

### Personality tags
Personality tags represent character traits and modify a characters personality and behavior, e.g.:
 - Optimist: Sociable+, Patient+, pensive-
 - Pessimist: Sociable-, Patient-, pensive-
 - Supportive: More likely to select or accept `<support>` skills in plans, less likely to select/accept `<aggressive>` skill use.
 - Violent: More likely to select/accept `<violent>` skills, less likely to accept `<healing>` or `<supporting>` skills.
 - Curious: Patient - 0.1, pensive + 0.1, more likely to select/accept `<investigative>` skills.

Each tag should attempt to balance the personality scores and behaviors, e.g.: if it increases one personality score, it should lower another.

## Practicals
In battle, the basic mechanical stats are affected by personality scores as follows:

- *Inititive*: 
  - `[base inititive] / [Pensive]`
- *cogitation*: 
  - `[base cogitation] * ([Pensive] + [Patient])`
- *Communication*:
  - `[base communication] * ([Sociable] + [Patient])`

### Examples:

Assume a bog-standard human:
```
    Social:  0.5
    Patient: 0.5
    Pensive: 0.5

    base initiative: 10
    base cogitation: 10
    base communication: 10

    Initiative: 10 / 0.5 = 20
    Cogitation: 10 * (0.5 + 0.5)  = 10
    Communication: 10 * (0.5 + 0.5) = 10
```

*Brugg the Barbarian*
```
Brugg is a higly impulsive, human barbarian with anger management issues who wears his feelings on his sleeve:
    Social: 1.0
    Patient: 0.1
    Pensive: 0.2

    base initiative: 10
    base cogitation: 10
    base communication: 10


    Initiative: 10 / 0.2 = 50
    Cogitation: 10 * (0.2 + 0.1)  = 3
    Communication: 10 * (1.0 + 0.1) = 11

So Brugg will get to act quickly however he won't be doing much thinking (but he will likely be able to communicate all his thougts :))
```

*Merlin the Wizard*
```
Merlin is a consumate, wizard who cares for his companions but knows that discretion is the better part of valor:
    Social:  0.5
    Patient: 0.7
    Pensive: 0.9

    base initiative: 10
    base cogitation: 10
    base communication: 10

    Initiative: 10 / 0.9 = 9
    Cogitation: 10 * (0.9 + 0.7) = 16
    Communication: 10 * (0.5 + 0.7) = 12

Merlin will be considerably slower to act than Brugg, but will be able to propose a much more extensive plan to the party (so much so that he may noot be able to explaion it all).
```

*Roland the Soldier*
```
Roland is a gregarious, human soldier with a decade of campaign under his belt:
    Social:  0.8
    Patient: 0.7
    Pensive: 0.5

    base initiative: 10
    base cogitation: 10
    base communication: 10

    Initiative: 10 / 0.5 = 20
    Cogitation: 10 * (0.5 + 0.7) = 12
    Communication: 10 * (0.8 + 0.7) = 15
```