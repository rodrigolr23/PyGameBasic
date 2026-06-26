import pygame
import sys
import random
import os
from collections import deque

pygame.init()
pygame.mixer.init()
pygame.font.init()

CELL = 40
COLS = 21
ROWS = 14
PLAY_W = COLS * CELL
PLAY_H = ROWS * CELL
MARGEM_X = 30
PLAY_TOP = 150
LARGURA_TELA = PLAY_W + 2 * MARGEM_X
ALTURA_TELA = PLAY_TOP + PLAY_H + 90
TITULO = "Serpente - New York"

COR_CEU_TOPO = (150, 32, 32)
COR_CEU_BASE = (52, 12, 16)
COR_PREDIO = (16, 12, 18)
COR_JANELA = (228, 196, 110)
COR_FEIXE = (236, 226, 150)
COR_CREME = (233, 224, 202)
COR_OURO = (201, 162, 75)
COR_PAINEL = (17, 14, 20)
COR_GRADE = (38, 30, 40)
COR_TEXTO = (233, 224, 202)
COR_CARTELA = (12, 9, 13)

COR_CORPO = (28, 82, 48)
COR_CORPO_CLARO = (54, 124, 70)
COR_CORPO_ESCURO = (10, 36, 22)
COR_OLHO = (245, 224, 86)
COR_PUPILA = (150, 16, 16)
COR_PRESA = (240, 236, 222)

VEL_INICIAL = 7.0
GANHO_POR_FRUTA = 0.25
PENALIDADE_VELOCIDADE = 1.0
MARCO_PENALIDADE = 150
PONTOS_PAUSA = 100
VEL_MAXIMA = 25.0
VEL_MINIMA = 4.0
PONTOS_POR_FRUTA = 10

PASTA_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_FRUTAS = os.path.join(PASTA_RAIZ, "Imagens", "frutas")
ARQUIVO_RECORDE = os.path.join(PASTA_RAIZ, "recorde.txt")


def achar_pasta(*nomes):
    for nome in nomes:
        caminho = os.path.join(PASTA_RAIZ, nome)
        if os.path.isdir(caminho):
            return caminho
    return os.path.join(PASTA_RAIZ, nomes[0])


PASTA_SONS = achar_pasta("Sounds", "Sons")

tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption(TITULO)
relogio = pygame.time.Clock()
fonte_titulo = pygame.font.SysFont("bahnschrift,arialblack,arial", 54, bold=True)
fonte_placar = pygame.font.SysFont("bahnschrift,arial", 24, bold=True)
fonte_pequena = pygame.font.SysFont("bahnschrift,arial", 18, bold=True)
fonte_fim = pygame.font.SysFont("bahnschrift,arialblack,arial", 72, bold=True)

NOMES_FRUTAS = ["maca", "melancia", "banana", "laranja", "cereja", "abacaxi", "uva", "limao", "morango"]


def carregar_frutas():
    catalogo = {}
    for nome in NOMES_FRUTAS:
        try:
            imagem = pygame.image.load(os.path.join(PASTA_FRUTAS, nome + ".png")).convert_alpha()
        except (FileNotFoundError, pygame.error):
            continue
        largura, altura = imagem.get_size()
        alvo = CELL - 6
        escala = alvo / max(largura, altura)
        imagem = pygame.transform.scale(imagem, (max(1, int(largura * escala)), max(1, int(altura * escala))))
        catalogo[nome] = imagem
    return catalogo


def carregar_som(nome):
    try:
        return pygame.mixer.Sound(os.path.join(PASTA_SONS, nome))
    except (FileNotFoundError, pygame.error):
        return None


