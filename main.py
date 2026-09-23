import os
import math
import asyncio
import pygame

# ============================================================
# AVENTURA DOS CRISTAIS 2D
# main.py limpo e compatível com Pygbag/GitHub Pages
# ============================================================

LARGURA_TELA = 960
ALTURA_TELA = 540
FPS = 60
GRAVIDADE = 0.75
LARGURA_FASE = 2450

MENU = "menu"
JOGANDO = "jogando"
PAUSADO = "pausado"
VITORIA = "vitoria"
DERROTA = "derrota"

BRANCO = (245, 245, 245)
PRETO = (10, 10, 20)
AZUL_CEU = (110, 180, 240)
AZUL_ESCURO = (25, 35, 70)
VERDE = (50, 180, 90)
VERDE_ESCURO = (30, 100, 55)
ROXO = (120, 70, 180)
ROXO_ESCURO = (65, 40, 110)
ROXO_CLARO = (170, 120, 220)
AMARELO = (255, 215, 80)
LARANJA = (255, 140, 50)
VERMELHO = (220, 55, 55)
CINZA = (90, 90, 110)
MARROM = (110, 70, 40)
CIANO = (80, 235, 255)
PELE = (255, 210, 210)
CABELO = (120, 65, 40)
SOMBRA = (35, 35, 50)
VERDE_CLARO = (120, 220, 120)
VERDE_SLIME = (90, 210, 110)

# ------------------------------------------------------------
# INICIALIZAÇÃO
# ------------------------------------------------------------

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

TELA = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Aventura dos Cristais - Jogo 2D")
RELOGIO = pygame.time.Clock()

FONTE_PEQUENA = pygame.font.SysFont("arial", 20)
FONTE_MEDIA = pygame.font.SysFont("arial", 28, bold=True)
FONTE_GRANDE = pygame.font.SysFont("arial", 50, bold=True)

# ------------------------------------------------------------
# SOM OPCIONAL
# Se a pasta assets/sons existir, os sons serão usados.
# Se não existir, o jogo continua funcionando normalmente.
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SONS_DIR = os.path.join(BASE_DIR, "assets", "sons")


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
    try:
        caminho = os.path.join(SONS_DIR, "musica.wav")
        if pygame.mixer.get_init() and os.path.exists(caminho):
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.set_volume(0.25)
            pygame.mixer.music.play(-1)
    except Exception:
        pass


iniciar_musica()

# ------------------------------------------------------------
# CLASSES
# ------------------------------------------------------------


