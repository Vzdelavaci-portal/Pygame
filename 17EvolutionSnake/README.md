# Evolution Snake

## English

Evolution Snake is a modern variation of the classic Snake game created with Python and Pygame.

Instead of collecting apples, the snake collects DNA fragments. Every 20 DNA points, the game pauses and the player chooses one of three randomly selected mutations.

Each mutation changes the gameplay, which means every run can develop differently.

## Features

- Classic Snake movement with a modern neon visual style
- DNA fragments instead of apples
- Evolution selection every 20 DNA points
- Three random mutation choices
- Multiple mutation levels
- Special DNA types
- Particle effects and floating score text
- Active abilities with cooldowns
- Final game statistics
- Keyboard and mouse controls

## Mutations

### Swift

Increases the snake's movement speed.

Swift can be selected multiple times to increase its effect.

### Magnet

Pulls nearby DNA fragments toward the snake.

Higher levels increase the magnet range.

### Ghost

Allows the snake to temporarily move through its own body.

Press `G` to activate Ghost Mode.

### Turtle

Provides one shield that prevents death after a collision.

After activation, the snake is moved back to a safe position.

### Dash

Temporarily increases the snake's movement speed.

Press `SPACE` to activate Dash.

### Lucky DNA

Increases the chance of valuable DNA fragments appearing.

It can also provide bonus DNA points.

## DNA Types

- Green DNA: `+1 DNA`
- Blue DNA: `+5 DNA`
- Gold DNA: `+10 DNA`

The Lucky DNA mutation increases the chance of receiving more valuable DNA.

## Installation

Make sure Python 3 is installed.

Install Pygame:

```bash
pip install pygame