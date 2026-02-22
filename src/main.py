# %% [markdown]
# # Implementação Avançada do Protocolo QKD BB84 - COBENGE
# Integração HÍBRIDA: IBM Quantum (Qiskit) + Google Quantum AI (Cirq)
# Código estruturado em células para Jupyter/Colab.

# %% [Instalação e Verificação de Ambiente]
# O comando de instalação solicitado pelo Boss:
# !pip install qiskit qiskit-aer qiskit-ibm-runtime matplotlib rich cirq pandas pylatexenc

import sys
import subprocess

# Verificação automática de ambiente (Colab vs PC Local)
IN_COLAB = "google.colab" in sys.modules

if IN_COLAB:
    print("🌐 Detectado ambiente Google Colab! Instalando as dependências pesadas...")
    # Executa a instalação via subprocess para manter a compatibilidade como script Python puro
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "qiskit",
        "qiskit-aer",
        "qiskit-ibm-runtime",
        "matplotlib",
        "rich",
        "cirq",
        "pandas",
        "pylatexenc",
    ])
    print("✅ Todas as bibliotecas quânticas foram instaladas e injetadas no Colab!")
else:
    print(
        "💻 Detectado ambiente Local (Seu PC)! Assumindo que as dependências já estão instaladas."
    )
    print(
        "Se faltar algo, rode no seu terminal: pip install qiskit qiskit-aer qiskit-ibm-runtime matplotlib rich cirq pandas"
    )

# %% [Importações e Configuração de Diretórios]
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit_ibm_runtime import QiskitRuntimeService
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.prompt import Confirm
from rich.live import Live
import pathlib
import numpy as np
import matplotlib.pyplot as plt
import time

# Importação do Ecossistema Google (Cirq)
try:
    import cirq

    CIRQ_DISPONIVEL = True
except ImportError:
    CIRQ_DISPONIVEL = False

# Criação automática da pasta de figuras para não sujar o diretório raiz
FIGURES_DIR = (
    pathlib.Path(__file__).parent.parent / "figures"
    if not IN_COLAB
    else pathlib.Path("/content/figures")
)
FIGURES_DIR.mkdir(exist_ok=True, parents=True)

console = Console()

# %% [Autenticação IBM Cloud]
import getpass

# ==========================================
# CHAVES DE ACESSO DA IBM
# ==========================================

# Pergunta interativa ao invés de variável hardcoded. O padrão (default=False) é NÃO usar a nuvem.
console.print("\n[cyan]⚙️ Configuração do Ambiente de Execução[/cyan]")
USAR_HARDWARE_REAL_IBM = Confirm.ask(
    "[bold yellow]Deseja enviar a 'Nossa Proposta' para rodar no Hardware Físico Real da IBM na nuvem?[/bold yellow]",
    default=False,
)

backend_real_ibm = None

if USAR_HARDWARE_REAL_IBM:
    console.print("\n[yellow]🔒 Modo de Autenticação Segura Ativado...[/yellow]")
    # O getpass pede o token sem o imprimir no ecrã e sem o guardar no código fonte!
    MEU_TOKEN_IBM = getpass.getpass(
        "🔑 Cole o seu Token da IBM Quantum aqui (o texto ficará invisível por segurança): "
    )

    console.print("[yellow]A autenticar nos servidores da IBM Quantum...[/yellow]")
    service = QiskitRuntimeService(channel="ibm_quantum", token=MEU_TOKEN_IBM)
    console.print(
        "[yellow]A procurar o computador quântico com a menor fila global...[/yellow]"
    )
    backend_real_ibm = service.least_busy(
        operational=True, simulator=False, min_num_qubits=4
    )
    console.print(
        f"[bold green]✔ Alvo fixado! Usaremos o hardware: {backend_real_ibm.name}[/bold green]\n"
    )
else:
    console.print(
        "[dim]Execução 100% local selecionada. Nenhuma conexão com a IBM será feita.[/dim]\n"
    )


