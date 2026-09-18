import os
import sys
import math
import wave
import struct
import pygame

# =========================
# AVENTURA DOS CRISTAIS 2D
# Jogo demo em Python/Pygame
# =========================

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


def pasta_base():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = pasta_base()
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SONS_DIR = os.path.join(ASSETS_DIR, "sons")
os.makedirs(SONS_DIR, exist_ok=True)


def criar_som_simples(caminho, frequencia=440, duracao=0.15, volume=0.35):
    if os.path.exists(caminho):
        return

    taxa = 44100
    total_amostras = int(taxa * duracao)

    with wave.open(caminho, "w") as arquivo:
        arquivo.setnchannels(1)
        arquivo.setsampwidth(2)
        arquivo.setframerate(taxa)

        for i in range(total_amostras):
            t = i / taxa
            envelope = max(0, 1 - (i / total_amostras))
            onda = math.sin(2 * math.pi * frequencia * t)
            valor = int(32767 * volume * envelope * onda)
            arquivo.writeframes(struct.pack("<h", valor))


def criar_musica(caminho):
    if os.path.exists(caminho):
        return

    taxa = 44100
    notas = [392, 440, 523, 440, 392, 330, 349, 392]
    duracao_nota = 0.25

    with wave.open(caminho, "w") as arquivo:
        arquivo.setnchannels(1)
        arquivo.setsampwidth(2)
        arquivo.setframerate(taxa)

        for freq in notas:
            total = int(taxa * duracao_nota)
            for i in range(total):
                t = i / taxa
                onda = math.sin(2 * math.pi * freq * t)
                valor = int(32767 * 0.13 * 0.45 * onda)
                arquivo.writeframes(struct.pack("<h", valor))


def preparar_assets():
    criar_som_simples(os.path.join(SONS_DIR, "pulo.wav"), 620, 0.13)
    criar_som_simples(os.path.join(SONS_DIR, "cristal.wav"), 880, 0.16)
    criar_som_simples(os.path.join(SONS_DIR, "ataque.wav"), 250, 0.12)
    criar_som_simples(os.path.join(SONS_DIR, "dano.wav"), 160, 0.22)
    criar_som_simples(os.path.join(SONS_DIR, "vitoria.wav"), 1000, 0.35)
    criar_som_simples(os.path.join(SONS_DIR, "derrota.wav"), 90, 0.45)
    criar_musica(os.path.join(SONS_DIR, "musica.wav"))


preparar_assets()

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

TELA = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Aventura dos Cristais - Jogo 2D")
RELOGIO = pygame.time.Clock()

FONTE_PEQUENA = pygame.font.SysFont("arial", 20)
FONTE_MEDIA = pygame.font.SysFont("arial", 28, bold=True)
FONTE_GRANDE = pygame.font.SysFont("arial", 54, bold=True)

BRANCO = (245, 245, 245)
PRETO = (10, 10, 20)
AZUL_CEU = (110, 180, 240)
AZUL_ESCURO = (25, 35, 70)
VERDE = (50, 180, 90)
VERDE_ESCURO = (30, 100, 55)
ROXO = (120, 70, 180)
ROXO_ESCURO = (65, 40, 110)
AMARELO = (255, 215, 80)
LARANJA = (255, 140, 50)
VERMELHO = (220, 55, 55)
CINZA = (90, 90, 110)
MARROM = (110, 70, 40)
CIANO = (80, 235, 255)
ROSA = (255, 90, 170)
PELE = (255, 210, 210)
CABELO = (120, 65, 40)
SOMBRA = (35, 35, 50)
VERDE_CLARO = (120, 220, 120)
VERDE_SLIME = (90, 210, 110)
ROXO_CLARO = (170, 120, 220)

def carregar_som(nome):
    try:
        return pygame.mixer.Sound(os.path.join(SONS_DIR, nome))
    except pygame.error:
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
    som = SONS.get(nome)
    if som:
        som.play()


try:
    pygame.mixer.music.load(os.path.join(SONS_DIR, "musica.wav"))
    pygame.mixer.music.set_volume(0.25)
    pygame.mixer.music.play(-1)