def carregar_recorde():
    try:
        with open(ARQUIVO_RECORDE, "r", encoding="utf-8") as arquivo:
            return int(arquivo.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def salvar_recorde(valor):
    try:
        with open(ARQUIVO_RECORDE, "w", encoding="utf-8") as arquivo:
            arquivo.write(str(valor))
    except OSError:
        pass


def interpolar_cor(cor_a, cor_b, fator):
    return tuple(int(a + (b - a) * fator) for a, b in zip(cor_a, cor_b))


def desenhar_gradiente(superficie):
    for y in range(ALTURA_TELA):
        fator = y / (ALTURA_TELA - 1)
        pygame.draw.line(superficie, interpolar_cor(COR_CEU_TOPO, COR_CEU_BASE, fator), (0, y), (LARGURA_TELA, y))


def desenhar_feixes(superficie):
    feixes = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    topo = (LARGURA_TELA // 2, -30)
    pygame.draw.polygon(feixes, (*COR_FEIXE, 42), [topo, (LARGURA_TELA * 0.02, ALTURA_TELA * 0.72), (LARGURA_TELA * 0.28, ALTURA_TELA * 0.78)])
    pygame.draw.polygon(feixes, (*COR_FEIXE, 42), [topo, (LARGURA_TELA * 0.72, ALTURA_TELA * 0.78), (LARGURA_TELA * 0.98, ALTURA_TELA * 0.72)])
    pygame.draw.polygon(feixes, (*COR_FEIXE, 26), [topo, (LARGURA_TELA * 0.40, ALTURA_TELA), (LARGURA_TELA * 0.60, ALTURA_TELA)])
    superficie.blit(feixes, (0, 0))


def desenhar_skyline(superficie, base_y, altura_min, altura_max, gerador):
    x = -10
    while x < LARGURA_TELA:
        largura_predio = gerador.randint(42, 92)
        altura_predio = gerador.randint(altura_min, altura_max)
        topo = base_y - altura_predio
        pygame.draw.rect(superficie, COR_PREDIO, (x, topo, largura_predio, base_y - topo))
        passo_largura = largura_predio
        topo_passo = topo
        for _ in range(2):
            passo_largura = int(passo_largura * 0.6)
            centro = x + (largura_predio - passo_largura) // 2
            topo_passo -= 11
            pygame.draw.rect(superficie, COR_PREDIO, (centro, topo_passo, passo_largura, 13))
        pygame.draw.rect(superficie, COR_PREDIO, (x + largura_predio // 2 - 2, topo_passo - 16, 4, 18))
        for janela_y in range(topo + 9, base_y - 4, 11):
            for janela_x in range(x + 6, x + largura_predio - 5, 10):
                if gerador.random() < 0.55:
                    superficie.fill(COR_JANELA, (janela_x, janela_y, 3, 4))
        x += largura_predio + gerador.randint(2, 10)


def desenhar_moldura(superficie):
    x0 = MARGEM_X - 12
    y0 = PLAY_TOP - 12
    largura = PLAY_W + 24
    altura = PLAY_H + 24
    pygame.draw.rect(superficie, COR_OURO, (x0, y0, largura, altura), 4)
    pygame.draw.rect(superficie, COR_CREME, (x0 - 6, y0 - 6, largura + 12, altura + 12), 2)
    for canto_x, canto_y in [(x0, y0), (x0 + largura, y0), (x0, y0 + altura), (x0 + largura, y0 + altura)]:
        pygame.draw.rect(superficie, COR_OURO, (canto_x - 8, canto_y - 8, 16, 16))
        pygame.draw.rect(superficie, COR_CEU_BASE, (canto_x - 4, canto_y - 4, 8, 8))
    centro_x = LARGURA_TELA // 2
    for i in range(-3, 4):
        pygame.draw.line(superficie, COR_OURO, (centro_x, y0 - 10), (centro_x + i * 16, y0 - 34), 2)


def criar_segmento_corpo():
    segmento = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    pygame.draw.rect(segmento, COR_CORPO_ESCURO, (1, 1, CELL - 2, CELL - 2))
    pygame.draw.rect(segmento, COR_CORPO, (3, 3, CELL - 6, CELL - 6))
    centro = CELL // 2
    losango = [(centro, 7), (CELL - 7, centro), (centro, CELL - 7), (7, centro)]
    pygame.draw.polygon(segmento, COR_CORPO_CLARO, losango)
    pygame.draw.polygon(segmento, COR_CORPO_ESCURO, losango, 1)
    return segmento


def centro_y(deslocamento):
    return CELL // 2 + deslocamento


def criar_cabeca(morta=False):
    cabeca = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    pygame.draw.rect(cabeca, COR_CORPO_ESCURO, (1, 1, CELL - 2, CELL - 2))
    pygame.draw.rect(cabeca, COR_CORPO, (3, 3, CELL - 6, CELL - 6))
    pygame.draw.rect(cabeca, COR_CORPO_CLARO, (CELL - 12, 8, 7, CELL - 16))
    if morta:
        for cima in (11, CELL - 11):
            pygame.draw.line(cabeca, COR_PUPILA, (CELL - 22, cima - 4), (CELL - 10, cima + 4), 3)
            pygame.draw.line(cabeca, COR_PUPILA, (CELL - 22, cima + 4), (CELL - 10, cima - 4), 3)
    else:
        olho_superior = [(CELL - 23, 7), (CELL - 8, 11), (CELL - 11, 18), (CELL - 24, 14)]
        olho_inferior = [(CELL - 23, CELL - 7), (CELL - 8, CELL - 11), (CELL - 11, CELL - 18), (CELL - 24, CELL - 14)]
        pygame.draw.polygon(cabeca, COR_OLHO, olho_superior)
        pygame.draw.polygon(cabeca, COR_OLHO, olho_inferior)
        pygame.draw.polygon(cabeca, COR_PUPILA, [(CELL - 14, 11), (CELL - 8, 12), (CELL - 10, 17)])
        pygame.draw.polygon(cabeca, COR_PUPILA, [(CELL - 14, CELL - 11), (CELL - 8, CELL - 12), (CELL - 10, CELL - 17)])
        pygame.draw.line(cabeca, COR_CORPO_ESCURO, (CELL - 26, 9), (CELL - 8, 4), 3)
        pygame.draw.line(cabeca, COR_CORPO_ESCURO, (CELL - 26, CELL - 9), (CELL - 8, CELL - 4), 3)
    pygame.draw.polygon(cabeca, COR_PRESA, [(CELL - 5, centro_y(-7)), (CELL - 1, centro_y(-4)), (CELL - 7, centro_y(-2))])
    pygame.draw.polygon(cabeca, COR_PRESA, [(CELL - 5, centro_y(7)), (CELL - 1, centro_y(4)), (CELL - 7, centro_y(2))])
    return cabeca


ANGULOS = {(1, 0): 0, (0, -1): 90, (-1, 0): 180, (0, 1): -90}


def construir_fundo():
    fundo = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
    desenhar_gradiente(fundo)
    desenhar_feixes(fundo)
    desenhar_skyline(fundo, PLAY_TOP, 60, 138, random.Random(7))
    desenhar_skyline(fundo, ALTURA_TELA, 40, 92, random.Random(23))
    sombra = fonte_titulo.render("SERPENTE", True, (18, 8, 10))
    titulo = fonte_titulo.render("SERPENTE", True, COR_CREME)
    fundo.blit(sombra, (LARGURA_TELA // 2 - titulo.get_width() // 2 + 3, 27))
    fundo.blit(titulo, (LARGURA_TELA // 2 - titulo.get_width() // 2, 24))
    subtitulo = fonte_pequena.render("A R T   D E C O   ·   N E W   Y O R K", True, COR_OURO)
    fundo.blit(subtitulo, (LARGURA_TELA // 2 - subtitulo.get_width() // 2, 84))
    pygame.draw.rect(fundo, COR_PAINEL, (MARGEM_X, PLAY_TOP, PLAY_W, PLAY_H))
    for coluna in range(COLS + 1):
        x = MARGEM_X + coluna * CELL
        pygame.draw.line(fundo, COR_GRADE, (x, PLAY_TOP), (x, PLAY_TOP + PLAY_H))
    for linha in range(ROWS + 1):
        y = PLAY_TOP + linha * CELL
        pygame.draw.line(fundo, COR_GRADE, (MARGEM_X, y), (MARGEM_X + PLAY_W, y))
    desenhar_moldura(fundo)
    return fundo


def desenhar_cartela(texto, centro, cor):
    superficie = fonte_placar.render(texto, True, cor)
    retangulo = superficie.get_rect(center=centro)
    moldura = retangulo.inflate(22, 12)
    pygame.draw.rect(tela, COR_CARTELA, moldura)
    pygame.draw.rect(tela, COR_OURO, moldura, 2)
    tela.blit(superficie, retangulo)


def celula_para_pixel(coluna, linha):
    return MARGEM_X + coluna * CELL, PLAY_TOP + linha * CELL


frutas = carregar_frutas()
som_mordida = carregar_som("comer.wav")
som_morte = carregar_som("morte.wav")
som_nivel = carregar_som("nivel.wav")
fundo_estatico = construir_fundo()
segmento_corpo = criar_segmento_corpo()
cabeca_viva = criar_cabeca(False)
cabeca_morta = criar_cabeca(True)
recorde = carregar_recorde()

corpo_cobra = []
direcao = (1, 0)
fila_direcoes = deque(maxlen=3)
score = 0
frutas_comidas = 0
fase = 1
velocidade = VEL_INICIAL
pausa_ate = 0
acumulador = 0.0
estado = "jogando"
lista_frutas = []


def fase_atual():
    return score // MARCO_PENALIDADE + 1


def quantidade_frutas():
    return 1 if fase_atual() < 2 else 2


def repor_frutas():
    while len(lista_frutas) < quantidade_frutas():
        ocupadas = [list(posicao) for posicao, _ in lista_frutas]
        livres = [(c, r) for c in range(COLS) for r in range(ROWS)
                  if [c, r] not in corpo_cobra and [c, r] not in ocupadas]
        if not livres:
            return
        posicao = random.choice(livres)
        nome = random.choice(list(frutas.keys())) if frutas else None
        lista_frutas.append((posicao, nome))


def iniciar_partida():
    global corpo_cobra, direcao, score, frutas_comidas, fase, velocidade, pausa_ate, acumulador, estado
    meio_coluna = COLS // 2
    meio_linha = ROWS // 2
    corpo_cobra = [[meio_coluna, meio_linha], [meio_coluna - 1, meio_linha], [meio_coluna - 2, meio_linha]]
    direcao = (1, 0)
    fila_direcoes.clear()
    score = 0
    frutas_comidas = 0
    fase = 1
    velocidade = VEL_INICIAL
    pausa_ate = 0
    acumulador = 0.0
    estado = "jogando"
    lista_frutas.clear()
    repor_frutas()


def desenhar_frutas():
    for posicao, nome in lista_frutas:
        x, y = celula_para_pixel(*posicao)
        centro = (x + CELL // 2, y + CELL // 2)
        if nome and nome in frutas:
            sprite = frutas[nome]
            tela.blit(sprite, sprite.get_rect(center=centro))
        else:
            pygame.draw.rect(tela, (220, 60, 60), (x + 6, y + 6, CELL - 12, CELL - 12))


def desenhar_cobra():
    for indice, parte in enumerate(corpo_cobra):
        x, y = celula_para_pixel(parte[0], parte[1])
        if indice == 0:
            base = cabeca_viva if estado == "jogando" else cabeca_morta
            tela.blit(pygame.transform.rotate(base, ANGULOS[direcao]), (x, y))
        else:
            tela.blit(segmento_corpo, (x, y))


def desenhar_hud():
    desenhar_cartela(f"SCORE {score}", (140, 122), COR_CREME)
    desenhar_cartela(f"FASE {fase_atual()}", (360, 122), COR_CREME)
    desenhar_cartela(f"VEL {velocidade:.2f}", (LARGURA_TELA - 360, 122), COR_CREME)
    desenhar_cartela(f"RECORDE {recorde}", (LARGURA_TELA - 140, 122), COR_OURO)


def desenhar_fim():
    cortina = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    cortina.fill((6, 4, 8, 200))
    tela.blit(cortina, (0, 0))
    centro_x = LARGURA_TELA // 2
    sombra = fonte_fim.render("GAME OVER", True, (10, 4, 6))
    titulo = fonte_fim.render("GAME OVER", True, (196, 48, 48))
    tela.blit(sombra, (centro_x - titulo.get_width() // 2 + 3, ALTURA_TELA // 2 - 117))
    tela.blit(titulo, (centro_x - titulo.get_width() // 2, ALTURA_TELA // 2 - 120))
    info_score = fonte_placar.render(f"Pontuacao: {score}", True, COR_CREME)
    info_recorde = fonte_placar.render(f"Recorde: {recorde}", True, COR_OURO)
    info_reinicio = fonte_pequena.render("ENTER ou ESPACO para jogar de novo    -    ESC para sair", True, COR_CREME)
    tela.blit(info_score, (centro_x - info_score.get_width() // 2, ALTURA_TELA // 2 - 20))
    tela.blit(info_recorde, (centro_x - info_recorde.get_width() // 2, ALTURA_TELA // 2 + 14))
    tela.blit(info_reinicio, (centro_x - info_reinicio.get_width() // 2, ALTURA_TELA // 2 + 64))


def eh_oposta(uma, outra):
    return uma[0] == -outra[0] and uma[1] == -outra[1]


iniciar_partida()

rodando = True
while rodando:
    dt = min(relogio.tick(60), 100)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                rodando = False
            elif estado == "fim":
                if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                    iniciar_partida()
            else:
                if evento.key in (pygame.K_LEFT, pygame.K_a):
                    desejada = (-1, 0)
                elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                    desejada = (1, 0)
                elif evento.key in (pygame.K_UP, pygame.K_w):
                    desejada = (0, -1)
                elif evento.key in (pygame.K_DOWN, pygame.K_s):
                    desejada = (0, 1)
                else:
                    desejada = None
                if desejada:
                    referencia = fila_direcoes[-1] if fila_direcoes else direcao
                    if desejada != referencia and not eh_oposta(desejada, referencia):
                        fila_direcoes.append(desejada)

    if estado == "jogando":
        acumulador += dt
        intervalo = 1000.0 / velocidade
        while estado == "jogando" and acumulador >= intervalo:
            acumulador -= intervalo
            if fila_direcoes:
                proxima = fila_direcoes.popleft()
                if not eh_oposta(proxima, direcao):
                    direcao = proxima
            nova_cabeca = [corpo_cobra[0][0] + direcao[0], corpo_cobra[0][1] + direcao[1]]
            bateu_parede = nova_cabeca[0] < 0 or nova_cabeca[0] >= COLS or nova_cabeca[1] < 0 or nova_cabeca[1] >= ROWS
            bateu_corpo = nova_cabeca in corpo_cobra[:-1]
            if bateu_parede or bateu_corpo:
                estado = "fim"
                if som_morte:
                    som_morte.play()
            else:
                corpo_cobra.insert(0, nova_cabeca)
                indice_comida = None
                for indice, (posicao, _) in enumerate(lista_frutas):
                    if tuple(nova_cabeca) == posicao:
                        indice_comida = indice
                        break
                if indice_comida is not None:
                    lista_frutas.pop(indice_comida)
                    frutas_comidas += 1
                    score += PONTOS_POR_FRUTA
                    if som_mordida:
                        som_mordida.play()
                    if score > pausa_ate:
                        velocidade = min(velocidade + GANHO_POR_FRUTA, VEL_MAXIMA)
                    if score % MARCO_PENALIDADE == 0:
                        velocidade = max(velocidade - PENALIDADE_VELOCIDADE, VEL_MINIMA)
                        pausa_ate = score + PONTOS_PAUSA
                    if score > recorde:
                        recorde = score
                        salvar_recorde(recorde)
                    nova_fase = fase_atual()
                    if nova_fase > fase:
                        fase = nova_fase
                        if som_nivel:
                            som_nivel.play()
                    repor_frutas()
                else:
                    corpo_cobra.pop()
            intervalo = 1000.0 / velocidade

    tela.blit(fundo_estatico, (0, 0))
    desenhar_frutas()
    desenhar_cobra()
    desenhar_hud()
    if estado == "fim":
        desenhar_fim()

    pygame.display.flip()

pygame.quit()
sys.exit()
