import os
import math
import random
import asyncio
import pygame

# ============================================================
# AVENTURA DOS CRISTAIS 2D
# Versão atualizada: celular, tablet e computador
# - Controles touch: TRÁS, FRENTE, PULAR e FACA
# - 3 fases
# - Visuais mais bonitos
# - Mais inimigos
# - Tela inicial e telas finais melhoradas
# - Compatível com Pygbag / GitHub Pages
# ============================================================

# ------------------------------------------------------------
# CONFIGURAÇÕES
# ------------------------------------------------------------

LARGURA_TELA = 960
ALTURA_TELA = 540
FPS = 60
GRAVIDADE = 0.78

MENU = "menu"
JOGANDO = "jogando"
PAUSADO = "pausado"
FASE_COMPLETA = "fase_completa"
VITORIA = "vitoria"
DERROTA = "derrota"

# ------------------------------------------------------------
# CORES
# ------------------------------------------------------------

BRANCO = (248, 250, 255)
PRETO = (8, 10, 18)
AZUL_ESCURO = (18, 28, 58)
AZUL_NOITE = (10, 18, 42)
CIANO = (69, 236, 255)
CIANO_CLARO = (155, 248, 255)
ROXO = (128, 76, 230)
ROXO_CLARO = (194, 144, 255)
ROXO_ESCURO = (55, 34, 105)
VERDE = (52, 205, 112)
VERDE_CLARO = (126, 245, 157)
VERDE_ESCURO = (22, 105, 63)
VERDE_SLIME = (87, 231, 116)
AMARELO = (255, 221, 77)
LARANJA = (255, 145, 52)
VERMELHO = (242, 65, 88)
VERMELHO_ESCURO = (140, 38, 62)
CINZA = (95, 105, 130)
CINZA_CLARO = (183, 193, 214)
MARROM = (108, 68, 44)
MARROM_ESCURO = (62, 42, 36)
PELE = (255, 211, 180)
CABELO = (83, 48, 36)
SOMBRA = (24, 27, 42)
DOURADO = (255, 191, 64)
MAGENTA = (239, 90, 207)

# Paletas visuais de cada fase
PALETAS = [
    {
        "nome": "Vale Celeste",
        "ceu_topo": (62, 153, 235),
        "ceu_base": (154, 228, 255),
        "montanha_1": (63, 116, 165),
        "montanha_2": (77, 146, 188),
        "solo": (110, 70, 43),
        "grama": (55, 201, 99),
        "detalhe": CIANO,
        "sol": (255, 220, 88),
    },
    {
        "nome": "Floresta Encantada",
        "ceu_topo": (78, 50, 151),
        "ceu_base": (177, 104, 190),
        "montanha_1": (72, 51, 112),
        "montanha_2": (95, 64, 128),
        "solo": (77, 54, 49),
        "grama": (78, 192, 116),
        "detalhe": ROXO_CLARO,
        "sol": (255, 213, 127),
    },
    {
        "nome": "Ruínas de Cristal",
        "ceu_topo": (19, 30, 72),
        "ceu_base": (67, 73, 129),
        "montanha_1": (38, 44, 86),
        "montanha_2": (52, 58, 104),
        "solo": (66, 63, 82),
        "grama": (91, 126, 134),
        "detalhe": MAGENTA,
        "sol": (210, 225, 255),
    },
]

# ------------------------------------------------------------
# DADOS DAS FASES
# ------------------------------------------------------------

FASES = [
    {
        "nome": "FASE 1 - VALE CELESTE",
        "largura": 2450,
        "plataformas": [
            (0, 470, 520, 70),
            (620, 470, 430, 70),
            (1140, 470, 390, 70),
            (1640, 470, 810, 70),
            (300, 370, 170, 24),
            (770, 345, 180, 24),
            (1260, 335, 160, 24),
            (1770, 365, 190, 24),
            (2050, 300, 160, 24),
        ],
        "cristais": [
            (350, 320),
            (830, 295),
            (1285, 285),
            (1840, 315),
            (2110, 250),
        ],
        "inimigos": [
            (220, 435, "slime", 90, 430),
            (700, 435, "slime", 650, 950),
            (1210, 435, "slime", 1160, 1460),
            (1700, 435, "slime", 1660, 1940),
            (980, 260, "morcego", 880, 1110),
            (1510, 260, "morcego", 1420, 1620),
            (2180, 225, "morcego", 2060, 2320),
        ],
        "portal": (2310, 378),
    },
    {
        "nome": "FASE 2 - FLORESTA ENCANTADA",
        "largura": 2700,
        "plataformas": [
            (0, 470, 420, 70),
            (510, 470, 390, 70),
            (990, 470, 390, 70),
            (1470, 470, 370, 70),
            (1930, 470, 770, 70),
            (210, 365, 150, 24),
            (600, 330, 160, 24),
            (1080, 350, 155, 24),
            (1530, 315, 180, 24),
            (2020, 355, 175, 24),
            (2310, 290, 160, 24),
        ],
        "cristais": [
            (260, 315),
            (655, 280),
            (1125, 300),
            (1585, 265),
            (2365, 240),
        ],
        "inimigos": [
            (170, 435, "slime", 70, 350),
            (610, 435, "golem", 540, 820),
            (1100, 435, "slime", 1020, 1310),
            (1540, 420, "golem", 1490, 1760),
            (2010, 435, "slime", 1970, 2230),
            (850, 250, "morcego", 760, 980),
            (1380, 240, "morcego", 1260, 1450),
            (2200, 230, "morcego", 2080, 2350),
        ],
        "portal": (2560, 378),
    },
    {
        "nome": "FASE 3 - RUÍNAS DE CRISTAL",
        "largura": 2920,
        "plataformas": [
            (0, 470, 390, 70),
            (480, 470, 390, 70),
            (960, 470, 350, 70),
            (1400, 470, 330, 70),
            (1820, 470, 430, 70),
            (2340, 470, 580, 70),
            (190, 355, 150, 24),
            (570, 320, 155, 24),
            (1040, 345, 150, 24),
            (1480, 300, 170, 24),
            (1900, 350, 160, 24),
            (2370, 320, 160, 24),
            (2630, 260, 155, 24),
        ],
        "cristais": [
            (245, 305),
            (625, 270),
            (1090, 295),
            (1538, 250),
            (2680, 210),
        ],
        "inimigos": [
            (160, 435, "golem", 70, 330),
            (560, 435, "slime", 510, 800),
            (1040, 435, "golem", 990, 1240),
            (1470, 420, "golem", 1420, 1660),
            (1890, 435, "slime", 1840, 2180),
            (2410, 420, "golem", 2370, 2680),
            (820, 245, "morcego", 730, 940),
            (1310, 225, "morcego", 1210, 1430),
            (2220, 230, "morcego", 2100, 2330),
        ],
        "portal": (2790, 378),
    },
]

# ------------------------------------------------------------
# INICIALIZAÇÃO
# ------------------------------------------------------------

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

TELA = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Aventura dos Cristais - Jogo 2D")
RELOGIO = pygame.time.Clock()

FONTE_MICRO = pygame.font.SysFont("arial", 15, bold=True)
FONTE_PEQUENA = pygame.font.SysFont("arial", 19)
FONTE_PEQUENA_BOLD = pygame.font.SysFont("arial", 19, bold=True)
FONTE_MEDIA = pygame.font.SysFont("arial", 27, bold=True)
FONTE_GRANDE = pygame.font.SysFont("arial", 48, bold=True)
FONTE_TITULO = pygame.font.SysFont("arial", 58, bold=True)

