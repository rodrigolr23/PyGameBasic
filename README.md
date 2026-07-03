# PyGame - Projeto da Faculdade

Projeto desenvolvido por mim, Rodrigo Lima Rodrigues, e por meu colega, Matheus Assis.

Um jogo da cobrinha (Snake) feito em **Python** com **Pygame**, com tema
visual de Nova York. É Trabalho acadêmico da disciplina de Algoritimos e Programação do Prof. Filipo Novo Mór.

O código-fonte está em `game/main.py`.

- **ENTER** ou **ESPAÇO** — inicia a partida e reinicia depois de perder/vencer.
- **ESC** — sai do jogo.

**Objetivo:** comer as frutas para pontuar, desviar das paredes (obstáculos) e
do próprio corpo, chegar até a **fase 10** e comer todas as frutas finais para
vencer.

---

## Requisitos e execução

- Python 3
- Pygame (`pip install pygame`)

Para rodar:

```bash
python game/main.py

---
Estrutura do projeto

PyGameBasic/
├── game/
│   └── main.py          # todo o jogo
├── Images/
│   └── fruits/          # sprites das frutas (.png)
├── sounds/              # efeitos sonoros (.wav)
├── recorde.txt          # recorde salvo automaticamente
└── README.md
---
Como o jogo funciona (o que foi implementado)

Tabuleiro e tamanhos

O tabuleiro é uma grade de células. Cada célula tem 48 pixels, e a grade
tem 21 colunas × 14 linhas. A janela é montada a partir disso: a área de
jogo (1008 × 672) mais margens laterais e um espaço no topo (150 px) reservado
para o título e o placar. Mudar o tamanho da célula (CELL) aumenta ou diminui
proporcionalmente todos os elementos e a janela inteira.


As teclas não movem a cobra na hora: elas entram numa fila de direções
(buffer de até 3), aplicada no próximo passo. Isso deixa os controles mais
responsivos e evita perder comandos rápidos.

Velocidade e dificuldade

- A cobra começa em 7 células por segundo.
- Cada fruta comida acelera +0,25.
- A velocidade tem teto de 25 e piso de 4.
- A cada 150 pontos (um marco / troca de fase) a velocidade sofre um
alívio de −1,0 e abre-se uma janela de 100 pontos sem acelerar, para
o jogo não ficar impossível logo após subir de fase.

Pontuação e fases

- Cada fruta vale 10 pontos.
- Uma fase nova a cada 150 pontos (fase = pontos ÷ 150 + 1).
- A fase 10 é a final (1350 pontos).
- O número de frutas no tabuleiro cresce com a fase: começa com 1 e vai até
4 frutas ao mesmo tempo.

Crescimento da cobra

Para o jogo ser vencível (chegar até a fase 10 sem a cobra ficar
gigante), ela só cresce a cada 5 frutas comidas. Nas outras frutas, ela
pontua e acelera normalmente, mas a cauda sai para manter o tamanho.

Obstáculos (paredes) e aleatoriedade

- Não há obstáculos na fase 1; eles aparecem a partir da fase 2.
- A quantidade cresce 1 por fase, até no máximo 3 obstáculos.
- O tamanho de cada obstáculo cresce com a fase, até 3 células cada.
- Os obstáculos são posicionados aleatoriamente (horizontais ou verticais),
sempre longe do corpo da cobra, das 3 casas à frente da cabeça e das
frutas — para nunca criar uma morte injusta.
- Eles trocam de lugar a cada 5 frutas comidas e a cada troca de fase.

Frutas e aleatoriedade

- As frutas aparecem em células livres escolhidas aleatoriamente (sem cobra,
sem outra fruta e sem obstáculo).
- O tipo de fruta (maçã, melancia, banana, laranja, cereja, abacaxi, uva,
limão, morango) também é sorteado.
- Cada sprite é carregado da pasta Images/fruits e redimensionado para caber
na célula. Se faltar a imagem de alguma fruta, o jogo desenha um quadradinho
de reserva no lugar (não quebra).

Fase final e vitória

Ao chegar na fase 10, o tabuleiro para de repor frutas e solta as
5 frutas finais. O jogador precisa comer todas para vencer. A tela de
vitória fica piscando entre vermelho e azul para comemorar.

Formas de morrer

A cobra morre (e toca o som de morte) se:

- bater em uma parede da borda;
- bater no próprio corpo (a cauda que vai sair no mesmo passo é ignorada);
- bater em um obstáculo;
- tentar virar 180° (apertar a direção oposta à que ela segue).

Sons

Três efeitos sonoros, carregados da pasta sounds:

- comer.wav — ao comer uma fruta;
- morte.wav — ao morrer;
- nivel.wav — ao subir de fase.

Se algum arquivo de som não existir, o jogo continua funcionando normalmente,
apenas sem aquele efeito.

Recorde

O maior placar é salvo automaticamente em recorde.txt e recarregado toda vez
que o jogo abre, aparecendo no canto do placar.

---
Gráficos e visual (tudo desenhado em código)

Quase tudo na tela é desenhado por código, não são imagens prontas
(exceto os sprites das frutas):

- Céu em degradê — pintado linha a linha, interpolando duas cores.
- Feixes de luz translúcidos saindo do topo (estilo holofotes).
- Skyline de prédios, com silhuetas e janelas acesas
distribuídas aleatoriamente. O cenário usa uma semente fixa de aleatoriedade
para o desenho dos prédios ficar sempre igual entre partidas.
- Moldura dourada em volta da área de jogo, com detalhes nos cantos.
- Grade sutil marcando as células do tabuleiro.
- A cobra é desenhada com polígonos: a cabeça gira conforme a direção,
tem olhos e presas, e ao morrer os olhos viram "X". O corpo tem um
losango central para dar textura.
- Obstáculos desenhados como blocos de pedra cinza (para não se
confundirem com frutas).
- Efeito de flash na troca de fase: o cenário de fora pisca 3 vezes
entre vermelho e azul, deixando a área de jogo livre.
- HUD (placar superior) mostrando SCORE, FASE x/10, VELOCIDADE e
RECORDE, cada um numa cartela com moldura dourada.
- Telas de início, game over e vitória sobrepostas ao tabuleiro.

Para desempenho, o fundo e os sprites da cobra são montados uma única vez
antes do loop e apenas reaproveitados a cada quadro.
