# 🏭 Arkanoid Factory

## English

Arkanoid Factory is a modern factory-themed version of the classic **Arkanoid / Breakout** game, built with **Python** and **Pygame**.

Break material bricks, collect falling resources, complete production orders, earn money, and improve your equipment between levels.

Unlike a traditional Arkanoid game, destroying bricks is only the beginning. You must also catch the materials before they fall out of the playfield.

---

## 🎮 Gameplay

Move the paddle with your mouse and keep the ball in play.

When the ball destroys a brick, the brick may release a material:

- Iron
- Copper
- Crystal

Catch the falling material with the paddle to add it to your inventory.

Complete the current order to receive a reward and open the upgrade screen.

---

## ✨ Features

- Classic Arkanoid gameplay
- Factory and automation theme
- Three collectible materials
- Resource inventory
- Production orders
- Money and reward system
- Upgrade shop between levels
- Three paddle modes
- Bomb bricks
- Energy bricks
- Combo system
- Increasing level difficulty
- Particle effects
- Neon visual style
- Game over and restart system

---

## 📦 Materials

### Iron

The most common material.

```text
Value: $3
```

### Copper

Less common and more valuable.

```text
Value: $5
```

### Crystal

Rare material used in more advanced orders.

```text
Value: $10
```

---

## 🎯 Orders

Every level contains a production order.

Example:

```text
Iron:   8
Copper: 6
Crystal: 2
```

Catch enough materials to complete the order.

After completion:

- required materials are removed from inventory,
- you receive a money reward,
- the upgrade shop opens,
- the next level becomes available.

---

## 🏓 Paddle Modes

Switch between paddle modes with `TAB`.

### 🟢 Catch Mode

The ball sticks to the paddle after contact.

Press `SPACE` to launch it again.

This mode gives you more control over the launch direction.

### 🔵 Power Mode

The ball receives a speed boost when it hits the paddle.

Useful for breaking bricks faster.

### 🟣 Magnet Mode

Falling materials are attracted toward the paddle.

Useful when several resources fall at the same time.

---

## 🧱 Special Bricks

### 💣 Bomb Brick

Destroys nearby bricks when broken.

Nearby bricks also release their materials.

### ⚡ Energy Brick

Creates a special visual effect and contributes to the factory theme.

---

## 🛒 Upgrade Shop

Between levels, spend money on upgrades.

### 1 — Wider Paddle

Increases the width of the paddle.

### 2 — Faster Ball

Increases the base speed of newly created balls.

### 3 — Stronger Magnet

Improves the range and strength of material attraction.

### 4 — Multiball Upgrade

Prepares the upgrade system for stronger multiball mechanics in future versions.

---

## 🎮 Controls

| Control | Action |
|---|---|
| Mouse | Move the paddle |
| `SPACE` | Launch a captured ball |
| `TAB` | Change paddle mode |
| `R` | Restart the current level |
| `1–4` | Buy an upgrade |
| `ENTER` | Continue to the next level |
| `ENTER` | Restart after game over |

---

## ▶️ Installation

Install Python 3 and Pygame.

```bash
pip install pygame
```

---

## 🚀 Run

```bash
python arkanoid_factory.py
```

---

## 📂 Project Structure

```text
ArkanoidFactory/
├── arkanoid_factory.py
└── README.md
```

---

## 🛠️ Built With

- Python 3
- Pygame

---

## 🚧 Future Ideas

- Fully functional multiball
- Laser paddle
- Shield under the paddle
- More material types
- Factory recipes
- Timed contracts
- Boss levels
- Moving bricks
- Reinforced bricks
- New paddle modes
- Sound effects
- Background music
- Local high scores
- Achievements
- Permanent upgrades
- Animated factory background

---

# 🇨🇿 Česky

Arkanoid Factory je moderní tovární varianta klasické hry **Arkanoid / Breakout**, vytvořená v **Pythonu** pomocí knihovny **Pygame**.

Rozbíjej materiálové cihly, chytej padající suroviny, plň výrobní objednávky, vydělávej peníze a mezi levely vylepšuj své vybavení.

Na rozdíl od klasického Arkanoidu nestačí cihlu pouze rozbít. Uvolněnou surovinu musíš ještě zachytit pálkou.