# Gradientes pré-calculados para não pesar no navegador
FUNDOS_GRADIENTE = []


def criar_gradiente(cor_topo, cor_base):
    superficie = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
    for y in range(ALTURA_TELA):
        t = y / max(1, ALTURA_TELA - 1)
        cor = (
            int(cor_topo[0] * (1 - t) + cor_base[0] * t),
            int(cor_topo[1] * (1 - t) + cor_base[1] * t),
            int(cor_topo[2] * (1 - t) + cor_base[2] * t),
        )
        pygame.draw.line(superficie, cor, (0, y), (LARGURA_TELA, y))
    return superficie


for p in PALETAS:
    FUNDOS_GRADIENTE.append(criar_gradiente(p["ceu_topo"], p["ceu_base"]))

# ------------------------------------------------------------
# SOM
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SONS_DIR = os.path.join(BASE_DIR, "assets", "sons")
musica_iniciada = False


def carregar_som(nome):
    try:
        caminho = os.path.join(SONS_DIR, nome)
        if pygame.mixer.get_init() and os.path.exists(caminho):
            return pygame.mixer.Sound(caminho)
    except Exception:
        pass
    return None


SONS = {
    "pulo": carregar_som("pulo.wav"),
    "cristal": carregar_som("cristal.wav"),
    "ataque": carregar_som("ataque.wav"),
    "dano": carregar_som("dano.wav"),
    "vitoria": carregar_som("vitoria.wav"),
    "derrota": carregar_som("derrota.wav"),
}


def tocar(nome):
    try:
        som = SONS.get(nome)
        if som:
            som.play()
    except Exception:
        pass


def iniciar_musica():
    global musica_iniciada
    if musica_iniciada:
        return
    try:
        caminho = os.path.join(SONS_DIR, "musica.wav")
        if pygame.mixer.get_init() and os.path.exists(caminho):
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.set_volume(0.22)
            pygame.mixer.music.play(-1)
            musica_iniciada = True
    except Exception:
        pass

# ------------------------------------------------------------
# UTILITÁRIOS
# ------------------------------------------------------------


def escrever(texto, fonte, cor, x, y, centralizado=False, sombra=False):
    if sombra:
        img_sombra = fonte.render(texto, True, PRETO)
        rect_sombra = img_sombra.get_rect()
        if centralizado:
            rect_sombra.center = (x + 2, y + 3)
        else:
            rect_sombra.topleft = (x + 2, y + 3)
        TELA.blit(img_sombra, rect_sombra)

    img = fonte.render(texto, True, cor)
    rect = img.get_rect()
    if centralizado:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    TELA.blit(img, rect)


def cor_lerp(a, b, t):
    return (
        int(a[0] * (1 - t) + b[0] * t),
        int(a[1] * (1 - t) + b[1] * t),
        int(a[2] * (1 - t) + b[2] * t),
    )


def desenhar_cristal_icone(tela, x, y, tamanho=16, cor=CIANO):
    pontos = [
        (x, y - tamanho),
        (x + tamanho, y),
        (x, y + tamanho),
        (x - tamanho, y),
    ]
    pygame.draw.polygon(tela, cor, pontos)
    pygame.draw.polygon(tela, BRANCO, pontos, 2)
    pygame.draw.line(tela, BRANCO, (x, y - tamanho + 4), (x + 5, y - 1), 2)


def desenhar_coracao(tela, x, y, cheio=True):
    cor = VERMELHO if cheio else (78, 82, 105)
    pygame.draw.circle(tela, cor, (x - 5, y - 3), 7)
    pygame.draw.circle(tela, cor, (x + 5, y - 3), 7)
    pygame.draw.polygon(tela, cor, [(x - 12, y), (x + 12, y), (x, y + 15)])
    if cheio:
        pygame.draw.circle(tela, (255, 150, 160), (x - 6, y - 5), 2)


# ------------------------------------------------------------
# PARTÍCULAS
# ------------------------------------------------------------


class Particula:
    def __init__(self, x, y, cor, quantidade=1):
        self.x = x
        self.y = y
        angulo = random.uniform(0, math.tau)
        velocidade = random.uniform(1.5, 4.2)
        self.vx = math.cos(angulo) * velocidade
        self.vy = math.sin(angulo) * velocidade - 1.5
        self.vida = random.randint(22, 42)
        self.tamanho = random.randint(2, 5)
        self.cor = cor
        self.quantidade = quantidade

    def atualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.09
        self.vx *= 0.98
        self.vida -= 1

    def desenhar(self, tela, camera_x):
        if self.vida <= 0:
            return
        raio = max(1, int(self.tamanho * min(1, self.vida / 20)))
        pygame.draw.circle(
            tela,
            self.cor,
            (int(self.x - camera_x), int(self.y)),
            raio,
        )


def criar_particulas(lista, x, y, cor, n=10):
    for _ in range(n):
        lista.append(Particula(x, y, cor))


# ------------------------------------------------------------
# CLASSES DO JOGO
# ------------------------------------------------------------


