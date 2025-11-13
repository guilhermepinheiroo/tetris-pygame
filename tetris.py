import pygame, random, sys, os

largura_bloco = 30
colunas = 10
linhas = 20
largura_tela = largura_bloco * colunas
painel_lateral = 150
altura_tela = largura_bloco * linhas
tamanho_tela = (largura_tela + painel_lateral, altura_tela)

preto = (0, 0, 0)
cinza = (40, 40, 40)
branco = (255, 255, 255)
cinza_claro = (90, 90, 90)
cores = [
    (0, 255, 255),
    (0, 0, 255),
    (255, 165, 0),
    (255, 255, 0),
    (0, 255, 0),
    (128, 0, 128),
    (255, 0, 0)
]

formas = [
    [[[1, 1, 1, 1]], [[1], [1], [1], [1]]],
    [[[2, 0, 0], [2, 2, 2]], [[2, 2], [2, 0], [2, 0]], [[2, 2, 2], [0, 0, 2]], [[0, 2], [0, 2], [2, 2]]],
    [[[0, 0, 3], [3, 3, 3]], [[3, 0], [3, 0], [3, 3]], [[3, 3, 3], [3, 0, 0]], [[3, 3], [0, 3], [0, 3]]],
    [[[4, 4], [4, 4]]],
    [[[0, 5, 5], [5, 5, 0]], [[5, 0], [5, 5], [0, 5]]],
    [[[0, 6, 0], [6, 6, 6]], [[6, 0], [6, 6], [6, 0]], [[6, 6, 6], [0, 6, 0]], [[0, 6], [6, 6], [0, 6]]],
    [[[7, 7, 0], [0, 7, 7]], [[0, 7], [7, 7], [7, 0]]]
]

def carregar_recorde():
    if not os.path.exists("recorde.txt"):
        with open("recorde.txt", "w") as f:
            f.write("0")
        return 0
    with open("recorde.txt", "r") as f:
        try:
            return int(f.read().strip())
        except ValueError:
            return 0

def salva_recorde(valor):
    with open("recorde.txt", "w") as f:
        f.write(str(valor))

class Peca:
    def __init__(self, x, y, forma):
        self.x = x
        self.y = y
        self.forma = forma
        self.rotacao = 0

    def imagem(self):
        return self.forma[self.rotacao % len(self.forma)]

    def coordenadas(self):
        pos = []
        matriz = self.imagem()
        for i, linha in enumerate(matriz):
            for j, valor in enumerate(linha):
                if valor != 0:
                    pos.append((self.x + j, self.y + i))
        return pos

def criar_grade(fixa):
    grade = [[0 for _ in range(colunas)] for _ in range(linhas)]
    for (x, y), valor in fixa.items():
        if 0 <= y < linhas and 0 <= x < colunas:
            grade[y][x] = valor
    return grade

def forma_valida(peca, grade):
    for x, y in peca.coordenadas():
        if x < 0 or x >= colunas or y >= linhas:
            return False
        if y >= 0 and grade[y][x] != 0:
            return False
    return True

def remover_linhas(grade, fixa):
    linhas_completas = [i for i, linha in enumerate(grade) if 0 not in linha]
    if not linhas_completas:
        return fixa, 0
    for i in linhas_completas:
        for x in range(colunas):
            fixa.pop((x, i), None)
    nova_fixa = {}
    for (x, y), valor in fixa.items():
        desloc = sum(1 for linha in linhas_completas if y < linha)
        nova_fixa[(x, y + desloc)] = valor
    return nova_fixa, len(linhas_completas)

def desenhar_grade(tela, grade):
    for y in range(linhas):
        for x in range(colunas):
            cor = cinza if grade[y][x] == 0 else cores[grade[y][x] - 1]
            pygame.draw.rect(tela, cor, (x * largura_bloco, y * largura_bloco, largura_bloco, largura_bloco), 0)
            pygame.draw.rect(tela, preto, (x * largura_bloco, y * largura_bloco, largura_bloco, largura_bloco), 1)