class Jogador:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 38, 58)
        self.vel_x = 0
        self.vel_y = 0
        self.velocidade = 5
        self.forca_pulo = -15
        self.no_chao = False
        self.vidas = 3
        self.direcao = 1
        self.invencivel = 0
        self.cooldown_ataque = 0
        self.tempo_ataque = 0
        self.ataque_rect = pygame.Rect(0, 0, 0, 0)

    def reiniciar_posicao(self):
        self.rect.x = 70
        self.rect.y = 330
        self.vel_x = 0
        self.vel_y = 0
        self.invencivel = 90

    def atualizar(self, teclas, plataformas, toque_esquerda=False,
                  toque_direita=False, toque_pulo=False, toque_ataque=False):
        self.vel_x = 0

        esquerda = teclas[pygame.K_a] or teclas[pygame.K_LEFT] or toque_esquerda
        direita = teclas[pygame.K_d] or teclas[pygame.K_RIGHT] or toque_direita
        pulo = (
            teclas[pygame.K_SPACE]
            or teclas[pygame.K_w]
            or teclas[pygame.K_UP]
            or toque_pulo
        )
        ataque = (
            teclas[pygame.K_LCTRL]
            or teclas[pygame.K_RCTRL]
            or toque_ataque
        )

        if esquerda:
            self.vel_x = -self.velocidade
            self.direcao = -1

        if direita:
            self.vel_x = self.velocidade
            self.direcao = 1

        if pulo and self.no_chao:
            self.vel_y = self.forca_pulo
            self.no_chao = False
            tocar("pulo")

        if ataque and self.cooldown_ataque <= 0:
            self.cooldown_ataque = 28
            self.tempo_ataque = 10
            tocar("ataque")

        if self.cooldown_ataque > 0:
            self.cooldown_ataque -= 1

        if self.tempo_ataque > 0:
            self.tempo_ataque -= 1

        if self.invencivel > 0:
            self.invencivel -= 1

        self.rect.x += self.vel_x
        self.colisao_horizontal(plataformas)

        self.vel_y += GRAVIDADE
        if self.vel_y > 18:
            self.vel_y = 18

        self.rect.y += int(self.vel_y)
        self.colisao_vertical(plataformas)

        if self.rect.left < 0:
            self.rect.left = 0

        if self.rect.right > LARGURA_FASE:
            self.rect.right = LARGURA_FASE

        if self.tempo_ataque > 0:
            if self.direcao == 1:
                self.ataque_rect = pygame.Rect(
                    self.rect.right, self.rect.y + 16, 44, 24
                )
            else:
                self.ataque_rect = pygame.Rect(
                    self.rect.left - 44, self.rect.y + 16, 44, 24
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

    def desenhar(self, tela, camera_x):
        x = self.rect.x - camera_x
        y = self.rect.y

        if self.invencivel > 0 and (self.invencivel // 6) % 2 == 0:
            return

        pygame.draw.ellipse(tela, SOMBRA, (x + 8, y + 52, 24, 8))

        pygame.draw.ellipse(tela, CABELO, (x + 7, y + 1, 24, 14))
        pygame.draw.circle(tela, PELE, (x + 19, y + 13), 12)

        pygame.draw.circle(tela, PRETO, (x + 15, y + 11), 2)
        pygame.draw.circle(tela, PRETO, (x + 23, y + 11), 2)
        pygame.draw.arc(tela, PRETO, (x + 14, y + 12, 10, 7), 0.2, 2.9, 1)

        pygame.draw.rect(
            tela, ROXO, (x + 8, y + 24, 22, 23), border_radius=8
        )
        pygame.draw.rect(
            tela, ROXO_CLARO, (x + 12, y + 27, 14, 8), border_radius=4
        )

        pygame.draw.line(tela, PELE, (x + 8, y + 29), (x + 2, y + 38), 4)
        pygame.draw.line(tela, PELE, (x + 30, y + 29), (x + 36, y + 38), 4)

        pygame.draw.line(
            tela, AZUL_ESCURO, (x + 14, y + 47), (x + 12, y + 57), 4
        )
        pygame.draw.line(
            tela, AZUL_ESCURO, (x + 24, y + 47), (x + 26, y + 57), 4
        )

        pygame.draw.ellipse(tela, SOMBRA, (x + 7, y + 55, 10, 6))
        pygame.draw.ellipse(tela, SOMBRA, (x + 22, y + 55, 10, 6))

        pygame.draw.rect(
            tela, SOMBRA, (x + 8, y + 24, 22, 23), 2, border_radius=8
        )

        if self.tempo_ataque > 0:
            ataque = self.ataque_rect.move(-camera_x, 0)
            pygame.draw.rect(tela, AMARELO, ataque, border_radius=8)
            pygame.draw.rect(tela, LARANJA, ataque, 2, border_radius=8)


class Inimigo:
    def __init__(self, x, y, tipo="slime", esquerda=None, direita=None):
        self.tipo = tipo
        if tipo == "slime":
            self.rect = pygame.Rect(x, y, 42, 34)
        else:
            self.rect = pygame.Rect(x, y, 46, 30)

        self.y_inicial = y
        self.vel = 2 if tipo == "slime" else 2.5
        self.direcao = 1
        self.esquerda = esquerda if esquerda is not None else x - 120
        self.direita = direita if direita is not None else x + 120
        self.vivo = True
        self.tempo = 0

    def atualizar(self):
        if not self.vivo:
            return

        self.tempo += 1
        self.rect.x += int(self.vel * self.direcao)

        if self.rect.x <= self.esquerda:
            self.direcao = 1

        if self.rect.x >= self.direita:
            self.direcao = -1

        if self.tipo == "morcego":
            self.rect.y = self.y_inicial + int(math.sin(self.tempo * 0.08) * 22)

    def desenhar(self, tela, camera_x):
        if not self.vivo:
            return

        x = self.rect.x - camera_x
        y = self.rect.y

        if self.tipo == "slime":
            pygame.draw.ellipse(tela, SOMBRA, (x + 6, y + 28, 28, 6))
            pygame.draw.ellipse(tela, VERDE_SLIME, (x, y + 5, 42, 28))
            pygame.draw.ellipse(tela, VERDE_CLARO, (x + 6, y + 8, 16, 8))
            pygame.draw.ellipse(tela, VERDE_ESCURO, (x + 4, y + 22, 34, 9))

            pygame.draw.circle(tela, PRETO, (x + 14, y + 16), 2)
            pygame.draw.circle(tela, PRETO, (x + 28, y + 16), 2)

            pygame.draw.arc(
                tela, PRETO, (x + 14, y + 16, 14, 8), 0.2, 2.9, 1
            )
            pygame.draw.ellipse(tela, VERDE_ESCURO, (x, y + 5, 42, 28), 2)

        else:
            pygame.draw.ellipse(tela, SOMBRA, (x + 10, y + 22, 24, 6))

            pygame.draw.polygon(
                tela, ROXO, [(x + 16, y + 16), (x - 6, y + 2), (x + 5, y + 26)]
            )
            pygame.draw.polygon(
                tela, ROXO, [(x + 30, y + 16), (x + 52, y + 2), (x + 41, y + 26)]
            )

            pygame.draw.ellipse(tela, ROXO_ESCURO, (x + 12, y + 10, 22, 16))

            pygame.draw.polygon(
                tela, ROXO_ESCURO,
                [(x + 15, y + 12), (x + 18, y + 4), (x + 21, y + 12)]
            )
            pygame.draw.polygon(
                tela, ROXO_ESCURO,
                [(x + 25, y + 12), (x + 28, y + 4), (x + 31, y + 12)]
            )

            pygame.draw.circle(tela, AMARELO, (x + 20, y + 17), 2)
            pygame.draw.circle(tela, AMARELO, (x + 27, y + 17), 2)


class Cristal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 28, 34)
        self.coletado = False
        self.tempo = 0

    def atualizar(self):
        self.tempo += 1

    def desenhar(self, tela, camera_x):
        if self.coletado:
            return

        x = self.rect.x - camera_x
        y = self.rect.y + int(math.sin(self.tempo * 0.08) * 5)

        pontos = [
            (x + 14, y),
            (x + 28, y + 16),
            (x + 14, y + 34),
            (x, y + 16),
        ]

        pygame.draw.polygon(tela, CIANO, pontos)
        pygame.draw.polygon(
            tela,
            BRANCO,
            [
                (x + 14, y + 3),
                (x + 22, y + 16),
                (x + 14, y + 28),
                (x + 7, y + 16),
            ],
            2,
        )

        pygame.draw.circle(tela, BRANCO, (x + 10, y + 10), 2)
        pygame.draw.circle(tela, BRANCO, (x + 18, y + 14), 1)


class Portal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 72, 92)
        self.tempo = 0

    def atualizar(self):
        self.tempo += 1

    def desenhar(self, tela, camera_x, aberto):
        x = self.rect.x - camera_x
        y = self.rect.y
        cor = CIANO if aberto else CINZA

        pygame.draw.ellipse(tela, cor, (x + 6, y, 60, 92), 6)
        pygame.draw.ellipse(
            tela,
            ROXO if aberto else AZUL_ESCURO,
            (x + 16, y + 12, 40, 68),
        )

        if aberto:
            pygame.draw.circle(tela, BRANCO, (x + 36, y + 46), 6)