class Jogador:
    def __init__(self, x, y, vidas=3):
        self.rect = pygame.Rect(x, y, 40, 60)
        self.vel_x = 0
        self.vel_y = 0
        self.velocidade = 5.4
        self.forca_pulo = -15
        self.no_chao = False
        self.vidas = vidas
        self.direcao = 1
        self.invencivel = 0
        self.cooldown_ataque = 0
        self.tempo_ataque = 0
        self.ataque_rect = pygame.Rect(0, 0, 0, 0)
        self.animacao = 0

    def reiniciar_posicao(self):
        self.rect.x = 70
        self.rect.y = 330
        self.vel_x = 0
        self.vel_y = 0
        self.invencivel = 90

    def atualizar(
        self,
        teclas,
        plataformas,
        largura_fase,
        toque_tras=False,
        toque_frente=False,
        toque_pulo=False,
        toque_ataque=False,
    ):
        self.vel_x = 0

        tras = teclas[pygame.K_a] or teclas[pygame.K_LEFT] or toque_tras
        frente = teclas[pygame.K_d] or teclas[pygame.K_RIGHT] or toque_frente
        pulo = (
            teclas[pygame.K_SPACE]
            or teclas[pygame.K_w]
            or teclas[pygame.K_UP]
            or toque_pulo
        )
        ataque = (
            teclas[pygame.K_LCTRL]
            or teclas[pygame.K_RCTRL]
            or teclas[pygame.K_f]
            or toque_ataque
        )

        if tras and not frente:
            self.vel_x = -self.velocidade
            self.direcao = -1

        if frente and not tras:
            self.vel_x = self.velocidade
            self.direcao = 1

        if pulo and self.no_chao:
            self.vel_y = self.forca_pulo
            self.no_chao = False
            tocar("pulo")

        if ataque and self.cooldown_ataque <= 0:
            self.cooldown_ataque = 24
            self.tempo_ataque = 11
            tocar("ataque")

        if self.cooldown_ataque > 0:
            self.cooldown_ataque -= 1

        if self.tempo_ataque > 0:
            self.tempo_ataque -= 1

        if self.invencivel > 0:
            self.invencivel -= 1

        if abs(self.vel_x) > 0.1:
            self.animacao += 0.22
        else:
            self.animacao += 0.07

        self.rect.x += int(self.vel_x)
        self.colisao_horizontal(plataformas)

        self.vel_y += GRAVIDADE
        self.vel_y = min(self.vel_y, 18)

        self.rect.y += int(self.vel_y)
        self.colisao_vertical(plataformas)

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(largura_fase, self.rect.right)

        if self.tempo_ataque > 0:
            alcance = 52
            if self.direcao == 1:
                self.ataque_rect = pygame.Rect(
                    self.rect.right - 2, self.rect.y + 14, alcance, 32
                )
            else:
                self.ataque_rect = pygame.Rect(
                    self.rect.left - alcance + 2, self.rect.y + 14, alcance, 32
                )
        else:
            self.ataque_rect = pygame.Rect(0, 0, 0, 0)

    def colisao_horizontal(self, plataformas):
        for plataforma in plataformas:
            if self.rect.colliderect(plataforma):
                if self.vel_x > 0:
                    self.rect.right = plataforma.left
                elif self.vel_x < 0:
                    self.rect.left = plataforma.right

    def colisao_vertical(self, plataformas):
        self.no_chao = False
        for plataforma in plataformas:
            if self.rect.colliderect(plataforma):
                if self.vel_y > 0:
                    self.rect.bottom = plataforma.top
                    self.vel_y = 0
                    self.no_chao = True
                elif self.vel_y < 0:
                    self.rect.top = plataforma.bottom
                    self.vel_y = 0

    def tomar_dano(self):
        if self.invencivel <= 0:
            self.vidas -= 1
            self.invencivel = 90
            self.vel_y = -9
            tocar("dano")
            return True
        return False

    def desenhar(self, tela, camera_x):
        x = self.rect.x - camera_x
        y = self.rect.y

        if self.invencivel > 0 and (self.invencivel // 5) % 2 == 0:
            return

        # sombra
        pygame.draw.ellipse(tela, (20, 25, 38), (x + 5, y + 54, 30, 8))

        # capa
        capa_x = x + (4 if self.direcao == 1 else 19)
        pygame.draw.polygon(
            tela,
            ROXO_ESCURO,
            [(capa_x, y + 27), (capa_x + 17, y + 27), (capa_x + 11, y + 52)],
        )

        # pernas com animação
        passo = math.sin(self.animacao) * 3 if self.no_chao else 0
        pygame.draw.line(
            tela, AZUL_ESCURO, (x + 15, y + 47), (x + 12 - passo, y + 58), 5
        )
        pygame.draw.line(
            tela, AZUL_ESCURO, (x + 25, y + 47), (x + 28 + passo, y + 58), 5
        )
        pygame.draw.ellipse(tela, PRETO, (x + 5 - passo, y + 55, 15, 7))
        pygame.draw.ellipse(tela, PRETO, (x + 21 + passo, y + 55, 15, 7))

        # corpo
        pygame.draw.rect(tela, ROXO, (x + 8, y + 23, 25, 27), border_radius=8)
        pygame.draw.rect(
            tela, ROXO_CLARO, (x + 12, y + 27, 17, 7), border_radius=3
        )
        pygame.draw.rect(tela, SOMBRA, (x + 8, y + 23, 25, 27), 2, border_radius=8)

        # braços
        pygame.draw.line(tela, PELE, (x + 10, y + 29), (x + 3, y + 40), 5)
        pygame.draw.line(tela, PELE, (x + 31, y + 29), (x + 37, y + 40), 5)

        # cabeça/cabelo
        pygame.draw.circle(tela, PELE, (x + 20, y + 13), 13)
        pygame.draw.ellipse(tela, CABELO, (x + 6, y, 28, 16))
        pygame.draw.polygon(
            tela,
            CABELO,
            [(x + 7, y + 9), (x + 12, y + 20), (x + 15, y + 8)],
        )

        # rosto
        if self.direcao == 1:
            pygame.draw.circle(tela, PRETO, (x + 23, y + 12), 2)
            pygame.draw.circle(tela, PRETO, (x + 29, y + 12), 2)
        else:
            pygame.draw.circle(tela, PRETO, (x + 11, y + 12), 2)
            pygame.draw.circle(tela, PRETO, (x + 17, y + 12), 2)

        pygame.draw.arc(tela, PRETO, (x + 15, y + 13, 11, 8), 0.2, 2.9, 1)

        # brilho mágico
        brilho_x = x + 20 + int(math.sin(self.animacao * 0.8) * 2)
        pygame.draw.circle(tela, CIANO_CLARO, (brilho_x, y + 31), 3)

        # faca animada
        if self.tempo_ataque > 0:
            if self.direcao == 1:
                punho = (x + 36, y + 38)
                ponta = (x + 74, y + 28)
                base1 = (x + 40, y + 34)
                base2 = (x + 42, y + 42)
            else:
                punho = (x + 4, y + 38)
                ponta = (x - 34, y + 28)
                base1 = (x, y + 34)
                base2 = (x - 2, y + 42)

            pygame.draw.line(tela, MARROM_ESCURO, punho, base1, 6)
            pygame.draw.polygon(tela, CIANO_CLARO, [base1, base2, ponta])
            pygame.draw.line(tela, BRANCO, base1, ponta, 2)


class Inimigo:
    def __init__(self, x, y, tipo="slime", esquerda=None, direita=None):
        self.tipo = tipo

        if tipo == "slime":
            self.rect = pygame.Rect(x, y, 44, 35)
            self.vel = 2.0
        elif tipo == "morcego":
            self.rect = pygame.Rect(x, y, 50, 32)
            self.vel = 2.6
        else:  # golem
            self.rect = pygame.Rect(x, y, 52, 54)
            self.vel = 1.3

        self.y_inicial = y
        self.direcao = 1
        self.esquerda = esquerda if esquerda is not None else x - 120
        self.direita = direita if direita is not None else x + 120
        self.vivo = True
        self.tempo = random.randint(0, 100)

    def atualizar(self):
        if not self.vivo:
            return

        self.tempo += 1
        self.rect.x += int(self.vel * self.direcao)

        if self.rect.x <= self.esquerda:
            self.direcao = 1
        elif self.rect.x >= self.direita:
            self.direcao = -1

        if self.tipo == "morcego":
            self.rect.y = self.y_inicial + int(math.sin(self.tempo * 0.08) * 25)

    def desenhar(self, tela, camera_x, fase_indice):
        if not self.vivo:
            return

        x = self.rect.x - camera_x
        y = self.rect.y

        if self.tipo == "slime":
            cor = VERDE_SLIME if fase_indice != 2 else (127, 231, 244)
            escuro = VERDE_ESCURO if fase_indice != 2 else (36, 118, 154)

            pygame.draw.ellipse(tela, SOMBRA, (x + 7, y + 29, 30, 6))
            pygame.draw.ellipse(tela, cor, (x, y + 4, 44, 30))
            pygame.draw.ellipse(tela, escuro, (x + 3, y + 23, 38, 10))
            pygame.draw.ellipse(tela, BRANCO, (x + 9, y + 9, 9, 11))
            pygame.draw.ellipse(tela, BRANCO, (x + 26, y + 9, 9, 11))
            pygame.draw.circle(tela, PRETO, (x + 14, y + 15), 2)
            pygame.draw.circle(tela, PRETO, (x + 30, y + 15), 2)
            pygame.draw.arc(tela, PRETO, (x + 14, y + 17, 16, 8), 3.3, 6.0, 2)
            pygame.draw.ellipse(tela, escuro, (x, y + 4, 44, 30), 2)

        elif self.tipo == "morcego":
            asa = 6 + int(abs(math.sin(self.tempo * 0.18)) * 8)
            pygame.draw.ellipse(tela, SOMBRA, (x + 12, y + 25, 25, 6))
            pygame.draw.polygon(
                tela,
                ROXO,
                [(x + 17, y + 16), (x - 9, y + 16 - asa), (x + 4, y + 28)],
            )
            pygame.draw.polygon(
                tela,
                ROXO,
                [(x + 33, y + 16), (x + 59, y + 16 - asa), (x + 46, y + 28)],
            )
            pygame.draw.ellipse(tela, ROXO_ESCURO, (x + 12, y + 8, 26, 20))
            pygame.draw.polygon(
                tela, ROXO_ESCURO, [(x + 15, y + 10), (x + 18, y + 1), (x + 22, y + 11)]
            )
            pygame.draw.polygon(
                tela, ROXO_ESCURO, [(x + 28, y + 11), (x + 33, y + 1), (x + 36, y + 11)]
            )
            pygame.draw.circle(tela, AMARELO, (x + 21, y + 17), 2)
            pygame.draw.circle(tela, AMARELO, (x + 30, y + 17), 2)
            pygame.draw.line(tela, BRANCO, (x + 24, y + 23), (x + 26, y + 27), 1)

        else:
            # golem de pedra
            cor_pedra = (125, 114, 145) if fase_indice == 1 else (92, 102, 130)
            cor_sombra = (71, 64, 89)
            pygame.draw.ellipse(tela, SOMBRA, (x + 5, y + 48, 42, 8))
            pygame.draw.rect(tela, cor_sombra, (x + 4, y + 14, 44, 38), border_radius=7)
            pygame.draw.rect(tela, cor_pedra, (x + 7, y + 10, 38, 36), border_radius=6)
            pygame.draw.rect(tela, cor_sombra, (x + 10, y, 31, 22), border_radius=6)
            pygame.draw.rect(tela, cor_pedra, (x + 12, y + 2, 27, 18), border_radius=5)
            pygame.draw.circle(tela, CIANO, (x + 19, y + 11), 3)
            pygame.draw.circle(tela, CIANO, (x + 32, y + 11), 3)
            pygame.draw.line(tela, cor_sombra, (x + 18, y + 29), (x + 36, y + 29), 3)
            # rachaduras
            pygame.draw.line(tela, (186, 175, 205), (x + 17, y + 37), (x + 22, y + 31), 2)
            pygame.draw.line(tela, (186, 175, 205), (x + 22, y + 31), (x + 26, y + 38), 2)


class Cristal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 38)
        self.coletado = False
        self.tempo = random.randint(0, 80)

    def atualizar(self):
        self.tempo += 1

    def desenhar(self, tela, camera_x, cor):
        if self.coletado:
            return

        x = self.rect.x - camera_x
        y = self.rect.y + int(math.sin(self.tempo * 0.08) * 5)

        brilho = 4 + int((math.sin(self.tempo * 0.12) + 1) * 2)
        pygame.draw.circle(tela, cor, (x + 15, y + 18), 22 + brilho, 1)

        pontos = [
            (x + 15, y),
            (x + 30, y + 17),
            (x + 15, y + 38),
            (x, y + 17),
        ]
        pygame.draw.polygon(tela, cor, pontos)
        pygame.draw.polygon(tela, BRANCO, pontos, 2)
        pygame.draw.polygon(
            tela,
            CIANO_CLARO,
            [(x + 15, y + 4), (x + 23, y + 17), (x + 15, y + 27), (x + 8, y + 17)],
            2,
        )
        pygame.draw.circle(tela, BRANCO, (x + 10, y + 10), 2)