# %% [Funções do Protocolo Quântico - IBM QISKIT]
def codificar_mensagem(bits, bases):
    """Alice prepara os qubits (X para 1, H para base Diagonal)"""
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
    """Bob mede os fótons no final do canal óptico"""
    n = len(bases_medicao)
    if qubits_alvo is None:
        qubits_alvo = range(n)
    for i in qubits_alvo:
        if bases_medicao[i] == 1:
            qc.h(i)
        qc.measure(i, i)
    return qc


def ataque_eve(qc, bases_eve, qubits_alvo=None):
    """Eve aplica o ataque Intercept-Resend (Mede e re-prepara a partícula)"""
    n = len(bases_eve)
    if qubits_alvo is None:
        qubits_alvo = range(n)
    for i in qubits_alvo:
        if bases_eve[i] == 1:
            qc.h(i)
        qc.measure(i, i)
        if bases_eve[i] == 1:
            qc.h(i)  # Re-preparação
    return qc


def criar_modelo_ruido_hardware():
    """Modela as falhas físicas (Decoerência) de um chip NISQ (5% de erro)"""
    noise_model = NoiseModel()
    error_1q = depolarizing_error(0.05, 1)
    noise_model.add_all_qubit_quantum_error(error_1q, ["u1", "u2", "u3", "x", "h"])
    return noise_model


def simular_circuito(qc, shots=4096, usar_ruido=False, forcado_na_ibm=False):
    """Executa o circuito (Simulador Ideal, Simulador com Ruído ou Hardware Real)"""
    if forcado_na_ibm and backend_real_ibm is not None:
        circuito_compilado = transpile(qc, backend_real_ibm)
        job = backend_real_ibm.run(circuito_compilado, shots=shots)
        # O terminal vai ficar girando o Qubit em ASCII Art enquanto espera!
        resultado = job.result()
        return resultado.get_counts()
    else:
        simulador = AerSimulator(
            noise_model=criar_modelo_ruido_hardware() if usar_ruido else None
        )
        circuito_compilado = transpile(qc, simulador)
        resultado = simulador.run(circuito_compilado, shots=shots).result()
        return resultado.get_counts()


def calcular_qber(contagens, estado_correto, shots):
    """Calcula a Taxa de Erro de Bit Quântico (QBER) com precisão de bit individual"""
    total_bits = 0
    erros_bits = 0
    for estado, contagem in contagens.items():
        total_bits += len(estado_correto) * contagem
        for bit_medido, bit_correto in zip(estado, estado_correto):
            if bit_medido != bit_correto:
                erros_bits += contagem
    return (erros_bits / total_bits) * 100


# %% [Função do Protocolo Quântico - GOOGLE CIRQ]
def simular_google_cirq_parcial(bits_a, bases_a, bases_b, bases_e, shots=4096):
    """Simula a 'Nossa Proposta' no motor quântico da Google (Validação cruzada)"""
    qubits = cirq.LineQubit.range(4)
    circuito = cirq.Circuit()

    for i in range(4):
        if bits_a[i] == 1:
            circuito.append(cirq.X(qubits[i]))
        if bases_a[i] == 1:
            circuito.append(cirq.H(qubits[i]))

    # Ataque Parcial (Eve ataca Qubits 0 e 1)
    for i in [0, 1]:
        if bases_e[i] == 1:
            circuito.append(cirq.H(qubits[i]))
        circuito.append(cirq.measure(qubits[i], key=f"eve_{i}"))
        if bases_e[i] == 1:
            circuito.append(cirq.H(qubits[i]))

    for i in range(4):
        if bases_b[i] == 1:
            circuito.append(cirq.H(qubits[i]))
        circuito.append(cirq.measure(qubits[i], key=f"bob_{i}"))

    # Injeção de ruído NISQ padrão da Google (5%)
    ruido = cirq.depolarize(p=0.05)
    circuito_ruidoso = circuito.with_noise(ruido)

    simulador = cirq.Simulator()
    resultado = simulador.run(circuito_ruidoso, repetitions=shots)

    contagens = {}
    for i in range(shots):
        bit_string = "".join([
            str(resultado.measurements[f"bob_{q}"][i][0]) for q in [3, 2, 1, 0]
        ])
        contagens[bit_string] = contagens.get(bit_string, 0) + 1

    return contagens


