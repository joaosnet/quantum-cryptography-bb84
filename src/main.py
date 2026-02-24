# %% [markdown]
# # Implementação Avançada do Protocolo QKD BB84 - COBENGE
# Integração HÍBRIDA: IBM Quantum (Qiskit) + Google Quantum AI (Cirq)
# Módulo de Investigação Avançada: Escalabilidade e Micro-Ataques

# %% [Instalação e Verificação de Ambiente]
import subprocess
import sys

IN_COLAB = "google.colab" in sys.modules

if IN_COLAB:
    print("🌐 Detectado ambiente Google Colab! Instalando as dependências...")
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
else:
    print("💻 Detectado ambiente Local (Seu PC)!")

# %% [Importações e Configuração]
import getpass
import logging
import pathlib

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

logging.getLogger("qiskit_ibm_runtime").setLevel(logging.ERROR)

try:
    import cirq

    CIRQ_DISPONIVEL = True
except ImportError:
    CIRQ_DISPONIVEL = False

FIGURES_DIR = (
    pathlib.Path(__file__).parent.parent / "figures"
    if not IN_COLAB
    else pathlib.Path("/content/figures")
)
FIGURES_DIR.mkdir(exist_ok=True, parents=True)

console = Console()

# %% [Autenticação IBM Cloud]
console.print("\n[cyan]⚙️ Configuração do Ambiente de Execução[/cyan]")
USAR_HARDWARE_REAL_IBM = Confirm.ask(
    "[bold yellow]Deseja enviar a 'Nossa Proposta' para rodar no Hardware Físico Real da IBM na nuvem?[/bold yellow]",
    default=False,
)

backend_real_ibm = None

if USAR_HARDWARE_REAL_IBM:
    console.print("\n[yellow]🔒 Modo de Autenticação Segura Ativado...[/yellow]")
    MEU_TOKEN_IBM = getpass.getpass("🔑 Cole o seu Token da IBM Quantum aqui: ")

    with console.status(
        "[bold yellow]Conectando à matriz da IBM...[/bold yellow]", spinner="earth"
    ):
        service = QiskitRuntimeService(
            channel="ibm_quantum_platform", token=MEU_TOKEN_IBM
        )
        backend_real_ibm = service.least_busy(
            operational=True, simulator=False, min_num_qubits=4
        )
    console.print(
        f"[bold green]✔ Alvo fixado! Hardware: {backend_real_ibm.name}[/bold green]\n"
    )
else:
    console.print("[dim]Execução 100% local selecionada.[/dim]\n")


# %% [Funções Core do BB84]
def codificar_mensagem(bits, bases):
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
    n = len(bases_medicao)
    if qubits_alvo is None:
        qubits_alvo = range(n)
    for i in qubits_alvo:
        if bases_medicao[i] == 1:
            qc.h(i)
        qc.measure(i, i)
    return qc


def ataque_eve(qc, bases_eve, qubits_alvo=None):
    n = len(bases_eve)
    if qubits_alvo is None:
        qubits_alvo = range(n)
    for i in qubits_alvo:
        if bases_eve[i] == 1:
            qc.h(i)
        qc.measure(i, i)
        if bases_eve[i] == 1:
            qc.h(i)
    return qc


def criar_modelo_ruido_hardware():
    noise_model = NoiseModel()
    error_1q = depolarizing_error(0.05, 1)
    noise_model.add_all_qubit_quantum_error(error_1q, ["u1", "u2", "u3", "x", "h"])
    return noise_model


def simular_circuito(qc, shots=4096, usar_ruido=False, forcado_na_ibm=False):
    if forcado_na_ibm and backend_real_ibm is not None:
        circuito_compilado = transpile(qc, backend_real_ibm)
        sampler = SamplerV2(mode=backend_real_ibm)
        sampler.options.default_shots = shots
        job = sampler.run([circuito_compilado])
        resultado = job.result()
        creg_name = circuito_compilado.cregs[0].name
        return getattr(resultado[0].data, creg_name).get_counts()
    else:
        simulador = AerSimulator(
            noise_model=criar_modelo_ruido_hardware() if usar_ruido else None
        )
        circuito_compilado = transpile(qc, simulador)
        return simulador.run(circuito_compilado, shots=shots).result().get_counts()