class Portal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 76, 92)
        self.tempo = 0

    def atualizar(self):
        self.tempo += 1

    def desenhar(self, tela, camera_x, aberto, cor):
        x = self.rect.x - camera_x
        y = self.rect.y

        base = cor if aberto else (95, 101, 121)
        interno = ROXO_ESCURO if aberto else AZUL_ESCURO

        pygame.draw.ellipse(tela, SOMBRA, (x + 5, y + 82, 66, 10))
        pygame.draw.ellipse(tela, base, (x + 4, y, 68, 92), 7)
        pygame.draw.ellipse(tela, interno, (x + 15, y + 11, 46, 70))

        if aberto:
            for i in range(3):
                ang = self.tempo * 0.05 + i * 2.1
                px = x + 38 + int(math.cos(ang) * (11 + i * 3))
                py = y + 46 + int(math.sin(ang) * (19 + i * 2))
                pygame.draw.circle(tela, BRANCO, (px, py), 3)
            pygame.draw.circle(tela, CIANO_CLARO, (x + 38, y + 46), 8)
        else:
            pygame.draw.line(tela, CINZA_CLARO, (x + 30, y + 34), (x + 48, y + 57), 4)
            pygame.draw.line(tela, CINZA_CLARO, (x + 48, y + 34), (x + 30, y + 57), 4)


# ------------------------------------------------------------
# CRIAÇÃO DE FASE
# ------------------------------------------------------------


def criar_fase(indice, vidas=3):
    dados = FASES[indice]
    plataformas = [pygame.Rect(*p) for p in dados["plataformas"]]
    cristais = [Cristal(x, y) for x, y in dados["cristais"]]
    inimigos = [
        Inimigo(x, y, tipo, esquerda, direita)
        for x, y, tipo, esquerda, direita in dados["inimigos"]
    ]
    portal = Portal(*dados["portal"])
    jogador = Jogador(70, 330, vidas)
    return jogador, plataformas, cristais, inimigos, portal, dados["largura"]


def reiniciar_fase(indice, vidas=3):
    jogador, plataformas, cristais, inimigos, portal, largura = criar_fase(indice, vidas)
    return jogador, plataformas, cristais, inimigos, portal, largura, 0, False, []


# ------------------------------------------------------------
# CENÁRIO
# ------------------------------------------------------------

NUVENS = [
    (150, 92, 1.0),
    (470, 70, 0.8),
    (790, 125, 1.1),
    (1160, 82, 0.9),
    (1540, 118, 1.0),
    (1990, 75, 1.2),
    (2450, 115, 0.9),
]

ESTRELAS = [
    (70, 75), (140, 130), (215, 55), (310, 115), (385, 68),
    (480, 120), (565, 78), (660, 145), (745, 65), (840, 110),
    (910, 55), (1040, 135), (1170, 72), (1280, 105), (1410, 52),
    (1560, 118), (1700, 66), (1840, 135), (1980, 78), (2110, 108),
    (2260, 52), (2400, 126), (2570, 70), (2740, 112),
]


def desenhar_nuvem(x, y, escala=1.0):
    r1 = int(18 * escala)
    r2 = int(23 * escala)
    pygame.draw.circle(TELA, BRANCO, (int(x), int(y)), r1)
    pygame.draw.circle(TELA, BRANCO, (int(x + 24 * escala), int(y + 7 * escala)), r2)
    pygame.draw.circle(TELA, BRANCO, (int(x - 26 * escala), int(y + 9 * escala)), int(16 * escala))
    pygame.draw.rect(
        TELA,
        BRANCO,
        (
            int(x - 30 * escala),
            int(y + 8 * escala),
            int(62 * escala),
            int(18 * escala),
        ),
        border_radius=10,
    )


