AN ANALYSIS OF QKD BB84 PROTOCOL IMPLEMENTATION OVER REAL IBM QUANTUM PROCESSORS VS. SIMULATION (UMA ANÁLISE DA IMPLEMENTAÇÃO DO PROTOCOLO QKD BB84 EM PROCESSADORES QUÂNTICOS REAIS IBM VS. SIMULAÇÃO)

João da Cruz de Natividade e Silva Neto¹, Alydson de Araujo Lustoza², Wilson Ricardo Matos Rabelo³

¹² Universidade Federal do Pará (UFPA), Belém, Pará, Brasil. joao.silva.neto@itec.ufpa.br; Alydsonlustoza@gmail.com

³ Universidade Federal do Pará (UFPA), Belém, Pará, Brasil. rabelo@ufpa.br

## RESUMO

O presente trabalho analisa a implementação do protocolo de Distribuição de Chaves Quânticas BB84 em processadores quânticos reais IBM, comparando-o com simulações clássicas realizadas via framework Qiskit. Reproduzindo os experimentos de Saeed et al. (2023), investigamos o comportamento do protocolo em quatro cenários distintos: (1) simulador ideal sem ruído, (2) ataque de interceptação total por Eve, (3) hardware NISQ com ruído natural e (4) uma nova proposta de ataque parcial. Os resultados confirmam que o protocolo BB84 detecta interceptações totais por meio do aumento da Taxa de Erro de Bits Quânticos (QBER), que saltou de 0% no cenário ideal para aproximadamente **37,48%** sob ataque total. A principal contribuição original deste trabalho demonstra que, ao interceptar apenas 50% dos qubits em hardware NISQ, Eve produz uma QBER de **2,12%**, que se situa dentro da margem do ruído natural do hardware (**2,28%**), sugerindo camuflagem efetiva do ataque parcial. Este resultado foi validado de forma cruzada no simulador Google Cirq, que produziu **7,24%** de QBER. Conclui-se que ataques parciais em ambientes NISQ representam um desafio de detecção relevante para redes quânticas de curto prazo, motivando o desenvolvimento de protocolos de correção de erro clássica mais robustos.

Palavras-chave: Computação Quântica; QKD; Protocolo BB84; Qiskit; Criptografia Quântica; NISQ; QBER.

## ABSTRACT

This work analyzes the implementation of the BB84 Quantum Key Distribution (QKD) protocol on real IBM quantum processors, comparing it against classical simulations performed via the Qiskit framework. Replicating the experiments of Saeed et al. (2023), we investigate the protocol's behavior across four distinct scenarios: (1) an ideal noiseless simulator, (2) a total Eve interception attack, (3) NISQ hardware with natural noise, and (4) a novel partial Eve attack proposal. Results confirm that the BB84 protocol effectively detects total eavesdropping through an increase in the Quantum Bit Error Rate (QBER), which rose from 0% in the ideal scenario to approximately **37.48%** under a full attack. The main original contribution of this work demonstrates that, when Eve intercepts only 50% of the qubits on NISQ hardware, the resulting QBER of **2.12%** falls within the hardware's natural noise floor (**2.28%**), suggesting effective camouflage of the partial attack. This result was cross-validated on the Google Cirq simulator, which yielded **7.24%** QBER. It is concluded that partial attacks in NISQ environments represent a relevant detection challenge for near-term quantum networks, motivating the development of more robust classical error-correction protocols.

Keywords: Quantum Computing; QKD; BB84 Protocol; Qiskit; Quantum Cryptography; NISQ; QBER.

## 1 INTRODUÇÃO

A base da segurança da informação moderna está ancorada em problemas matemáticos complexos. Protocolos clássicos, como o RSA, confiam inteiramente na extrema dificuldade computacional de fatorar grandes números primos. O problema real surge com a iminência da computação quântica de larga escala: algoritmos como o de Shor provam matematicamente que computadores quânticos poderão quebrar essas chaves em tempo polinomial. É para solucionar essa vulnerabilidade fatal que a Distribuição de Chaves Quânticas (QKD - Quantum Key Distribution) ganha destaque. Em vez de depender de complexidade matemática, a QKD utiliza as leis fundamentais da física quântica para garantir uma segurança incondicional.

Este trabalho tem como objetivo central reproduzir e analisar a implementação proposta no artigo "An Analysis of QKD BB84 Protocol Implementation over Real IBM Quantum Processors vs. Simulation", de Saeed et al. (2023). Nossa proposta é demonstrar, na prática, como ocorre a troca de chaves criptográficas utilizando o protocolo BB84 e evidenciar como a presença de um interceptador (Eve) é naturalmente detectada pelo colapso da função de onda.

## 2 METODOLOGIA

Para colocar o experimento em prática e responder às questões estruturais da pesquisa, adotamos o ecossistema da IBM. Toda a nossa implementação foi desenvolvida na linguagem Python, utilizando o framework Qiskit, dispensando o uso de interfaces visuais arrastar-e-soltar, a fim de termos controle total sobre as lógicas de automação e medição.

