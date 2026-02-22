# Implementação Avançada do Protocolo QKD BB84 - COBENGE
# Replicação do Artigo IEEE (2023) + Nova Proposta (Ataque Parcial em NISQ)

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import pathlib
import numpy as np
import matplotlib.pyplot as plt

FIGURES_DIR = pathlib.Path(__file__).parent.parent / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

console = Console()

# ==========================================
# FUNÇÕES DO PROTOCOLO QUÂNTICO
# ==========================================


def codificar_mensagem(bits, bases):
    """Alice prepara os qubits aplicando X (para bit 1) e H (para base Diagonal)"""
    n = len(bits)
    qc = QuantumCircuit(n, n)
    for i in range(n):
        if bits[i] == 1:
            qc.x(i)
        if bases[i] == 1:
            qc.h(i)
    qc.barrier()
    return qc


def medir_mensagem(qc, bases_medicao, qubits_alvo=None):
    """Bob mede os qubits no final do canal quântico"""
    n = len(bases_medicao)
    if qubits_alvo is None:
        qubits_alvo = range(n)

    for i in qubits_alvo:
        if bases_medicao[i] == 1:
            qc.h(i)
        qc.measure(i, i)
    return qc


def ataque_eve(qc, bases_eve, qubits_alvo=None):
    """
    CORREÇÃO FÍSICA: Eve intercepta, mede e TEM de re-preparar o estado
    na mesma base antes de o reencaminhar para o Bob (Intercept-Resend verdadeiro).
    """
    n = len(bases_eve)
    if qubits_alvo is None:
        qubits_alvo = range(n)

    for i in qubits_alvo:
        # Eve altera para a sua base de medição
        if bases_eve[i] == 1:
            qc.h(i)

        # Eve mede (o que colapsa irreversivelmente a função de onda)
        qc.measure(i, i)

        # RE-PREPARAÇÃO: Se Eve usou a base Diagonal (1), ela precisa de aplicar H
        # novamente para que o qubit siga viagem na base correta.
        if bases_eve[i] == 1:
            qc.h(i)
    return qc


def criar_modelo_ruido_hardware():
    """Simula a decoerência e o ruído térmico de um hardware real (ex: ibmqx2)"""
    noise_model = NoiseModel()
    # Erro depolarizante de 5% para simular o ruído de fundo da máquina (NISQ)
    error_1q = depolarizing_error(0.05, 1)
    noise_model.add_all_qubit_quantum_error(error_1q, ["u1", "u2", "u3", "x", "h"])
    return noise_model


def simular_circuito(qc, shots=8192, usar_ruido=False):
    """Executa o circuito no simulador (com ou sem modelo de ruído)"""
    simulador = AerSimulator(
        noise_model=criar_modelo_ruido_hardware() if usar_ruido else None
    )
    circuito_compilado = transpile(qc, simulador)
    resultado = simulador.run(circuito_compilado, shots=shots).result()
    return resultado.get_counts()


def calcular_qber(contagens, estado_correto, shots):
    """Calcula a verdadeira Taxa de Erro de Bit Quântico (QBER) bit a bit"""
    total_bits = 0
    erros_bits = 0

    for estado, contagem in contagens.items():
        total_bits += len(estado_correto) * contagem
        # Compara bit a bit para encontrar os erros exatos no fluxo
        for bit_medido, bit_correto in zip(estado, estado_correto):
            if bit_medido != bit_correto:
                erros_bits += contagem

    return (erros_bits / total_bits) * 100


# ==========================================
# FUNÇÕES DE PLOTAGEM (ESTILO ARTIGO IEEE)
# ==========================================


def plot_estilo_ieee(contagens, shots, titulo, nome_ficheiro, cor="#6495ED"):
    """Gera gráficos a replicar a estética do artigo base, mas em Português"""
    # Converte contagens para probabilidades
    probabilidades = {k: v / shots for k, v in contagens.items()}

    # Preenche SEMPRE os 16 estados para o gráfico manter a escala X consistente
    for i in range(16):
        estado = format(i, "04b")
        if estado not in probabilidades:
            probabilidades[estado] = 0.0

    chaves = sorted(probabilidades.keys())
    valores = [probabilidades[k] for k in chaves]

    plt.figure(figsize=(12, 6))
    barras = plt.bar(
        chaves, valores, color=cor, edgecolor="black", linewidth=0.5, width=0.6
    )

    plt.ylabel("Probabilidades", fontsize=12, fontweight="bold")
    plt.title(titulo, fontsize=14, pad=15)

    # Dá um espaço extra no topo do eixo Y para o texto não ser cortado
    limite_y = max(valores) + 0.15
    plt.ylim(0, limite_y if limite_y <= 1.1 else 1.1)

    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Adiciona os valores em cima das barras (Formato 0.xxx igual ao artigo)
    for barra in barras:
        yval = barra.get_height()
        if yval > 0.005:  # Filtra ruídos minúsculos na etiqueta
            plt.text(
                barra.get_x() + barra.get_width() / 2,
                yval + 0.02,
                f"{yval:.3f}",
                ha="center",
                va="bottom",
                fontsize=9,
                rotation=45,
            )

    plt.tight_layout()
    plt.savefig(nome_ficheiro, format="pdf", dpi=300)
    plt.close()


