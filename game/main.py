import pygame
import sys

pygame.init()

# --- Configuracoes da janela ---
LARGURA_TELA = 800
ALTURA_TELA = 600
TITULO = "Python Snake - Introdução ao PyGame"
FPS = 60

# --- Cores (R,G,B) ---
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

velocidade = 6  # pixels por quadro

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
    # Trata os eventos (ex.: fechar a janela).
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # Le o estado atual do teclado (permite movimento continuo enquanto a tecla esta pressionada).
    teclas = pygame.key.get_pressed()

    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
        pos_x -= velocidade
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
        pos_x += velocidade
    if teclas[pygame.K_UP] or teclas[pygame.K_w]:
        pos_y -= velocidade
    if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
        pos_y += velocidade

    # Impede o personagem de sair pelas bordas (limita a posicao a area da tela).
    if pos_x < 0:
        pos_x = 0
    elif pos_x > LARGURA_TELA - tam_personagem:
        pos_x = LARGURA_TELA - tam_personagem

    if pos_y < 0:
        pos_y = 0
    elif pos_y > ALTURA_TELA - tam_personagem:
        pos_y = ALTURA_TELA - tam_personagem

    # Desenha o quadro: limpa o fundo e desenha o personagem.
    tela.fill(COR_FUNDO)

    if usa_imagem:
        tela.blit(imagem_personagem, (pos_x, pos_y))
    else:
        pygame.draw.rect(tela, COR_RETANGULO, (pos_x, pos_y, tam_personagem, tam_personagem))

    pygame.display.flip()  # atualiza a tela com o que foi desenhado

    relogio.tick(FPS)  # espera o necessario para manter os FPS definidos

pygame.quit()
sys.exit()