except pygame.error:
    pass


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

    def atualizar(self, teclas, plataformas):
        self.vel_x = 0

        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            self.vel_x = -self.velocidade
            self.direcao = -1

        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            self.vel_x = self.velocidade
            self.direcao = 1

        if (teclas[pygame.K_SPACE] or teclas[pygame.K_w] or teclas[pygame.K_UP]) and self.no_chao:
            self.vel_y = self.forca_pulo
            self.no_chao = False
            tocar("pulo")

        if (teclas[pygame.K_LCTRL] or teclas[pygame.K_RCTRL]) and self.cooldown_ataque <= 0:
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
                self.ataque_rect = pygame.Rect(self.rect.right, self.rect.y + 16, 44, 24)
            else:
                self.ataque_rect = pygame.Rect(self.rect.left - 44, self.rect.y + 16, 44, 24)
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

        # sombra
        pygame.draw.ellipse(tela, (0, 0, 0, 60), (x + 8, y + 52, 24, 8))

        # cabelo
        pygame.draw.ellipse(tela, CABELO, (x + 7, y + 1, 24, 14))

        # cabeça
        pygame.draw.circle(tela, PELE, (x + 19, y + 13), 12)
        pygame.draw.circle(tela, PRETO, (x + 15, y + 11), 2)
        pygame.draw.circle(tela, PRETO, (x + 23, y + 11), 2)

        # sorriso
        pygame.draw.arc(tela, PRETO, (x + 14, y + 12, 10, 7), 0.2, 2.9, 1)

        # corpo
        pygame.draw.rect(tela, ROXO, (x + 8, y + 24, 22, 23), border_radius=8)
        pygame.draw.rect(tela, ROXO_CLARO, (x + 12, y + 27, 14, 8), border_radius=4)

        # braços
        pygame.draw.line(tela, PELE, (x + 8, y + 29), (x + 2, y + 38), 4)
        pygame.draw.line(tela, PELE, (x + 30, y + 29), (x + 36, y + 38), 4)

        # pernas
        pygame.draw.line(tela, AZUL_ESCURO, (x + 14, y + 47), (x + 12, y + 57), 4)
        pygame.draw.line(tela, AZUL_ESCURO, (x + 24, y + 47), (x + 26, y + 57), 4)

        # pés
        pygame.draw.ellipse(tela, SOMBRA, (x + 7, y + 55, 10, 6))
        pygame.draw.ellipse(tela, SOMBRA, (x + 22, y + 55, 10, 6))

        # contorno leve
        pygame.draw.rect(tela, SOMBRA, (x + 8, y + 24, 22, 23), 2, border_radius=8)

        # ataque
        if self.tempo_ataque > 0:
            ataque = self.ataque_rect.move(-camera_x, 0)
            pygame.draw.rect(tela, AMARELO, ataque, border_radius=8)
            pygame.draw.rect(tela, LARANJA, ataque, 2, border_radius=8)


