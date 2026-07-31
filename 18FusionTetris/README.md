# Fusion Tetris

## English

Fusion Tetris is a unique twist on the classic Tetris formula built with **Python** and **Pygame**.

Instead of clearing complete rows, blocks of the same material merge together and evolve into stronger materials. Every merge can trigger gravity, causing chain reactions and massive combos.

Your ultimate goal is to create the legendary **Diamond** block before the board fills up.

---

## Features

- 🎮 Classic Tetris gameplay
- 🧩 Material fusion instead of line clearing
- ⚡ Chain reaction system
- 🏆 Combo multiplier
- 👻 Ghost piece preview
- 📦 Next piece preview
- 💥 Particle effects
- ✨ Floating score animations
- 📊 Game statistics
- 🌟 Modern neon UI

---

## Materials

Materials evolve through multiple tiers.

```text
Stone
   ↓
Copper
   ↓
Iron
   ↓
Steel
   ↓
Titanium
   ↓
Crystal
   ↓
Diamond
```

Every successful merge upgrades the material by one level.

---

## How It Works

1. Place tetrominoes on the board.
2. When two or more connected blocks share the same material, they merge.
3. The merged block evolves into the next material tier.
4. Gravity pulls remaining blocks downward.
5. New chain reactions may occur automatically.
6. Continue merging until you create Diamond.

Unlike traditional Tetris, **rows are never removed**.

---

## Controls

| Key | Action |
|------|--------|
| **A / D** | Move left / right |
| **W** or **↑** | Rotate |
| **S** or **↓** | Soft Drop |
| **SPACE** | Hard Drop |
| **R** | Restart |
| **ENTER** | Play Again |

---

## Installation

Install Pygame:

```bash
pip install pygame
```

---

## Run

```bash
python fusion_tetris.py
```

---

## Game Over Statistics

After every game you can see:

- Final Score
- Highest Material
- Best Combo
- Total Merges
- Pieces Placed
- Survival Time

---

## Project Structure

```text
FusionTetris/
│
├── fusion_tetris.py
└── README.md
```

---

## Built With

- Python 3
- Pygame

---

## Future Ideas

- Special power blocks
- Bomb blocks
- Rainbow blocks
- Material abilities
- Endless mode
- Daily challenges
- Online leaderboard
- Achievements
- New material trees
- Animated backgrounds
- Sound effects and music

---

# Česky

Fusion Tetris je originální varianta klasického Tetrisu vytvořená v **Pythonu** a knihovně **Pygame**.

Místo mazání řádků se spojují bloky stejného materiálu. Spojením vzniká vyšší materiál a díky gravitaci mohou vznikat řetězové reakce a velká komba.

Cílem hry je vytvořit legendární **Diamond** dříve, než se herní plocha zaplní.

---

## Funkce

- 🎮 Klasické ovládání Tetrisu
- 🧩 Spojování materiálů místo mazání řádků
- ⚡ Řetězové reakce
- 🏆 Combo systém
- 👻 Ghost Piece
- 📦 Náhled další kostky
- 💥 Částicové efekty
- ✨ Animované body
- 📊 Statistiky po skončení hry
- 🌟 Moderní neonový vzhled

---

## Materiály

Jednotlivé materiály se vyvíjejí.

```text
Stone
   ↓
Copper
   ↓
Iron
   ↓
Steel
   ↓
Titanium
   ↓
Crystal
   ↓
Diamond
```

Každé úspěšné spojení vytvoří materiál vyšší úrovně.

---

## Jak hrát

1. Pokládejte tetromina na hrací plochu.
2. Pokud se dotýkají alespoň dva stejné materiály, spojí se.
3. Vznikne nový materiál vyšší úrovně.
4. Ostatní bloky spadnou dolů.
5. Mohou vzniknout další automatické kombinace.
6. Pokuste se vytvořit Diamond.

Na rozdíl od klasického Tetrisu se **řádky nemažou**.

---

## Ovládání

| Klávesa | Akce |
|----------|------|
| **A / D** | Pohyb doleva / doprava |
| **W** nebo **↑** | Otočení |
| **S** nebo **↓** | Rychlejší pád |
| **SPACE** | Okamžitý pád |
| **R** | Restart |
| **ENTER** | Nová hra |

---

## Instalace

```bash
pip install pygame
```

---

## Spuštění

```bash
python fusion_tetris.py
```

---

## Statistiky

Po skončení hry se zobrazí:

- Konečné skóre
- Nejvyšší vytvořený materiál
- Nejlepší combo
- Celkový počet spojení
- Počet položených kostek
- Doba hraní

---

## Struktura projektu

```text
FusionTetris/
│
├── fusion_tetris.py
└── README.md
```

---

## Použité technologie

- Python 3
- Pygame

---

## Nápady pro další verze

- Speciální bloky
- Bomb bloky
- Rainbow bloky
- Schopnosti materiálů
- Endless režim
- Denní výzvy
- Online žebříček
- Achievementy
- Nové větve materiálů
- Animované pozadí
- Zvuky a hudba