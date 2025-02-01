# gemini_maze_exploration
A playground using LLM to explore/navigate a robot through an unknown environment

## Description
Basic logic
```text
LLM-Guided Navigation System
---------------------------
Algorithm Overview:
1. Agent starts at random position (-0.5 to 0.5)
2. LLM receives current position → generate waypoint sequence suggestions
3. Agent moves step-by-step through waypoints
4. Success: All waypoints reached -> End
   Failure: Hit invalid grid cell -> Promptback the LLM for another suggestion

Trial Loop:
    START → Send position to LLM → Get waypoints → Navigate → Check result
    - If success: End
    - If failure: Retry with new initial position (max 20 trials)

Navigation Loop:
    Move → Record position → Check grid → Update target
```

## Usage
Work in progress.

## Result
![](assets/floor1_result.gif) ![](assets/floor3_result.gif)