def calcular_qber(contagens, estado_correto, shots):
    total_bits = 0
    erros_bits = 0
    for estado, contagem in contagens.items():
        total_bits += len(estado_correto) * contagem
        for bit_medido, bit_correto in zip(estado, estado_correto):
            if bit_medido != bit_correto:
                erros_bits += contagem
    return (erros_bits / total_bits) * 100


def simular_google_cirq_parcial(bits_a, bases_a, bases_b, bases_e, shots=4096):
    qubits = cirq.LineQubit.range(4)
    circuito = cirq.Circuit()
    for i in range(4):
        if bits_a[i] == 1:
            circuito.append(cirq.X(qubits[i]))
        if bases_a[i] == 1:
            circuito.append(cirq.H(qubits[i]))
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
    ruido = cirq.depolarize(p=0.05)
    resultado = cirq.Simulator().run(circuito.with_noise(ruido), repetitions=shots)
    contagens = {}
    for i in range(shots):
        bit_string = "".join([
            str(resultado.measurements[f"bob_{q}"][i][0]) for q in [3, 2, 1, 0]
        ])
        contagens[bit_string] = contagens.get(bit_string, 0) + 1
    return contagens


def plot_estilo_ieee(contagens, shots, titulo, nome_ficheiro, cor="#6495ED"):
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
    plt.ylim(0, min(max(valores) + 0.15, 1.1))
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    for barra in barras:
        if (yval := barra.get_height()) > 0.005:
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


# %% [Módulo 1: Experimento Clássico 4 Qubits]
n_qubits = 4
shots = 4096
bits_alice = [1, 0, 1, 0]
bases_compartilhadas = [1, 0, 1, 0]
estado_correto_str = "".join(map(str, reversed(bits_alice)))

qbers = []
cenarios_nomes = []

