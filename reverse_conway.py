import pygame
from copy import deepcopy

# Set up size of conway game, this is considered the size of the starting state of the game
# Game is assumed to have run in a Toroidal simulation
width, height = (20,20)
cell_size = 20
game_state = [[0 for _ in range(height)] for _ in range(width)]

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((width * cell_size, height * cell_size))
pygame.display.set_caption("Conway's Game of Life")
clock = pygame.time.Clock()

def draw():
    for i in range(width):
        for j in range(height):
            color = (255, 255, 255) if game_state[i][j] == 1 else (0, 0, 0)  # White for alive, black for dead
            pygame.draw.rect(screen, color, (j * cell_size, i * cell_size, cell_size, cell_size))

def draw_cells(x, y):
    grid_y = y // cell_size
    grid_x = x // cell_size
    if 0 <= grid_x < width and 0 <= grid_y < height:
        game_state[grid_y][grid_x] = 1  # Set cell to alive

def wrap(num):
    wrap_x = num[0]
    wrap_y = num[1]

    wrap_x = wrap_x % width if wrap_x >= 0 else (wrap_x + width) % width
    wrap_y = wrap_y % height if wrap_y >= 0 else (wrap_y + height) % height
    return (wrap_x, wrap_y)

def update(board):
    # Dimensions of the board
    width, height = len(board), len(board[0])

    # Set to track cells that need to be checked (live cells and their neighbors)
    to_check = set()

    # Track live cells and their neighbors
    for i in range(width):
        for j in range(height):
            if board[i][j] == 1:
                to_check.add((i, j))
                # Check neighboring cells (including wrapping)
                checks = [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1] if (x, y) != (0, 0)]
                for dx, dy in checks:
                    wrapped_x, wrapped_y = wrap((i + dx, j + dy))  # Use existing wrap function
                    to_check.add((wrapped_x, wrapped_y))

    # Create a new empty board
    new_game = [[0 for _ in range(height)] for _ in range(width)]

    # Update only the cells in the to_check set
    for i, j in to_check:
        checks = [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1] if (x, y) != (0, 0)]
        sum_neighbors = 0

        for dx, dy in checks:
            wrapped_x, wrapped_y = wrap((i + dx, j + dy))  # Use existing wrap function
            sum_neighbors += board[wrapped_x][wrapped_y]

        if board[i][j] == 1:
            if sum_neighbors in [2, 3]:  # Survival condition
                new_game[i][j] = 1
            else:
                new_game[i][j] = 0  # Death condition
        else:
            if sum_neighbors == 3:  # Birth condition
                new_game[i][j] = 1
    
    return new_game


if True:
    ### All possible combinations of neighbors to keep/make a cell (alive)
    combinations = []

    # All possible positions around x and y
    possible_states = [(sx, sy) for sx in [-1, 0, 1] for sy in [-1, 0, 1] if (sx, sy) != (0, 0)]

    # Create all possible states of 2 neighbors
    for first_state in possible_states:
        for second_state in possible_states:
            if first_state != second_state: # Neighbors can't exist on top of each other
                combinations.append([first_state, second_state])

    # Create all possible states of 3 neighbors
    for first_state in possible_states:
        for second_state in possible_states:
            if first_state != second_state: # Neighbors can't exist on top of each other
                for third_state in possible_states:
                    if second_state != third_state: # Neighbors can't exist on top of each other
                        combinations.append([first_state, second_state, third_state])
    
    print([(1,1),(1,-1)] in combinations)

def partial_match(mock_state, game_state):
    for i in range(width):
        for j in range(height):
            # Check for violations
            if mock_state[i][j] == 1 and game_state[i][j] == 0:
                #print("Invalid")
                return False  # Invalid if a cell is alive in mock but dead in game_state
    return True  # No violations


def reverse_game_state():
    global game_state
    possibilities = []
    on = []

    # collect all currently alive states from board
    for x, column in enumerate(game_state):
        for y, state in enumerate(column):
            if state == 1:
                on.append((x, y))
    
    # iterate over all possible combinations for first on neighbor
    for combo_idx, combo in enumerate(combinations):
        print(f"{(combo_idx/len(combinations))*100}% done")

        mock_states = {
            "0": [[0 for _ in range(height)] for _ in range(width)] # create new board for each combination of states at depth 1
        }
        #mock_state = [[0 for _ in range(height)] for _ in range(width)] # create new board for each combination
        
        for state in combo: # set 1st state's combination into mock_state
            first_x = on[0][0]+state[0]
            first_y = on[0][1]+state[1]
            wrapped_coords = wrap((first_x, first_y))
            mock_states["0"][wrapped_coords[0]][wrapped_coords[1]] = 1

        # iterate over each consecutive currently on neighbor (after 1st)
        for idx, coordinate in enumerate(on[1:]):
            idx += 1
            co_x = coordinate[0]
            co_y = coordinate[1]
            mock_states[str(idx)] = deepcopy(mock_states[str(idx-1)]) # copy previous board state to edit

            for consec_combo in combinations: # iterate over each possible prior neighbor configuration
                for consec_state in consec_combo: # iterate over each neighbor in said configuration
                    mock_states[str(idx)][wrap((co_x+consec_state[0], co_y+consec_state[1]))[0]][wrap((co_x+consec_state[0], co_y+consec_state[1]))[1]] = 1

                hypothetical_board = update(deepcopy(mock_states[str(idx)]))
                if partial_match(hypothetical_board, game_state): # check for partial match between board state and game state
                    if idx == len(on) - 1:  # only check for a full match at the last "on" cell
                        if hypothetical_board == game_state:
                            return [deepcopy(mock_states[str(idx)])]
                            #print("valid previous state found!")
                            if not(deepcopy(mock_states[str(idx)]) in possibilities): # check if it exists
                                possibilities.append(deepcopy(mock_states[str(idx)])) # found valid previous state
                    else:
                        continue # continue to the next "on" cell

                else:
                    mock_states[str(idx)] = deepcopy(mock_states[str(idx-1)]) # copy previous board state (refresh due to failure of point)

        #print("no can do buckaroo")

    return possibilities

running = True
fps = 60
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Mouse button down
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                draw_cells(*event.pos) 
        # LR keys down
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                # for possibility in reverse_game_state():
                #     game_state = possibility
                #     draw()
                #     pygame.display.flip()  # Update the display
                #     clock.tick(fps)  # Control the speed of the simulation
                #     pygame.time.delay(2000)
                game_state = reverse_game_state()[0]
            if event.key == pygame.K_RIGHT:
                game_state = update(game_state)
        
    draw()
    pygame.display.flip()  # Update the display
    clock.tick(fps)  # Control the speed of the simulation