def desenhar_painel_lateral(tela, pontos, recorde):
    fonte_titulo = pygame.font.SysFont('Arial', 22, bold=True)
    fonte_texto = pygame.font.SysFont('Arial', 16)
    pygame.draw.rect(tela, cinza_claro, (largura_tela, 0, painel_lateral, altura_tela))
    tela.blit(fonte_titulo.render("TETRIS", True, branco), (largura_tela + 35, 20))
    tela.blit(fonte_texto.render(f"Pontos: {pontos}", True, branco), (largura_tela + 20, 70))
    tela.blit(fonte_texto.render(f"Recorde: {recorde}", True, (255, 215, 0)), (largura_tela + 20, 100))
    tela.blit(fonte_titulo.render("Controles:", True, branco), (largura_tela + 20, 150))
    controles = ["← / → : mover", "↓ : acelerar", "R : girar", "ESC : sair"]
    y = 180
    for c in controles:
        tela.blit(fonte_texto.render(c, True, branco), (largura_tela + 20, y))
        y += 25

def game_over(tela, pontos, recorde):
    if pontos > recorde:
        recorde = pontos
        salva_recorde(recorde)
    fonte_titulo = pygame.font.SysFont('arial', 38, bold=True)
    fonte_texto = pygame.font.SysFont('arial', 24)
    tela.fill(preto)
    linhas = [
        ("FIM DE JOGO!", branco, fonte_titulo),
        (f"Sua pontuação: {pontos}", branco, fonte_texto),
        (f"Recorde: {recorde}", (255, 215, 0), fonte_texto),
        ("ENTER = jogar novamente", branco, fonte_texto),
        ("ESC = sair", branco, fonte_texto)
    ]
    y = 200
    for texto, cor, fonte in linhas:
        render = fonte.render(texto, True, cor)
        x = (largura_tela + painel_lateral) / 2 - render.get_width() / 2
        tela.blit(render, (x, y))
        y += 50
    pygame.display.update()
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    main()
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def main():
    pygame.init()
    tela = pygame.display.set_mode(tamanho_tela)
    pygame.display.set_caption("Tetris com Matrizes 🧱")
    relogio = pygame.time.Clock()
    fixa = {}
    peca_atual = Peca(3, 0, random.choice(formas))
    proxima_peca = Peca(3, 0, random.choice(formas))
    tempo_queda = 0
    velocidade_queda = 0.050
    pontos = 0
    recorde = carregar_recorde()
    while True:
        grade = criar_grade(fixa)
        tempo_queda += relogio.get_rawtime()
        relogio.tick(30)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if evento.key == pygame.K_LEFT:
                    peca_atual.x -= 1
                    if not forma_valida(peca_atual, grade):
                        peca_atual.x += 1
                elif evento.key == pygame.K_RIGHT:
                    peca_atual.x += 1
                    if not forma_valida(peca_atual, grade):
                        peca_atual.x -= 1
                elif evento.key == pygame.K_DOWN:
                    peca_atual.y += 1
                    if not forma_valida(peca_atual, grade):
                        peca_atual.y -= 1
                elif evento.key == pygame.K_r:
                    rot_anterior = peca_atual.rotacao
                    peca_atual.rotacao = (peca_atual.rotacao + 1) % len(peca_atual.forma)
                    if not forma_valida(peca_atual, grade):
                        peca_atual.rotacao = rot_anterior
        if tempo_queda / 1000 > velocidade_queda:
            peca_atual.y += 1
            if not forma_valida(peca_atual, grade):
                peca_atual.y -= 1
                for x, y in peca_atual.coordenadas():
                    fixa[(x, y)] = formas.index(peca_atual.forma) + 1
                fixa, linhas = remover_linhas(criar_grade(fixa), fixa)
                pontos += linhas * 100
                peca_atual = proxima_peca
                proxima_peca = Peca(3, 0, random.choice(formas))
                if not forma_valida(peca_atual, criar_grade(fixa)):
                    game_over(tela, pontos, recorde)
                    return
            tempo_queda = 0
        for x, y in peca_atual.coordenadas():
            if y >= 0:
                grade[y][x] = formas.index(peca_atual.forma) + 1
        tela.fill(preto)
        desenhar_grade(tela, grade)
        desenhar_painel_lateral(tela, pontos, recorde)
        pygame.display.update()

if __name__ == "__main__":
    main()
