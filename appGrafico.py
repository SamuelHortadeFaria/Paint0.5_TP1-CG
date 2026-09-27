# Código desenvolvido por Samuel Horta de Faria - 801528, com intuito de desenvolver uma aplicação gráfica semelhante ao Paint para a matéria de Computação Gráfica.

import tkinter as tk
from tkinter import messagebox
import math

class CGApp:
    #--------| INICIALIZAÇÃO |--------
    def __init__(self, root):
        
        self.root = root
        self.root.title("TP1 CG - Paint 0.5")
        self.root.configure(bg="#E0FFFF")
        
        #Barar de Ferramentas
        self.tools_frame = tk.Frame(root, width=220, bg="#E0FFFF", padx=15, pady=15)
        self.tools_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        #Canvas 800x600
        self.canvas_width = 800
        self.canvas_height = 600
        
        #Criação do canvas
        self.canvas = tk.Canvas(
            root, 
            width=self.canvas_width, 
            height=self.canvas_height, 
            bg="white", 
            highlightthickness=1, 
            highlightbackground="#CCCCCC"
        )
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=(0, 15), pady=15)
        
        #Matriz de pixels
        self.img = tk.PhotoImage(width=self.canvas_width, height=self.canvas_height) #PhotoImage permite acender pixels individualmente (x, y)
        self.canvas.create_image((self.canvas_width//2, self.canvas_height//2), image=self.img, state="normal")
        
        #Preenche toda a matriz de pixels inicialmente com branco
        self.img.put("#FFFFFF", to=(0, 0, self.canvas_width, self.canvas_height))
        
        #Variáveis de controle de estado e estruturas de dados
        self.current_tool = "DDA"
        self.color = "#000000"
        self.clicks = [] #Armazena temporariamente os cliques do mouse na tela
        self.primitives = [] #Guarda os objetos desenhados
        self.buttons = {} #Dicionário para referenciar os botões e destacar a ferramenta ativa
        self.clip_window = None #Armazena os limites da janela de recorte
        
        #Setup dos botões da barra lateral
        self.setup_buttons()
        
        # incula os eventos de clique do mouse na Área de Desenho
        self.canvas.bind("<Button-1>", self.on_click)       #Clique esquerdo registra os pontos
        self.canvas.bind("<Button-3>", self.on_right_click) #Clique direito fecha e desenha polígonos

    #----| Cria e estiliza botões de ferramentas na barra lateral |----
    def setup_buttons(self):
        tools = [
            "DDA", "Bresenham Reta", "Círculo", "Polígono", 
            "Preenchimento Flood", "Preenchimento Boundary",
            "Recorte Cohen-Sutherland", "Recorte Liang-Barsky",
            "Translação", "Escala", "Rotação", "Reflexão X", "Reflexão Y", "Reflexão XY"
        ]
        
        #Título barra lateral
        tk.Label(
            self.tools_frame, 
            text="Ferramentas", 
            bg="#E0FFFF", 
            fg="#2C3E50", 
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(0, 12))
        
        #Criação de cada botão da lista
        for tool in tools:
            btn = tk.Button(
                self.tools_frame, 
                text=tool, 
                command=lambda t=tool: self.select_tool(t),
                bg="#FFFFFF",
                fg="#34495E",
                font=("Segoe UI", 9, "bold"),
                relief="flat",              
                borderwidth=0,
                activebackground="#B0E0E6", 
                activeforeground="#000000",
                pady=5,                     
                cursor="hand2"
            )
            btn.pack(fill=tk.X, pady=2)
            self.buttons[tool] = btn
            
        #Botão para limpar
        tk.Button(
            self.tools_frame, 
            text="Limpar Tela", 
            command=self.clear_screen, 
            bg="#FFEBEE",
            fg="#C0392B",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            borderwidth=0,
            activebackground="#FADBD8",
            pady=7,
            cursor="hand2"
        ).pack(fill=tk.X, pady=(15, 0))
        
        #Seleciona a ferramenta padrão inicial
        self.select_tool("DDA")

    #----| Gerencia troca de ferramentas ou caixas de texto para transformações |----
    def select_tool(self, tool):

        #TRANSFORMAÇÕES: Abre a janela de inserção de valores
        if tool in ["Translação", "Escala", "Rotação"]:
            self.open_transform_dialog(tool)
            return
        #REFLEXÕES: Aplica sobre a última primitiva desenhada
        elif tool in ["Reflexão X", "Reflexão Y", "Reflexão XY"]:
            if self.primitives:
                self.apply_transformation(tool, None)
            else:
                messagebox.showwarning("Aviso", "Desenhe um objeto primeiro!")
            return

        #Atualiza a ferramenta de desenho ativa e limpa cliques pendentes
        self.current_tool = tool
        self.clicks = []
        self.canvas.delete("temp_click")
        
        #Reseta a cor de todos os botões e destaca em azul apenas a ferramenta selecionada
        for name, btn in self.buttons.items():
            btn.config(bg="#FFFFFF", fg="#34495E")
            
        if tool in self.buttons:
            self.buttons[tool].config(bg="#3498DB", fg="#FFFFFF")

    #----| Captura as coordenadas do clique do mouse e executa o algoritmo |----
    def on_click(self, event):

        x, y = event.x, event.y
        self.clicks.append((x, y)) 
        
        #Ponto de referência visual
        self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="red", tags="temp_click")
        
        #----| RASTERIZAÇÃO DE RETAS (Requer 2 cliques: Ponto Inicial e Ponto Final) |----
        if self.current_tool in ["DDA", "Bresenham Reta"]:
            if len(self.clicks) == 2:
                if self.current_tool == "DDA":
                    self.dda(self.clicks[0][0], self.clicks[0][1], self.clicks[1][0], self.clicks[1][1], self.color)
                else:
                    self.bresenham_line(self.clicks[0][0], self.clicks[0][1], self.clicks[1][0], self.clicks[1][1], self.color)
                
                #Salva a reta
                self.primitives.append({"type": "line", "pts": self.clicks.copy()})
                self.clicks = []
                self.canvas.delete("temp_click")
                
        #----| RASTERIZAÇÃO DE CIRCUNFERÊNCIA (Requer 2 cliques: Centro e Borda para definir o Raio) |----
        elif self.current_tool == "Círculo":
            if len(self.clicks) == 2:
                xc, yc = self.clicks[0]

                #Calcula a distância euclidiana entre o centro e o segundo ponto para obter o raio (r)
                r = int(math.hypot(self.clicks[1][0] - xc, self.clicks[1][1] - yc))
                self.bresenham_circle(xc, yc, r, self.color)
                self.primitives.append({"type": "circle", "center": (xc, yc), "r": r})
                self.clicks = []
                self.canvas.delete("temp_click")

        #----| ALGORITMOS DE PREENCHIMENTO |----
        elif self.current_tool == "Preenchimento Flood":
            if len(self.clicks) == 1:
                old_color = self.get_pixel(x, y)

                #Flood Fill: substitui a cor interna antiga pela nova cor
                self.flood_fill(x, y, "#FF0000", old_color) 
                self.clicks = []
                self.canvas.delete("temp_click")
                
        elif self.current_tool == "Preenchimento Boundary":
            if len(self.clicks) == 1:

                #Boundary Fill: preenche com Azul em todas as direções até encontrar a cor de borda
                self.boundary_fill(x, y, "#0000FF", "#000000") 
                self.clicks = []
                self.canvas.delete("temp_click")
                
        #----| ALGORITMOS DE RECORTE (Requer 2 cliques para definir os cantos da janela retangular) |----
        elif self.current_tool.startswith("Recorte"):
            if len(self.clicks) == 2:

                #Ordena as coordenadas para garantir xmin < xmax e ymin < ymax
                xmin, xmax = sorted([self.clicks[0][0], self.clicks[1][0]])
                ymin, ymax = sorted([self.clicks[0][1], self.clicks[1][1]])

                #Define a janela de recorte ativa
                self.clip_window = (xmin, ymin, xmax, ymax)
                new_primitives = []
                
                for obj in self.primitives:
                    if obj["type"] == "line":
                        l = obj["pts"]
                        if self.current_tool == "Recorte Cohen-Sutherland":
                            res = self.cohen_sutherland(xmin, ymin, xmax, ymax, l[0][0], l[0][1], l[1][0], l[1][1])
                        else:
                            res = self.liang_barsky(xmin, ymin, xmax, ymax, l[0][0], l[0][1], l[1][0], l[1][1])
                        
                        #Se a reta tiver parte visível dentro da janela, atualiza seus pontos extremos
                        if res:
                            new_pts = [(int(round(res[0])), int(round(res[1]))), (int(round(res[2])), int(round(res[3])))]
                            new_primitives.append({"type": "line", "pts": new_pts})
                    
                    elif obj["type"] == "polygon":

                        #Para polígonos, recorta individualmente cada uma de suas arestas usando o algoritmo selecionado
                        pts = obj["pts"]
                        for i in range(len(pts)):
                            p1 = pts[i]
                            p2 = pts[(i + 1) % len(pts)]
                            if self.current_tool == "Recorte Cohen-Sutherland":
                                res = self.cohen_sutherland(xmin, ymin, xmax, ymax, p1[0], p1[1], p2[0], p2[1])
                            else:
                                res = self.liang_barsky(xmin, ymin, xmax, ymax, p1[0], p1[1], p2[0], p2[1])
                            if res:
                                new_pts = [(int(round(res[0])), int(round(res[1]))), (int(round(res[2])), int(round(res[3])))]
                                new_primitives.append({"type": "line", "pts": new_pts})
                    else:
                        
                        new_primitives.append(obj) 
                        
                self.primitives = new_primitives
                self.redraw_all()
                
                #Retângulo tracejado vermelho indicando a janela
                self.canvas.create_rectangle(xmin, ymin, xmax, ymax, outline="red", dash=(4,4), tag="clip_win")
                self.clicks = []
                self.canvas.delete("temp_click")

    #----| Finaliza o desenho de um polígono ao clicar com o botão direito do mouse |---
    def on_right_click(self, event):

        if self.current_tool == "Polígono" and len(self.clicks) > 1:
            #Percorre vértices com o algoritmo de Bresenham
            for i in range(len(self.clicks)):
                p1 = self.clicks[i]
                p2 = self.clicks[(i + 1) % len(self.clicks)] #O operador % conecta o último ponto de volta ao primeiro
                self.bresenham_line(p1[0], p1[1], p2[0], p2[1], self.color)
            
            #Armazena o polígono finalizado na lista de primitivas
            self.primitives.append({"type": "polygon", "pts": self.clicks.copy()})
            self.clicks = []
            self.canvas.delete("temp_click")

    #----| Janela para valores de transformação |----
    def open_transform_dialog(self, trans_type):

        if not self.primitives:
            messagebox.showwarning("Aviso", "Desenhe um objeto primeiro!")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title(trans_type)
        dialog.geometry("250x180")
        dialog.resizable(False, False)
        
        entries = {}
        if trans_type in ["Translação", "Escala"]:
            tk.Label(dialog, text="Fator X:").pack(pady=5)
            e_x = tk.Entry(dialog)
            e_x.pack()
            entries['x'] = e_x
            
            tk.Label(dialog, text="Fator Y:").pack(pady=5)
            e_y = tk.Entry(dialog)
            e_y.pack()
            entries['y'] = e_y
        elif trans_type == "Rotação":
            tk.Label(dialog, text="Ângulo (em graus):").pack(pady=5)
            e_ang = tk.Entry(dialog)
            e_ang.pack()
            entries['ang'] = e_ang
            
        def apply():
            try:
                if trans_type in ["Translação", "Escala"]:
                    mod = (float(entries['x'].get()), float(entries['y'].get()))
                    if trans_type == "Escala" and (mod[0] == 0 or mod[1] == 0):
                        messagebox.showerror("Erro", "O fator de escala não pode ser zero!")
                        return
                elif trans_type == "Rotação":
                    mod = float(entries['ang'].get())
                self.apply_transformation(trans_type, mod)
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Insira valores numéricos válidos!")
                
        tk.Button(dialog, text="Confirmar", command=apply).pack(pady=15)

    #----| Acende um pixel, respeitando os limites da tela e da janela |----
    def set_pixel(self, x, y, color):

        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:

            #Se houver uma janela de recorte ativa, descarta pixels fora dos limites
            if self.clip_window:
                xmin, ymin, xmax, ymax = self.clip_window
                if not (xmin <= x <= xmax and ymin <= y <= ymax):
                    return
            self.img.put(color, (x, y))

    #----| Consulta cor atual e retorna no padrão hexadecimal |----
    def get_pixel(self, x, y):
        try:
            rgb = self.img.get(int(x), int(y))
            if isinstance(rgb, tuple):
                return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2]).upper()
            elif isinstance(rgb, str):
                if rgb.startswith("#"): return rgb.upper()
                parts = rgb.split()
                if len(parts) == 3:
                    return "#{:02x}{:02x}{:02x}".format(int(parts[0]), int(parts[1]), int(parts[2])).upper()
            return "#FFFFFF"
        except tk.TclError:
            return "#FFFFFF"

