# Factory Builder V2

## English

Factory Builder V2 is a small playable factory automation game made with Python 3 and Pygame. Build miners on ore deposits, draw conveyor belts, unlock smelters, produce iron plates, earn money, buy upgrades, and complete increasingly larger orders.

### Install

```bash
pip install pygame
```

### Run

```bash
cd 16FactoryBuilder
python main.py
```

You can also run the compatibility launcher:

```bash
python factory_builder.py
```

### Controls

- Left click a toolbar button to select Miner, Belt, or Remove.
- Left click the map to build or remove.
- With Belt selected, hold left mouse and draw across tiles. Belts are placed automatically in the drag direction.
- With Remove selected, hold left mouse and drag across buildings to remove them.
- Right click a miner, belt, or smelter to rotate its direction.
- Press `R` to reset the game.
- Press `TAB` to toggle Engineer Mode.

### Goal

Deliver requested items into the factory. The first mission requires 20 iron ore. After that, the smelter unlocks and later orders require iron plates. When an order is complete, you receive a money reward and a new order starts automatically.

### V2 Features

- Smelter building: turns iron ore into iron plates.
- Iron plate orders after the first mission.
- Miner Speed and Belt Speed upgrades in the bottom toolbar.
- Drag-to-remove for faster editing.

### Engineer Mode

Engineer Mode displays diagnostic labels above buildings:

- Miner: Running / Waiting for belt
- Belt: Flow
- Smelter: Waiting for ore / Smelting / Waiting for output belt / Output blocked
- Factory: Delivered count

Green means running, yellow means waiting, and red is used for invalid placement feedback.

## Cesky

Factory Builder V2 je mala hratelna automatizacni hra v Pythonu 3 a Pygame. Stavite tezice na loziska rudy, kreslite dopravni pasy, odemykate smeltery, vyrabite iron plates, vydelavate penize, kupujete upgrady a plnite stale vetsi objednavky.

### Instalace

```bash
pip install pygame
```

### Spusteni

```bash
cd 16FactoryBuilder
python main.py
```

Funguje i puvodni soubor:

```bash
python factory_builder.py
```

### Ovladani

- Levym kliknutim na spodni listu vyberete Miner, Belt nebo Remove.
- Levym kliknutim do mapy stavite nebo mazete.
- S vybranym Belt podrzte leve tlacitko a kreslete pres policka. Pasy se samy natoci podle smeru tahu.
- S vybranym Remove podrzte leve tlacitko a tahem mazete budovy.
- Pravym kliknutim na tezic, pas nebo smelter otocite jeho smer.
- Klavesa `R` resetuje hru.
- Klavesa `TAB` zapina a vypina Engineer Mode.

### Cil hry

Dorucujte pozadovane itemy do tovarny. Prvni mise chce 20 iron ore. Potom se odemkne smelter a dalsi objednavky chteji iron plates. Po splneni objednavky dostanete odmenu a automaticky zacne nova objednavka.

### V2 funkce

- Smelter: meni iron ore na iron plates.
- Objednavky na iron plates po prvni misi.
- Upgrady Miner Speed a Belt Speed ve spodni liste.
- Mazani tahem pro rychlejsi upravy linky.

### Engineer Mode

Engineer Mode zobrazuje diagnosticke popisky nad budovami:

- Miner: Running / Waiting for belt
- Belt: Flow
- Smelter: Waiting for ore / Smelting / Waiting for output belt / Output blocked
- Factory: Delivered count

Zelena znamena, ze vse bezi, zluta znamena cekani a cervena se pouziva pro neplatne staveni.