---

## 🎮 Princip hry

Pohybuj pálkou pomocí myši a udržuj míček ve hře.

Po rozbití cihly může vypadnout jedna ze surovin:

- železo,
- měď,
- krystal.

Padající surovinu zachyť pálkou a přidej ji do inventáře.

Jakmile splníš aktuální objednávku, získáš odměnu a otevře se nabídka vylepšení.

---

## ✨ Funkce

- Klasický Arkanoid
- Tovární a automatizační motiv
- Tři druhy surovin
- Inventář materiálů
- Výrobní objednávky
- Peníze a odměny
- Obchod mezi levely
- Tři režimy pálky
- Výbušné cihly
- Energetické cihly
- Combo systém
- Rostoucí obtížnost
- Částicové efekty
- Moderní neonový vzhled
- Game Over a restart

---

## 📦 Suroviny

### Železo

Nejběžnější materiál.

```text
Hodnota: $3
```

### Měď

Méně běžný a hodnotnější materiál.

```text
Hodnota: $5
```

### Krystal

Vzácná surovina používaná v pokročilejších objednávkách.

```text
Hodnota: $10
```

---

## 🎯 Objednávky

Každý level obsahuje výrobní objednávku.

Například:

```text
Iron:   8
Copper: 6
Crystal: 2
```

Zachyť požadovaný počet surovin.

Po dokončení objednávky:

- se požadované materiály odečtou,
- získáš finanční odměnu,
- otevře se obchod,
- můžeš pokračovat do dalšího levelu.

---

## 🏓 Režimy pálky

Mezi režimy přepínáš klávesou `TAB`.

### 🟢 Catch Mode

Míček se po kontaktu zachytí na pálce.

Klávesou `SPACE` jej znovu odpálíš.

Tento režim umožňuje lépe připravit další odpal.

### 🔵 Power Mode

Míček po odrazu od pálky získá vyšší rychlost.

Hodí se pro rychlejší rozbíjení cihel.

### 🟣 Magnet Mode

Padající suroviny jsou přitahovány k pálce.

Pomáhá při zachytávání více materiálů současně.

---

## 🧱 Speciální cihly

### 💣 Bomb Brick

Po rozbití zničí okolní cihly.

Zničené okolní cihly také uvolní své materiály.

### ⚡ Energy Brick

Vytváří speciální efekt a rozšiřuje tovární atmosféru hry.

---

## 🛒 Obchod s vylepšeními

Mezi levely můžeš utrácet peníze za upgrady.

### 1 — Wider Paddle

Zvětší šířku pálky.

### 2 — Faster Ball

Zvýší základní rychlost nových míčků.

### 3 — Stronger Magnet

Zvětší dosah a sílu přitahování materiálů.

### 4 — Multiball Upgrade

Připravuje systém pro pokročilejší multiball mechaniku v dalších verzích.

---

## 🎮 Ovládání

| Ovládání | Akce |
|---|---|
| Myš | Pohyb pálky |
| `SPACE` | Odpálení zachyceného míčku |
| `TAB` | Přepnutí režimu pálky |
| `R` | Restart aktuálního levelu |
| `1–4` | Nákup upgradu |
| `ENTER` | Pokračování do dalšího levelu |
| `ENTER` | Restart po prohře |

---

## ▶️ Instalace

Nainstaluj Python 3 a knihovnu Pygame.

```bash
pip install pygame
```

---

## 🚀 Spuštění

```bash
python arkanoid_factory.py
```

---

## 📂 Struktura projektu

```text
ArkanoidFactory/
├── arkanoid_factory.py
└── README.md
```

---

## 🛠️ Použité technologie

- Python 3
- Pygame

---

## 🚧 Nápady pro další verze

- Plně funkční multiball
- Laserová pálka
- Ochranný štít
- Více druhů surovin
- Výrobní recepty
- Časově omezené zakázky
- Boss levely
- Pohyblivé cihly
- Odolnější cihly
- Nové režimy pálky
- Zvukové efekty
- Hudba
- Lokální rekordy
- Achievementy
- Trvalá vylepšení
- Animované tovární pozadí
