import tkinter as tk
from PIL import Image, ImageTk
import os
import random

maravilhas = [
    {"nome": "Cristo Redentor", "ano": 1931, "imagem": "imagens/cristo.jpg"},
    {"nome": "Coliseu",         "ano": 80,   "imagem": "imagens/coliseu.jpg"},
    {"nome": "Petra",           "ano": -312, "imagem": "imagens/petra.jpg"},
    {"nome": "Machu Picchu",    "ano": 1450, "imagem": "imagens/machu.jpg"},
    {"nome": "Taj Mahal",       "ano": 1653, "imagem": "imagens/tajmahal.jpg"},
    {"nome": "Chichen Itza",    "ano": 600,  "imagem": "imagens/chichen.jpg"},
    {"nome": "Muralha da China","ano": -700, "imagem": "imagens/muralha.jpg"},
]

# ── layout ────────────────────────────────────────────────────────────────────
CARD_W   = 120
CARD_H   = 165
IMG_W, IMG_H = 100, 72
ESPACO   = 140
INICIO_X = 80
CANVAS_W = 1020
CANVAS_H = 560          # canvas mais compacto

# Banner no topo do canvas
BANNER_H = 86
BANNER_Y = BANNER_H // 2

# Linha principal dos cards (logo abaixo do banner)
Y_LINHA  = BANNER_H + CARD_H // 2 + 20   # ≈ 189

# Pivô sobe para meio-caminho entre banner e grupos
PIVO_Y   = BANNER_H + CARD_H // 2 + 30   # ≈ 169, centro do card logo abaixo do banner

# Grupos esq/dir descem só o suficiente para não sobrepor o pivô
GRUPO_Y  = Y_LINHA + CARD_H + 30          # ≈ 384

PIVO_X       = CANVAS_W // 2
CARD_SEP     = CARD_W + 10

# ── cores ─────────────────────────────────────────────────────────────────────
COR_BG          = "#0f1117"
COR_CARD        = "#1e2130"
COR_BORDA       = "#3a3f5c"
COR_TEXTO       = "#e8e8f0"
COR_ANO         = "#a0a8cc"
COR_PIVO_BG     = "#f0e0a0"
COR_PIVO_BD     = "#b09020"
COR_MENOR_BG    = "#c87a30"
COR_MENOR_BD    = "#905020"
COR_MAIOR_BG    = "#5080c0"
COR_MAIOR_BD    = "#3060a0"
COR_FIXADO      = "#8040e0"
COR_ACERTO      = "#40c080"
COR_ERRO        = "#e04040"
COR_BANNER_BG   = "#13151f"
COR_BANNER_LINE = "#2a2f45"
COR_BOTAO_BG    = "#1e2130"
COR_BOTAO_FG    = "#e8e8f0"
COR_BOTAO_HOVER = "#2d334f"

# ── estado ────────────────────────────────────────────────────────────────────
estado = {
    "animando": False,
    "verificado": False,
    "mostrar_anos": False,
    "drag_idx": None,
    "drag_start_x": 0,
    "card_start_x": 0,
}
fixados    = set()
imagens_tk = []
cards_info = []

random.shuffle(maravilhas)

# ── janela ────────────────────────────────────────────────────────────────────
janela = tk.Tk()
janela.title("Quick Sort — 7 Maravilhas do Mundo Moderno")
janela.geometry(f"{CANVAS_W}x{CANVAS_H + 70}")
janela.configure(bg=COR_BG)
janela.resizable(False, False)

canvas = tk.Canvas(janela, width=CANVAS_W, height=CANVAS_H,
                   bg=COR_BG, highlightthickness=0)
canvas.pack()

# Barra de botões abaixo do canvas
barra = tk.Frame(janela, bg=COR_BG)
barra.pack(pady=(4, 8))

# ── banner de status (desenhado no canvas) ─────────────────────────────────
def _criar_banner():
    """Cria os itens gráficos permanentes do banner. Chamado uma vez."""
    canvas.create_rectangle(
        0, 0, CANVAS_W, BANNER_H,
        fill=COR_BANNER_BG, outline="", tags="banner_bg")
    canvas.create_line(
        0, BANNER_H, CANVAS_W, BANNER_H,
        fill=COR_BANNER_LINE, width=1, tags="banner_line")
    # título fixo pequeno
    canvas.create_text(
        CANVAS_W // 2, 14,
        text="7 MARAVILHAS DO MUNDO MODERNO — Quick Sort",
        font=("Georgia", 9, "italic"), fill="#3a3f5c",
        tags="banner_title")
    # texto principal (grande)
    canvas.create_text(
        CANVAS_W // 2, 46,
        text="", font=("Georgia", 14, "bold"),
        fill=COR_TEXTO, justify="center", tags="banner_main")
    # texto secundário (pequeno, subtítulo)
    canvas.create_text(
        CANVAS_W // 2, 72,
        text="", font=("Georgia", 9, "italic"),
        fill="#6a72a0", justify="center", tags="banner_sub")