# ------------------------------------------------------------
# FASE
# ------------------------------------------------------------


def criar_fase():
    plataformas = [
        pygame.Rect(0, 470, 520, 70),
        pygame.Rect(620, 470, 430, 70),
        pygame.Rect(1140, 470, 390, 70),
        pygame.Rect(1640, 470, 820, 70),
        pygame.Rect(300, 370, 170, 24),
        pygame.Rect(770, 345, 180, 24),
        pygame.Rect(1260, 335, 160, 24),
        pygame.Rect(1770, 365, 190, 24),
        pygame.Rect(2050, 300, 160, 24),
    ]

    cristais = [
        Cristal(350, 320),
        Cristal(830, 295),
        Cristal(1285, 285),
        Cristal(1840, 315),
        Cristal(2110, 250),
    ]

    inimigos = [
        Inimigo(220, 435, "slime", 90, 430),
        Inimigo(700, 435, "slime", 650, 950),
        Inimigo(1210, 435, "slime", 1160, 1460),
        Inimigo(1700, 435, "slime", 1660, 1950),
        Inimigo(980, 260, "morcego", 880, 1100),
        Inimigo(1510, 260, "morcego", 1420, 1620),
        Inimigo(2160, 210, "morcego", 2050, 2290),
    ]

    portal = Portal(2310, 378)
    jogador = Jogador(70, 330)

    return jogador, plataformas, cristais, inimigos, portal