def desenhar_arvore(x, base_y, escala, cor_folha):
    tronco_w = int(18 * escala)
    tronco_h = int(58 * escala)
    pygame.draw.rect(
        TELA,
        MARROM_ESCURO,
        (int(x - tronco_w / 2), int(base_y - tronco_h), tronco_w, tronco_h),
        border_radius=4,
    )
    raio = int(28 * escala)
    pygame.draw.circle(TELA, cor_folha, (int(x), int(base_y - tronco_h - 14 * escala)), raio)
    pygame.draw.circle(
        TELA,
        cor_lerp(cor_folha, BRANCO, 0.14),
        (int(x - 20 * escala), int(base_y - tronco_h - 3 * escala)),
        int(22 * escala),
    )
    pygame.draw.circle(
        TELA,
        cor_lerp(cor_folha, PRETO, 0.18),
        (int(x + 18 * escala), int(base_y - tronco_h - 2 * escala)),
        int(20 * escala),
    )


def desenhar_fundo(fase_indice, camera_x):
    paleta = PALETAS[fase_indice]
    TELA.blit(FUNDOS_GRADIENTE[fase_indice], (0, 0))

    # sol/lua
    if fase_indice == 2:
        pygame.draw.circle(TELA, (224, 230, 255), (815, 85), 40)
        pygame.draw.circle(TELA, paleta["ceu_topo"], (831, 72), 38)
    else:
        pygame.draw.circle(TELA, paleta["sol"], (820, 82), 43)

    # céu
    if fase_indice < 2:
        for cx, cy, escala in NUVENS:
            sx = cx - camera_x * 0.18
            while sx < -150:
                sx += 1250
            while sx > LARGURA_TELA + 150:
                sx -= 1250
            desenhar_nuvem(sx, cy, escala)
    else:
        for sx0, sy in ESTRELAS:
            sx = sx0 - camera_x * 0.08
            while sx < 0:
                sx += 1100
            while sx > LARGURA_TELA:
                sx -= 1100
            brilho = 1 + ((sx0 + sy) % 3)
            pygame.draw.circle(TELA, BRANCO, (int(sx), sy), brilho)

    # montanhas em duas camadas
    largura_fase = FASES[fase_indice]["largura"]
    for mx in range(-300, largura_fase + 700, 360):
        sx = mx - camera_x * 0.28
        pygame.draw.polygon(
            TELA,
            paleta["montanha_1"],
            [(sx, 470), (sx + 195, 215), (sx + 390, 470)],
        )
        pygame.draw.polygon(
            TELA,
            paleta["montanha_2"],
            [(sx + 105, 470), (sx + 255, 280), (sx + 445, 470)],
        )

    # elementos de cada fase
    if fase_indice == 1:
        for tx in range(-100, largura_fase + 400, 250):
            sx = tx - camera_x * 0.55
            desenhar_arvore(sx, 470, 1.0, (61, 143, 105))
            desenhar_arvore(sx + 105, 470, 0.75, (74, 161, 121))

    if fase_indice == 2:
        for rx in range(120, largura_fase, 420):
            sx = rx - camera_x * 0.55
            pygame.draw.rect(TELA, (72, 70, 101), (sx, 330, 42, 140))
            pygame.draw.rect(TELA, (102, 96, 132), (sx - 7, 320, 56, 16))
            pygame.draw.line(TELA, (150, 115, 178), (sx + 11, 350), (sx + 31, 400), 3)
            desenhar_cristal_icone(TELA, int(sx + 21), 355, 8, MAGENTA)


