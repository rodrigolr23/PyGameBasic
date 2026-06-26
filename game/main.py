"""Versao 5: jogo da cobra com fases, vidas, bombas e recorde persistente.

Evolucao das versoes anteriores: agora a cobra cresce ao comer, ha sistema de
vidas, fases com dificuldade crescente (FPS, chance de bomba, metas de score),
itens com tempo de vida, vida extra a cada 100 pontos e recorde salvo em disco.
Se os sprites/sons nao forem encontrados, o jogo usa retangulos coloridos e
segue sem audio (fallback automatico).
"""

import pygame
import sys
import random
import os

pygame.init()
pygame.mixer.init()
pygame.font.init()

# --- Configuracoes da janela ---
LARGURA_TELA = 800
ALTURA_TELA = 600
TITULO = "Python Crash - v5: Recorde Persistente"

# --- Cores (R, G, B) ---
COR_FUNDO_PADRAO = (30, 41, 59)
COR_CABECA = (34, 197, 94)
COR_CORPO = (22, 163, 74)
COR_MACA = (239, 68, 68)
COR_BOMBA = (244, 63, 94)
COR_TEXTO = (248, 250, 252)
COR_DESTAQUE = (234, 179, 8)

# Efeito de fundo "estrobo" usado na fase final.
VELOCIDADE_STROBO = 150
CORES_STROBO = [(239, 68, 68), (34, 197, 94), (59, 130, 246), (234, 179, 8)]

# --- Caminhos de arquivos (assets e recorde), relativos a raiz do projeto ---
PASTA_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_IMAGENS = os.path.join(PASTA_RAIZ, "Imagens")
PASTA_SONS = os.path.join(PASTA_RAIZ, "sounds")
ARQUIVO_RECORDE = os.path.join(PASTA_RAIZ, "recorde.txt")

# Cria a janela, o relogio e as fontes do placar.
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption(TITULO)
relogio = pygame.time.Clock()
fonte_placar = pygame.font.SysFont("Arial", 24, bold=True)
fonte_titulo = pygame.font.SysFont("Arial", 48, bold=True)

# --- Estado da partida ---
score = 0
vidas = 3
fase_atual = 1
vidas_ganhas_consecutivas = 0
pontos_acumulados_proxima_vida = 0  # acumula pontos rumo a proxima vida extra

tam_personagem = 50
velocidade_base = tam_personagem  # move uma celula inteira por passo (grade alinhada)

# --- Estado da cobra ---
pos_x = 0
pos_y = 0
dir_x = 0
dir_y = 0
corpo_cobra = []  # lista de celulas [x, y]; indice 0 = cabeca
cobra_viva = True

# Configuracao de cada fase: FPS, chance de bomba, tempo de vida do item e meta de score.
CONFIG_FASES = {
    1: {"fps": 5, "chance_bomba": 0.15, "tempo_item": 6000, "meta_score": 50},
    2: {"fps": 6, "chance_bomba": 0.25, "tempo_item": 5000, "meta_score": 70},
    3: {"fps": 7, "chance_bomba": 0.35, "tempo_item": 4500, "meta_score": 90},
    4: {"fps": 8, "chance_bomba": 0.45, "tempo_item": 4000, "meta_score": 110},
    5: {"fps": 10, "chance_bomba": 0.60, "tempo_item": 5000, "meta_score": None},
}
FASE_MAXIMA = max(CONFIG_FASES.keys())

# Carrega os sprites; se algum faltar, desliga os sprites e o jogo usa retangulos.
sprites = {}
usa_sprites = True
arquivos_sprites = {
    "cabeca": "snake_green_head.png",
    "morta": "snake_green_xx.png",
    "corpo": "snake_green_blob.png",
    "maca_vermelha": "apple_alt.png",
    "maca_verde": "apple_green.png",
    "bomba": "bomb.png",
}
for chave, arquivo in arquivos_sprites.items():
    try:
        imagem = pygame.image.load(os.path.join(PASTA_IMAGENS, arquivo)).convert_alpha()
        sprites[chave] = pygame.transform.scale(imagem, (tam_personagem, tam_personagem))
    except (FileNotFoundError, pygame.error):
        usa_sprites = False

