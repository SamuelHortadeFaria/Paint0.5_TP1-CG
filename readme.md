# 🎨 TP1 Computação Gráfica - Paint 0.5

Aplicação gráfica interativa estilo *Paint* desenvolvida em **Python** com **Tkinter** para o Trabalho Prático 1 da disciplina de Computação Gráfica. O projeto implementa diretamente sobre uma estrutura de matriz de pixels os algoritmos de rasterização, preenchimento de áreas, recorte e transformações geométricas 2D.

## Funcionalidades Implementadas

### 1. Rasterização de Primitivas
* **Retas (DDA - *Digital Differential Analyzer*):** Traçado de retas utilizando aritmética de ponto flutuante e arredondamento incremental.
* **Retas (Bresenham Genérico):** Rasterização de retas em todos os 8 octantes utilizando exclusivamente aritmética de números inteiros.
* **Circunferências (Bresenham):** Traçado de círculos calculando o primeiro octante com variável de decisão inteira e espelhando os pontos por simetria de 8 lados.
* **Polígonos:** Construção de polígonos fechados de N vértices conectados pelo algoritmo de Bresenham.

### 2. Preenchimento de Áreas (Conectividade-4)
* **Flood Fill:** Substituição da cor interna de uma região delimitada por uma cor vermelha, utilizando estrutura de pilha iterativa.
* **Boundary Fill:** Expansão da pintura com a cor azul a partir de um ponto semente até atingir os pixels da cor de fronteira/borda (Preto).

### 3. Algoritmos de Recorte
* **Cohen-Sutherland:** Recorte de segmentos de reta e arestas utilizando codificação binária de 4 bits para as 9 regiões do espaço.
* **Liang-Barsky:** Recorte baseado em equações paramétricas ($0 \le u \le 1$) analisando os pontos de entrada e saída nas fronteiras da janela.

### 4. Transformações Geométricas 2D
Aplicadas sobre o último objeto criado na cena com fatores informados pelo usuário:
* **Translação:** Deslocamento nos eixos $X$ e $Y$ ($t_x, t_y$).
* **Escala:** Redimensionamento em torno do centroide do objeto ($s_x, s_y$).
* **Rotação:** Rotação trigonométrica em graus em torno do centroide do objeto.
* **Reflexões ($X$, $Y$ e $XY$):** Espelhamento das coordenadas em relação aos eixos centrais do Canvas.

---

## Como Utilizar na Interface

| Ferramenta | Ação no Mouse |
| :--- | :--- |
| **DDA / Bresenham Reta** | **2 cliques esquerdos:** 1º define o ponto inicial e o 2º o ponto final. |
| **Círculo** | **2 cliques esquerdos:** 1º define o centro e o 2º define o raio. |
| **Polígono** | **Cliques esquerdos** adicionam vértices; **1 clique direito** fecha o polígono. |
| **Flood / Boundary Fill** | **1 clique esquerdo** no interior do polígono inicia o preenchimento. |
| **Recortes (Cohen / Liang)** | **2 cliques esquerdos** desenham e definem o tamanho da janela. |
| **Transformações / Reflexões** | Basta clicar no botão correspondente na barra lateral para aplicar ao último objeto. |

---

## Como Executar o Projeto

* É apenas necessário o **Python 3.x** instalado .A biblioteca `tkinter` já vem incluída por padrão na instalação oficial do Python no Windows/macOS. Após isto, é necessário apenas escrever o seguinte comando para abrir:
```
python .\appGrafico.py