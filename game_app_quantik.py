import pygame
from pygame.locals import *
from pygame import Vector2
import random

from game_quantik import QuantikAI 

# AI player method, name from QuantikAI class
AI_METHOD = "minimax"

SIZE = 800, 500
# ======= DEFINE VISUALS: COLOR, SHAPES, FONT ======
pygame.font.init() 
font = pygame.font.SysFont("monospace", 15)

def get_rand_color(seed=None):
    random.seed(seed)
    r, g, b = random.randint(50,255), random.randint(30,255), random.randint(40,255)
    return (r, g, b)

COLORS = {'black_tokens': (15, 5, 5),
          'white_tokens': (230,240,230),
          'selection_frame': (230,240,230),
          'fields': (60,50,55),
          'text': (0,0,0),
          'background': (30,15,35),
          'token_stash': (60,30,70),
          'pick_notif': (220,110,190)}

# # random colors
# background_seed = random.randint(1,100)
# COLORS = {'black_tokens': get_rand_color(),
#           'white_tokens': get_rand_color(),
#           'selection_frame': get_rand_color(),
#           'fields': get_rand_color(),
#           'text': (0,0,0),
#           'background': get_rand_color(background_seed),
#           'token_stash': get_rand_color(background_seed),
#           'pick_notif': get_rand_color()}

# ==== SHAPES ==== 
FIELDS = [(50+i*100, 50+j*100, 95, 95) for j in range(4) for i in range(4)]
LEFT_TOKEN_AREAS = [(600+i*60, 100+j*60, 55, 55) for i in range(2) for j in range(4)]
left_tokens = list(zip(['C', 'S', 'T', 'H', 'C', 'S', 'T', 'H'], LEFT_TOKEN_AREAS))
# parameters for drawing the tokens
CIRCLE_RADIUS = 40
BASE_TRIANGLE = [Vector2(-40,35), Vector2(40,35), Vector2(0,-35)]
SQUARE_LENGTH = 60

# define rectangles for text and buttons
NOTIF_BANNER = (100, 10, 350, 25)
CHOSE_BLACK_BUTTON = (500, 10, 100, 30)
CHOSE_WHITE_BUTTON = (620, 10, 100, 30)

def draw_token(screen, color, token_type, center_coordinates, scale=1):
    """
    token_types:
    C: circle, T: Triangle, H: halfcircle, s: square
    """
    if token_type=='C':
        pygame.draw.circle(screen, color, center_coordinates, scale*CIRCLE_RADIUS)
    elif token_type=='T':
        pygame.draw.polygon(screen, color, [scale*p+center_coordinates for p in BASE_TRIANGLE]),
    elif token_type=='S':
        pygame.draw.rect(screen, color, Rect(center_coordinates[0] - scale*SQUARE_LENGTH/2,
                                                      center_coordinates[1] - scale*SQUARE_LENGTH/2,
                                                      scale*SQUARE_LENGTH, scale*SQUARE_LENGTH)),
    elif token_type=='H':
        pygame.draw.circle(screen, color, center_coordinates + Vector2(0, scale*CIRCLE_RADIUS/2), scale*CIRCLE_RADIUS, 
                                   draw_top_right=True, draw_top_left=True)
    return 

def is_pos_in_rect(pos, r): 
    """check if given coordinates are a point in given rectangle"""
    return (pos[0]>=r[0]) and (pos[0]<=r[0]+r[2]) and (pos[1]>=r[1]) and (pos[1]<=r[1]+r[3])

def get_player_choice_from_click(pos):
    """ get selection from player buttons click"""
    if is_pos_in_rect(pos, CHOSE_BLACK_BUTTON):
        return CHOSE_BLACK_BUTTON, 'b'
    elif is_pos_in_rect(pos, CHOSE_WHITE_BUTTON): 
        return CHOSE_WHITE_BUTTON, 'w'
    else:
        return None, None
    
def get_field_or_token_from_click(pos):
    """ get selection from click either on on token to pick
    or on field to put token
    return rectangle clicked, if field or a token (and which) was selected, 
    and enumaration of the field"""
    if pos[0] < 600:
        for enum, r in enumerate(FIELDS):
            if is_pos_in_rect(pos, r):
                kind = 'field'
                return r, kind, enum
        return None, None, None
    else:
        for enum, (t, r) in enumerate(left_tokens):
            if is_pos_in_rect(pos, r):
                kind = t
                return r, kind, enum
        return None, None, None

def get_rect_center(rect):
    """get the center coordinates of a rectangle"""
    return Vector2(rect[0]+0.5*rect[2], rect[1]+0.5*rect[3])