# %% [Funções de Plotagem Estilo IEEE]
def plot_estilo_ieee(contagens, shots, titulo, nome_ficheiro, cor="#6495ED"):
    """Clona o layout visual dos gráficos do paper IEEE original"""
    probabilidades = {k: v / shots for k, v in contagens.items()}
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
    limite_y = max(valores) + 0.15
    plt.ylim(0, limite_y if limite_y <= 1.1 else 1.1)
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    for barra in barras:
        yval = barra.get_height()
        if yval > 0.005:
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


# %% [Classe da Animação do Qubit em ASCII Art]
class AnimacaoQubit:
    """Renderizável dinâmico para rodar a pixel art do qubit em background."""

    def __init__(self):
        self.frames = [
            "[bold cyan]   ⬡   \n ┌───┐ \n │ 0 │ \n └───┘ \n   ⬡   [/bold cyan]",
            "[bold yellow]   ✧   \n ┌───┐ \n │ + │ \n └───┘ \n   ✧   [/bold yellow]",
            "[bold magenta]   ⬢   \n ┌───┐ \n │ 1 │ \n └───┘ \n   ⬢   [/bold magenta]",
            "[bold green]   ✦   \n ┌───┐ \n │ - │ \n └───┘ \n   ✦   [/bold green]",
        ]

    def __rich__(self):
        # Altera o frame baseado no relógio do sistema (aproximadamente 4 fps)
        frame_idx = int(time.time() * 4) % len(self.frames)
        return Panel(
            self.frames[frame_idx],
            title="[dim]Qubit View[/dim]",
            border_style="cyan",
            expand=False,
        )


# %% [Configuração do Experimento - Alice & Bob]
n_qubits = 4
shots = 4096

console.print(
    Panel.fit(
        "[bold magenta]Experimento HÍBRIDO BB84 - Submissão COBENGE[/bold magenta]\n"
        "[dim]Cross-Platform: IBM Qiskit vs Google Cirq | Modo Células Interativas[/dim]",
        border_style="cyan",
    )
)

bits_alice = [1, 0, 1, 0]
bases_compartilhadas = [1, 0, 1, 0]
bases_alice = bases_compartilhadas
bases_bob = bases_compartilhadas
estado_correto_str = "".join(map(str, reversed(bits_alice)))

