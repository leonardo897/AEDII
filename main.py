import sys
import random
import math

# ----------------------------------------------------------------------------
# Geração de grafo aleatório 
# ---------------------------------------------------------------------------
def gerar_grafo_aleatorio():
    n = random.randint(20, 30) # número de vértices
    m = random.randint(n * 2, n * 3) # número de arestas
    vertices = list(range(n))
    random.shuffle(vertices)

    # gerar altitudes aleatórias para garantir descida (peso negativo) e subida (peso positivo)
    altitudes = [random.randint(0, 20) for _ in range(n)]

    castelo = 0  # o castelo é o vértice 0

    altitudes[castelo] = max(altitudes) + 1  # o castelo tem a maior altitude

    # Escolhe 6 portos (que não sejam o castelo)
    portos_candidatos = [v for v in vertices if v != castelo]
    random.shuffle(portos_candidatos)
    portos = portos_candidatos[:6]

    for porto in portos:
        altitudes[porto] = 0  #  Portos têm a menor altitude (nível do mar)

    arestas = set()
    # Garantir conectividade mínima entre os vértices
    for i in range(n-1):
        u, v = vertices[i], vertices[i+1]
        if altitudes[v] < altitudes[u]:
            peso = -random.uniform(1, 5)
        else:
            peso = random.uniform(6, 10)
        arestas.add((u, v, peso))

    # Adicionar arestas extras aleatórias
    while len(arestas) < m:
        u = random.randint(0, n-1)
        v = random.randint(0, n-1)
        if u == v:
            continue
        if altitudes[v] == altitudes[u]:
            peso = 0
        if altitudes[v] < altitudes[u]:
            peso = -random.uniform(1, 5)
        else:
            peso = random.uniform(6, 10)
        arestas.add((u, v, peso))

    arestas = list(arestas)
    m = len(arestas)

    # Calcular grau de entrada total dos portos
    grau_entrada_portos = 0
    for u, v, _ in arestas:
        if v in portos:
            grau_entrada_portos += 1
            
    num_policiais = random.randint(5, grau_entrada_portos - 1) # pelo menos 5 policiais, no máximo um a menos que o grau de entrada total dos portos

    posicoes_policiais = [random.randint(1, n-1) for _ in range(num_policiais)] # os policiais começam em vértices aleatórios (exceto o castelo)
    
    with open('entrada.txt', 'w') as f: # salva o grafo gerado em entrada.txt
        f.write(f"{n} {m}\n")
        for u, v, w in arestas:
            f.write(f"{u} {v} {w:.2f}\n")
        f.write(f"{castelo}\n")
        f.write(" ".join(map(str, portos)) + "\n")
        f.write(f"{num_policiais}\n")
        f.write(" ".join(map(str, posicoes_policiais)) + "\n")
    return n, m, arestas, castelo, portos, num_policiais, posicoes_policiais, altitudes

# --------------------------------------------------------------------------------
# Leitura do arquivo de entrada
# --------------------------------------------------------------------------------
def ler_entrada():
    try:
        with open('entrada.txt', 'r') as f:
            linhas = f.readlines()
    except FileNotFoundError:
        print("Arquivo entrada.txt não encontrado. Gerando grafo aleatório...")
        return gerar_grafo_aleatorio()

    linhas = [linha.strip() for linha in linhas if linha.strip()]
    if not linhas:
        print("Arquivo vazio. Gerando grafo aleatório...")
        return gerar_grafo_aleatorio()

    idx = 0
    n, m = map(int, linhas[idx].split())
    idx += 1
    arestas = []
    for _ in range(m):
        partes = linhas[idx].split()
        u, v, w = int(partes[0]), int(partes[1]), float(partes[2])
        arestas.append((u, v, w))
        idx += 1
    castelo = int(linhas[idx])
    idx += 1
    portos = list(map(int, linhas[idx].split()))
    idx += 1
    num_policiais = int(linhas[idx])
    idx += 1
    posicoes_policiais = list(map(int, linhas[idx].split()))
    
    # Calcular altitudes simuladas a partir dos pesos para consistência
    # Para simplificar, atribuímos altitudes baseadas nos vértices
    altitudes = [i * 10 for i in range(n)]
    return n, m, arestas, castelo, portos, num_policiais, posicoes_policiais, altitudes

# -----------------------------------------------------------------------------------------
# Construção da lista de adjacência
# -----------------------------------------------------------------------------------------
def construir_adjacencias(arestas, n):
    adj = [[] for _ in range(n)]
    for u, v, w in arestas:
        adj[u].append((v, w))
    return adj

