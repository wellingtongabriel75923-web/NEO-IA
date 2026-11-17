import json
import os
import re
import ssl
import math
import random
import string
import webbrowser
import urllib.parse
import urllib.request
from datetime import datetime
from difflib import get_close_matches

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle

try:
    from gerador_imagens import criar_imagem_neo
    estudio_ativo = True
except Exception:
    estudio_ativo = False

# Destrava certificados HTTPS antigos no Android para a Wikipédia funcionar
ssl._create_default_https_context = ssl._create_unverified_context

try:
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
    Locale = autoclass('java.util.Locale')
    JavaString = autoclass('java.lang.String')
    tts = TextToSpeech(PythonActivity.mActivity, None)
    voz_ativa = True
except Exception as erro:
    voz_ativa = False
    motivo_erro = erro

# Tema Escuro Moderno (Estilo Material Design 2018)
Window.clearcolor = (0.09, 0.11, 0.15, 1)

NOME_IA = "NEO"
ARQUIVO_MEMORIA = "memoria_neo.json"
ARQUIVO_TAREFAS = "tarefas_neo.json"

ABREVIACOES = {
    "vc": "você", "vcs": "vocês", "oq": "o que", "pq": "porque",
    "blz": "beleza", "tb": "também", "tbm": "também", "hj": "hoje",
    "q": "que", "td": "tudo", "cmg": "comigo", "ctg": "contigo",
    "mto": "muito", "mt": "muito", "pfv": "por favor", "obg": "obrigado",
    "vlw": "valeu", "flw": "falou", "kd": "cadê", "eh": "é",
    "ta": "está", "tá": "está", "to": "estou", "tô": "estou",
    "nao": "não", "voce": "você", "esta": "está", "n": "não",
    "s": "sim", "mds": "meu deus", "slk": "você é louco"
}