# ------------------------------------------------------------
# FUNÇÕES DE DESENHO
# ------------------------------------------------------------


def escrever(texto, fonte, cor, x, y, centralizado=False):
    img = fonte.render(texto, True, cor)
    rect = img.get_rect()

    if centralizado:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    TELA.blit(img, rect)


def desenhar_fundo(camera_x):
    TELA.fill(AZUL_CEU)

    pygame.draw.circle(TELA, AMARELO, (820, 80), 42)

    nuvens = [
        (170, 90),
        (480, 70),
        (760, 130),
        (1110, 85),
        (1500, 120),
        (1980, 80),
    ]

    for cx, cy in nuvens:
        sx = cx - camera_x * 0.25

        while sx < -140:
            sx += 1200

        while sx > LARGURA_TELA + 140:
            sx -= 1200

        pygame.draw.circle(TELA, BRANCO, (int(sx), cy), 22)
        pygame.draw.circle(TELA, BRANCO, (int(sx + 25), cy + 8), 26)
        pygame.draw.circle(TELA, BRANCO, (int(sx - 28), cy + 10), 19)
        pygame.draw.rect(TELA, BRANCO, (int(sx - 32), cy + 10, 68, 18))

    for mx in range(-200, LARGURA_FASE + 600, 360):
        sx = mx - camera_x * 0.35

        pygame.draw.polygon(
            TELA,
            (65, 120, 170),
            [(sx, 470), (sx + 190, 210), (sx + 380, 470)],
        )

        pygame.draw.polygon(
            TELA,
            (80, 145, 185),
            [(sx + 80, 470), (sx + 240, 260), (sx + 430, 470)],
        )


def desenhar_plataformas(plataformas, camera_x):
    for p in plataformas:
        r = pygame.Rect(p.x - camera_x, p.y, p.w, p.h)

        pygame.draw.rect(TELA, MARROM, r)

        topo = pygame.Rect(r.x, r.y, r.w, 12)
        pygame.draw.rect(TELA, VERDE, topo)

        pygame.draw.rect(TELA, VERDE_ESCURO, r, 2)


def desenhar_hud(jogador, cristais_coletados):
    pygame.draw.rect(TELA, AZUL_ESCURO, (0, 0, LARGURA_TELA, 58))

    escrever(
        f"Vidas: {jogador.vidas}",
        FONTE_MEDIA,
        BRANCO,
        18,
        14,
    )

    escrever(
        f"Cristais: {cristais_coletados}/5",
        FONTE_MEDIA,
        BRANCO,
        160,
        14,
    )

    escrever(
        "Pegue 5 cristais e entre no portal!",
        FONTE_PEQUENA,
        AMARELO,
        340,
        18,
    )