tabela = Table(
    title="Setup Inicial: Chave Quântica", show_header=True, header_style="bold cyan"
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

qbers = []
cenarios_nomes = []

# %% [Execução Quântica com UI Hacker Simultânea]
console.print(
    "\n[bold yellow]Iniciando Hack Quântico... Quebrando o limite da decoerência...[/bold yellow]"
)

# Criando a barra de progresso como um componente isolado
progress = Progress(
    SpinnerColumn("dots", style="magenta"),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(complete_style="cyan", finished_style="green"),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
)

# Criando a grelha visual: Progresso à esquerda, Animação do Qubit à direita
layout_ui = Table.grid(expand=True)
layout_ui.add_column(ratio=1)  # Estica para ocupar o espaço da barra
layout_ui.add_column(justify="right")  # Empurra o qubit pro canto direito da tela
layout_ui.add_row(progress, AnimacaoQubit())

# O Live inicia uma thread em background que atualiza a tela 10x por segundo
with Live(layout_ui, console=console, refresh_per_second=10):
    tarefa_qiskit = progress.add_task(
        "[cyan]Processando Tensores IBM Qiskit...", total=4
    )

    # --- Cenário 1 ---
    progress.update(
        tarefa_qiskit, description="[cyan]Gerando Cenário 1: Simulador Ideal...[/cyan]"
    )
    time.sleep(1)  # Delay estético
    qc1 = medir_mensagem(codificar_mensagem(bits_alice, bases_alice), bases_bob)
    qc1.draw("mpl").savefig(
        str(FIGURES_DIR / "fig0_circuito_bb84_base.pdf"),
        format="pdf",
        bbox_inches="tight",
        dpi=300,
    )
    contagens_1 = simular_circuito(qc1, shots, usar_ruido=False)
    qber_1 = calcular_qber(contagens_1, estado_correto_str, shots)
    qbers.append(qber_1)
    cenarios_nomes.append("Simulador Ideal\n(Qiskit)")
    plot_estilo_ieee(
        contagens_1,
        shots,
        "Cenário 1: Simulador Ideal (IBM Qiskit)",
        str(FIGURES_DIR / "fig1_simulador_ideal.pdf"),
    )
    progress.advance(tarefa_qiskit)

    # --- Cenário 2 ---
    progress.update(
        tarefa_qiskit, description="[red]Simulando Intrusão Total (Eve)...[/red]"
    )
    time.sleep(1)
    qc_eve_total = codificar_mensagem(bits_alice, bases_alice)
    bases_eve_total = np.random.randint(2, size=n_qubits)
    qc_eve_total = ataque_eve(qc_eve_total, bases_eve_total)
    qc_eve_total.barrier()
    qc_eve_total = medir_mensagem(qc_eve_total, bases_bob)
    contagens_2 = simular_circuito(qc_eve_total, shots, usar_ruido=False)
    qber_2 = calcular_qber(contagens_2, estado_correto_str, shots)
    qbers.append(qber_2)
    cenarios_nomes.append("Ataque Total\n(Qiskit)")
    plot_estilo_ieee(
        contagens_2,
        shots,
        "Cenário 2: Simulador Ideal com Interceptação Total",
        str(FIGURES_DIR / "fig2_simulador_eve_total.pdf"),
        cor="#ff6b6b",
    )
    progress.advance(tarefa_qiskit)

    # --- Cenário 3 ---
    progress.update(
        tarefa_qiskit,
        description="[yellow]Injetando Ruído NISQ (Modelo Termodinâmico)...[/yellow]",
    )
    time.sleep(1)
    qc3 = medir_mensagem(codificar_mensagem(bits_alice, bases_alice), bases_bob)
    contagens_3 = simular_circuito(qc3, shots, usar_ruido=True)
    qber_3 = calcular_qber(contagens_3, estado_correto_str, shots)
    qbers.append(qber_3)
    cenarios_nomes.append("Hardware Ruído\n(Qiskit)")
    plot_estilo_ieee(
        contagens_3,
        shots,
        "Cenário 3: Hardware Quântico NISQ (Sem Espião)",
        str(FIGURES_DIR / "fig3_hardware_natural.pdf"),
    )
    progress.advance(tarefa_qiskit)

    # --- Cenário 4 ---
    descricao_c4 = (
        "[magenta]Aguardando resposta da IBM Cloud...[/magenta]"
        if USAR_HARDWARE_REAL_IBM
        else "[magenta]Aplicando a NOSSA PROPOSTA: Ataque Parcial...[/magenta]"
    )
    progress.update(tarefa_qiskit, description=descricao_c4)
    time.sleep(1)

    qc_proposta_ibm = codificar_mensagem(bits_alice, bases_alice)
    bases_eve_parcial = np.random.randint(2, size=n_qubits)
    qc_proposta_ibm = ataque_eve(qc_proposta_ibm, bases_eve_parcial, qubits_alvo=[0, 1])
    qc_proposta_ibm.barrier()
    qc_proposta_ibm = medir_mensagem(qc_proposta_ibm, bases_bob)
    qc_proposta_ibm.draw("mpl").savefig(
        str(FIGURES_DIR / "fig4a_circuito_nossa_proposta.pdf"),
        format="pdf",
        bbox_inches="tight",
        dpi=300,
    )

    contagens_4 = simular_circuito(
        qc_proposta_ibm,
        shots,
        usar_ruido=not USAR_HARDWARE_REAL_IBM,
        forcado_na_ibm=USAR_HARDWARE_REAL_IBM,
    )

    qber_4 = calcular_qber(contagens_4, estado_correto_str, shots)
    qbers.append(qber_4)
    cenarios_nomes.append("Ataque Parcial\n(Qiskit)")
    nome_cenario_4 = (
        "Hardware Real IBM" if USAR_HARDWARE_REAL_IBM else "Simulador Ruidoso"
    )
    plot_estilo_ieee(
        contagens_4,
        shots,
        f"Cenário 4: Nossa Proposta - {nome_cenario_4} (Qiskit)",
        str(FIGURES_DIR / "fig4_hardware_ataque_parcial.pdf"),
        cor="#ff9f43",
    )
    progress.advance(tarefa_qiskit)
    progress.update(
        tarefa_qiskit, description="[green]✔ IBM Qiskit Finalizado![/green]"
    )

    # --- Cenário 5 (Validação Google) ---
    if CIRQ_DISPONIVEL:
        tarefa_cirq = progress.add_task(
            "[blue]Validando resultados no Motor Google (Cirq)...", total=1
        )
        time.sleep(1.5)
        contagens_5 = simular_google_cirq_parcial(
            bits_alice, bases_alice, bases_bob, bases_eve_parcial, shots=shots
        )
        qber_5 = calcular_qber(contagens_5, estado_correto_str, shots)
        qbers.append(qber_5)
        cenarios_nomes.append("Ataque Parcial\n(Google Cirq)")
        plot_estilo_ieee(
            contagens_5,
            shots,
            "Cenário 5: Nossa Proposta Validada na Google (Cirq)",
            str(FIGURES_DIR / "fig5_google_cirq_parcial.pdf"),
            cor="#00d2d3",
        )
        progress.advance(tarefa_cirq)
        progress.update(
            tarefa_cirq, description="[green]✔ Google Cirq Finalizado![/green]"
        )

# %% [Geração do Gráfico Comparativo Final]
plt.figure(figsize=(11, 6))
cores_qber = ["#1dd1a1", "#ff6b6b", "#54a0ff", "#ff9f43", "#00d2d3"][: len(qbers)]
barras_qber = plt.bar(
    cenarios_nomes, qbers, color=cores_qber, edgecolor="black", width=0.5
)
plt.ylabel("Taxa de Erro Quântico (QBER) %", fontsize=12, fontweight="bold")
plt.title(
    "Validação Cross-Platform (QBER): Replicação vs IBM vs Google", fontsize=14, pad=15
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
plt.savefig(str(FIGURES_DIR / "fig6_diferencas_qber.pdf"), format="pdf", dpi=300)
plt.close()

# %% [Tabela de Resultados e Resumo Final]
console.rule("[bold blue]RESUMO ESTATÍSTICO DE COMPARAÇÃO CRUZADA[/bold blue]")

tabela_resumo = Table(show_header=True, header_style="bold yellow")
tabela_resumo.add_column("Cenário Analisado")
tabela_resumo.add_column("Origem / Framework")
tabela_resumo.add_column("QBER (%)", justify="right")

tabela_resumo.add_row(
    "1. Simulador Ideal (Sem Eve)", "IBM Qiskit", f"[green]{qber_1:.2f}%[/green]"
)
tabela_resumo.add_row(
    "2. Simulador Ideal (Ataque Total)", "IBM Qiskit", f"[red]{qber_2:.2f}%[/red]"
)
tabela_resumo.add_row(
    "3. Hardware NISQ (Ruído Natural)", "IBM Qiskit", f"[blue]{qber_3:.2f}%[/blue]"
)
tabela_resumo.add_row(
    "4. Hardware NISQ (Ataque Parcial)",
    "[bold magenta]Nossa Proposta (IBM)[/bold magenta]",
    f"[yellow]{qber_4:.2f}%[/yellow]",
)

if CIRQ_DISPONIVEL:
    tabela_resumo.add_row(
        "5. Ecossistema Google (Ataque Parcial)",
        "[bold cyan]Nossa Proposta (Google)[/bold cyan]",
        f"[cyan]{qber_5:.2f}%[/cyan]",
    )

console.print(tabela_resumo)
console.print(
    f"\n[bold green]✔ Todos os cálculos foram finalizados e salvos em {FIGURES_DIR}![/bold green]"
)
