"""Versao 2: inputs e movimento por vetores de direcao.

Evolucao da v1: em vez de mover so enquanto a tecla esta pressionada, o
personagem agora anda sozinho na direcao atual (dir_x, dir_y). As teclas
trocam essa direcao, com uma "trava de eixo" que impede a inversao direta
de sentido (base para a mecanica da cobra). O jogo comeca andando para a direita.
"""

import pygame
import sys

pygame.init()

# --- Configuracoes da janela ---
LARGURA_TELA = 800
ALTURA_TELA = 600
TITULO = "Python Snake - Introdução ao PyGame"
FPS = 60

# --- Cores (R, G, B) ---
COR_FUNDO = (30, 41, 59)
COR_RETANGULO = (55, 118, 171)

# Cria a janela e define o titulo.
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption(TITULO)

relogio = pygame.time.Clock()  # controla a taxa de quadros (FPS)

tam_personagem = 50

# Posicao inicial: centraliza o personagem na tela.
pos_x = (LARGURA_TELA - tam_personagem) // 2
pos_y = (ALTURA_TELA - tam_personagem) // 2

velocidade_base = 5  # pixels por quadro

# Vetor de direcao atual: o jogo comeca andando para a direita.
dir_x = velocidade_base
dir_y = 0

imagem_personagem = None
usa_imagem = False

# Tenta carregar a imagem do personagem; se nao existir, gera uma textura alternativa.
try:
    imagem_original = pygame.image.load("personagem.png")

    imagem_personagem = pygame.transform.scale(imagem_original, (tam_personagem, tam_personagem))
    usa_imagem = True
    print("[INFO] Imagem 'personagem.png' carregada com sucesso!")

except FileNotFoundError:
    print("[Aviso] Imagem 'personagem.png' não encontrada. Criando uma textura alternativa em memória...")

    # Desenha uma carinha simples numa superficie transparente.
    imagem_personagem = pygame.Surface((tam_personagem, tam_personagem), pygame.SRCALPHA)

    pygame.draw.circle(imagem_personagem, (254, 240, 138), (tam_personagem // 2, tam_personagem // 2),
                       tam_personagem // 2)  # rosto
    pygame.draw.circle(imagem_personagem, (15, 23, 42), (tam_personagem // 3, tam_personagem // 3), 4)  # olho esquerdo
    pygame.draw.circle(imagem_personagem, (15, 23, 42), (2 * tam_personagem // 3, tam_personagem // 3),
                       4)  # olho direito
    pygame.draw.arc(imagem_personagem, (15, 23, 42),
                    (tam_personagem // 4, tam_personagem // 3, tam_personagem // 2, tam_personagem // 3), 3.14, 0,
                    2)  # sorriso

    usa_imagem = True

# --- Loop principal do jogo ---
rodando = True
while rodando:
    # Trata os eventos: fechar a janela e teclas pressionadas (KEYDOWN = clique unico).
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        elif evento.type == pygame.KEYDOWN:
            # Cada direcao so e aceita se o eixo correspondente estiver livre (trava de eixo),
            # evitando que o personagem inverta o sentido diretamente.
            if evento.key in [pygame.K_LEFT, pygame.K_a]:
                if dir_x == 0:
                    dir_x = -velocidade_base
                    dir_y = 0

            elif evento.key in [pygame.K_RIGHT, pygame.K_d]:
                if dir_x == 0:
                    dir_x = velocidade_base
                    dir_y = 0

            elif evento.key in [pygame.K_UP, pygame.K_w]:
                if dir_y == 0:
                    dir_x = 0
                    dir_y = -velocidade_base

            elif evento.key in [pygame.K_DOWN, pygame.K_s]:
                if dir_y == 0:
                    dir_x = 0
                    dir_y = velocidade_base

    # Movimento automatico e continuo: aplica o vetor de direcao a cada quadro.
    pos_x += dir_x
    pos_y += dir_y

    # Colisao com as bordas: trava na borda e zera o eixo (libera comando no outro eixo).
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

    # Desenha o quadro: limpa o fundo e desenha o personagem.
    tela.fill(COR_FUNDO)

    if usa_imagem:
        tela.blit(imagem_personagem, (pos_x, pos_y))
    else:
        pygame.draw.rect(tela, COR_RETANGULO, (pos_x, pos_y, tam_personagem, tam_personagem))

    pygame.display.flip()  # atualiza a tela com o que foi desenhado

    relogio.tick(FPS)  # mantem a taxa de FPS definida

pygame.quit()
sys.exit()