def desenhar_botao(rect, texto, cor_fundo, fonte=FONTE_MEDIA, cor_texto=BRANCO):
    pygame.draw.rect(TELA, cor_fundo, rect, border_radius=12)
    pygame.draw.rect(TELA, BRANCO, rect, 2, border_radius=12)
    escrever(
        texto,
        fonte,
        cor_texto,
        rect.centerx,
        rect.centery,
        True,
    )


def desenhar_menu():
    desenhar_fundo(0)

    pygame.draw.rect(
        TELA,
        AZUL_ESCURO,
        (100, 35, 760, 470),
        border_radius=22,
    )

    pygame.draw.rect(
        TELA,
        ROXO,
        (100, 35, 760, 470),
        4,
        border_radius=22,
    )

    escrever(
        "AVENTURA DOS CRISTAIS",
        FONTE_GRANDE,
        AMARELO,
        LARGURA_TELA // 2,
        92,
        True,
    )

    escrever(
        "Jogo 2D para computador, celular e tablet",
        FONTE_MEDIA,
        BRANCO,
        LARGURA_TELA // 2,
        140,
        True,
    )

    escrever(
        "CONTROLES NA TELA",
        FONTE_MEDIA,
        CIANO,
        LARGURA_TELA // 2,
        195,
        True,
    )

    escrever(
        "ESQ / DIR  -  Andar",
        FONTE_PEQUENA,
        BRANCO,
        LARGURA_TELA // 2,
        235,
        True,
    )

    escrever(
        "PULAR  -  Pular obstáculos",
        FONTE_PEQUENA,
        BRANCO,
        LARGURA_TELA // 2,
        270,
        True,
    )

    escrever(
        "FACA  -  Atacar inimigos",
        FONTE_PEQUENA,
        BRANCO,
        LARGURA_TELA // 2,
        305,
        True,
    )

    escrever(
        "II = Pausar     R = Reiniciar     MENU = Voltar",
        FONTE_PEQUENA,
        BRANCO,
        LARGURA_TELA // 2,
        340,
        True,
    )

    escrever(
        "Objetivo: pegue 5 cristais e entre no portal final!",
        FONTE_PEQUENA,
        AMARELO,
        LARGURA_TELA // 2,
        390,
        True,
    )

    desenhar_botao(
        BOTAO_INICIAR,
        "TOQUE AQUI PARA COMEÇAR",
        VERDE,
        FONTE_MEDIA,
    )


def desenhar_tela_final(titulo, subtitulo, cor):
    desenhar_fundo(0)

    pygame.draw.rect(
        TELA,
        AZUL_ESCURO,
        (150, 95, 660, 360),
        border_radius=22,
    )

    pygame.draw.rect(
        TELA,
        cor,
        (150, 95, 660, 360),
        4,
        border_radius=22,
    )

    escrever(
        titulo,
        FONTE_GRANDE,
        cor,
        LARGURA_TELA // 2,
        165,
        True,
    )

    escrever(
        subtitulo,
        FONTE_MEDIA,
        BRANCO,
        LARGURA_TELA // 2,
        225,
        True,
    )

    desenhar_botao(
        BOTAO_FINAL_JOGAR,
        "JOGAR DE NOVO",
        VERDE,
        FONTE_MEDIA,
    )

    desenhar_botao(
        BOTAO_FINAL_MENU,
        "VOLTAR AO MENU",
        ROXO,
        FONTE_MEDIA,
    )