console.print(
    "\n[bold yellow]Iniciando Fase 1: Replicação IEEE e Ataque Parcial...[/bold yellow]"
)
with console.status("[cyan]Processando Tensores (4 Qubits)...[/cyan]", spinner="dots"):
    # 1. Ideal
    qc1 = medir_mensagem(
        codificar_mensagem(bits_alice, bases_compartilhadas), bases_compartilhadas
    )
    qc1.draw("mpl").savefig(
        str(FIGURES_DIR / "fig0_circuito_bb84_base.pdf"),
        format="pdf",
        bbox_inches="tight",
        dpi=300,
    )
    contagens_1 = simular_circuito(qc1, shots, usar_ruido=False)
    qbers.append(calcular_qber(contagens_1, estado_correto_str, shots))
    cenarios_nomes.append("Ideal")
    plot_estilo_ieee(
        contagens_1,
        shots,
        "Cenário 1: Simulador Ideal",
        str(FIGURES_DIR / "fig1_simulador_ideal.pdf"),
    )

    # 2. Total
    qc_eve_total = medir_mensagem(
        ataque_eve(
            codificar_mensagem(bits_alice, bases_compartilhadas),
            np.random.randint(2, size=n_qubits),
        ),
        bases_compartilhadas,
    )
    contagens_2 = simular_circuito(qc_eve_total, shots, usar_ruido=False)
    qbers.append(calcular_qber(contagens_2, estado_correto_str, shots))
    cenarios_nomes.append("Eve Total")
    plot_estilo_ieee(
        contagens_2,
        shots,
        "Cenário 2: Interceptação Total",
        str(FIGURES_DIR / "fig2_simulador_eve_total.pdf"),
        cor="#ff6b6b",
    )

    # 3. Ruído NISQ
    contagens_3 = simular_circuito(qc1, shots, usar_ruido=True)
    qbers.append(calcular_qber(contagens_3, estado_correto_str, shots))
    cenarios_nomes.append("Hardware Ruído")
    plot_estilo_ieee(
        contagens_3,
        shots,
        "Cenário 3: Hardware Quântico NISQ",
        str(FIGURES_DIR / "fig3_hardware_natural.pdf"),
    )

    # 4. Proposta (Parcial 50%)
    bases_eve_parcial = np.random.randint(2, size=n_qubits)
    qc_proposta = medir_mensagem(
        ataque_eve(
            codificar_mensagem(bits_alice, bases_compartilhadas),
            bases_eve_parcial,
            [0, 1],
        ),
        bases_compartilhadas,
    )
    qc_proposta.draw("mpl").savefig(
        str(FIGURES_DIR / "fig4a_circuito_nossa_proposta.pdf"),
        format="pdf",
        bbox_inches="tight",
        dpi=300,
    )
    contagens_4 = simular_circuito(
        qc_proposta,
        shots,
        usar_ruido=not USAR_HARDWARE_REAL_IBM,
        forcado_na_ibm=USAR_HARDWARE_REAL_IBM,
    )
    qbers.append(calcular_qber(contagens_4, estado_correto_str, shots))
    cenarios_nomes.append("Ataque Parcial")
    plot_estilo_ieee(
        contagens_4,
        shots,
        "Cenário 4: Nossa Proposta (Ataque Parcial)",
        str(FIGURES_DIR / "fig4_hardware_ataque_parcial.pdf"),
        cor="#ff9f43",
    )

    # 5. Cirq
    if CIRQ_DISPONIVEL:
        contagens_5 = simular_google_cirq_parcial(
            bits_alice,
            bases_compartilhadas,
            bases_compartilhadas,
            bases_eve_parcial,
            shots=shots,
        )
        qbers.append(calcular_qber(contagens_5, estado_correto_str, shots))
        cenarios_nomes.append("Google Cirq")
        plot_estilo_ieee(
            contagens_5,
            shots,
            "Cenário 5: Google Cirq",
            str(FIGURES_DIR / "fig5_google_cirq_parcial.pdf"),
            cor="#00d2d3",
        )

plt.figure(figsize=(11, 6))
cores = ["#1dd1a1", "#ff6b6b", "#54a0ff", "#ff9f43", "#00d2d3"][: len(qbers)]
barras = plt.bar(cenarios_nomes, qbers, color=cores, edgecolor="black", width=0.5)
plt.title("Validação Cross-Platform (4 Qubits)", fontsize=14, pad=15)
plt.ylabel("QBER %")
plt.ylim(0, max(qbers) + 10)
for b in barras:
    plt.text(
        b.get_x() + b.get_width() / 2,
        b.get_height() + 1,
        f"{b.get_height():.2f}%",
        ha="center",
        va="bottom",
        fontweight="bold",
    )
plt.tight_layout()
plt.savefig(str(FIGURES_DIR / "fig6_diferencas_qber.pdf"), format="pdf")
plt.close()

# %% [Módulo 2: Investigação Avançada - Escala e Micro-Ataques]
console.print(
    "\n[bold magenta]Iniciando Fase 2: Testes de Escala (16 Qubits) e Micro-Ataques...[/bold magenta]"
)


def exp_escala(n, q_atacados):
    """Simulador dinâmico focado exclusivamente em QBER para canais largos"""
    b_alice = np.random.randint(2, size=n)
    bases = np.random.randint(2, size=n)
    estado_c = "".join(map(str, reversed(b_alice)))

    qc = codificar_mensagem(b_alice, bases)
    if q_atacados > 0:
        b_eve = np.random.randint(2, size=n)
        qc = ataque_eve(qc, b_eve, range(q_atacados))  # Ataca os primeiros X qubits
    qc = medir_mensagem(qc, bases)

    # Roda com ruído
    simulador = AerSimulator(noise_model=criar_modelo_ruido_hardware())
    contagens = (
        simulador.run(transpile(qc, simulador), shots=shots).result().get_counts()
    )
    return calcular_qber(contagens, estado_c, shots)