_criar_banner()

def set_status(principal, sub="", cor=COR_TEXTO):
    canvas.itemconfig("banner_main", text=principal, fill=cor)
    canvas.itemconfig("banner_sub",  text=sub)
    canvas.tag_raise("banner_bg")
    canvas.tag_raise("banner_line")
    canvas.tag_raise("banner_title")
    canvas.tag_raise("banner_main")
    canvas.tag_raise("banner_sub")

set_status("Arraste os cards para ordená-los do mais antigo ao mais recente")

# ── utilitários ───────────────────────────────────────────────────────────────
def fmt_ano(ano):
    return str(ano) if ano > 0 else f"{abs(ano)} a.C."

def slot_x(idx):
    return INICIO_X + idx * ESPACO

# ── desenho dos cards ─────────────────────────────────────────────────────────
def desenhar_cards():
    global cards_info, imagens_tk
    canvas.delete("card")
    cards_info  = []
    imagens_tk  = []

    caminho_base = os.path.dirname(os.path.abspath(__file__))
    for item in maravilhas:
        caminho = os.path.join(caminho_base, item["imagem"])
        img = Image.open(caminho).resize((IMG_W, IMG_H))
        imagens_tk.append(ImageTk.PhotoImage(img))

    for i, item in enumerate(maravilhas):
        x, y = slot_x(i), Y_LINHA
        tag  = f"card_{i}"
        bc   = COR_FIXADO if i in fixados else COR_BORDA
        ano_txt = ""
        if estado["mostrar_anos"]:
            ano_txt = fmt_ano(item["ano"])

        shadow  = canvas.create_rectangle(
            x - CARD_W//2 + 4, y - CARD_H//2 + 4,
            x + CARD_W//2 + 4, y + CARD_H//2 + 4,
            fill="#0a0c12", outline="", tags=("card", tag))
        rect    = canvas.create_rectangle(
            x - CARD_W//2, y - CARD_H//2,
            x + CARD_W//2, y + CARD_H//2,
            fill=COR_CARD, outline=bc, width=2, tags=("card", tag))
        img_id  = canvas.create_image(x, y - 24, image=imagens_tk[i], tags=("card", tag))
        nome_id = canvas.create_text(x, y + 42, text=item["nome"],
            font=("Georgia", 8, "bold"), fill=COR_TEXTO,
            width=CARD_W - 8, justify="center", tags=("card", tag))
        ano_id  = canvas.create_text(x, y + 62, text=ano_txt,
            font=("Georgia", 8, "italic"), fill=COR_ANO, tags=("card", tag))

        cards_info.append({
            "tag": tag, "shadow": shadow, "rect": rect,
            "img_id": img_id, "nome_id": nome_id, "ano_id": ano_id,
            "x": x, "y": y
        })

    # garante banner sempre visível sobre os cards
    canvas.tag_raise("banner_bg")
    canvas.tag_raise("banner_line")
    canvas.tag_raise("banner_title")
    canvas.tag_raise("banner_main")
    canvas.tag_raise("banner_sub")

# ── drag & drop ───────────────────────────────────────────────────────────────
def idx_slot_mais_proximo(x_pixel):
    melhor, dist = 0, float("inf")
    for i in range(len(maravilhas)):
        d = abs(x_pixel - slot_x(i))
        if d < dist:
            dist, melhor = d, i
    return melhor

def on_press(event):
    if estado["animando"] or estado["verificado"]:
        return
    if event.y < BANNER_H:          # clique no banner → ignorar
        return
    itens = canvas.find_overlapping(event.x - 2, event.y - 2,
                                     event.x + 2, event.y + 2)
    for item_id in reversed(itens):
        for t in canvas.gettags(item_id):
            if t.startswith("card_") and t.count("_") == 1:
                idx = int(t.split("_")[1])
                estado["drag_idx"]    = idx
                estado["drag_start_x"] = event.x
                estado["card_start_x"] = cards_info[idx]["x"]
                canvas.tag_raise(t)
                return