def desenhar_pause():
    overlay = pygame.Surface(
        (LARGURA_TELA, ALTURA_TELA),
        pygame.SRCALPHA,
    )

    overlay.fill((0, 0, 0, 175))
    TELA.blit(overlay, (0, 0))

    pygame.draw.rect(
        TELA,
        AZUL_ESCURO,
        (235, 125, 490, 300),
        border_radius=22,
    )

    pygame.draw.rect(
        TELA,
        AMARELO,
        (235, 125, 490, 300),
        3,
        border_radius=22,
    )

    escrever(
        "PAUSADO",
        FONTE_GRANDE,
        AMARELO,
        LARGURA_TELA // 2,
        190,
        True,
    )

    desenhar_botao(
        BOTAO_PAUSA_CONTINUAR,
        "CONTINUAR",
        VERDE,
        FONTE_MEDIA,
    )

    desenhar_botao(
        BOTAO_PAUSA_MENU,
        "VOLTAR AO MENU",
        ROXO,
        FONTE_MEDIA,
    )


# ------------------------------------------------------------
# BOTÕES PARA TABLET/CELULAR
# ------------------------------------------------------------

# Botão da tela inicial
BOTAO_INICIAR = pygame.Rect(285, 425, 390, 58)

# Botões durante o jogo
BOTAO_ESQUERDA = pygame.Rect(20, 445, 105, 75)
BOTAO_DIREITA = pygame.Rect(140, 445, 105, 75)
BOTAO_PULO = pygame.Rect(650, 445, 120, 75)
BOTAO_ATAQUE = pygame.Rect(785, 445, 155, 75)

BOTAO_PAUSA = pygame.Rect(680, 8, 75, 42)
BOTAO_REINICIAR = pygame.Rect(765, 8, 75, 42)
BOTAO_MENU = pygame.Rect(850, 8, 95, 42)

# Botões da tela de pausa
BOTAO_PAUSA_CONTINUAR = pygame.Rect(325, 270, 310, 55)
BOTAO_PAUSA_MENU = pygame.Rect(325, 345, 310, 55)

# Botões das telas de vitória/derrota
BOTAO_FINAL_JOGAR = pygame.Rect(285, 285, 390, 55)
BOTAO_FINAL_MENU = pygame.Rect(285, 360, 390, 55)

# Toques ativos permitem segurar uma direção e tocar em PULAR/FACA
# ao mesmo tempo em celulares e tablets.
toques_ativos = {}
mouse_ativo = False
mouse_posicao = (0, 0)


def posicao_toque(evento):
    return (
        int(evento.x * LARGURA_TELA),
        int(evento.y * ALTURA_TELA),
    )


def desenhar_botao_touch(rect, texto, cor_fundo):
    superficie = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    superficie.fill((cor_fundo[0], cor_fundo[1], cor_fundo[2], 190))
    TELA.blit(superficie, rect.topleft)
    pygame.draw.rect(TELA, BRANCO, rect, 3, border_radius=14)

    escrever(
        texto,
        FONTE_MEDIA,
        BRANCO,
        rect.centerx,
        rect.centery,
        True,
    )


def desenhar_controles_touch():
    desenhar_botao_touch(BOTAO_ESQUERDA, "ESQ", ROXO)
    desenhar_botao_touch(BOTAO_DIREITA, "DIR", ROXO)
    desenhar_botao_touch(BOTAO_PULO, "PULAR", VERDE)
    desenhar_botao_touch(BOTAO_ATAQUE, "FACA", VERMELHO)

    desenhar_botao_touch(BOTAO_PAUSA, "II", CINZA)
    desenhar_botao_touch(BOTAO_REINICIAR, "R", LARANJA)
    desenhar_botao_touch(BOTAO_MENU, "MENU", AZUL_ESCURO)


def pontos_touch_ativos():
    pontos = list(toques_ativos.values())
    if mouse_ativo:
        pontos.append(mouse_posicao)
    return pontos


def ler_touch():
    esquerda = False
    direita = False
    pulo = False
    ataque = False

    for pos in pontos_touch_ativos():
        if BOTAO_ESQUERDA.collidepoint(pos):
            esquerda = True
        if BOTAO_DIREITA.collidepoint(pos):
            direita = True
        if BOTAO_PULO.collidepoint(pos):
            pulo = True
        if BOTAO_ATAQUE.collidepoint(pos):
            ataque = True

    return esquerda, direita, pulo, ataque