O circuito base utilizado no experimento consiste em um registro de 4 qubits. O protocolo BB84 foi programado simulando três entidades: Alice (emissora), Bob (receptor) e Eve (espiã).

![[figures/fig0_circuito_bb84_base.pdf|Figura 1: Diagrama do circuito quântico base de 4 qubits gerado via Qiskit.]]

Para testar a resiliência do modelo, rodamos o experimento em múltiplos cenários, simulando o hardware perfeito e o processador quântico real da IBM Cloud com modelos de ruído NISQ. Para a nossa Nova Proposta, desenvolvemos um ataque tático onde Eve intercepta apenas 50% da transmissão (apenas nas linhas q0 e q1).

![[figures/fig4a_circuito_nossa_proposta.pdf|Figura 2: Diagrama do circuito evidenciando a interceptação parcial (Ataque nas linhas 0 e 1).]]

## 3 RESULTADOS E DISCUSSÃO

Ao executar nosso código no simulador clássico sem qualquer interferência externa, o comportamento da distribuição de chaves foi perfeito. A probabilidade de leitura correta do estado foi cravada em 100%.

![[figures/fig1_simulador_ideal.pdf|Figura 3: Cenário 1 - Distribuição de probabilidade perfeita em ambiente simulado ideal.]]

O cenário muda drasticamente quando forçamos a inserção de "Eve" no código com interceptação total. Devido ao Teorema da Não-Clonagem da mecânica quântica, a taxa de erro saltou de 0% para aproximadamente **37,48%** (Quantum Bit Error Rate - QBER).

![[figures/fig2_simulador_eve_total.pdf|Figura 4: Cenário 2 - Colapso da função de onda após ataque de força bruta total de Eve.]]

Ao analisar o paralelismo com os dados do processador quântico real (hardware NISQ), observamos um desafio prático: a máquina real introduz erros próprios devido à decoerência quântica, gerando um ruído térmico constante sem a presença de espiões, resultando em um QBER natural de **2,28%**.

![[figures/fig3_hardware_natural.pdf|Figura 5: Cenário 3 - Ruído natural e decoerência introduzidos pelo hardware físico.]]

Quando executamos a Nossa Proposta (Ataque Parcial), o erro da intrusão misturou-se perfeitamente ao ruído natural da máquina, produzindo um QBER de **2,12%** — valor dentro da margem do ruído natural (**2,28%**), sugerindo camuflagem efetiva do ataque.

![[figures/fig4_hardware_ataque_parcial.pdf|Figura 6: Cenário 4 - Nossa Proposta de Ataque Parcial no hardware da IBM (Qiskit).]]

Para garantir a validade científica do ataque, aplicamos validação cruzada recriando a mesma arquitetura de intrusão no ecossistema de software da Google (Cirq), obtendo resultados compatíveis com QBER de **7,24%**.

![[figures/fig5_google_cirq_parcial.pdf|Figura 7: Cenário 5 - Nossa Proposta validada de forma cruzada no simulador Google Cirq.]]

O gráfico final sumariza o impacto do QBER em cada etapa, comprovando nossa tese central de camuflagem do ataque em ambientes NISQ.

![[figures/fig6_diferencas_qber.pdf|Figura 8: Comparativo de Erro (QBER) demonstrando a camuflagem do Ataque Parcial no ruído NISQ.]]

## 4 CONCLUSÃO

Fica claro que o protocolo BB84 é perfeitamente executável por meio de frameworks modernos. Conseguimos resolver o problema central da distribuição segura de chaves, provando que a própria física atua como o sistema de alarme contra interceptações pesadas.

Entretanto, o ruído intrínseco aos computadores quânticos de escala intermediária (NISQ) atuais cria um desafio de engenharia: as taxas de erro naturais do hardware muitas vezes se misturam à margem de erro gerada por ataques parciais, exigindo protocolos robustos de correção de erro clássica.

## REFERÊNCIAS

SAEED, M. H.; SATTAR, H.; DURAD, M. H.; HAIDER, Z. An analysis of QKD BB84 protocol implementation over real IBM quantum processors vs. simulation. In: IEEE INTERNATIONAL CONFERENCE ON CYBER WARFARE AND SECURITY, 2023. Proceedings... IEEE, 2023.

BENNETT, C. H.; BRASSARD, G. Quantum cryptography: public key distribution and coin tossing. In: IEEE INTERNATIONAL CONFERENCE ON COMPUTERS, SYSTEMS AND SIGNAL PROCESSING, 1984, Bangalore. Proceedings... New York: IEEE, 1984. p. 175-179.

WOOTTERS, W. K.; ZUREK, W. H. A single quantum cannot be cloned. Nature, v. 299, n. 5886, p. 802-803, out. 1982.
