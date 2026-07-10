import pygame

from settings import (
    BOTTOM_TOOLBAR_HEIGHT,
    FPS,
    GRID_COLS,
    GRID_ROWS,
    HEIGHT,
    TILE_SIZE,
    TOP_PANEL_HEIGHT,
    WIDTH,
)
from toolbar import Toolbar
from tutorial import Tutorial
from ui import Renderer
from world import World


def tile_at_pos(pos):
    x, y = pos
    if y < TOP_PANEL_HEIGHT or y >= HEIGHT - BOTTOM_TOOLBAR_HEIGHT:
        return None
    tile = (x // TILE_SIZE, (y - TOP_PANEL_HEIGHT) // TILE_SIZE)
    if 0 <= tile[0] < GRID_COLS and 0 <= tile[1] < GRID_ROWS:
        return tile
    return None


def drag_direction(start, end):
    if start is None or end is None:
        return "right"
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    if abs(dx) >= abs(dy):
        return "right" if dx >= 0 else "left"
    return "down" if dy >= 0 else "up"


def step_direction(start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    if abs(dx) >= abs(dy):
        return (1, 0, "right") if dx > 0 else (-1, 0, "left")
    return (0, 1, "down") if dy > 0 else (0, -1, "up")


def paint_belts(world, start, end):
    if start is None or end is None or start == end:
        return start, None, False

    current = start
    last_direction = None
    changed = False

    while current != end:
        dx, dy, direction = step_direction(current, end)
        next_tile = (current[0] + dx, current[1] + dy)
        placed = world.place_belt(current, direction, quiet=True)
        changed = changed or placed
        last_direction = direction

        if next_tile == world.factory_pos:
            return current, last_direction, changed
        current = next_tile

    return current, last_direction, changed


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Factory Builder V2")
    clock = pygame.time.Clock()

    world = World()
    toolbar = Toolbar()
    tutorial = Tutorial()
    renderer = Renderer(screen)
    belt_last_tile = None
    belt_last_direction = "right"
    belt_drag_moved = False
    remove_dragging = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        mouse_tile = tile_at_pos(pygame.mouse.get_pos())
        ghost_valid = False
        if mouse_tile is not None:
            if world.selected_tool == "remove":
                ghost_valid = world.in_bounds(mouse_tile)
            else:
                ghost_valid = world.can_place(mouse_tile, world.selected_tool)[0]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    world.reset()
                elif event.key == pygame.K_TAB:
                    world.engineer_mode = not world.engineer_mode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked_tool = toolbar.tool_at(event.pos)
                    clicked_upgrade = toolbar.upgrade_at(event.pos)
                    if clicked_upgrade:
                        world.buy_upgrade(clicked_upgrade)
                    elif clicked_tool:
                        world.selected_tool = clicked_tool
                        world.set_message(f"Selected {clicked_tool}.")
                    else:
                        tile = tile_at_pos(event.pos)
                        if world.selected_tool == "belt":
                            belt_last_tile = tile
                            belt_last_direction = "right"
                            belt_drag_moved = False
                        elif world.selected_tool == "remove":
                            remove_dragging = True
                            if tile is not None:
                                world.build(tile, "remove")
                        elif tile is not None:
                            world.build(tile, world.selected_tool)
                elif event.button == 3:
                    tile = tile_at_pos(event.pos)
                    if tile is not None:
                        world.rotate_building(tile)
            elif event.type == pygame.MOUSEMOTION:
                if world.selected_tool == "belt" and belt_last_tile is not None and event.buttons[0]:
                    current_tile = tile_at_pos(event.pos)
                    next_tile, direction, changed = paint_belts(world, belt_last_tile, current_tile)
                    if direction is not None:
                        belt_last_direction = direction
                    if next_tile is not None:
                        belt_last_tile = next_tile
                    belt_drag_moved = belt_drag_moved or changed
                elif world.selected_tool == "remove" and remove_dragging and event.buttons[0]:
                    tile = tile_at_pos(event.pos)
                    if tile is not None and tile in world.buildings:
                        world.build(tile, "remove")
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and world.selected_tool == "belt" and belt_last_tile is not None:
                    if belt_drag_moved:
                        world.place_belt(belt_last_tile, belt_last_direction)
                    else:
                        world.place_belt(belt_last_tile, drag_direction(belt_last_tile, tile_at_pos(event.pos)))
                    belt_last_tile = None
                    belt_drag_moved = False
                elif event.button == 1:
                    remove_dragging = False

        world.update(dt)
        world.update_message(tutorial.hint(world), dt)
        renderer.update(dt)
        renderer.draw(world, toolbar, mouse_tile, ghost_valid)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