def reiniciar_jogo():
    jogador, plataformas, cristais, inimigos, portal = criar_fase()
    return jogador, plataformas, cristais, inimigos, portal, 0, False


# ------------------------------------------------------------
# LOOP PRINCIPAL
# ------------------------------------------------------------


async def main():
    global mouse_ativo, mouse_posicao

    estado = MENU

    jogador, plataformas, cristais, inimigos, portal = criar_fase()
    cristais_coletados = 0
    som_final_tocado = False
    rodando = True

    def novo_jogo():
        return reiniciar_jogo()

    def acao_toque(pos):
        nonlocal estado
        nonlocal jogador, plataformas, cristais, inimigos, portal
        nonlocal cristais_coletados, som_final_tocado

        if estado == MENU:
            if BOTAO_INICIAR.collidepoint(pos):
                (
                    jogador,
                    plataformas,
                    cristais,
                    inimigos,
                    portal,
                    cristais_coletados,
                    som_final_tocado,
                ) = novo_jogo()
                estado = JOGANDO
                toques_ativos.clear()

        elif estado == JOGANDO:
            if BOTAO_PAUSA.collidepoint(pos):
                estado = PAUSADO
                toques_ativos.clear()

            elif BOTAO_REINICIAR.collidepoint(pos):
                (
                    jogador,
                    plataformas,
                    cristais,
                    inimigos,
                    portal,
                    cristais_coletados,
                    som_final_tocado,
                ) = novo_jogo()
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

        elif estado in (VITORIA, DERROTA):
            if BOTAO_FINAL_JOGAR.collidepoint(pos):
                (
                    jogador,
                    plataformas,
                    cristais,
                    inimigos,
                    portal,
                    cristais_coletados,
                    som_final_tocado,
                ) = novo_jogo()
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

            # ------------------------------------------------
            # TECLADO - continua funcionando no computador
            # ------------------------------------------------
            if evento.type == pygame.KEYDOWN:
                if estado == MENU:
                    if evento.key in (
                        pygame.K_RETURN,
                        pygame.K_KP_ENTER,
                        pygame.K_SPACE,
                    ):
                        (
                            jogador,
                            plataformas,
                            cristais,
                            inimigos,
                            portal,
                            cristais_coletados,
                            som_final_tocado,
                        ) = novo_jogo()
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
                            cristais_coletados,
                            som_final_tocado,
                        ) = novo_jogo()

                    elif evento.key == pygame.K_m:
                        estado = MENU

                elif estado == PAUSADO:
                    if evento.key == pygame.K_p:
                        estado = JOGANDO

                    elif evento.key == pygame.K_m:
                        estado = MENU

                elif estado in (VITORIA, DERROTA):
                    if evento.key in (
                        pygame.K_RETURN,
                        pygame.K_KP_ENTER,
                        pygame.K_SPACE,
                    ):
                        (
                            jogador,
                            plataformas,
                            cristais,
                            inimigos,
                            portal,
                            cristais_coletados,
                            som_final_tocado,
                        ) = novo_jogo()
                        estado = JOGANDO

                    elif evento.key == pygame.K_m:
                        estado = MENU

            # ------------------------------------------------
            # TOQUE REAL - celular/tablet (multitouch)
            # ------------------------------------------------
            if evento.type == pygame.FINGERDOWN:
                pos = posicao_toque(evento)
                toques_ativos[evento.finger_id] = pos
                acao_toque(pos)

            elif evento.type == pygame.FINGERMOTION:
                toques_ativos[evento.finger_id] = posicao_toque(evento)

            elif evento.type == pygame.FINGERUP:
                toques_ativos.pop(evento.finger_id, None)

            # ------------------------------------------------
            # MOUSE - computador e fallback do navegador
            # Ignora mouse gerado automaticamente por touch para
            # não executar PAUSA/MENU duas vezes.
            # ------------------------------------------------
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # No navegador (Pygbag), um toque na tela pode chegar como
                # evento de mouse com touch=True. Por isso processamos o
                # clique mesmo quando ele veio do toque do celular/tablet.
                mouse_ativo = True
                mouse_posicao = evento.pos
                acao_toque(evento.pos)

            elif evento.type == pygame.MOUSEMOTION:
                if mouse_ativo:
                    mouse_posicao = evento.pos

            elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                mouse_posicao = evento.pos
                mouse_ativo = False

        # ----------------------------------------------------
        # ATUALIZAÇÃO DO JOGO
        # ----------------------------------------------------
        if estado == JOGANDO:
            teclas = pygame.key.get_pressed()

            toque_esquerda, toque_direita, toque_pulo, toque_ataque = ler_touch()

            jogador.atualizar(
                teclas,
                plataformas,
                toque_esquerda,
                toque_direita,
                toque_pulo,
                toque_ataque,
            )

            for inimigo in inimigos:
                inimigo.atualizar()

                if (
                    inimigo.vivo
                    and jogador.ataque_rect.colliderect(inimigo.rect)
                ):
                    inimigo.vivo = False
                    tocar("ataque")

                if (
                    inimigo.vivo
                    and jogador.rect.colliderect(inimigo.rect)
                ):
                    jogador.tomar_dano()

            for cristal in cristais:
                cristal.atualizar()

                if (
                    not cristal.coletado
                    and jogador.rect.colliderect(cristal.rect)
                ):
                    cristal.coletado = True
                    cristais_coletados += 1
                    tocar("cristal")

            portal.atualizar()

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

            if (
                cristais_coletados >= 5
                and jogador.rect.colliderect(portal.rect)
            ):
                estado = VITORIA
                toques_ativos.clear()

                if not som_final_tocado:
                    tocar("vitoria")
                    som_final_tocado = True

        # ----------------------------------------------------
        # CÂMERA
        # ----------------------------------------------------
        camera_x = jogador.rect.centerx - LARGURA_TELA // 2
        camera_x = max(
            0,
            min(
                camera_x,
                LARGURA_FASE - LARGURA_TELA,
            ),
        )

        # ----------------------------------------------------
        # DESENHO DAS TELAS
        # ----------------------------------------------------
        if estado == MENU:
            desenhar_menu()

        elif estado == JOGANDO:
            desenhar_fundo(camera_x)
            desenhar_plataformas(plataformas, camera_x)

            for cristal in cristais:
                cristal.desenhar(TELA, camera_x)

            for inimigo in inimigos:
                inimigo.desenhar(TELA, camera_x)

            portal.desenhar(
                TELA,
                camera_x,
                cristais_coletados >= 5,
            )

            jogador.desenhar(TELA, camera_x)
            desenhar_hud(jogador, cristais_coletados)
            desenhar_controles_touch()

        elif estado == PAUSADO:
            desenhar_fundo(camera_x)
            desenhar_plataformas(plataformas, camera_x)

            for cristal in cristais:
                cristal.desenhar(TELA, camera_x)

            for inimigo in inimigos:
                inimigo.desenhar(TELA, camera_x)

            portal.desenhar(
                TELA,
                camera_x,
                cristais_coletados >= 5,
            )

            jogador.desenhar(TELA, camera_x)
            desenhar_hud(jogador, cristais_coletados)
            desenhar_pause()

        elif estado == VITORIA:
            desenhar_tela_final(
                "VOCÊ VENCEU!",
                "Pegou os 5 cristais e abriu o portal!",
                CIANO,
            )

        elif estado == DERROTA:
            desenhar_tela_final(
                "GAME OVER",
                "Você perdeu todas as vidas.",
                VERMELHO,
            )

        pygame.display.flip()

        # ESSENCIAL para funcionar no navegador com Pygbag
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