with console.status(
    "[magenta]Processando Tensores Profundos (16 Qubits)...[/magenta]", spinner="dots"
):
    n_largo = 16

    # Teste A: Só ruído natural (16 Qubits)
    qber_largo_ruido = exp_escala(n_largo, 0)

    # Teste B: Ataque Parcial Proporcional (Eve ataca 50% = 8 Qubits)
    qber_largo_50 = exp_escala(n_largo, 8)

    # Teste C: MICRO-ATAQUE (Eve ataca apenas 2 Qubits = 12.5% da rede)
    qber_micro = exp_escala(n_largo, 2)

# Gráfico da Investigação Avançada
cenarios_adv = [
    "Apenas Ruído NISQ\n(16 Qubits)",
    "Micro-Ataque (12.5%)\nCamuflagem Perfeita",
    "Limiar de Aborto\nProtocolo BB84",
    "Ataque Proporcional\n(50%)",
]
valores_adv = [qber_largo_ruido, qber_micro, 11.0, qber_largo_50]

plt.figure(figsize=(10, 6))
cores_adv = ["#54a0ff", "#ff9f43", "#dc2626", "#ff6b6b"]
barras_adv = plt.bar(
    cenarios_adv, valores_adv, color=cores_adv, edgecolor="black", width=0.5
)

# Linha da morte (11%)
plt.axhline(
    y=11.0, color="red", linestyle="--", linewidth=2, label="Limiar Crítico (11%)"
)

plt.ylabel("Taxa de Erro Quântico (QBER) %", fontsize=12, fontweight="bold")
plt.title(
    "Análise de Escalabilidade e Micro-Ataques em Hardware NISQ (16 Qubits)",
    fontsize=14,
    pad=15,
)
plt.ylim(0, max(valores_adv) + 5)
plt.legend()

for i, b in enumerate(barras_adv):
    if i != 2:  # Pula a barra fake do limiar
        plt.text(
            b.get_x() + b.get_width() / 2,
            b.get_height() + 0.5,
            f"{b.get_height():.2f}%",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

plt.tight_layout()
plt.savefig(str(FIGURES_DIR / "fig7_escala_microataque.pdf"), format="pdf", dpi=300)
plt.close()

# %% [Tabela de Resultados e Resumo Final]
console.rule("[bold blue]RESUMO ESTATÍSTICO GLOBAL[/bold blue]")
t_res = Table(show_header=True, header_style="bold yellow")
t_res.add_column("Cenário", style="cyan")
t_res.add_column("QBER (%)", justify="right")
t_res.add_row("1. Ideal (4q)", f"{qbers[0]:.2f}%")
t_res.add_row("2. Eve Total (4q)", f"{qbers[1]:.2f}%")
t_res.add_row("3. Ruído NISQ (4q)", f"{qbers[2]:.2f}%")
t_res.add_row("4. Ataque Parcial 50% (4q)", f"{qbers[3]:.2f}%")
t_res.add_row("---", "---")
t_res.add_row("A. Ruído NISQ (16q)", f"{qber_largo_ruido:.2f}%")
t_res.add_row(
    "B. Micro-Ataque 12.5% (16q) [CAMUFLADO]",
    f"[bold green]{qber_micro:.2f}%[/bold green]",
)
t_res.add_row("C. Limiar de Alarme BB84", "[bold red]11.00%[/bold red]")
console.print(t_res)

console.print(
    "\n[bold green]✔ Pipeline concluído. Novo gráfico 'fig7_escala_microataque.pdf' gerado![/bold green]"
)

# %%