def on_drag(event):
    if estado["drag_idx"] is None:
        return
    i     = estado["drag_idx"]
    novo_x = estado["card_start_x"] + (event.x - estado["drag_start_x"])
    delta  = novo_x - cards_info[i]["x"]
    canvas.move(cards_info[i]["tag"], delta, 0)
    cards_info[i]["x"] = novo_x

def on_release(event):
    if estado["drag_idx"] is None:
        return
    i     = estado["drag_idx"]
    alvo  = idx_slot_mais_proximo(cards_info[i]["x"])
    estado["drag_idx"] = None
    if alvo != i:
        maravilhas[i], maravilhas[alvo] = maravilhas[alvo], maravilhas[i]
    desenhar_cards()

canvas.bind("<ButtonPress-1>",   on_press)
canvas.bind("<B1-Motion>",       on_drag)
canvas.bind("<ButtonRelease-1>", on_release)

# ── verificação ───────────────────────────────────────────────────────────────
def verificar():
    estado["mostrar_anos"] = True
    estado["verificado"]   = True
    desenhar_cards()
    correto = all(
        maravilhas[i]["ano"] <= maravilhas[i + 1]["ano"]
        for i in range(len(maravilhas) - 1))
    if correto:
        set_status("Incrível! Você acertou a ordem cronológica! 🎉",
                   "As datas foram reveladas.", COR_ACERTO)
        btn_verificar.pack_forget()
        btn_embaralhar.pack(side=tk.LEFT, padx=6)
    else:
        set_status("Não foi dessa vez — mas as datas são difíceis!",
                   "Veja o Quick Sort ordenar automaticamente →", COR_ERRO)
        btn_verificar.pack_forget()
        btn_sort.pack(side=tk.LEFT, padx=6)
        btn_embaralhar.pack(side=tk.LEFT, padx=6)

