# Factory Builder V1

## English

Factory Builder V1 is a small playable factory automation game made with Python 3 and Pygame. Build miners on ore deposits, connect conveyor belts to the factory, deliver iron, earn money, and complete increasingly larger orders.

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
- Right click a miner or belt to rotate its direction.
- Press `R` to reset the game.
- Press `TAB` to toggle Engineer Mode.

### Goal

Deliver iron ore into the factory. The first mission requires 20 iron. When the order is complete, you receive a money reward and a new order with a higher target starts automatically.

### Engineer Mode

Engineer Mode displays diagnostic labels above buildings:

- Miner: Running / Waiting for belt
- Belt: Flow
- Factory: Delivered count

Green means running, yellow means waiting, and red is used for invalid placement feedback.

## Cesky

Factory Builder V1 je mala hratelna automatizacni hra v Pythonu 3 a Pygame. Stavite tezice na loziska rudy, propojujete je pasy s tovarnou, dorucujete zelezo, vydelavate penize a plnite stale vetsi objednavky.

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
- Pravym kliknutim na tezic nebo pas otocite jeho smer.
- Klavesa `R` resetuje hru.
- Klavesa `TAB` zapina a vypina Engineer Mode.

### Cil hry

Dorucujte zeleznou rudu do tovarny. Prvni mise chce 20 zeleza. Po splneni objednavky dostanete odmenu a automaticky zacne nova objednavka s vyssim cilem.

### Engineer Mode

Engineer Mode zobrazuje diagnosticke popisky nad budovami:

- Miner: Running / Waiting for belt
- Belt: Flow
- Factory: Delivered count

Zelena znamena, ze vse bezi, zluta znamena cekani a cervena se pouziva pro neplatne staveni.