# ------------------------------------------------------------
# Dijkstra para menor caminho (retorna distâncias)
# ------------------------------------------------------------
def dijkstra(adj, origem):
    n = len(adj)
    dist = [float('inf')] * n
    prev = [-1] * n
    dist[origem] = 0
    visitado = [False] * n
    for _ in range(n):
        u = -1
        menor = float('inf')
        for i in range(n):
            if not visitado[i] and dist[i] < menor:
                menor = dist[i]
                u = i
        if u == -1:
            break
        visitado[u] = True
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
    return dist, prev

def reconstruir_caminho(prev, destino):
    caminho = []
    atual = destino
    while atual != -1:
        caminho.append(atual)
        atual = prev[atual]
    caminho.reverse()
    return caminho

# ------------------------------------------------------------
# Encontrar melhor rota de fuga do ladrão
# O ladrão quer chegar a um porto descendo ou por planícies (peso negativo ou zero)
# ------------------------------------------------------------
def encontrar_melhor_rota_fuga(adj, origem, portos):
    n = len(adj)
    # Seleciona apenas arestas com peso negativo ou zero (descida ou planície)
    adj_descida = [[] for _ in range(n)]
    for u in range(n):
        for v, w in adj[u]:
            if (w < 0) or (w == 0): 
                adj_descida[u].append((v, -1 * w))
    
    # usa Dijkstra para encontrar caminho com menor peso em módulo
    dist, prev = dijkstra(adj_descida, origem)
    
    # Encontra o porto alcançável mais próximo
    melhor_porto = None
    melhor_dist = float('inf')  # o menor valor

    for p in portos:
        if dist[p] < melhor_dist:
            melhor_dist = dist[p]
            melhor_porto = p
    
    if melhor_porto is None or math.isinf(melhor_dist):
        return None, None
    
    caminho = reconstruir_caminho(prev, melhor_porto)
    return caminho, melhor_dist

# -------------------------------------------------------------------
# Identificar vértices críticos no caminho do ladrão (gargalos)
# -------------------------------------------------------------------
def encontrar_vertices_criticos(caminho_ladrao):
    # Vértices que não são portos e têm apenas um vizinho no caminho
    if not caminho_ladrao:
        return []
    criticos = []
    for i in range(1, len(caminho_ladrao) - 1):
        # Vértices intermediários que são "estreitos"
        criticos.append(caminho_ladrao[i])
    return criticos

# ----------------------------------------------------------------------------
# Movimentação do ladrão seguindo a melhor rota de fuga
# -----------------------------------------------------------------------------
def mover_ladrao_rota_fixa(caminho_fuga, index_atual):
    if index_atual + 1 < len(caminho_fuga):
        return caminho_fuga[index_atual + 1], index_atual + 1, False
    return caminho_fuga[-1], index_atual, True  # chegou no porto

# ---------------------------------------------------------------------------   
# Movimentação dos policiais (tentam bloquear rota de fuga)
# Cada policial se move 2 vértices por rodada
# -----------------------------------------------------------------------------
def mover_policiais_bloqueio(adj, posicoes, alvo, vertices_criticos):
    novas_posicoes = []
    for p in posicoes:
        # Se há vértices críticos (bloqueio possível)
        if vertices_criticos:
            # Encontra o vértice crítico mais próximo
            melhor_critico = None
            menor_dist = float('inf')
            for critico in vertices_criticos:
                dist, _ = dijkstra(adj, p)
                if dist[critico] < menor_dist:
                    menor_dist = dist[critico]
                    melhor_critico = critico
            
            if melhor_critico is not None:
                # Vai em direção ao vértice crítico
                dist, prev = dijkstra(adj, p)
                caminho = reconstruir_caminho(prev, melhor_critico)
                if len(caminho) <= 1:
                    novas_posicoes.append(p)
                elif len(caminho) >= 3:
                    novas_posicoes.append(caminho[2])
                else:
                    novas_posicoes.append(caminho[1])
                continue
        
        # Se não há críticos ou já está bloqueando, vai em direção ao ladrão
        dist, prev = dijkstra(adj, p)
        caminho = reconstruir_caminho(prev, alvo)
        if len(caminho) <= 1:
            novas_posicoes.append(p)
        elif len(caminho) >= 3:
            novas_posicoes.append(caminho[2])
        else:
            novas_posicoes.append(caminho[1])
    
    return novas_posicoes

# ---------------------------------------------------------------------------------------------------
# Geração do relatório final da simulação
# ---------------------------------------------------------------------------------------------------