# ── animação Quick Sort ───────────────────────────────────────────────────────
def animar_quick_sort():
    global fixados
    estado["animando"]     = True
    estado["mostrar_anos"] = True
    fixados = set()
    btn_sort.config(state="disabled")
    btn_embaralhar.config(state="disabled")

    global imagens_tk
    caminho_base = os.path.dirname(os.path.abspath(__file__))
    imagens_tk   = []
    for item in maravilhas:
        caminho = os.path.join(caminho_base, item["imagem"])
        img = Image.open(caminho).resize((IMG_W, IMG_H))
        imagens_tk.append(ImageTk.PhotoImage(img))

    canvas.delete("card")
    anim_por_nome = {}

    for i, item in enumerate(maravilhas):
        x, y = slot_x(i), Y_LINHA
        tag  = f"ac_{item['nome'].replace(' ', '_')}"
        shadow  = canvas.create_rectangle(
            x - CARD_W//2 + 4, y - CARD_H//2 + 4,
            x + CARD_W//2 + 4, y + CARD_H//2 + 4,
            fill="#0a0c12", outline="", tags=("card", tag))
        rect    = canvas.create_rectangle(
            x - CARD_W//2, y - CARD_H//2,
            x + CARD_W//2, y + CARD_H//2,
            fill=COR_CARD, outline=COR_BORDA, width=2, tags=("card", tag))
        img_id  = canvas.create_image(x, y - 24, image=imagens_tk[i], tags=("card", tag))
        nome_id = canvas.create_text(x, y + 42, text=item["nome"],
            font=("Georgia", 8, "bold"), fill=COR_TEXTO,
            width=CARD_W - 8, justify="center", tags=("card", tag))
        ano_id  = canvas.create_text(x, y + 62, text=fmt_ano(item["ano"]),
            font=("Georgia", 8, "italic"), fill=COR_ANO, tags=("card", tag))
        anim_por_nome[item["nome"]] = {
            "tag": tag, "shadow": shadow, "rect": rect,
            "img_id": img_id, "nome_id": nome_id, "ano_id": ano_id,
            "x": x, "y": y, "item": item, "foto": imagens_tk[i]
        }

    # eleva banner sobre cards de animação
    canvas.tag_raise("banner_bg")
    canvas.tag_raise("banner_line")
    canvas.tag_raise("banner_title")
    canvas.tag_raise("banner_main")
    canvas.tag_raise("banner_sub")

    ids_fixados = set()

    def get_a(nome):
        return anim_por_nome[nome]

    def colorir(nome, fill, borda=None, texto=COR_TEXTO):
        a = get_a(nome)
        canvas.itemconfig(a["rect"], fill=fill, outline=borda or fill, width=2)
        canvas.itemconfig(a["nome_id"], fill=texto)

    def restaurar_cor(nome):
        a = get_a(nome)
        if id(a) in ids_fixados:
            canvas.itemconfig(a["rect"], fill=COR_CARD, outline=COR_FIXADO, width=3)
        else:
            canvas.itemconfig(a["rect"], fill=COR_CARD, outline=COR_BORDA, width=2)
        canvas.itemconfig(a["nome_id"], fill=COR_TEXTO)

    def mover_card(nome, tx, ty, passos=22, delay=11, cb=None):
        a  = get_a(nome)
        cx = [a["x"]]
        cy = [a["y"]]
        dx = (tx - a["x"]) / passos
        dy = (ty - a["y"]) / passos
        p  = [0]
        tag = a["tag"]
        canvas.tag_raise(tag)

        def _tick():
            if p[0] >= passos:
                canvas.move(tag, tx - cx[0], ty - cy[0])
                a["x"], a["y"] = tx, ty
                if cb:
                    cb()
                return
            canvas.move(tag, dx, dy)
            cx[0] += dx
            cy[0] += dy
            p[0]  += 1
            janela.after(delay, _tick)

        _tick()

    def gerar_cenas():
        cenas = []
        arr   = [m["nome"] for m in maravilhas]
        anos  = {m["nome"]: m["ano"] for m in maravilhas}
        
        ########################################################################

        # QUICK SORT
        def qs(ini, fim):
            if ini >= fim:
                if ini == fim:
                    cenas.append({"tipo": "unitario", "nome": arr[ini], "pos": ini})
                return
            pivo_nome = arr[fim]
            i = ini - 1
            for j in range(ini, fim):
                if anos[arr[j]] <= anos[pivo_nome]:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
            pos = i + 1
            arr[pos], arr[fim] = arr[fim], arr[pos]

            menores = list(arr[ini:pos])
            maiores = list(arr[pos + 1:fim + 1])
            cenas.append({
                "tipo":     "partição",
                "pivo":     pivo_nome,
                "menores":  menores,
                "maiores":  maiores,
                "pos_pivo": pos,
                "ini":      ini,
                "fim":      fim,
                "ordem":    list(arr),
            })
            qs(ini, pos - 1)
            qs(pos + 1, fim)
        
        ########################################################################

        qs(0, len(arr) - 1)
        return cenas

    cenas    = gerar_cenas()
    cena_idx = [0]

    def proxima_cena():
        cena_idx[0] += 1
        if cena_idx[0] >= len(cenas):
            finalizar()
        else:
            executar_cena()

    def executar_cena():
        cena = cenas[cena_idx[0]]

        if cena["tipo"] == "unitario":
            nome = cena["nome"]
            a    = get_a(nome)
            ids_fixados.add(id(a))
            canvas.itemconfig(a["rect"], fill=COR_CARD, outline=COR_FIXADO, width=3)
            set_status(f"{nome}  ·  posição definitiva ✓",
                       fmt_ano(a["item"]["ano"]), COR_FIXADO)
            janela.after(900, proxima_cena)
            return

        pivo   = cena["pivo"]
        menores = cena["menores"]
        maiores = cena["maiores"]
        ini    = cena["ini"]
        fim    = cena["fim"]
        ordem  = cena["ordem"]
        a_pivo = get_a(pivo)

        # ── Banner: mostrar pivô ──────────────────────────────────────────────
        set_status(
            f"Pivô:  {pivo}  ({fmt_ano(a_pivo['item']['ano'])})",
            f"Lado Esquerdo: anteriores  ·  Lado Direito: posteriores",
            COR_PIVO_BG)

        colorir(pivo, COR_PIVO_BG, COR_PIVO_BD, "#7a6010")
        canvas.tag_raise(a_pivo["tag"])

        def apos_subir_pivo():
            for nm in menores:
                colorir(nm, COR_MENOR_BG, COR_MENOR_BD, "#5a3010")
            for nm in maiores:
                colorir(nm, COR_MAIOR_BG, COR_MAIOR_BD, "#102040")

            esq_nomes = "  ·  ".join(menores) if menores else "—"
            dir_nomes = "  ·  ".join(maiores) if maiores else "—"

            # ── Banner: separação ─────────────────────────────────────────────
            set_status(
                f"Pivô: {pivo}",
                f"◀ Esquerda ({len(menores)}):  {esq_nomes}     "
                f"Direita ({len(maiores)}):  {dir_nomes}  ▶",
                COR_PIVO_BG)

            n_esq = len(menores)
            n_dir = len(maiores)
            total = n_esq + n_dir

            if total == 0:
                janela.after(600, reagrupar)
                return

            concluidos = [0]

            def mov_ok():
                concluidos[0] += 1
                if concluidos[0] >= total:
                    janela.after(1400, reagrupar)

            GAP = 30

            if n_esq:
                larg_esq = n_esq * CARD_SEP - (CARD_SEP - CARD_W)
                x_esq_fim = PIVO_X - CARD_W // 2 - GAP
                cx_esq = max(x_esq_fim - larg_esq + CARD_W // 2, CARD_W // 2 + 8)
            else:
                cx_esq = 0

            if n_dir:
                cx_dir = PIVO_X + CARD_W // 2 + GAP + CARD_W // 2
                larg_dir = n_dir * CARD_SEP
                if cx_dir + larg_dir > CANVAS_W - 8:
                    cx_dir = CANVAS_W - 8 - larg_dir + CARD_W // 2
            else:
                cx_dir = 0

            for j, nm in enumerate(menores):
                mover_card(nm, cx_esq + j * CARD_SEP, GRUPO_Y, cb=mov_ok)
            for j, nm in enumerate(maiores):
                mover_card(nm, cx_dir + j * CARD_SEP, GRUPO_Y, cb=mov_ok)

        def reagrupar():
            set_status(
                "Reagrupando...",
                f"{pivo} desce para sua posição definitiva",
                COR_ANO)

            total      = fim - ini + 1
            concluidos = [0]

            def mov_ok():
                concluidos[0] += 1
                if concluidos[0] >= total:
                    a_p = get_a(pivo)
                    ids_fixados.add(id(a_p))
                    canvas.itemconfig(a_p["rect"], fill=COR_CARD,
                                      outline=COR_FIXADO, width=3)
                    canvas.itemconfig(a_p["nome_id"], fill=COR_TEXTO)
                    for nm in menores + maiores:
                        restaurar_cor(nm)
                    set_status(
                        f"{pivo}  ·  posição definitiva ✓",
                        fmt_ano(a_pivo["item"]["ano"]), COR_FIXADO)
                    janela.after(1100, proxima_cena)

            for pos_l in range(ini, fim + 1):
                nm = ordem[pos_l]
                mover_card(nm, slot_x(pos_l), Y_LINHA, cb=mov_ok)

        mover_card(pivo, PIVO_X, PIVO_Y, passos=28, delay=9, cb=apos_subir_pivo)

    def finalizar():
        for nome in anim_por_nome:
            a = anim_por_nome[nome]
            canvas.itemconfig(a["rect"], fill=COR_CARD, outline=COR_FIXADO, width=3)
            canvas.itemconfig(a["nome_id"], fill=COR_TEXTO)
        set_status(
            "Ordenação concluída!  Do mais antigo ao mais recente  ✓",
            "O Quick Sort dividiu repetidamente até nada restar para dividir.",
            COR_ACERTO)
        estado["animando"] = False
        btn_embaralhar.config(state="normal")

    executar_cena()

# ── embaralhar ────────────────────────────────────────────────────────────────
def embaralhar():
    global fixados
    fixados = set()
    random.shuffle(maravilhas)
    estado["mostrar_anos"] = False
    estado["verificado"]   = False
    estado["animando"]     = False
    btn_sort.pack_forget()
    btn_embaralhar.pack_forget()
    btn_verificar.pack(side=tk.LEFT, padx=6)
    set_status("Arraste os cards para ordená-los do mais antigo ao mais recente")
    desenhar_cards()

# ── botões ────────────────────────────────────────────────────────────────────
def _make_btn(parent, text, cmd):
    b = tk.Button(parent, text=text, command=cmd,
                  font=("Georgia", 10), bg=COR_BOTAO_BG, fg=COR_BOTAO_FG,
                  activebackground=COR_BOTAO_HOVER, activeforeground=COR_BOTAO_FG,
                  relief="flat", padx=20, pady=8, cursor="hand2", bd=0)
    b.bind("<Enter>", lambda e: b.configure(bg=COR_BOTAO_HOVER))
    b.bind("<Leave>", lambda e: b.configure(bg=COR_BOTAO_BG))
    return b

btn_verificar  = _make_btn(barra, "✓  Verificar minha ordem",       verificar)
btn_sort       = _make_btn(barra, "▶  Ver o Quick Sort organizar",   animar_quick_sort)
btn_embaralhar = _make_btn(barra, "↺  Embaralhar novamente",         embaralhar)
btn_sort.configure(command=animar_quick_sort)
btn_embaralhar.configure(command=embaralhar)

btn_verificar.pack(side=tk.LEFT, padx=6)

# ── início ────────────────────────────────────────────────────────────────────
desenhar_cards()
janela.mainloop()
