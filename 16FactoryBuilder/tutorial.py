class Tutorial:
    def hint(self, world):
        if not world.has_miner():
            return "Tutorial: Build a miner on an orange ore deposit."
        if not world.has_belt_next_to_miner():
            return "Tutorial: Build belts from the miner output arrow toward the factory."
        if world.factory.delivered_total == 0:
            return "Tutorial: Ore only leaves a miner when its arrow points into a belt."
        if world.orders.number == 1:
            return "Tutorial: Keep the belt line connected until 20 iron reaches the factory."
        if world.smelter_unlocked and not world.has_smelter():
            return "V2: Smelter unlocked. Build one, feed ore into it, then send plates to the factory."
        if world.orders.item_kind == "iron_plate":
            return "V2: Smelters turn ore into plates. Right click a smelter to rotate its output."
        return "New order received. Expand the line or buy upgrades to deliver faster."