class Inimigo:
    def __init__(self, x, y, tipo="slime", esquerda=None, direita=None):
        self.tipo = tipo
        self.rect = pygame.Rect(x, y, 42, 34) if tipo == "slime" else pygame.Rect(x, y, 46, 30)
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
            # sombra
            pygame.draw.ellipse(tela, (0, 0, 0, 60), (x + 6, y + 28, 28, 6))

            # corpo
            pygame.draw.ellipse(tela, VERDE_SLIME, (x, y + 5, 42, 28))
            pygame.draw.ellipse(tela, VERDE_CLARO, (x + 6, y + 8, 16, 8))
            pygame.draw.ellipse(tela, VERDE_ESCURO, (x + 4, y + 22, 34, 9))

            # olhos
            pygame.draw.circle(tela, PRETO, (x + 14, y + 16), 2)
            pygame.draw.circle(tela, PRETO, (x + 28, y + 16), 2)

            # sorriso
            pygame.draw.arc(tela, PRETO, (x + 14, y + 16, 14, 8), 0.2, 2.9, 1)

            # contorno
            pygame.draw.ellipse(tela, VERDE_ESCURO, (x, y + 5, 42, 28), 2)

        else:
            # morcego
            pygame.draw.ellipse(tela, SOMBRA, (x + 10, y + 22, 24, 6))

            # asas
            pygame.draw.polygon(tela, ROXO, [(x + 16, y + 16), (x - 6, y + 2), (x + 5, y + 26)])
            pygame.draw.polygon(tela, ROXO, [(x + 30, y + 16), (x + 52, y + 2), (x + 41, y + 26)])

            # corpo
            pygame.draw.ellipse(tela, ROXO_ESCURO, (x + 12, y + 10, 22, 16))

            # orelhas
            pygame.draw.polygon(tela, ROXO_ESCURO, [(x + 15, y + 12), (x + 18, y + 4), (x + 21, y + 12)])
            pygame.draw.polygon(tela, ROXO_ESCURO, [(x + 25, y + 12), (x + 28, y + 4), (x + 31, y + 12)])

            # olhos
            pygame.draw.circle(tela, AMARELO, (x + 20, y + 17), 2)
            pygame.draw.circle(tela, AMARELO, (x + 27, y + 17), 2)

            # dentinhos
            pygame.draw.polygon(tela, BRANCO, [(x + 21, y + 22), (x + 23, y + 26), (x + 25, y + 22)])
            pygame.draw.polygon(tela, BRANCO, [(x + 25, y + 22), (x + 27, y + 26), (x + 29, y + 22)])


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
            [(x + 14, y + 3), (x + 22, y + 16), (x + 14, y + 28), (x + 7, y + 16)],
            2,
        )

        # brilho
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
        pygame.draw.ellipse(tela, ROXO if aberto else AZUL_ESCURO, (x + 16, y + 12, 40, 68))

        if aberto:
            pygame.draw.circle(tela, BRANCO, (x + 36, y + 46), 6)


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

    for cx, cy in [(170, 90), (480, 70), (760, 130), (1110, 85), (1500, 120), (1980, 80)]:
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
        pygame.draw.polygon(TELA, (65, 120, 170), [(sx, 470), (sx + 190, 210), (sx + 380, 470)])
        pygame.draw.polygon(TELA, (80, 145, 185), [(sx + 80, 470), (sx + 240, 260), (sx + 430, 470)])


def desenhar_plataformas(plataformas, camera_x):
    for p in plataformas:
        r = pygame.Rect(p.x - camera_x, p.y, p.w, p.h)
        pygame.draw.rect(TELA, MARROM, r)
        topo = pygame.Rect(r.x, r.y, r.w, 12)
        pygame.draw.rect(TELA, VERDE, topo)
        pygame.draw.rect(TELA, VERDE_ESCURO, r, 2)


def desenhar_hud(jogador, cristais_coletados):
    pygame.draw.rect(TELA, AZUL_ESCURO, (0, 0, LARGURA_TELA, 58))
    escrever(f"Vidas: {jogador.vidas}", FONTE_MEDIA, BRANCO, 20, 14)
    escrever(f"Cristais: {cristais_coletados}/5", FONTE_MEDIA, BRANCO, 170, 14)
    escrever("P - Pausar | R - Reiniciar | ESC - Menu", FONTE_PEQUENA, BRANCO, 610, 19)