# ==========================================
# CONFIGURAÇÃO DO EXPERIMENTO
# ==========================================

n_qubits = 4
shots = 8192

console.print(
    Panel.fit(
        "[bold magenta]Experimento Avançado QKD BB84 - Submissão COBENGE[/bold magenta]\n"
        "[dim]Replicação do Estudo IEEE (2023) + Proposta de Ataque Parcial NISQ[/dim]",
        border_style="cyan",
    )
)

# Para fins de demonstração clara nos gráficos, vamos fixar o estado enviado por Alice
# e garantir que Bob escolha as mesmas bases (Sifting perfeito)
bits_alice = [1, 0, 1, 0]
bases_compartilhadas = [1, 0, 1, 0]  # 1 = Diagonal (X), 0 = Retilínea (Z)
bases_alice = bases_compartilhadas
bases_bob = bases_compartilhadas

# O Qiskit lê os qubits da direita para a esquerda (q3 q2 q1 q0)
estado_correto_str = "".join(map(str, reversed(bits_alice)))

tabela = Table(
    title="Setup do Canal Quântico (Pós-Sifting)",
    show_header=True,
    header_style="bold cyan",
)
tabela.add_column("Qubit", justify="center")
tabela.add_column("Bit Preparado", justify="center", style="bold white")
tabela.add_column("Base Utilizada", justify="center", style="green")
for i in range(n_qubits):
    tabela.add_row(
        str(i),
        str(bits_alice[i]),
        "Diagonal (X)" if bases_alice[i] else "Retilínea (Z)",
    )
console.print(tabela)
console.print(
    f"[bold white]Estado Esperado no Receptor (Bob):[/bold white] [bold green]{estado_correto_str}[/bold green]\n"
)

# ==========================================
# EXECUÇÃO DOS CENÁRIOS
# ==========================================

qbers = []
cenarios_nomes = []

with console.status(
    "[bold yellow]A executar simulações quânticas e a gerar gráficos (em PDF)...[/bold yellow]",
    spinner="dots",
):
    # 1. Replicação: Simulador Ideal (Sem Eve)
    qc1 = medir_mensagem(codificar_mensagem(bits_alice, bases_alice), bases_bob)

    # Guardar o diagrama do circuito BASE (Para os slides e artigo)
    fig_circuito = qc1.draw("mpl")
    fig_circuito.savefig(
        str(FIGURES_DIR / "fig0_circuito_bb84_base.pdf"), format="pdf", bbox_inches="tight", dpi=300
    )

    contagens_1 = simular_circuito(qc1, shots, usar_ruido=False)
    qber_1 = calcular_qber(contagens_1, estado_correto_str, shots)
    qbers.append(qber_1)
    cenarios_nomes.append("Simulador (Ideal)")
    plot_estilo_ieee(
        contagens_1,
        shots,
        "Cenário 1: Simulador Ideal (Sem Espião)",
        str(FIGURES_DIR / "fig1_simulador_ideal.pdf"),
    )

    # 2. Replicação: Simulador Ideal com Ataque Total de Eve (Artigo Original)
    qc_eve_total = codificar_mensagem(bits_alice, bases_alice)
    bases_eve_total = np.random.randint(2, size=n_qubits)  # Eve adivinha todas as bases
    qc_eve_total = ataque_eve(
        qc_eve_total, bases_eve_total
    )  # Interceptação e re-preparação total
    qc_eve_total.barrier()
    qc_eve_total = medir_mensagem(qc_eve_total, bases_bob)  # Bob mede após a Eve

    contagens_2 = simular_circuito(qc_eve_total, shots, usar_ruido=False)
    qber_2 = calcular_qber(contagens_2, estado_correto_str, shots)
    qbers.append(qber_2)
    cenarios_nomes.append("Ataque Total (Eve)")
    plot_estilo_ieee(
        contagens_2,
        shots,
        "Cenário 2: Simulador Ideal com Interceptação Total (Eve)",
        str(FIGURES_DIR / "fig2_simulador_eve_total.pdf"),
        cor="#ff6b6b",
    )

    # 3. Replicação: Hardware Quântico Real (NISQ - Sem Eve)
    qc3 = medir_mensagem(codificar_mensagem(bits_alice, bases_alice), bases_bob)
    contagens_3 = simular_circuito(qc3, shots, usar_ruido=True)
    qber_3 = calcular_qber(contagens_3, estado_correto_str, shots)
    qbers.append(qber_3)
    cenarios_nomes.append("Hardware (Ruído)")
    plot_estilo_ieee(
        contagens_3,
        shots,
        "Cenário 3: Hardware Quântico Real NISQ (Sem Espião)",
        str(FIGURES_DIR / "fig3_hardware_natural.pdf"),
    )

    # 4. NOSSA PROPOSTA: Hardware Quântico Real com Ataque Parcial
    qc_proposta = codificar_mensagem(bits_alice, bases_alice)
    bases_eve_parcial = np.random.randint(2, size=n_qubits)
    qc_proposta = ataque_eve(
        qc_proposta, bases_eve_parcial, qubits_alvo=[0, 1]
    )  # Eve intercepta só metade
    qc_proposta.barrier()
    qc_proposta = medir_mensagem(qc_proposta, bases_bob)

    # Guardar o diagrama do circuito da NOSSA PROPOSTA (A demonstrar o ataque parcial)
    fig_circuito_proposta = qc_proposta.draw("mpl")
    fig_circuito_proposta.savefig(
        str(FIGURES_DIR / "fig4a_circuito_nossa_proposta.pdf"), format="pdf", bbox_inches="tight", dpi=300
    )

    contagens_4 = simular_circuito(qc_proposta, shots, usar_ruido=True)
    qber_4 = calcular_qber(contagens_4, estado_correto_str, shots)
    qbers.append(qber_4)
    cenarios_nomes.append("Nossa Proposta\n(Ataque Parcial)")
    plot_estilo_ieee(
        contagens_4,
        shots,
        "Cenário 4: Nossa Proposta - Hardware NISQ com Ataque Parcial",
        str(FIGURES_DIR / "fig4_hardware_ataque_parcial.pdf"),
        cor="#ff9f43",
    )