# TODO:
def update_banner(stage, game_inst=None):
    if game_inst and game_inst.winner:
        if game_inst.winner == player_choice:
            text = "You Win! Pick color for new game"
        else:
            text = "Computer Wins! Pick color for new game"
        label = font.render(text, 1, COLORS['text'])
        pygame.draw.rect(screen, COLORS['pick_notif'], Rect(NOTIF_BANNER))
        screen.blit(label, NOTIF_BANNER[:2])
        pygame.draw.rect(screen, COLORS['pick_notif'], Rect(CHOSE_WHITE_BUTTON))
        pygame.draw.rect(screen, COLORS['pick_notif'], Rect(CHOSE_BLACK_BUTTON))
        text_b = font.render("black", 1, COLORS['text'])
        text_w = font.render("white", 1, COLORS['text'])
        screen.blit(text_w, CHOSE_WHITE_BUTTON[:2])
        screen.blit(text_b, CHOSE_BLACK_BUTTON[:2])

    elif stage == "ai turn":
        text = "computer's turn"
        label = font.render(text, 1, COLORS['text'])
        pygame.draw.rect(screen, COLORS['pick_notif'], Rect(NOTIF_BANNER))
        screen.blit(label, NOTIF_BANNER[:2])
        pygame.draw.rect(screen, COLORS['background'], Rect(CHOSE_WHITE_BUTTON))
        pygame.draw.rect(screen, COLORS['background'], Rect(CHOSE_BLACK_BUTTON))
        
    elif stage == "your turn":
        text = "your turn (pick a token, then a field)"
        label = font.render(text, 1, COLORS['text'])
        pygame.draw.rect(screen, COLORS['pick_notif'], Rect(NOTIF_BANNER))
        screen.blit(label, NOTIF_BANNER[:2])
        pygame.draw.rect(screen, COLORS['background'], Rect(CHOSE_WHITE_BUTTON))
        pygame.draw.rect(screen, COLORS['background'], Rect(CHOSE_BLACK_BUTTON))
        
    elif stage == "entry":
        text = "pick token color (white begins) ->"
        label = font.render(text, 1, COLORS['text'])
        pygame.draw.rect(screen, COLORS['pick_notif'], Rect(NOTIF_BANNER))
        screen.blit(label, NOTIF_BANNER[:2])
        pygame.draw.rect(screen, COLORS['pick_notif'], Rect(CHOSE_WHITE_BUTTON))
        pygame.draw.rect(screen, COLORS['pick_notif'], Rect(CHOSE_BLACK_BUTTON))
        text_b = font.render("black", 1, COLORS['text'])
        text_w = font.render("white", 1, COLORS['text'])
        screen.blit(text_w, CHOSE_WHITE_BUTTON[:2])
        screen.blit(text_b, CHOSE_BLACK_BUTTON[:2])
            
    return 


pygame.init()
screen = pygame.display.set_mode(SIZE)
screen.fill(COLORS['background'])
for r in FIELDS:
    pygame.draw.rect(screen, COLORS['fields'], Rect(r))


pygame.display.flip()
running = True
f_select = None 
picked_token = None

"""
TODO:
- check if winner and stop update and show
- allow play w and b 
- text displays, for ai comp, etc.
- why does ai play so bad ?
"""

player_choice = None
player_color_map = {'w': COLORS['white_tokens'], 'b': COLORS['black_tokens']}
ai_color_map = {'w': COLORS['black_tokens'], 'b': COLORS['white_tokens']}
update_banner("entry")
while running:
    
    if player_choice and q_game.winner:
        player_choice = None

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif not player_choice:
            # if player not yet selected, wait for selection
            if event.type == MOUSEBUTTONDOWN:
                r, player_choice = get_player_choice_from_click(event.pos)
                if r:
                    # reset game class and visuals to start of new round
                    q_game = QuantikAI()
                    left_tokens = list(zip(['C', 'S', 'T', 'H', 'C', 'S', 'T', 'H'], LEFT_TOKEN_AREAS))
                    #pygame.draw.rect(screen, COLORS['selection_frame'], Rect(r), width=2)
                    for t, r in left_tokens:
                        pygame.draw.rect(screen, COLORS['token_stash'], Rect(r))
                        r_center = get_rect_center(r)
                        draw_token(screen, player_color_map[player_choice], t, r_center, scale=0.4)
                    for r in FIELDS:
                        pygame.draw.rect(screen, COLORS['fields'], Rect(r))
                    if player_choice == 'b':
                        update_banner("ai turn")
                    else: 
                        update_banner("your turn")
            

        elif q_game.player != player_choice:
            # turn of the ai to play
            pygame.time.delay(500)
            q_game.make_AI_move(method=AI_METHOD)
            # get the field and token of ai move and draw it
            ai_move_field, ai_move_token = q_game.move_sequence[-1]
            field_idx = q_game.fields.index(ai_move_field)
            field_center_coordinates = get_rect_center(FIELDS[field_idx])
            draw_token(screen, ai_color_map[player_choice], ai_move_token, field_center_coordinates)
            #pygame.draw.rect(screen, COLORS['background'], Rect(NOTIF_BANNER))
            update_banner("your turn", game_inst=q_game)

        elif event.type == MOUSEBUTTONDOWN:
            update_banner("your turn")
            r, kind, enum = get_field_or_token_from_click(event.pos)
            #  if a token is already selected, click was on field and the field and selected token comprise a legit move
            if (picked_token and kind and (kind == 'field') and 
                 ((q_game.fields[enum], picked_token) in q_game.get_possible_moves())): 
                # remove used token
                pygame.draw.rect(screen, COLORS['token_stash'], Rect(picked_token_r))
                left_tokens[picked_token_enum] = (None, picked_token_r)
                # draw token to clicked field
                r_center = get_rect_center(r)
                draw_token(screen, player_color_map[player_choice], picked_token, r_center)
                # make the move on game instance
                q_game.make_move((q_game.fields[enum], picked_token))
                update_banner("ai turn", game_inst=q_game)
                picked_token = None
                picked_token_r = None
                picked_token_enum = None
            # if instead token stash was clicked
            elif kind and (kind != 'field'):
                # remove previous selection highlight
                if picked_token:
                    pygame.draw.rect(screen, COLORS['token_stash'], Rect(picked_token_r), width=1)
                # highlight this selection
                pygame.draw.rect(screen, COLORS['selection_frame'], Rect(r), width=1)
                picked_token = kind
                picked_token_r = r
                picked_token_enum = enum     
      
    pygame.display.flip()
    
pygame.quit()

