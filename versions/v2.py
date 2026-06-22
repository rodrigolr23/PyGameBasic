import pygame
import sys

from game.settings import dir_x, velocidade_base

pygame.init()

LARGURA_TELA = 800
ALTURA_TELA = 600
TITULO = "Python Snake - Introdução ao PyGame"
FPS = 60

COR_FUNDO = (30, 41, 59)
COR_RETANGULO = (55, 118, 171)

tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption(TITULO)

relogio = pygame.time.Clock()

tam_personagem = 50

pos_x = (LARGURA_TELA - tam_personagem) // 2
pos_y = (ALTURA_TELA - tam_personagem) // 2

velocidade = 6

imagem_personagem = None
usa_imagem = False

try:
    imagem_original = pygame.image.load("personagem.png")

    imagem_personagem = pygame.transform.scale(imagem_original, (tam_personagem, tam_personagem))
    usa_imagem = True
    print("[INFO] Imagem 'personagem.png' carregada com sucesso!")

except FileNotFoundError:
    print("[Aviso] Imagem 'personagem.png' não encontrada. Criando uma textura alternativa em memória...")

    imagem_personagem = pygame.Surface((tam_personagem, tam_personagem), pygame.SRCALPHA)

    pygame.draw.circle(imagem_personagem, (254, 240, 138), (tam_personagem // 2, tam_personagem // 2),
                       tam_personagem // 2)
    pygame.draw.circle(imagem_personagem, (15, 23, 42), (tam_personagem // 3, tam_personagem // 3), 4)
    pygame.draw.circle(imagem_personagem, (15, 23, 42), (2 * tam_personagem // 3, tam_personagem // 3),
                       4)
    pygame.draw.arc(imagem_personagem, (15, 23, 42),
                    (tam_personagem // 4, tam_personagem // 3, tam_personagem // 2, tam_personagem // 3), 3.14, 0,
                    2)

    usa_imagem = True

rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        elif evento.type == pygame.KEYDOWN:
            if evento.key in [pygame.K_LEFT,pygame.K_a]:
                if dir_x == 0:
                    dir_x = -velocidade_base
                    dir_y = 0

            elif evento.key in [pygame.K_RIGHT,pygame.K_d]:
                if dir_x == 0:
                    dir_x = -velocidade_base
                    dir_y = 0

            elif evento.key in [pygame.K_UP, pygame.K_w]:
                if dir_x == 0:
                    dir_x = -velocidade_base
                    dir_y = 0

            elif evento.key in [pygame.K_DOWN, pygame.K_s]:
                if dir_x == 0:
                    dir_x = -velocidade_base
                    dir_y = 0
    pos_x += dir_x
    pos_y += dir_y

    if pos_x < 0:
        pos_x = 0
        dir_x = 0
    elif pos_x > LARGURA_TELA - tam_personagem:
        pos_x = LARGURA_TELA - tam_personagem
        dir_x = 0

    if pos_y < 0:
        pos_y = 0
        dir_y = 0
    elif pos_y > ALTURA_TELA - tam_personagem:
        pos_y = ALTURA_TELA - tam_personagem
        dir_y = 0

    tela.fill(COR_FUNDO)

    if usa_imagem:
        tela.blit(imagem_personagem, (pos_x, pos_y))
    else:
        pygame.draw.rect(tela, COR_RETANGULO, (pos_x, pos_y, tam_personagem, tam_personagem))

    pygame.display.flip()

    relogio.tick(FPS)

pygame.quit()
sys.exit()
#test