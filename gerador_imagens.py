import os
import random
from PIL import Image, ImageDraw

PALETAS = [
    [(15, 23, 42), (56, 189, 248), (129, 140, 248)],
    [(24, 24, 27), (244, 63, 94), (251, 146, 60)],
    [(6, 78, 59), (52, 211, 153), (167, 243, 208)],
    [(49, 16, 66), (217, 70, 239), (240, 171, 252)],
    [(30, 27, 75), (99, 102, 241), (199, 210, 254)],
    [(69, 10, 10), (239, 68, 68), (254, 202, 202)],
    [(23, 37, 84), (59, 130, 246), (147, 197, 253)],
    [(67, 20, 7), (249, 115, 22), (254, 215, 170)],
    [(20, 83, 45), (34, 197, 94), (187, 247, 208)],
    [(17, 24, 39), (16, 185, 129), (245, 158, 11)],
    [(39, 39, 42), (236, 72, 153), (139, 92, 246)],
    [(12, 74, 110), (14, 165, 233), (224, 242, 254)],
    [(76, 5, 25), (225, 29, 72), (255, 228, 230)],
    [(54, 83, 20), (132, 204, 22), (236, 252, 203)],
    [(46, 16, 101), (168, 85, 247), (243, 232, 255)],
    [(9, 9, 11), (250, 204, 21), (254, 240, 138)]
]

def criar_imagem_neo(numero_id=None, tema=""):
    if numero_id is None:
        numero_id = random.randint(1, 256)
    numero_id = max(1, min(256, int(numero_id)))
    
    indice_paleta = (numero_id - 1) // 16
    estilo = (numero_id - 1) % 16
    cor_fundo, cor_primaria, cor_secundaria = PALETAS[indice_paleta]
    
    random.seed(numero_id + len(tema))
    img = Image.new("RGB", (512, 512), cor_fundo)
    desenho = ImageDraw.Draw(img)
    
    for i in range(12 + estilo * 2):
        x1 = random.randint(20, 420)
        y1 = random.randint(20, 420)
        tam = random.randint(30, 140)
        cor = cor_primaria if i % 2 == 0 else cor_secundaria
        
        if estilo % 4 == 0:
            desenho.ellipse([x1, y1, x1 + tam, y1 + tam], outline=cor, width=4)
        elif estilo % 4 == 1:
            desenho.rectangle([x1, y1, x1 + tam, y1 + tam], fill=cor)
        elif estilo % 4 == 2:
            desenho.polygon([(x1, y1), (x1 + tam, y1 + tam // 2), (x1, y1 + tam)], fill=cor)
        else:
            desenho.line([x1, y1, 512 - x1, 512 - y1], fill=cor, width=5)

    pasta_imagens = "imagens_neo"
    if not os.path.exists(pasta_imagens):
        os.makedirs(pasta_imagens)
        
    nome_arquivo = f"{pasta_imagens}/arte_neo_{numero_id:03d}.png"
    img.save(nome_arquivo)
    return nome_arquivo, numero_id