def desenhar_menu():
    desenhar_fundo(0)

    pygame.draw.rect(TELA, AZUL_ESCURO, (120, 35, 720, 470), border_radius=22)
    pygame.draw.rect(TELA, ROXO, (120, 35, 720, 470), 4, border_radius=22)

    escrever("AVENTURA DOS CRISTAIS", FONTE_GRANDE, AMARELO, LARGURA_TELA // 2, 90, True)
    escrever("Jogo 2D - demo jogável", FONTE_MEDIA, BRANCO, LARGURA_TELA // 2, 135, True)


    comandos = [
        "A / ←  - Andar para esquerda",
        "D / →  - Andar para direita",
        "ESPAÇO / W / ↑  - Pular",
        "CTRL  - Atacar",
        "P  - Pausar",
        "R  - Reiniciar",
        "ESC  - Voltar ao menu / sair",
    ]

    escrever("COMANDOS:", FONTE_MEDIA, CIANO, 250, 175)

    y = 212
    for c in comandos:
        escrever(c, FONTE_PEQUENA, BRANCO, 250, y)
        y += 27

    escrever("Objetivo: pegue 5 cristais e entre no portal final.", FONTE_PEQUENA, AMARELO, LARGURA_TELA // 2, 430, True)
    escrever("APERTE ENTER PARA COMEÇAR", FONTE_MEDIA, BRANCO, LARGURA_TELA // 2, 465, True)


def desenhar_tela_final(titulo, subtitulo, cor):
    desenhar_fundo(0)

    pygame.draw.rect(TELA, AZUL_ESCURO, (170, 115, 620, 300), border_radius=22)
    pygame.draw.rect(TELA, cor, (170, 115, 620, 300), 4, border_radius=22)

    escrever(titulo, FONTE_GRANDE, cor, LARGURA_TELA // 2, 190, True)
    escrever(subtitulo, FONTE_MEDIA, BRANCO, LARGURA_TELA // 2, 250, True)
    escrever("ENTER - Jogar de novo", FONTE_MEDIA, AMARELO, LARGURA_TELA // 2, 325, True)
    escrever("ESC - Voltar ao menu", FONTE_MEDIA, BRANCO, LARGURA_TELA // 2, 365, True)


def desenhar_pause():
    overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 155))
    TELA.blit(overlay, (0, 0))

    escrever("PAUSADO", FONTE_GRANDE, AMARELO, LARGURA_TELA // 2, 230, True)
    escrever("Aperte P para voltar", FONTE_MEDIA, BRANCO, LARGURA_TELA // 2, 290, True)


def main():
    estado = MENU

    jogador, plataformas, cristais, inimigos, portal = criar_fase()
    cristais_coletados = 0
    som_final_tocado = False

    rodando = True

    while rodando:
        RELOGIO.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            if evento.type == pygame.KEYDOWN:
                if estado == MENU:
                    if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        jogador, plataformas, cristais, inimigos, portal = criar_fase()
                        cristais_coletados = 0
                        som_final_tocado = False
                        estado = JOGANDO

                    elif evento.key == pygame.K_ESCAPE:
                        rodando = False

                elif estado == JOGANDO:
                    if evento.key == pygame.K_p:
                        estado = PAUSADO

                    elif evento.key == pygame.K_r:
                        jogador, plataformas, cristais, inimigos, portal = criar_fase()
                        cristais_coletados = 0
                        som_final_tocado = False

                    elif evento.key == pygame.K_ESCAPE:
                        estado = MENU

                elif estado == PAUSADO:
                    if evento.key == pygame.K_p:
                        estado = JOGANDO

                    elif evento.key == pygame.K_ESCAPE:
                        estado = MENU

                elif estado in (VITORIA, DERROTA):
                    if evento.key == pygame.K_RETURN:
                        jogador, plataformas, cristais, inimigos, portal = criar_fase()
                        cristais_coletados = 0
                        som_final_tocado = False
                        estado = JOGANDO

                    elif evento.key == pygame.K_ESCAPE:
                        estado = MENU

        if estado == JOGANDO:
            teclas = pygame.key.get_pressed()
            jogador.atualizar(teclas, plataformas)

            for inimigo in inimigos:
                inimigo.atualizar()

                if inimigo.vivo and jogador.ataque_rect.colliderect(inimigo.rect):
                    inimigo.vivo = False
                    tocar("cristal")

                if inimigo.vivo and jogador.rect.colliderect(inimigo.rect):
                    jogador.tomar_dano()

            for cristal in cristais:
                cristal.atualizar()

                if not cristal.coletado and jogador.rect.colliderect(cristal.rect):
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

                if not som_final_tocado:
                    tocar("derrota")
                    som_final_tocado = True

            if cristais_coletados >= 5 and jogador.rect.colliderect(portal.rect):
                estado = VITORIA

                if not som_final_tocado:
                    tocar("vitoria")
                    som_final_tocado = True

        camera_x = jogador.rect.centerx - LARGURA_TELA // 2
        camera_x = max(0, min(camera_x, LARGURA_FASE - LARGURA_TELA))

        if estado == MENU:
            desenhar_menu()

        elif estado in (JOGANDO, PAUSADO):
            desenhar_fundo(camera_x)
            desenhar_plataformas(plataformas, camera_x)

            for cristal in cristais:
                cristal.desenhar(TELA, camera_x)

            for inimigo in inimigos:
                inimigo.desenhar(TELA, camera_x)

            portal.desenhar(TELA, camera_x, cristais_coletados >= 5)
            jogador.desenhar(TELA, camera_x)
            desenhar_hud(jogador, cristais_coletados)

            if estado == PAUSADO:
                desenhar_pause()

        elif estado == VITORIA:
            desenhar_tela_final("VOCÊ VENCEU!", "Pegou os cristais e abriu o portal.", CIANO)

        elif estado == DERROTA:
            desenhar_tela_final("GAME OVER", "Você perdeu todas as vidas.", VERMELHO)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()