# Carrega os efeitos sonoros; ficam None (sem som) se os arquivos nao existirem.
som_morte = None
som_mordida = None
try:
    som_morte = pygame.mixer.Sound(os.path.join(PASTA_SONS, "morreu.mp3"))
except (FileNotFoundError, pygame.error):
    som_morte = None
try:
    som_mordida = pygame.mixer.Sound(os.path.join(PASTA_SONS, "crunchybite.ogg"))
except (FileNotFoundError, pygame.error):
    som_mordida = None


def carregar_recorde():
    """Le o recorde salvo em disco; devolve 0 se nao houver arquivo valido."""
    try:
        with open(ARQUIVO_RECORDE, "r", encoding="utf-8") as arquivo:
            return int(arquivo.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def salvar_recorde(valor):
    """Grava o recorde em disco, ignorando erros de escrita."""
    try:
        with open(ARQUIVO_RECORDE, "w", encoding="utf-8") as arquivo:
            arquivo.write(str(valor))
    except OSError:
        pass


recorde = carregar_recorde()

# --- Estado dos itens no tabuleiro ---
momento_geracao = 0  # instante (ms) em que os itens atuais foram gerados
pos_fruta = None
tipo_fruta = None
pos_bomba = None
bomba_ativa = False


def gerar_posicao_aleatoria():
    """Sorteia uma celula livre da grade (que nao esteja sobre o corpo da cobra)."""
    colunas = LARGURA_TELA // tam_personagem
    linhas = ALTURA_TELA // tam_personagem
    while True:
        x = random.randint(0, colunas - 1) * tam_personagem
        y = random.randint(0, linhas - 1) * tam_personagem
        if [x, y] not in corpo_cobra:
            return x, y


def spawnar_itens():
    """Gera os itens da rodada: as vezes uma bomba (com chance da fase), as vezes fruta."""
    global pos_fruta, tipo_fruta, pos_bomba, bomba_ativa, momento_geracao
    momento_geracao = pygame.time.get_ticks()
    chance_bomba = CONFIG_FASES[fase_atual]["chance_bomba"]
    if random.random() < chance_bomba:
        pos_bomba = gerar_posicao_aleatoria()
        bomba_ativa = True
        if random.random() < 0.50:  # com bomba, metade das vezes tambem sai fruta
            pos_fruta = gerar_posicao_aleatoria()
            tipo_fruta = random.choice(["vermelha", "verde"])
        else:
            pos_fruta = None
            tipo_fruta = None
    else:
        pos_fruta = gerar_posicao_aleatoria()
        tipo_fruta = random.choice(["vermelha", "verde"])
        pos_bomba = None
        bomba_ativa = False


def reiniciar_posicao_cobra():
    """Recoloca a cobra no centro, apontando para a direita, com tres segmentos."""
    global pos_x, pos_y, dir_x, dir_y, corpo_cobra, cobra_viva
    pos_x = (LARGURA_TELA // 2) // tam_personagem * tam_personagem
    pos_y = (ALTURA_TELA // 2) // tam_personagem * tam_personagem
    dir_x = velocidade_base
    dir_y = 0
    corpo_cobra = [
        [pos_x, pos_y],
        [pos_x - tam_personagem, pos_y],
        [pos_x - (2 * tam_personagem), pos_y],
    ]
    cobra_viva = True


def aplicar_morte_por_colisao():
    """Tira uma vida por bater na parede/corpo; se sobrar vida, recomeca a posicao."""
    global vidas, vidas_ganhas_consecutivas, pontos_acumulados_proxima_vida
    vidas -= 1
    vidas_ganhas_consecutivas = 0
    pontos_acumulados_proxima_vida = 0
    if som_morte:
        som_morte.play()
    if vidas > 0:
        reiniciar_posicao_cobra()
        spawnar_itens()


def aplicar_morte_por_bomba():
    """Morte por bomba: tira vida e ainda penaliza 100 pontos do score."""
    global score, vidas, vidas_ganhas_consecutivas, pontos_acumulados_proxima_vida
    vidas -= 1
    vidas_ganhas_consecutivas = 0
    score = max(0, score - 100)
    pontos_acumulados_proxima_vida = 0
    if som_morte:
        som_morte.play()
    if vidas > 0:
        reiniciar_posicao_cobra()
        spawnar_itens()


def reiniciar_partida():
    """Zera todo o estado para comecar uma nova partida (apos o game over)."""
    global score, vidas, fase_atual, vidas_ganhas_consecutivas, pontos_acumulados_proxima_vida
    score = 0
    vidas = 3
    fase_atual = 1
    vidas_ganhas_consecutivas = 0
    pontos_acumulados_proxima_vida = 0
    reiniciar_posicao_cobra()
    spawnar_itens()


# Prepara a primeira partida antes de entrar no loop.
reiniciar_posicao_cobra()
spawnar_itens()

# --- Loop principal do jogo ---
rodando = True
while rodando:
    tempo_atual = pygame.time.get_ticks()
    config_fase_atual = CONFIG_FASES[fase_atual]
    tempo_limite_item = config_fase_atual["tempo_item"]

    # Eventos: fechar a janela e teclas. No game over, qualquer tecla reinicia.
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.KEYDOWN:
            if vidas <= 0:
                reiniciar_partida()
                continue
            # Trava de eixo: so vira se o eixo correspondente estiver parado (nao inverte direto).
            if evento.key in [pygame.K_LEFT, pygame.K_a] and dir_x == 0:
                dir_x = -velocidade_base
                dir_y = 0
            elif evento.key in [pygame.K_RIGHT, pygame.K_d] and dir_x == 0:
                dir_x = velocidade_base
                dir_y = 0
            elif evento.key in [pygame.K_UP, pygame.K_w] and dir_y == 0:
                dir_x = 0
                dir_y = -velocidade_base
            elif evento.key in [pygame.K_DOWN, pygame.K_s] and dir_y == 0:
                dir_x = 0
                dir_y = velocidade_base

    if vidas > 0:
        # Se o item ficou tempo demais na tela, gera novos itens.
        if tempo_atual - momento_geracao > tempo_limite_item:
            spawnar_itens()

        # Calcula a proxima posicao da cabeca a partir da direcao atual.
        proximo_x = pos_x + dir_x
        proximo_y = pos_y + dir_y

        # Colisao com as bordas -> perde uma vida.
        if proximo_x < 0 or proximo_x > LARGURA_TELA - tam_personagem or proximo_y < 0 or proximo_y > ALTURA_TELA - tam_personagem:
            aplicar_morte_por_colisao()
            continue

        # Colisao com o proprio corpo -> perde uma vida.
        nova_cabeca = [proximo_x, proximo_y]
        if nova_cabeca in corpo_cobra:
            aplicar_morte_por_colisao()
            continue

        # Colisao com a bomba (cabeca ou qualquer parte do corpo) -> morte por bomba.
        colidiu_com_bomba = False
        if bomba_ativa and pos_bomba:
            if nova_cabeca == list(pos_bomba):
                colidiu_com_bomba = True
            else:
                for parte in corpo_cobra:
                    if parte == list(pos_bomba):
                        colidiu_com_bomba = True
                        break
        if colidiu_com_bomba:
            aplicar_morte_por_bomba()
            continue

        # Move a cobra: avanca a cabeca inserindo a nova celula no inicio da lista.
        pos_x = proximo_x
        pos_y = proximo_y
        corpo_cobra.insert(0, nova_cabeca)

        # Verifica se comeu a fruta.
        comeu_fruta = False
        if pos_fruta and nova_cabeca == list(pos_fruta):
            comeu_fruta = True
            if som_mordida:
                som_mordida.play()
            score += 10
            pontos_acumulados_proxima_vida += 10
            if score > recorde:
                recorde = score
                salvar_recorde(recorde)
            # A cada 100 pontos ganha uma vida extra (ate o limite de 6).
            if pontos_acumulados_proxima_vida >= 100:
                pontos_acumulados_proxima_vida -= 100
                if vidas < 6:
                    vidas += 1
                    vidas_ganhas_consecutivas += 1
            # Avanca de fase ao atingir a meta de score da fase atual.
            if fase_atual < FASE_MAXIMA:
                meta_score_fase = CONFIG_FASES[fase_atual]["meta_score"]
                if score >= meta_score_fase:
                    fase_atual += 1
                    vidas_ganhas_consecutivas = 0
            spawnar_itens()

        # Se nao comeu, remove a cauda (mantem o tamanho); se comeu, a cobra cresce.
        if not comeu_fruta:
            corpo_cobra.pop()

    # Fundo: na fase final pisca em cores (estrobo); nas demais, cor fixa.
    if fase_atual == FASE_MAXIMA and vidas > 0:
        indice_cor = (tempo_atual // VELOCIDADE_STROBO) % len(CORES_STROBO)
        cor_fundo_atual = CORES_STROBO[indice_cor]
    else:
        cor_fundo_atual = COR_FUNDO_PADRAO
    tela.fill(cor_fundo_atual)

    # Desenha a fruta (sprite ou retangulo de reserva).
    if pos_fruta:
        if usa_sprites:
            tela.blit(sprites["maca_vermelha"] if tipo_fruta == "vermelha" else sprites["maca_verde"], pos_fruta)
        else:
            pygame.draw.rect(tela, COR_MACA, (pos_fruta[0] + 5, pos_fruta[1] + 5, tam_personagem - 10, tam_personagem - 10))

    # Desenha a bomba, se ativa.
    if bomba_ativa and pos_bomba:
        if usa_sprites:
            tela.blit(sprites["bomba"], pos_bomba)
        else:
            pygame.draw.rect(tela, COR_BOMBA, (pos_bomba[0] + 5, pos_bomba[1] + 5, tam_personagem - 10, tam_personagem - 10))

    # Desenha a cobra: indice 0 e a cabeca (viva/morta), o resto e corpo.
    for indice, parte in enumerate(corpo_cobra):
        if indice == 0:
            if usa_sprites:
                tela.blit(sprites["cabeca"] if vidas > 0 else sprites["morta"], (parte[0], parte[1]))
            else:
                cor_cabeca = COR_CABECA if vidas > 0 else (127, 136, 140)
                pygame.draw.rect(tela, cor_cabeca, (parte[0], parte[1], tam_personagem, tam_personagem))
        else:
            if usa_sprites:
                tela.blit(sprites["corpo"], (parte[0], parte[1]))
            else:
                pygame.draw.rect(tela, COR_CORPO, (parte[0] + 2, parte[1] + 2, tam_personagem - 4, tam_personagem - 4))

    # HUD: score, recorde, vidas e fase.
    texto_fase = f"FASE: {fase_atual}" if fase_atual < FASE_MAXIMA else "FASE: FINAL"
    tela.blit(fonte_placar.render(f"SCORE: {score}", True, COR_TEXTO), (20, 20))
    tela.blit(fonte_placar.render(f"RECORDE: {recorde}", True, COR_DESTAQUE), (20, 50))
    tela.blit(fonte_placar.render(f"VIDAS: {vidas}", True, COR_TEXTO), (LARGURA_TELA - 160, 20))
    tela.blit(fonte_placar.render(texto_fase, True, COR_TEXTO), (LARGURA_TELA - 160, 50))

    # Tela de game over (quando acabam as vidas), com pontuacao e instrucao.
    if vidas <= 0:
        sobreposicao = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        sobreposicao.set_alpha(180)
        sobreposicao.fill((0, 0, 0))
        tela.blit(sobreposicao, (0, 0))
        titulo_fim = fonte_titulo.render("GAME OVER", True, COR_MACA)
        info_score = fonte_placar.render(f"Pontuacao: {score}", True, COR_TEXTO)
        info_recorde = fonte_placar.render(f"Recorde: {recorde}", True, COR_DESTAQUE)
        info_reinicio = fonte_placar.render("Pressione qualquer tecla para jogar de novo", True, COR_TEXTO)
        tela.blit(titulo_fim, (LARGURA_TELA // 2 - titulo_fim.get_width() // 2, ALTURA_TELA // 2 - 110))
        tela.blit(info_score, (LARGURA_TELA // 2 - info_score.get_width() // 2, ALTURA_TELA // 2 - 30))
        tela.blit(info_recorde, (LARGURA_TELA // 2 - info_recorde.get_width() // 2, ALTURA_TELA // 2 + 5))
        tela.blit(info_reinicio, (LARGURA_TELA // 2 - info_reinicio.get_width() // 2, ALTURA_TELA // 2 + 60))

    pygame.display.flip()
    relogio.tick(config_fase_atual["fps"])  # a velocidade do jogo depende da fase

pygame.quit()
sys.exit()