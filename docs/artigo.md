AN ANALYSIS OF QKD BB84 PROTOCOL IMPLEMENTATION OVER REAL IBM QUANTUM PROCESSORS VS. SIMULATION (UMA ANÁLISE DA IMPLEMENTAÇÃO DO PROTOCOLO QKD BB84 EM PROCESSADORES QUÂNTICOS REAIS IBM VS. SIMULAÇÃO)

INTRODUÇÃO

A base da segurança da informação moderna está ancorada em problemas matemáticos complexos. Protocolos clássicos, como o RSA, confiam inteiramente na extrema dificuldade computacional de fatorar grandes números primos. O problema real surge com a iminência da computação quântica de larga escala: algoritmos como o de Shor provam matematicamente que computadores quânticos poderão quebrar essas chaves em tempo polinomial. É para solucionar essa vulnerabilidade fatal que a Distribuição de Chaves Quânticas (QKD - Quantum Key Distribution) ganha destaque. Em vez de depender de complexidade matemática, a QKD utiliza as leis fundamentais da física quântica para garantir uma segurança incondicional.

Este trabalho tem como objetivo central reproduzir e analisar a implementação proposta no artigo "An Analysis of QKD BB84 Protocol Implementation over Real IBM Quantum Processors vs. Simulation" (Uma Análise da Implementação do Protocolo QKD BB84 em Processadores Quânticos Reais IBM vs. Simulação), de Saeed et al. (2023). Nossa proposta é demonstrar, na prática, como ocorre a troca de chaves criptográficas utilizando o protocolo BB84 e evidenciar como a presença de um interceptador (Eve) é naturalmente detectada pelo colapso da função de onda.

METODOLOGIA

Para colocar o experimento em prática e responder às questões estruturais da pesquisa, adotamos o ecossistema da IBM. Toda a nossa implementação foi desenvolvida na linguagem Python, utilizando o framework Qiskit, dispensando o uso de interfaces visuais arrastar-e-soltar como o IBM Quantum Composer, a fim de termos controle total sobre as lógicas de automação e medição.

O circuito base utilizado no experimento consiste em um registro de 4 qubits. O protocolo BB84 foi programado simulando três entidades: Alice (emissora), Bob (receptor) e Eve (espiã). O fluxo metodológico seguiu as seguintes etapas: (1) Codificação (Alice), onde Alice gera uma sequência aleatória de 4 bits; (2) Medição (Bob), onde Bob recebe os qubits e também aplica bases aleatórias para medi-los; e (3) Peneiramento (Sifting), onde Alice e Bob comparam publicamente quais bases usaram.

Para testar a resiliência do modelo, rodamos o experimento em dois cenários: localmente utilizando o simulador clássico do Qiskit, e submetendo o código a um processador quântico real da IBM Cloud com modelos de ruído NISQ. Para a nossa Nova Proposta, desenvolvemos um ataque tático onde Eve intercepta apenas 50% da transmissão.

![[figures/fig0_circuito_bb84_base.pdf|Figura 1: Diagrama do circuito quântico de 4 qubits gerado via Qiskit.]]

![[figures/fig4a_circuito_nossa_proposta.pdf|Figura 2: Diagrama do circuito evidenciando a interceptação parcial (Qubits 0 e 1).]]

RESULTADOS E DISCUSSÃO

Ao executar nosso código no simulador clássico sem qualquer interferência externa, o comportamento da distribuição de chaves foi perfeito. Quando comparamos as bases de Alice e Bob, a probabilidade de leitura correta do estado foi cravada, dividindo-se perfeitamente entre os estados esperados da chave.

O cenário muda drasticamente quando forçamos a inserção de "Eve" no código. Simulamos a espiã aplicando suas próprias bases de medição aleatórias e reenviando as partículas. Devido ao Teorema da Não-Clonagem da mecânica quântica, a taxa de erro nos bits que deveriam ser idênticos entre Alice e Bob saltou de 0% para aproximadamente 25% (Quantum Bit Error Rate - QBER). Essa alteração violenta na distribuição de probabilidade é a prova física de que a linha foi grampeada.

Ao analisar o paralelismo com os dados do processador quântico real (hardware NISQ), observamos um desafio prático: a máquina real introduz erros próprios devido à decoerência quântica. O chip físico gera um ruído de fundo entre 2% e 5%. Quando executamos a Nossa Proposta (Ataque Parcial), o erro da intrusão misturou-se ao ruído natural da máquina, provando um risco severo para redes quânticas não calibradas.

![[figures/fig6_diferencas_qber.pdf|Figura 3: Comparativo de Erro (QBER) demonstrando a camuflagem do Ataque Parcial no ruído NISQ.]]

CONCLUSÃO

Ao final da nossa implementação, fica claro que o protocolo BB84 não é apenas uma teoria elegante, mas uma ferramenta perfeitamente executável por meio de frameworks como o Qiskit e o Cirq. Conseguimos resolver o problema central da distribuição segura de chaves, provando que a própria física atua como o sistema de alarme contra interceptações.

Apesar do sucesso do experimento, a nossa execução restringiu-se a um registro de 4 qubits como prova de conceito. Além disso, o ruído intrínseco aos computadores quânticos de escala intermediária (NISQ) atuais cria um desafio de engenharia: as taxas de erro naturais do hardware muitas vezes se misturam à margem de erro que denotaria uma espionagem, exigindo a implementação de protocolos robustos de correção de erro.

REFERÊNCIAS

SAEED, M. H.; SATTAR, H.; DURAD, M. H.; HAIDER, Z. An Analysis of QKD BB84 Protocol Implementation over Real IBM Quantum Processors vs. Simulation. IEEE, 2023.

BENNETT, C. H.; BRASSARD, G. Quantum cryptography: Public key distribution and coin tossing. Proceedings of IEEE International Conference on Computers, Systems and Signal Processing, 1984.

WOOTTERS, W. K.; ZUREK, W. H. A single quantum cannot be cloned. Nature, vol. 299, no. 5886, pp. 802-803, 1982.