def desenhar_plataformas(plataformas, camera_x, fase_indice):
    paleta = PALETAS[fase_indice]

    for p in plataformas:
        r = pygame.Rect(p.x - camera_x, p.y, p.w, p.h)

        pygame.draw.rect(TELA, paleta["solo"], r, border_radius=4)
        pygame.draw.rect(
            TELA,
            cor_lerp(paleta["solo"], PRETO, 0.22),
            (r.x, r.y + 16, r.w, max(0, r.h - 16)),
            border_radius=4,
        )

        topo = pygame.Rect(r.x, r.y, r.w, 13)
        pygame.draw.rect(TELA, paleta["grama"], topo, border_radius=4)
        pygame.draw.rect(TELA, cor_lerp(paleta["grama"], BRANCO, 0.2), (r.x, r.y, r.w, 4))

        # pedrinhas/textura
        for px in range(r.x + 16, r.right - 10, 58):
            pygame.draw.circle(
                TELA,
                cor_lerp(paleta["solo"], BRANCO, 0.12),
                (px, r.y + min(35, max(20, r.h // 2))),
                3,
            )


# ------------------------------------------------------------
# HUD
# ------------------------------------------------------------


def desenhar_hud(jogador, cristais_coletados, total_cristais, fase_indice):
    overlay = pygame.Surface((LARGURA_TELA, 64), pygame.SRCALPHA)
    overlay.fill((11, 17, 38, 220))
    TELA.blit(overlay, (0, 0))

    # vidas
    escrever("VIDAS", FONTE_MICRO, CINZA_CLARO, 16, 7)
    for i in range(3):
        desenhar_coracao(TELA, 28 + i * 30, 34, i < jogador.vidas)

    # cristais
    desenhar_cristal_icone(TELA, 145, 34, 11, PALETAS[fase_indice]["detalhe"])
    escrever(
        f"{cristais_coletados}/{total_cristais}",
        FONTE_PEQUENA_BOLD,
        BRANCO,
        165,
        23,
    )

    # fase
    escrever(
        FASES[fase_indice]["nome"],
        FONTE_PEQUENA_BOLD,
        BRANCO,
        430,
        31,
        True,
    )

    if cristais_coletados < total_cristais:
        escrever(
            "Colete todos os cristais",
            FONTE_MICRO,
            AMARELO,
            430,
            51,
            True,
        )
    else:
        escrever(
            "Portal liberado!",
            FONTE_MICRO,
            CIANO_CLARO,
            430,
            51,
            True,
        )


# ------------------------------------------------------------
# BOTÕES
# ------------------------------------------------------------

BOTAO_INICIAR = pygame.Rect(295, 418, 370, 68)

BOTAO_TRAS = pygame.Rect(18, 430, 126, 92)
BOTAO_FRENTE = pygame.Rect(154, 430, 138, 92)
BOTAO_PULO = pygame.Rect(640, 430, 132, 92)
BOTAO_ATAQUE = pygame.Rect(782, 430, 160, 92)

BOTAO_PAUSA = pygame.Rect(702, 10, 64, 42)
BOTAO_REINICIAR = pygame.Rect(776, 10, 64, 42)
BOTAO_MENU = pygame.Rect(850, 10, 92, 42)

BOTAO_PAUSA_CONTINUAR = pygame.Rect(330, 274, 300, 58)
BOTAO_PAUSA_MENU = pygame.Rect(330, 350, 300, 58)

BOTAO_FINAL_JOGAR = pygame.Rect(294, 318, 372, 58)
BOTAO_FINAL_MENU = pygame.Rect(294, 390, 372, 58)

BOTAO_PROXIMA = pygame.Rect(294, 345, 372, 62)

toques_ativos = {}
mouse_ativo = False
mouse_posicao = (0, 0)


def posicao_toque(evento):
    return (
        int(evento.x * LARGURA_TELA),
        int(evento.y * ALTURA_TELA),
    )


def desenhar_botao(rect, texto, cor_fundo, fonte=FONTE_MEDIA, cor_texto=BRANCO):
    sombra = rect.move(0, 5)
    pygame.draw.rect(TELA, (10, 13, 28), sombra, border_radius=14)
    pygame.draw.rect(TELA, cor_fundo, rect, border_radius=14)
    pygame.draw.rect(TELA, cor_lerp(cor_fundo, BRANCO, 0.35), rect, 3, border_radius=14)
    escrever(texto, fonte, cor_texto, rect.centerx, rect.centery, True, True)


def desenhar_botao_touch(rect, texto, cor_fundo, pressionado=False, icone=None):
    cor = cor_lerp(cor_fundo, BRANCO, 0.18) if pressionado else cor_fundo
    alfa = 225 if pressionado else 185

    superficie = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(
        superficie,
        (cor[0], cor[1], cor[2], alfa),
        (0, 0, rect.w, rect.h),
        border_radius=20,
    )
    pygame.draw.rect(
        superficie,
        (255, 255, 255, 215),
        (0, 0, rect.w, rect.h),
        3,
        border_radius=20,
    )
    TELA.blit(superficie, rect.topleft)

    if icone == "tras":
        pygame.draw.polygon(
            TELA,
            BRANCO,
            [
                (rect.x + 24, rect.centery),
                (rect.x + 45, rect.centery - 15),
                (rect.x + 45, rect.centery + 15),
            ],
        )
        escrever(texto, FONTE_MICRO, BRANCO, rect.centerx + 18, rect.centery, True)

    elif icone == "frente":
        pygame.draw.polygon(
            TELA,
            BRANCO,
            [
                (rect.right - 24, rect.centery),
                (rect.right - 45, rect.centery - 15),
                (rect.right - 45, rect.centery + 15),
            ],
        )
        escrever(texto, FONTE_MICRO, BRANCO, rect.centerx - 16, rect.centery, True)

    elif icone == "pulo":
        pygame.draw.polygon(
            TELA,
            BRANCO,
            [
                (rect.centerx, rect.y + 18),
                (rect.centerx - 14, rect.y + 36),
                (rect.centerx + 14, rect.y + 36),
            ],
        )
        escrever(texto, FONTE_MICRO, BRANCO, rect.centerx, rect.y + 63, True)

    elif icone == "faca":
        cx = rect.centerx
        cy = rect.y + 30
        pygame.draw.rect(TELA, MARROM_ESCURO, (cx - 18, cy + 6, 20, 6), border_radius=3)
        pygame.draw.polygon(
            TELA,
            CIANO_CLARO,
            [(cx, cy), (cx + 30, cy - 11), (cx + 8, cy + 10)],
        )
        escrever(texto, FONTE_MICRO, BRANCO, rect.centerx, rect.y + 65, True)

    else:
        escrever(texto, FONTE_PEQUENA_BOLD, BRANCO, rect.centerx, rect.centery, True)


def pontos_touch_ativos():
    pontos = list(toques_ativos.values())
    if mouse_ativo:
        pontos.append(mouse_posicao)
    return pontos


def ler_touch():
    tras = False
    frente = False
    pulo = False
    ataque = False

    for pos in pontos_touch_ativos():
        if BOTAO_TRAS.collidepoint(pos):
            tras = True
        if BOTAO_FRENTE.collidepoint(pos):
            frente = True
        if BOTAO_PULO.collidepoint(pos):
            pulo = True
        if BOTAO_ATAQUE.collidepoint(pos):
            ataque = True

    return tras, frente, pulo, ataque


def desenhar_controles_touch():
    tras, frente, pulo, ataque = ler_touch()

    desenhar_botao_touch(BOTAO_TRAS, "TRÁS", ROXO_ESCURO, tras, "tras")
    desenhar_botao_touch(BOTAO_FRENTE, "FRENTE", ROXO, frente, "frente")
    desenhar_botao_touch(BOTAO_PULO, "PULAR", VERDE_ESCURO, pulo, "pulo")
    desenhar_botao_touch(BOTAO_ATAQUE, "FACA", VERMELHO_ESCURO, ataque, "faca")

    desenhar_botao_touch(BOTAO_PAUSA, "II", CINZA)
    desenhar_botao_touch(BOTAO_REINICIAR, "R", LARANJA)
    desenhar_botao_touch(BOTAO_MENU, "MENU", AZUL_ESCURO)


# ------------------------------------------------------------
# TELAS
# ------------------------------------------------------------


def desenhar_avatar_menu():
    # herói
    base_x = 145
    base_y = 288
    pygame.draw.ellipse(TELA, (20, 25, 40), (base_x - 35, base_y + 78, 78, 14))
    pygame.draw.circle(TELA, PELE, (base_x, base_y), 35)
    pygame.draw.ellipse(TELA, CABELO, (base_x - 38, base_y - 34, 76, 38))
    pygame.draw.rect(TELA, ROXO, (base_x - 31, base_y + 36, 62, 69), border_radius=18)
    pygame.draw.rect(TELA, ROXO_CLARO, (base_x - 20, base_y + 47, 40, 18), border_radius=8)
    pygame.draw.circle(TELA, PRETO, (base_x - 10, base_y - 3), 4)
    pygame.draw.circle(TELA, PRETO, (base_x + 11, base_y - 3), 4)
    pygame.draw.arc(TELA, PRETO, (base_x - 12, base_y + 4, 25, 14), 0.1, 3.0, 2)
    pygame.draw.line(TELA, PELE, (base_x - 29, base_y + 52), (base_x - 48, base_y + 74), 8)
    pygame.draw.line(TELA, PELE, (base_x + 29, base_y + 52), (base_x + 50, base_y + 68), 8)
    # faca
    pygame.draw.polygon(
        TELA,
        CIANO_CLARO,
        [(base_x + 48, base_y + 65), (base_x + 100, base_y + 47), (base_x + 62, base_y + 78)],
    )

    # inimigo slime
    sx = 800
    sy = 320
    pygame.draw.ellipse(TELA, SOMBRA, (sx - 36, sy + 34, 74, 12))
    pygame.draw.ellipse(TELA, VERDE_SLIME, (sx - 48, sy - 8, 96, 58))
    pygame.draw.circle(TELA, BRANCO, (sx - 20, sy + 8), 11)
    pygame.draw.circle(TELA, BRANCO, (sx + 20, sy + 8), 11)
    pygame.draw.circle(TELA, PRETO, (sx - 18, sy + 10), 4)
    pygame.draw.circle(TELA, PRETO, (sx + 18, sy + 10), 4)
    pygame.draw.arc(TELA, PRETO, (sx - 20, sy + 18, 40, 18), 3.3, 6.0, 3)


def desenhar_menu():
    desenhar_fundo(0, 0)

    overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    overlay.fill((7, 12, 32, 42))
    TELA.blit(overlay, (0, 0))

    # painel central
    painel = pygame.Surface((660, 420), pygame.SRCALPHA)
    pygame.draw.rect(painel, (14, 22, 53, 232), (0, 0, 660, 420), border_radius=28)
    pygame.draw.rect(painel, (117, 96, 244, 240), (0, 0, 660, 420), 4, border_radius=28)
    TELA.blit(painel, (150, 65))

    # título com brilho
    escrever(
        "AVENTURA DOS",
        FONTE_GRANDE,
        BRANCO,
        LARGURA_TELA // 2,
        105,
        True,
        True,
    )
    escrever(
        "CRISTAIS",
        FONTE_TITULO,
        AMARELO,
        LARGURA_TELA // 2,
        157,
        True,
        True,
    )

    desenhar_cristal_icone(TELA, 331, 155, 15, CIANO)
    desenhar_cristal_icone(TELA, 629, 155, 15, MAGENTA)

    escrever(
        "3 fases • cristais • portais • vilões",
        FONTE_PEQUENA_BOLD,
        CIANO_CLARO,
        LARGURA_TELA // 2,
        203,
        True,
    )

    escrever(
        "CONTROLES TOUCH",
        FONTE_PEQUENA_BOLD,
        ROXO_CLARO,
        LARGURA_TELA // 2,
        245,
        True,
    )
    escrever(
        "TRÁS / FRENTE   •   PULAR   •   FACA",
        FONTE_PEQUENA_BOLD,
        BRANCO,
        LARGURA_TELA // 2,
        277,
        True,
    )
    escrever(
        "Objetivo: colete os 5 cristais de cada fase e entre no portal.",
        FONTE_PEQUENA,
        BRANCO,
        LARGURA_TELA // 2,
        318,
        True,
    )
    escrever(
        "No celular/tablet, use em modo paisagem para ficar melhor.",
        FONTE_MICRO,
        AMARELO,
        LARGURA_TELA // 2,
        350,
        True,
    )

    desenhar_avatar_menu()

    desenhar_botao(
        BOTAO_INICIAR,
        "TOQUE PARA COMEÇAR",
        VERDE,
        FONTE_MEDIA,
        PRETO,
    )


def desenhar_tela_fase_completa(fase_indice):
    desenhar_fundo(fase_indice, 0)

    overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    overlay.fill((5, 8, 20, 145))
    TELA.blit(overlay, (0, 0))

    painel = pygame.Rect(210, 110, 540, 320)
    pygame.draw.rect(TELA, AZUL_ESCURO, painel, border_radius=26)
    pygame.draw.rect(TELA, CIANO, painel, 4, border_radius=26)

    escrever(
        "FASE CONCLUÍDA!",
        FONTE_GRANDE,
        CIANO_CLARO,
        LARGURA_TELA // 2,
        175,
        True,
        True,
    )
    escrever(
        PALETAS[fase_indice]["nome"],
        FONTE_MEDIA,
        BRANCO,
        LARGURA_TELA // 2,
        230,
        True,
    )
    escrever(
        "Todos os cristais foram coletados.",
        FONTE_PEQUENA,
        AMARELO,
        LARGURA_TELA // 2,
        270,
        True,
    )

    desenhar_botao(BOTAO_PROXIMA, "IR PARA A PRÓXIMA FASE", VERDE, FONTE_MEDIA, PRETO)


def desenhar_tela_final(titulo, subtitulo, cor):
    desenhar_fundo(2, 0)

    overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    overlay.fill((5, 8, 20, 150))
    TELA.blit(overlay, (0, 0))

    painel = pygame.Rect(185, 80, 590, 390)
    pygame.draw.rect(TELA, AZUL_NOITE, painel, border_radius=28)
    pygame.draw.rect(TELA, cor, painel, 4, border_radius=28)

    desenhar_cristal_icone(TELA, 290, 160, 20, CIANO)
    desenhar_cristal_icone(TELA, 670, 160, 20, MAGENTA)

    escrever(
        titulo,
        FONTE_GRANDE,
        cor,
        LARGURA_TELA // 2,
        165,
        True,
        True,
    )
    escrever(
        subtitulo,
        FONTE_MEDIA,
        BRANCO,
        LARGURA_TELA // 2,
        230,
        True,
    )

    desenhar_botao(BOTAO_FINAL_JOGAR, "JOGAR DE NOVO", VERDE, FONTE_MEDIA, PRETO)
    desenhar_botao(BOTAO_FINAL_MENU, "VOLTAR AO MENU", ROXO, FONTE_MEDIA)


def desenhar_pause(fase_indice):
    overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))
    TELA.blit(overlay, (0, 0))

    painel = pygame.Rect(250, 120, 460, 320)
    pygame.draw.rect(TELA, AZUL_NOITE, painel, border_radius=24)
    pygame.draw.rect(TELA, PALETAS[fase_indice]["detalhe"], painel, 3, border_radius=24)

    escrever(
        "PAUSADO",
        FONTE_GRANDE,
        AMARELO,
        LARGURA_TELA // 2,
        190,
        True,
        True,
    )
    escrever(
        "Você pode continuar ou voltar ao menu.",
        FONTE_PEQUENA,
        BRANCO,
        LARGURA_TELA // 2,
        235,
        True,
    )

    desenhar_botao(BOTAO_PAUSA_CONTINUAR, "CONTINUAR", VERDE, FONTE_MEDIA, PRETO)
    desenhar_botao(BOTAO_PAUSA_MENU, "VOLTAR AO MENU", ROXO, FONTE_MEDIA)


# ------------------------------------------------------------
# LOOP PRINCIPAL
# ------------------------------------------------------------


async def main():
    global mouse_ativo, mouse_posicao

    estado = MENU
    fase_indice = 0

    (
        jogador,
        plataformas,
        cristais,
        inimigos,
        portal,
        largura_fase,
        cristais_coletados,
        som_final_tocado,
        particulas,
    ) = reiniciar_fase(fase_indice, 3)

    rodando = True

    def carregar_fase(indice, vidas=3):
        return reiniciar_fase(indice, vidas)

    def iniciar_jogo_novo():
        nonlocal fase_indice
        fase_indice = 0
        return carregar_fase(0, 3)

    def acao_toque(pos):
        nonlocal estado, fase_indice
        nonlocal jogador, plataformas, cristais, inimigos, portal
        nonlocal largura_fase, cristais_coletados, som_final_tocado, particulas

        iniciar_musica()

        if estado == MENU:
            if BOTAO_INICIAR.collidepoint(pos):
                (
                    jogador,
                    plataformas,
                    cristais,
                    inimigos,
                    portal,
                    largura_fase,
                    cristais_coletados,
                    som_final_tocado,
                    particulas,
                ) = iniciar_jogo_novo()
                estado = JOGANDO
                toques_ativos.clear()

        elif estado == JOGANDO:
            if BOTAO_PAUSA.collidepoint(pos):
                estado = PAUSADO
                toques_ativos.clear()

            elif BOTAO_REINICIAR.collidepoint(pos):
                vidas = max(1, jogador.vidas)
                (
                    jogador,
                    plataformas,
                    cristais,
                    inimigos,
                    portal,
                    largura_fase,
                    cristais_coletados,
                    som_final_tocado,
                    particulas,
                ) = carregar_fase(fase_indice, vidas)
                toques_ativos.clear()

            elif BOTAO_MENU.collidepoint(pos):
                estado = MENU
                toques_ativos.clear()

        elif estado == PAUSADO:
            if BOTAO_PAUSA_CONTINUAR.collidepoint(pos):
                estado = JOGANDO
                toques_ativos.clear()

            elif BOTAO_PAUSA_MENU.collidepoint(pos):
                estado = MENU
                toques_ativos.clear()

        elif estado == FASE_COMPLETA:
            if BOTAO_PROXIMA.collidepoint(pos):
                fase_indice += 1
                (
                    jogador,
                    plataformas,
                    cristais,
                    inimigos,
                    portal,
                    largura_fase,
                    cristais_coletados,
                    som_final_tocado,
                    particulas,
                ) = carregar_fase(fase_indice, max(1, jogador.vidas))
                estado = JOGANDO
                toques_ativos.clear()

        elif estado in (VITORIA, DERROTA):
            if BOTAO_FINAL_JOGAR.collidepoint(pos):
                (
                    jogador,
                    plataformas,
                    cristais,
                    inimigos,
                    portal,
                    largura_fase,
                    cristais_coletados,
                    som_final_tocado,
                    particulas,
                ) = iniciar_jogo_novo()
                estado = JOGANDO
                toques_ativos.clear()

            elif BOTAO_FINAL_MENU.collidepoint(pos):
                estado = MENU
                toques_ativos.clear()

    while rodando:
        RELOGIO.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            # ---------------- TECLADO ----------------
            if evento.type == pygame.KEYDOWN:
                iniciar_musica()

                if estado == MENU:
                    if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        (
                            jogador,
                            plataformas,
                            cristais,
                            inimigos,
                            portal,
                            largura_fase,
                            cristais_coletados,
                            som_final_tocado,
                            particulas,
                        ) = iniciar_jogo_novo()
                        estado = JOGANDO

                elif estado == JOGANDO:
                    if evento.key == pygame.K_p:
                        estado = PAUSADO
                    elif evento.key == pygame.K_r:
                        (
                            jogador,
                            plataformas,
                            cristais,
                            inimigos,
                            portal,
                            largura_fase,
                            cristais_coletados,
                            som_final_tocado,
                            particulas,
                        ) = carregar_fase(fase_indice, max(1, jogador.vidas))
                    elif evento.key == pygame.K_m:
                        estado = MENU

                elif estado == PAUSADO:
                    if evento.key == pygame.K_p:
                        estado = JOGANDO
                    elif evento.key == pygame.K_m:
                        estado = MENU

                elif estado == FASE_COMPLETA:
                    if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        fase_indice += 1
                        (
                            jogador,
                            plataformas,
                            cristais,
                            inimigos,
                            portal,
                            largura_fase,
                            cristais_coletados,
                            som_final_tocado,
                            particulas,
                        ) = carregar_fase(fase_indice, max(1, jogador.vidas))
                        estado = JOGANDO

                elif estado in (VITORIA, DERROTA):
                    if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        (
                            jogador,
                            plataformas,
                            cristais,
                            inimigos,
                            portal,
                            largura_fase,
                            cristais_coletados,
                            som_final_tocado,
                            particulas,
                        ) = iniciar_jogo_novo()
                        estado = JOGANDO
                    elif evento.key == pygame.K_m:
                        estado = MENU

            # ---------------- TOUCH REAL ----------------
            if evento.type == pygame.FINGERDOWN:
                pos = posicao_toque(evento)
                toques_ativos[evento.finger_id] = pos
                acao_toque(pos)

            elif evento.type == pygame.FINGERMOTION:
                toques_ativos[evento.finger_id] = posicao_toque(evento)

            elif evento.type == pygame.FINGERUP:
                toques_ativos.pop(evento.finger_id, None)

            # ---------------- MOUSE / FALLBACK TOUCH ----------------
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mouse_ativo = True
                mouse_posicao = evento.pos
                acao_toque(evento.pos)

            elif evento.type == pygame.MOUSEMOTION:
                if mouse_ativo:
                    mouse_posicao = evento.pos

            elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                mouse_posicao = evento.pos
                mouse_ativo = False

        # ------------------------------------------------
        # ATUALIZAÇÃO
        # ------------------------------------------------
        if estado == JOGANDO:
            teclas = pygame.key.get_pressed()
            toque_tras, toque_frente, toque_pulo, toque_ataque = ler_touch()

            jogador.atualizar(
                teclas,
                plataformas,
                largura_fase,
                toque_tras,
                toque_frente,
                toque_pulo,
                toque_ataque,
            )

            for inimigo in inimigos:
                inimigo.atualizar()

                if inimigo.vivo and jogador.ataque_rect.colliderect(inimigo.rect):
                    inimigo.vivo = False
                    criar_particulas(
                        particulas,
                        inimigo.rect.centerx,
                        inimigo.rect.centery,
                        PALETAS[fase_indice]["detalhe"],
                        13,
                    )

                if inimigo.vivo and jogador.rect.colliderect(inimigo.rect):
                    if jogador.tomar_dano():
                        criar_particulas(
                            particulas,
                            jogador.rect.centerx,
                            jogador.rect.centery,
                            VERMELHO,
                            12,
                        )

            for cristal in cristais:
                cristal.atualizar()

                if not cristal.coletado and jogador.rect.colliderect(cristal.rect):
                    cristal.coletado = True
                    cristais_coletados += 1
                    tocar("cristal")
                    criar_particulas(
                        particulas,
                        cristal.rect.centerx,
                        cristal.rect.centery,
                        PALETAS[fase_indice]["detalhe"],
                        18,
                    )

            portal.atualizar()

            for p in particulas[:]:
                p.atualizar()
                if p.vida <= 0:
                    particulas.remove(p)

            if jogador.rect.top > ALTURA_TELA + 80:
                jogador.vidas -= 1
                tocar("dano")
                if jogador.vidas > 0:
                    jogador.reiniciar_posicao()

            if jogador.vidas <= 0:
                estado = DERROTA
                toques_ativos.clear()
                if not som_final_tocado:
                    tocar("derrota")
                    som_final_tocado = True

            total_cristais = len(cristais)
            if (
                cristais_coletados >= total_cristais
                and jogador.rect.colliderect(portal.rect)
            ):
                toques_ativos.clear()

                if fase_indice < len(FASES) - 1:
                    estado = FASE_COMPLETA
                else:
                    estado = VITORIA
                    if not som_final_tocado:
                        tocar("vitoria")
                        som_final_tocado = True

        # ------------------------------------------------
        # CÂMERA
        # ------------------------------------------------
        camera_x = jogador.rect.centerx - LARGURA_TELA // 2
        camera_x = max(0, min(camera_x, largura_fase - LARGURA_TELA))

        # ------------------------------------------------
        # DESENHO
        # ------------------------------------------------
        if estado == MENU:
            desenhar_menu()

        elif estado in (JOGANDO, PAUSADO):
            desenhar_fundo(fase_indice, camera_x)
            desenhar_plataformas(plataformas, camera_x, fase_indice)

            for cristal in cristais:
                cristal.desenhar(TELA, camera_x, PALETAS[fase_indice]["detalhe"])

            for inimigo in inimigos:
                inimigo.desenhar(TELA, camera_x, fase_indice)

            portal.desenhar(
                TELA,
                camera_x,
                cristais_coletados >= len(cristais),
                PALETAS[fase_indice]["detalhe"],
            )

            for p in particulas:
                p.desenhar(TELA, camera_x)

            jogador.desenhar(TELA, camera_x)

            desenhar_hud(
                jogador,
                cristais_coletados,
                len(cristais),
                fase_indice,
            )

            if estado == JOGANDO:
                desenhar_controles_touch()
            else:
                desenhar_pause(fase_indice)

        elif estado == FASE_COMPLETA:
            desenhar_tela_fase_completa(fase_indice)

        elif estado == VITORIA:
            desenhar_tela_final(
                "VOCÊ VENCEU!",
                "As três fases foram concluídas!",
                CIANO_CLARO,
            )

        elif estado == DERROTA:
            desenhar_tela_final(
                "GAME OVER",
                "Você perdeu todas as vidas.",
                VERMELHO,
            )

        pygame.display.flip()

        # ESSENCIAL para Pygbag no navegador
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
