AN ANALYSIS OF QKD BB84 PROTOCOL IMPLEMENTATION OVER REAL IBM QUANTUM PROCESSORS VS. SIMULATION (UMA ANÁLISE DA IMPLEMENTAÇÃO DO PROTOCOLO QKD BB84 EM PROCESSADORES QUÂNTICOS REAIS IBM VS. SIMULAÇÃO)

INTRODUÇÃO

A base da segurança da informação moderna está ancorada em problemas matemáticos complexos. Protocolos clássicos, como o RSA, confiam inteiramente na extrema dificuldade computacional de fatorar grandes números primos. O problema real surge com a iminência da computação quântica de larga escala: algoritmos como o de Shor provam matematicamente que computadores quânticos poderão quebrar essas chaves em tempo polinomial. É para solucionar essa vulnerabilidade fatal que a Distribuição de Chaves Quânticas (QKD - Quantum Key Distribution) ganha destaque. Em vez de depender de complexidade matemática, a QKD utiliza as leis fundamentais da física quântica para garantir uma segurança incondicional.

Este trabalho tem como objetivo central reproduzir e analisar a implementação proposta no artigo "An Analysis of QKD BB84 Protocol Implementation over Real IBM Quantum Processors vs. Simulation", de Saeed et al. (2023). Nossa proposta é demonstrar, na prática, como ocorre a troca de chaves criptográficas utilizando o protocolo BB84 e evidenciar como a presença de um interceptador (Eve) é naturalmente detectada pelo colapso da função de onda.

METODOLOGIA

Para colocar o experimento em prática e responder às questões estruturais da pesquisa, adotamos o ecossistema da IBM. Toda a nossa implementação foi desenvolvida na linguagem Python, utilizando o framework Qiskit, dispensando o uso de interfaces visuais arrastar-e-soltar, a fim de termos controle total sobre as lógicas de automação e medição.

O circuito base utilizado no experimento consiste em um registro de 4 qubits. O protocolo BB84 foi programado simulando três entidades: Alice (emissora), Bob (receptor) e Eve (espiã).

![[figures/fig0_circuito_bb84_base.pdf|Figura 1: Diagrama do circuito quântico base de 4 qubits gerado via Qiskit.]]

Para testar a resiliência do modelo, rodamos o experimento em múltiplos cenários, simulando o hardware perfeito e o processador quântico real da IBM Cloud com modelos de ruído NISQ. Para a nossa Nova Proposta, desenvolvemos um ataque tático onde Eve intercepta apenas 50% da transmissão (apenas nas linhas q0 e q1).

![[figures/fig4a_circuito_nossa_proposta.pdf|Figura 2: Diagrama do circuito evidenciando a interceptação parcial (Ataque nas linhas 0 e 1).]]

RESULTADOS E DISCUSSÃO

Ao executar nosso código no simulador clássico sem qualquer interferência externa, o comportamento da distribuição de chaves foi perfeito. A probabilidade de leitura correta do estado foi cravada em 100%.

![[figures/fig1_simulador_ideal.pdf|Figura 3: Cenário 1 - Distribuição de probabilidade perfeita em ambiente simulado ideal.]]

O cenário muda drasticamente quando forçamos a inserção de "Eve" no código com interceptação total. Devido ao Teorema da Não-Clonagem da mecânica quântica, a taxa de erro saltou de 0% para aproximadamente 25% (Quantum Bit Error Rate - QBER).

![[figures/fig2_simulador_eve_total.pdf|Figura 4: Cenário 2 - Colapso da função de onda após ataque de força bruta total de Eve.]]

Ao analisar o paralelismo com os dados do processador quântico real (hardware NISQ), observamos um desafio prático: a máquina real introduz erros próprios devido à decoerência quântica, gerando um ruído térmico constante sem a presença de espiões.

![[figures/fig3_hardware_natural.pdf|Figura 5: Cenário 3 - Ruído natural e decoerência introduzidos pelo hardware físico.]]

Quando executamos a Nossa Proposta (Ataque Parcial), o erro da intrusão misturou-se perfeitamente ao ruído natural da máquina.

![[figures/fig4_hardware_ataque_parcial.pdf|Figura 6: Cenário 4 - Nossa Proposta de Ataque Parcial no hardware da IBM (Qiskit).]]

Para garantir a validade científica do ataque, aplicamos validação cruzada recriando a mesma arquitetura de intrusão no ecossistema de software da Google (Cirq), obtendo resultados compatíveis.

![[figures/fig5_google_cirq_parcial.pdf|Figura 7: Cenário 5 - Nossa Proposta validada de forma cruzada no simulador Google Cirq.]]

O gráfico final sumariza o impacto do QBER em cada etapa, comprovando nossa tese central de camuflagem do ataque em ambientes NISQ.

![[figures/fig6_diferencas_qber.pdf|Figura 8: Comparativo de Erro (QBER) demonstrando a camuflagem do Ataque Parcial no ruído NISQ.]]

CONCLUSÃO

Fica claro que o protocolo BB84 é perfeitamente executável por meio de frameworks modernos. Conseguimos resolver o problema central da distribuição segura de chaves, provando que a própria física atua como o sistema de alarme contra interceptações pesadas.

Entretanto, o ruído intrínseco aos computadores quânticos de escala intermediária (NISQ) atuais cria um desafio de engenharia: as taxas de erro naturais do hardware muitas vezes se misturam à margem de erro gerada por ataques parciais, exigindo protocolos robustos de correção de erro clássica.

REFERÊNCIAS

SAEED, M. H.; SATTAR, H.; DURAD, M. H.; HAIDER, Z. An Analysis of QKD BB84 Protocol Implementation over Real IBM Quantum Processors vs. Simulation. IEEE, 2023.

BENNETT, C. H.; BRASSARD, G. Quantum cryptography: Public key distribution and coin tossing. Proceedings of IEEE International Conference on Computers, Systems and Signal Processing, 1984.

WOOTTERS, W. K.; ZUREK, W. H. A single quantum cannot be cloned. Nature, vol. 299, no. 5886, pp. 802-803, 1982.