#----| Limpa toda a matrix de pixels |----
    def clear_screen(self):
        self.img.blank()
        self.canvas.delete("all") 
        self.canvas.create_image((self.canvas_width//2, self.canvas_height//2), image=self.img, state="normal")
        self.img.put("#FFFFFF", to=(0, 0, self.canvas_width, self.canvas_height))
        self.primitives = []
        self.clicks = []
        self.clip_window = None 

    #----| ALGORITMOS DE RASTERIZAÇÃO |----
    def dda(self, x1, y1, x2, y2, color):

        x1, y1, x2, y2 = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))
        dx = x2 - x1
        dy = y2 - y1
        passos = abs(dx) if abs(dx) > abs(dy) else abs(dy) 
        
        if passos == 0:
            self.set_pixel(x1, y1, color)
            return
            
        x_incr = dx / passos
        y_incr = dy / passos
        x, y = x1, y1
        self.set_pixel(x, y, color)
        
        for _ in range(int(passos)):
            x += x_incr
            y += y_incr
            self.set_pixel(x, y, color) 

    def bresenham_line(self, x1, y1, x2, y2, color):

        x1, y1, x2, y2 = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        incrx = 1 if x2 >= x1 else -1 
        incry = 1 if y2 >= y1 else -1 
        x, y = x1, y1
        self.set_pixel(x, y, color)
        
        if dy < dx:
            p = 2 * dy - dx 
            const1 = 2 * dy
            const2 = 2 * (dy - dx)
            for _ in range(dx):
                x += incrx
                if p < 0:
                    p += const1
                else:
                    y += incry
                    p += const2 
                self.set_pixel(x, y, color)
                
        else:
            p = 2 * dx - dy
            const1 = 2 * dx
            const2 = 2 * (dx - dy)
            for _ in range(dy):
                y += incry
                if p < 0:
                    p += const1
                else:
                    x += incrx
                    p += const2
                self.set_pixel(x, y, color)

    def bresenham_circle(self, xc, yc, r, color):
        
        xc, yc, r = int(round(xc)), int(round(yc)), int(round(r))
        x = 0
        y = r
        p = 3 - 2 * r 
        self.plot_circle_points(xc, yc, x, y, color)
        
        while x < y:
            if p < 0:
                p = p + 4 * x + 6 
            else:
                p = p + 4 * (x - y) + 10 
                y -= 1
            x += 1
            self.plot_circle_points(xc, yc, x, y, color)
            
    def plot_circle_points(self, xc, yc, x, y, color):
        
        pontos = [
            (xc+x, yc+y), (xc-x, yc+y), (xc+x, yc-y), (xc-x, yc-y),
            (xc+y, yc+x), (xc-y, yc+x), (xc+y, yc-x), (xc-y, yc-x)
        ]
        for px, py in pontos:
            self.set_pixel(px, py, color)

    #----| ALGORITMOS DE PREENCHIMENTO DE ÁREAS |----
    def flood_fill(self, x, y, fill_color, old_color):
        
        fill_color = fill_color.upper()
        old_color = old_color.upper()
        if fill_color == old_color: return
        
        stack = [(x, y)]
        count = 0
        while stack:
            cx, cy = stack.pop()
            if 0 <= cx < self.canvas_width and 0 <= cy < self.canvas_height:
                if self.get_pixel(cx, cy) == old_color:
                    self.set_pixel(cx, cy, fill_color)
                    
                    stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])
                    
                    count += 1
                    if count % 2000 == 0:
                        self.root.update_idletasks()
        self.root.update_idletasks()

    def boundary_fill(self, x, y, fill_color, boundary_color):
        
        fill_color = fill_color.upper()
        boundary_color = boundary_color.upper()
        
        if self.get_pixel(x, y) == boundary_color or fill_color == boundary_color:
            return
        
        stack = [(x, y)]
        count = 0
        while stack:
            cx, cy = stack.pop()

            if 0 <= cx < self.canvas_width and 0 <= cy < self.canvas_height:
                current = self.get_pixel(cx, cy)

                if current != boundary_color and current != fill_color:
                    self.set_pixel(cx, cy, fill_color)
                    stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])
                    
                    count += 1

                    if count % 2000 == 0:
                        self.root.update_idletasks()
        self.root.update_idletasks()

    #----| ALGORITMOS DE RECORTE DE LINHAS |----
    def compute_outcode(self, x, y, xmin, ymin, xmax, ymax):
        
        code = 0
        if x < xmin: code |= 1 
        elif x > xmax: code |= 2 
        if y < ymin: code |= 4 
        elif y > ymax: code |= 8 
        return code

    def cohen_sutherland(self, xmin, ymin, xmax, ymax, x1, y1, x2, y2):
        
        c1 = self.compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
        c2 = self.compute_outcode(x2, y2, xmin, ymin, xmax, ymax)
        aceito = False

        while True:
            if c1 == 0 and c2 == 0:
                aceito = True
                break
            elif (c1 & c2) != 0:
                break
            else:
                
                x, y = 0.0, 0.0
                cfora = c1 if c1 != 0 else c2 

                if cfora & 8:
                    x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                    y = ymax
                elif cfora & 4:
                    x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                    y = ymin
                elif cfora & 2:
                    y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                    x = xmax
                elif cfora & 1:
                    y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                    x = xmin

                if cfora == c1:
                    x1, y1 = x, y
                    c1 = self.compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
                else:
                    x2, y2 = x, y
                    c2 = self.compute_outcode(x2, y2, xmin, ymin, xmax, ymax)

        if aceito:
            return (x1, y1, x2, y2)
        return None

    def liang_barsky(self, xmin, ymin, xmax, ymax, x1, y1, x2, y2):
        
        dx = x2 - x1
        dy = y2 - y1
        p = [-dx, dx, -dy, dy] 
        q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1] 
        u1, u2 = 0.0, 1.0

        for i in range(4):
            if p[i] == 0:
                
                if q[i] < 0: return None
            else:
                r = q[i] / p[i]
                if p[i] < 0:
                    u1 = max(u1, r)
                else:
                    u2 = min(u2, r)

        if u1 > u2:
            return None

        nx1 = x1 + u1 * dx
        ny1 = y1 + u1 * dy
        nx2 = x1 + u2 * dx
        ny2 = y1 + u2 * dy
        return (nx1, ny1, nx2, ny2)

    #----| TRANSFORMAÇÕES GEOMÉTRICAS 2D |----
    def apply_transformation(self, trans_type, mod):

        obj = self.primitives[-1]
        cx_tela = self.canvas_width / 2.0
        cy_tela = self.canvas_height / 2.0

        if obj["type"] == "circle":
            xc, yc = obj["center"]
            r = obj["r"]
            if trans_type == "Translação":
                obj["center"] = (int(round(xc + mod[0])), int(round(yc + mod[1])))
            elif trans_type == "Escala":
                
                fator = (abs(mod[0]) + abs(mod[1])) / 2.0
                obj["r"] = max(1, int(round(r * fator)))
            elif trans_type == "Reflexão X":
                obj["center"] = (xc, int(round(2 * cy_tela - yc)))
            elif trans_type == "Reflexão Y":
                obj["center"] = (int(round(2 * cx_tela - xc)), yc)
            elif trans_type == "Reflexão XY":
                obj["center"] = (int(round(2 * cx_tela - xc)), int(round(2 * cy_tela - yc)))
                
            self.redraw_all()
            return

        pts = obj.get("pts")
        if not pts: return

        new_pts = []

        if trans_type == "Translação":

            tx, ty = mod
            for x, y in pts:
                new_pts.append((int(round(x + tx)), int(round(y + ty))))
                
        elif trans_type == "Escala":
            
            sx, sy = mod
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            for x, y in pts:
                nx = cx + (x - cx) * sx
                ny = cy + (y - cy) * sy
                new_pts.append((int(round(nx)), int(round(ny))))
                
        elif trans_type == "Rotação":
            
            ang = math.radians(mod)
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            for x, y in pts:
                nx = cx + (x - cx) * math.cos(ang) - (y - cy) * math.sin(ang)
                ny = cy + (x - cx) * math.sin(ang) + (y - cy) * math.cos(ang)
                new_pts.append((int(round(nx)), int(round(ny))))
                
        elif trans_type == "Reflexão X":
            
            for x, y in pts:
                ny = 2 * cy_tela - y
                new_pts.append((int(round(x)), int(round(ny))))
                
        elif trans_type == "Reflexão Y":
            
            for x, y in pts:
                nx = 2 * cx_tela - x
                new_pts.append((int(round(nx)), int(round(y))))

        elif trans_type == "Reflexão XY":
            
            for x, y in pts:
                nx = 2 * cx_tela - x
                ny = 2 * cy_tela - y
                new_pts.append((int(round(nx)), int(round(ny))))

        if new_pts:
            self.primitives[-1]["pts"] = new_pts
            self.redraw_all()

    #----| Limpa matriz e redesenha todas as primitivas armazenadas com coordenadas atualizadas |----
    def redraw_all(self):

        self.img.blank()
        self.canvas.delete("clip_win")
        self.img.put("#FFFFFF", to=(0, 0, self.canvas_width, self.canvas_height))
        
        for obj in self.primitives:
            if obj["type"] == "line":
                self.bresenham_line(obj["pts"][0][0], obj["pts"][0][1], obj["pts"][1][0], obj["pts"][1][1], self.color)
            elif obj["type"] == "polygon":
                pts = obj["pts"]
                for i in range(len(pts)):
                    p1 = pts[i]
                    p2 = pts[(i + 1) % len(pts)]
                    self.bresenham_line(p1[0], p1[1], p2[0], p2[1], self.color)
            elif obj["type"] == "circle":
                self.bresenham_circle(obj["center"][0], obj["center"][1], obj["r"], self.color)

#Ponto de entrada da aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = CGApp(root)
    root.mainloop()