CEREBRO_EM1_E_PS2 = {
    # === ENSINO MÉDIO 1º ANO (11 MATÉRIAS) ===
    "o que é função afim": "É uma função polinomial do 1º grau no formato f(x) = ax + b, cujo gráfico é sempre uma reta.",
    "o que é função quadrática": "É uma função do 2º grau f(x) = ax² + bx + c, cujo gráfico forma uma parábola com concavidade para cima ou para baixo.",
    "o que é cinemática mru": "Movimento Retilíneo Uniforme: movimento em linha reta com velocidade constante e aceleração igual a zero.",
    "o que é mruv": "Movimento Retilíneo Uniformemente Variado: movimento onde a velocidade muda de forma constante porque existe uma aceleração fixa.",
    "o que é ligação iônica": "É a ligação química que ocorre pela transferência definitiva de elétrons entre um metal e um ametal, formando íons.",
    "o que é ligação covalente": "É a ligação química baseada no compartilhamento de pares de elétrons entre ametais ou hidrogênio.",
    "o que é citologia": "É o ramo da Biologia que estuda a estrutura, funções e organelas das células procariontes e eucariontes.",
    "o que são mitocôndrias": "São organelas celulares responsáveis pela respiração celular e produção de energia (ATP) para a célula.",
    "o que foi o trovadorismo": "Foi a primeira escola literária da língua portuguesa na Idade Média, marcada pelas cantigas de amor, amigo, escárnio e maldizer.",
    "o que foi o quinhentismo": "Foi o conjunto de textos escritos no Brasil no século 16 durante a chegada dos portugueses, como a Carta de Pero Vaz de Caminha.",
    "o que é geopolítica": "É o estudo das relações de poder, território, economia e fronteiras entre os países no cenário mundial.",
    "o que é simple present em inglês": "É o tempo verbal usado em inglês para falar de rotinas, hábitos e verdades gerais, usando 'do' ou 'does' nas perguntas.",
    "o que é verb to be": "Significa 'ser' ou 'estar' em inglês, conjugado no presente como am, is e are.",
    "o que é arte renascentista": "Movimento artístico que usou perspectiva, proporção matemática e valorização do ser humano, com mestres como Michelangelo e Rafael.",
    "o que é ética e moral na filosofia": "A moral são os costumes e regras de uma sociedade; a ética é a reflexão filosófica sobre o que é certo ou errado.",
    "o que é computação em nuvem e big data": "Nuvem é o processamento remoto em servidores; Big Data é a análise de volumes gigantescos de dados para treinar inteligências artificiais.",

    # === CLÁSSICOS DO PLAYSTATION 2 ===
    "gta san andreas ps2": "Lançado em 2004 pela Rockstar, conta a história de Carl 'CJ' Johnson voltando para Los Santos. É o jogo mais vendido da história do PlayStation 2!",
    "god of war 2 ps2": "Obra-prima de ação de 2007 onde Kratos enfrenta os deuses do Olimpo e as Irmãs do Destino usando as Lâminas de Atena.",
    "shadow of the colossus ps2": "Clássico épico de 2005 onde Wander precisa derrotar 16 colossos gigantes para salvar Mono.",
    "resident evil 4 ps2": "Revolucionou os jogos de ação e terror em 2005 colocando Leon S. Kennedy na missão de resgatar Ashley na Espanha.",
    "bully ps2": "Jogo da Rockstar de 2006 onde você controla Jimmy Hopkins tentando sobreviver e dominar a escola interna Bullworth Academy.",
    "need for speed underground 2 ps2": "Referência absoluta em corridas de rua e tunagem de carros com mundo aberto na cidade de Bayview.",
    "dragon ball z budokai tenkaichi 3 ps2": "Considerado por muitos o melhor jogo de anime do PS2, com mais de 160 personagens jogáveis e batalhas em 3D.",
    "naruto shippuden ultimate ninja 5 ps2": "Clássico de luta com modo história cobrindo o resgate de Gaara e o reencontro com Sasuke.",
    "black ps2": "Jogo de tiro em primeira pessoa famoso pelos gráficos absurdos para o PS2 e cenários altamente destrutíveis.",
    "bomba patch ps2": "Modificação brasileira lendária de Winning Eleven/PES que manteve o PlayStation 2 vivo no Brasil com elencos 100% atualizados."
}
class CartaoChat(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.14, 0.17, 0.23, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[18])

        self.bind(pos=self.atualizar_rect, size=self.atualizar_rect)

    def atualizar_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class NeoApp(App):
    def build(self):
        self.memoria = self.carregar_json(ARQUIVO_MEMORIA, CEREBRO_EM1_E_PS2)
        self.tarefas = self.carregar_json(ARQUIVO_TAREFAS, [])
        self.aguardando_ensino = False
        self.ultima_pergunta = ""
        self.numero_secreto = None

        layout = BoxLayout(orientation='vertical', padding=18, spacing=14)

        # Cabeçalho Moderno Estilo 2018
        cabecalho = Label(
            text=f"[b]{NOME_IA} 8.0[/b]  |  Ensino Médio • 256 Artes • 1.200 PS2",
            markup=True,
            font_size='16sp',
            color=(0.35, 0.78, 0.98, 1),
            size_hint=(1, 0.08)
        )
        layout.add_widget(cabecalho)

        # Cartão Principal de Resposta
        self.tela_chat = CartaoChat(
            text="Inicializando interface moderna e cérebro...",
            font_size='18sp',
            color=(0.95, 0.96, 0.98, 1),
            halign='center',
            valign='middle',
            padding=(20, 20),
            size_hint=(1, 0.58)
        )
        self.tela_chat.bind(size=self.tela_chat.setter('text_size'))
        layout.add_widget(self.tela_chat)

        # Campo de Digitação
        self.campo_texto = TextInput(
            hint_text="Digite um comando, jogo de PS2, conta ou peça uma arte...",
            multiline=False,
            font_size='17sp',
            background_color=(0.16, 0.19, 0.25, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.35, 0.78, 0.98, 1),
            padding=(15, 15),
            size_hint=(1, 0.16)
        )
        layout.add_widget(self.campo_texto)

        # Botão Arredondado Estilo Material 2018
        botao_enviar = Button(
            text="ENVIAR COMANDO",
            font_size='17sp',
            bold=True,
            background_normal='',
            background_color=(0.13, 0.59, 0.95, 1),
            size_hint=(1, 0.16)
        )
        botao_enviar.bind(on_press=self.processar_mensagem)
        layout.add_widget(botao_enviar)

        Clock.schedule_once(self.iniciar_voz_portugues, 1.5)
        return layout

    def iniciar_voz_portugues(self, dt):
        if voz_ativa:
            try:
                tts.setLanguage(Locale("pt", "BR"))
            except Exception:
                pass
        self.falar("NEO 8.0 no ar com visual moderno, 20 novas habilidades, estúdio de 256 imagens e enciclopédia de PlayStation 2!")

    def falar(self, texto):
        self.tela_chat.text = f"{NOME_IA}: {texto}"
        if voz_ativa:
            try:
                texto_java = JavaString(str(texto))
                tts.speak(texto_java, TextToSpeech.QUEUE_ADD, None)
            except Exception:
                pass

    def carregar_json(self, caminho, padrao):
        dados = dict(padrao) if isinstance(padrao, dict) else list(padrao)
        if os.path.exists(caminho):
            try:
                with open(caminho, "r", encoding="utf-8") as arq:
                    salvos = json.load(arq)
                    if isinstance(dados, dict):
                        dados.update(salvos)
                    else:
                        dados = salvos
            except Exception:
                pass
        self.salvar_json(caminho, dados)
        return dados

    def salvar_json(self, caminho, dados):
        try:
            with open(caminho, "w", encoding="utf-8") as arq:
                json.dump(dados, arq, ensure_ascii=False, indent=4)
        except Exception:
            pass
    def traduzir_girias(self, texto):
        palavras = texto.split()
        traduzidas = []
        for p in palavras:
            limpa = re.sub(r'[^\w\s]', '', p)
            traduzidas.append(ABREVIACOES.get(limpa, p))
        return " ".join(traduzidas)

    def buscar_wikipedia_ou_ps2(self, pergunta, modo_ps2=False):
        termo = re.sub(r'^(o que é|quem foi|quem é|fale sobre|explique|jogo|ps2)\s+', '', pergunta).strip(" ?.!").strip()
        if len(termo) < 2:
            return None
        busca = f"{termo} jogo PlayStation 2" if modo_ps2 else termo
        try:
            url_busca = f"https://wikipedia.org{urllib.parse.quote(busca)}&format=json&utf8=1"
            req = urllib.request.Request(url_busca, headers={'User-Agent': 'NEO-IA-Android/8.0'})
            with urllib.request.urlopen(req, timeout=6) as resp:
                dados = json.loads(resp.read().decode('utf-8'))
                resultados = dados.get("query", {}).get("search", [])
                if not resultados:
                    return None
                titulo = next(iter(resultados))["title"]

            url_resumo = f"https://wikipedia.org{urllib.parse.quote(titulo)}"
            req2 = urllib.request.Request(url_resumo, headers={'User-Agent': 'NEO-IA-Android/8.0'})
            with urllib.request.urlopen(req2, timeout=6) as resp2:
                resumo = json.loads(resp2.read().decode('utf-8')).get("extract", "")
                if resumo:
                    frases = resumo.split(". ")
                    curto = ". ".join(frases[:2]).strip()
                    return curto if curto.endswith(".") else curto + "."
        except Exception:
            return None
        return None
    def executar_20_habilidades(self, entrada):
        if any(p in entrada for p in ["criar imagem", "gerar imagem", "desenhar", "criar arte"]):
            if not estudio_ativo:
                return "O módulo gerador_imagens.py não foi encontrado na pasta."
            num = re.search(r'(\d+)', entrada)
            id_img = int(num.group(1)) if num else None
            arquivo, num_gerado = criar_imagem_neo(id_img, entrada)
            return f"Imagem número {num_gerado} de 256 criada e salva com sucesso em {arquivo}!"

        if "bhaskara" in entrada or "x²" in entrada or "x2" in entrada:
            nums = re.findall(r'-?\d+\.?\d*', entrada.replace("x²", "").replace("x2", ""))
            if len(nums) >= 3:
                a, b, c = map(float, nums[:3])
                delta = b**2 - 4*a*c
                if delta < 0:
                    return f"Delta deu {delta}. Essa equação não possui raízes reais."
                x1 = (-b + math.sqrt(delta)) / (2*a)
                x2 = (-b - math.sqrt(delta)) / (2*a)
                return f"Delta é {delta}. As raízes são x1 = {round(x1, 2)} e x2 = {round(x2, 2)}."

        temp = re.search(r'(\d+\.?\d*)\s*(?:graus\s*)?(celsius|fahrenheit)', entrada)
        if temp:
            val, escala = float(temp.group(1)), temp.group(2)
            if escala == "celsius":
                return f"{val} graus Celsius equivalem a {round((val * 9/5) + 32, 1)} graus Fahrenheit."
            return f"{val} graus Fahrenheit equivalem a {round((val - 32) * 5/9, 1)} graus Celsius."

        if "gerar senha" in entrada or "criar senha" in entrada:
            chars = string.ascii_letters + string.digits + "!@#$%"
            senha = "".join(random.choice(chars) for _ in range(10))
            return f"Senha segura gerada: {senha}"

        if "cara ou coroa" in entrada or "jogar moeda" in entrada:
            return f"Joguei a moeda para o alto e deu: {random.choice(['Cara', 'Coroa'])}!"

        if "rolar dado" in entrada or "jogar dado" in entrada or "d20" in entrada:
            lados = 20 if "d20" in entrada else 6
            return f"Rolei um dado de {lados} lados e caiu no número {random.randint(1, lados)}!"

        for jogada in ["pedra", "papel", "tesoura"]:
            if entrada == jogada or f"jogo {jogada}" in entrada:
                neo_j = random.choice(["pedra", "papel", "tesoura"])
                return f"Você escolheu {jogada} e eu joguei {neo_j}!"

        if "adivinhar número" in entrada or "jogo de adivinhação" in entrada:
            self.numero_secreto = random.randint(1, 50)
            return "Pensei em um número entre 1 e 50! Digite 'chute' seguido do número para tentar acertar."
        if entrada.startswith("chute ") and self.numero_secreto:
            palpite = int(re.search(r'\d+', entrada).group())
            if palpite == self.numero_secreto:
                self.numero_secreto = None
                return f"Acertou na mosca! O número secreto era {palpite}!"
            return "É maior que isso!" if palpite < self.numero_secreto else "É menor que isso!"

        if entrada.startswith("contar palavras "):
            frase = entrada.replace("contar palavras ", "")
            return f"Essa frase tem {len(frase.split())} palavras e {len(frase)} caracteres."

        dicionario_en = {"hello": "olá", "world": "mundo", "game": "jogo", "science": "ciência", "power": "poder", "brain": "cérebro"}
        if entrada.startswith("traduzir "):
            p = entrada.replace("traduzir ", "").strip()
            return f"Tradução de '{p}': {dicionario_en.get(p, 'palavra ainda não cadastrada no dicionário offline')}."

        if "curiosidade" in entrada:
            curiosidades = [
                "O PlayStation 2 é o console mais vendido da história, com mais de 155 milhões de unidades!",
                "Um raio é cinco vezes mais quente que a superfície do Sol.",
                "O cérebro humano gera energia suficiente para acender uma lâmpada pequena."
            ]
            return random.choice(curiosidades)

        if "piada" in entrada or "me faça rir" in entrada:
            piadas = [
                "O que o zero disse para o oito? Belo cinto!",
                "Por que o livro de matemática se suicidou? Porque tinha muitos problemas!",
                "Qual é o cúmulo da velocidade? Trancar a gaveta e jogar a chave lá dentro!"
            ]
            return random.choice(piadas)

        if "motivação" in entrada or "desanimado" in entrada:
            return "Lembre-se: você criou uma inteligência artificial do zero pelo celular aos 14 anos. Nada para quem tem persistência!"

        if entrada.startswith("anotar "):
            item = entrada.replace("anotar ", "").strip()
            self.tarefas.append(item)
            self.salvar_json(ARQUIVO_TAREFAS, self.tarefas)
            return f"Anotei '{item}' na sua lista de tarefas!"

        if "minhas tarefas" in entrada or "ver notas" in entrada:
            if not self.tarefas:
                return "Sua lista de tarefas está vazia."
            return "Suas tarefas salvas: " + ", ".join(self.tarefas)

        if "limpar tarefas" in entrada:
            self.tarefas = []
            self.salvar_json(ARQUIVO_TAREFAS, self.tarefas)
            return "Lista de tarefas limpa com sucesso!"

        imc = re.search(r'imc\s+(\d+\.?\d*)\s+(\d+\.?\d*)', entrada)
        if imc:
            peso, altura = float(imc.group(1)), float(imc.group(2))
            if altura > 3:
                altura = altura / 100
            return f"Seu IMC calculado é {round(peso / (altura ** 2), 1)}."

        vel = re.search(r'velocidade\s+(\d+\.?\d*)\s+(\d+\.?\d*)', entrada)
        if vel:
            dist, tempo = float(vel.group(1)), float(vel.group(2))
            return f"A velocidade média é de {round(dist / tempo, 2)} km/h (ou m/s)."

        if "status do sistema" in entrada or "diagnóstico" in entrada:
            return f"NEO 8.0 operando perfeitamente! Memória com {len(self.memoria)} conhecimentos ativos e estúdio de 256 artes pronto."

        if "youtube" in entrada:
            termo = re.sub(r'.*(pesquisar|buscar|no)\s*youtube\s*', '', entrada).strip()
            if termo:
                webbrowser.open(f"https://youtube.com{urllib.parse.quote(termo)}")
                return f"Abrindo o YouTube para buscar {termo}!"
        if "pesquisar no google" in entrada or "buscar no google" in entrada:
            termo = re.sub(r'.*(pesquisar|buscar)\s*no\s*google\s*', '', entrada).strip()
            if termo:
                webbrowser.open(f"https://google.com{urllib.parse.quote(termo)}")
                return f"Pesquisando no Google sobre {termo}!"

        return None
    def processar_mensagem(self, instance):
        original = self.campo_texto.text.strip()
        if not original:
            return
        self.campo_texto.text = ""

        if self.aguardando_ensino:
            self.memoria[self.ultima_pergunta] = original
            self.salvar_json(ARQUIVO_MEMORIA, self.memoria)
            self.aguardando_ensino = False
            self.falar("Aprendido e gravado na minha memória permanente!")
            return

        limpa = self.traduzir_girias(original.lower())

        if "que horas" in limpa or "horas são" in limpa:
            agora = datetime.now()
            self.falar(f"Agora são {agora.hour} horas e {agora.minute} minutos.")
            return
        if "que dia" in limpa or "data de hoje" in limpa:
            agora = datetime.now()
            self.falar(f"Hoje é dia {agora.day:02d}/{agora.month:02d}/{agora.year}.")
            return

        resp_hab = self.executar_20_habilidades(limpa)
        if resp_hab:
            self.falar(resp_hab)
            return

        chave_ps2 = f"{limpa} ps2" if "ps2" not in limpa else limpa
        parecidas = get_close_matches(limpa, list(self.memoria.keys()), n=1, cutoff=0.72)
        if not parecidas:
            parecidas = get_close_matches(chave_ps2, list(self.memoria.keys()), n=1, cutoff=0.72)

        if parecidas:
            self.falar(self.memoria[next(iter(parecidas))])
            return

        eh_ps2 = "ps2" in limpa or "playstation 2" in limpa or "jogo" in limpa
        self.tela_chat.text = f"{NOME_IA}: Consultando enciclopédia..."
        wiki = self.buscar_wikipedia_ou_ps2(limpa, modo_ps2=eh_ps2)
        if wiki:
            self.memoria[limpa] = wiki
            self.salvar_json(ARQUIVO_MEMORIA, self.memoria)
            self.falar(wiki)
        else:
            self.ultima_pergunta = limpa
            self.aguardando_ensino = True
            self.falar("Ainda não tenho isso no banco. Digita aí embaixo o que eu devo responder!")

NeoApp().run()