# ==========================================
# GRÁFICO COMPARATIVO DE DIFERENÇAS (QBER)
# ==========================================
plt.figure(figsize=(10, 6))
cores_qber = ["#1dd1a1", "#ff6b6b", "#54a0ff", "#ff9f43"]
barras_qber = plt.bar(
    cenarios_nomes, qbers, color=cores_qber, edgecolor="black", width=0.5
)
plt.ylabel("Taxa de Erro Quântico (QBER) %", fontsize=12, fontweight="bold")
plt.title(
    "Comparativo de Erro (QBER): Replicação vs Nossa Proposta", fontsize=14, pad=15
)
plt.ylim(0, max(qbers) + 15)

for barra in barras_qber:
    yval = barra.get_height()
    plt.text(
        barra.get_x() + barra.get_width() / 2,
        yval + 1,
        f"{yval:.2f}%",
        ha="center",
        va="bottom",
        fontweight="bold",
    )

plt.tight_layout()
plt.savefig(str(FIGURES_DIR / "fig5_diferencas_qber.pdf"), format="pdf", dpi=300)
plt.close()

# ==========================================
# SAÍDA DE RESULTADOS NO TERMINAL
# ==========================================
console.rule("[bold blue]RESUMO ESTATÍSTICO DOS RESULTADOS[/bold blue]")

tabela_resumo = Table(show_header=True, header_style="bold yellow")
tabela_resumo.add_column("Cenário Analisado")
tabela_resumo.add_column("Origem")
tabela_resumo.add_column("QBER (%)", justify="right")

tabela_resumo.add_row(
    "1. Simulador Ideal (Sem Eve)", "Replicação IEEE", f"[green]{qber_1:.2f}%[/green]"
)
tabela_resumo.add_row(
    "2. Simulador Ideal (Ataque Total)", "Replicação IEEE", f"[red]{qber_2:.2f}%[/red]"
)
tabela_resumo.add_row(
    "3. Hardware NISQ (Ruído Natural)", "Replicação IEEE", f"[blue]{qber_3:.2f}%[/blue]"
)
tabela_resumo.add_row(
    "4. Hardware NISQ (Ataque Parcial)",
    "[bold magenta]Nossa Proposta[/bold magenta]",
    f"[yellow]{qber_4:.2f}%[/yellow]",
)

console.print(tabela_resumo)

console.print(
    "\n[bold green]✔ Todos os gráficos e diagramas foram gerados e guardados em formato PDF com sucesso![/bold green]"
)
console.print(
    "-> [dim]figures/fig0_circuito_bb84_base.pdf[/dim] [bold cyan](O Diagrama Base IEEE)[/bold cyan]"
)
console.print("-> [dim]figures/fig1_simulador_ideal.pdf[/dim]")
console.print("-> [dim]figures/fig2_simulador_eve_total.pdf[/dim]")
console.print("-> [dim]figures/fig3_hardware_natural.pdf[/dim]")
console.print("-> [dim]figures/fig4_hardware_ataque_parcial.pdf[/dim]")
console.print(
    "-> [dim]figures/fig4a_circuito_nossa_proposta.pdf[/dim] [bold magenta](O Diagrama do Ataque Parcial)[/bold magenta]"
)
console.print("-> [dim]figures/fig5_diferencas_qber.pdf[/dim]")