def gerar_relatorio(rodada, caminho_fuga, visitados_ladrao, num_policiais, historico_policiais, capturado, escapou, rodada_captura, pos_ladrao, vertices_criticos, distancia_fuga):
    with open('relatorio.txt', 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("RELATORIO DA PERSEGUICAO\n")
        f.write("=" * 60 + "\n\n")

        if capturado:
            f.write(f"STATUS: Ladrao foi PRESO na rodada {rodada_captura}.\n")
            f.write(f"Numero de equipes policiais utilizadas: {num_policiais}\n")
        elif escapou:
            f.write("STATUS: Ladrao ESCAPOU por um dos portos.\n")
            f.write("Numero de equipes policiais foi insuficiente para bloquear a rota.\n")
        else:
            f.write("STATUS: Simulacao terminou sem captura ou fuga (limite de rodadas).\n")

        f.write(f"\nTotal de rodadas simuladas: {rodada}\n")

        f.write("\n" + "-" * 40 + "\n")
        f.write("ROTA DE FUGA DO LADRAO:\n")
        f.write(" -> ".join(map(str, caminho_fuga)) + "\n")
        f.write(f"Distancia total: {distancia_fuga:.2f}\n")

        f.write("\n" + "-" * 40 + "\n")
        f.write("SEQUENCIA DE VERTICES VISITADOS PELO LADRAO:\n")
        f.write(" -> ".join(map(str, visitados_ladrao)) + "\n")

        if capturado:
            f.write(f"\nRodada de captura: {rodada_captura}\n")
            f.write(f"Posicaoo final do ladrao: {pos_ladrao}\n")

        f.write("\n" + "-" * 40 + "\n")
        f.write("CAMINHO PERCORRIDO POR CADA POLICIAL:\n")
        for i in range(len(historico_policiais)):
            f.write(f"Policial {i+1}: " + " -> ".join(map(str, historico_policiais[i])) + "\n")

        f.write("\n" + "-" * 40 + "\n")
        if vertices_criticos:
            f.write(f"Vertices criticos identificados na rota: {vertices_criticos}\n")
        else:
            f.write("Nenhum vertice critico identificado na rota.\n")

    print("Simulação concluida. Relatorio salvo em relatorio.txt")
# ---------------------------------------------------------------------------------------------------
# Simulação da ilha
# ---------------------------------------------------------------------------------------------------
def simular():
    gerar_grafo_aleatorio()  # Gera um grafo aleatório e salva em entrada.txt

    n, m, arestas, castelo, portos, num_policiais, posicoes_policiais, altitudes = ler_entrada()
    adj = construir_adjacencias(arestas, n)

    # Ladrão calcula sua melhor rota de fuga
    caminho_fuga, distancia_fuga = encontrar_melhor_rota_fuga(adj, castelo, portos)
    
    if caminho_fuga is None:
        with open('relatorio.txt', 'w') as f:
            f.write("Nao ha rota de fuga possivel para o ladrao usando apenas descidas ou planicies.\n")
            f.write("Ladrao foi capturado imediatamente.\n")
            f.write(f"Numero de equipes policiais: {num_policiais}\n")
            f.write("Rodada: 0\n")
        return

    # Estado inicial
    idx_caminho_ladrao = 0
    pos_ladrao = castelo
    visitados_ladrao = [pos_ladrao]
    
    # Histórico de posições de cada policial
    historico_policiais = []
    for i, pos in enumerate(posicoes_policiais):
        historico_policiais.append([pos])
    
    capturado = False
    escapou = False
    rodada = 0
    rodada_captura = None

    while not capturado and not escapou:
        rodada += 1

        # 1. Ladrão se move seguindo rota de fuga
        vertices_criticos = encontrar_vertices_criticos(caminho_fuga[idx_caminho_ladrao:])
        nova_pos, novo_idx, chegou_porto = mover_ladrao_rota_fixa(caminho_fuga, idx_caminho_ladrao)
        pos_ladrao = nova_pos
        idx_caminho_ladrao = novo_idx
        visitados_ladrao.append(pos_ladrao)

        if chegou_porto or pos_ladrao in portos:
            escapou = True
            break

        # Verifica captura após movimento do ladrão
        if pos_ladrao in posicoes_policiais:
            capturado = True
            rodada_captura = rodada
            break

        # 2. Policiais se movem (tentam bloquear rota)
        adj_pol = []

        for a in adj:
            adj_pol.append([(v, abs(w)) for v, w in a])  # Policiais podem mover-se para qualquer vértice, então usam peso absoluto para movimentação

        posicoes_policiais = mover_policiais_bloqueio(adj_pol, posicoes_policiais, pos_ladrao, vertices_criticos)
        
        # Atualiza o caminho percorrido de cada policial
        for i in range(len(posicoes_policiais)):
            historico_policiais[i].append(posicoes_policiais[i])

        # Verifica captura após movimento dos policiais
        if pos_ladrao in posicoes_policiais:
            capturado = True
            rodada_captura = rodada
            break

        # Limite de segurança
        if rodada > 1000:
            break

    # Geração do relatório
    gerar_relatorio(rodada, caminho_fuga, visitados_ladrao, num_policiais, historico_policiais, capturado, escapou, rodada_captura, pos_ladrao, vertices_criticos, distancia_fuga)

# ------------------------------------------------------------
# Execução principal
# ------------------------------------------------------------
if __name__ == "__main__":
    simular()