AN ANALYSIS OF QKD BB84 PROTOCOL IMPLEMENTATION OVER REAL IBM QUANTUM PROCESSORS VS. SIMULATION (UMA ANÁLISE DA IMPLEMENTAÇÃO DO PROTOCOLO QKD BB84 EM PROCESSADORES QUÂNTICOS REAIS IBM VS. SIMULAÇÃO)

João da Cruz de Natividade e Silva Neto¹, Alydson de Araujo Lustoza²

¹² Universidade Federal do Pará (UFPA), Belém, Pará, Brasil. joao.silva.neto@itec.ufpa.br; Alydsonlustoza@gmail.com

## RESUMO

O presente trabalho analisa a implementação do protocolo de Distribuição de Chaves Quânticas BB84 em processadores quânticos reais IBM, comparando-o com simulações clássicas realizadas via framework Qiskit. Reproduzindo os experimentos de Saeed et al. (2023), investigamos o comportamento do protocolo em quatro cenários distintos: (1) simulador ideal sem ruído, (2) ataque de interceptação total por Eve, (3) hardware NISQ com ruído natural e (4) uma nova proposta de ataque parcial. Os resultados confirmam que o protocolo BB84 detecta interceptações totais por meio do aumento da Taxa de Erro de Bits Quânticos (QBER), que saltou de 0% no cenário ideal para aproximadamente **37,48%** sob ataque total. A principal contribuição original deste trabalho demonstra que, ao interceptar apenas 50% dos qubits em hardware NISQ, Eve produz uma QBER de **2,12%**, que se situa dentro da margem do ruído natural do hardware (**2,28%**), sugerindo camuflagem efetiva do ataque parcial. Este resultado foi validado de forma cruzada no simulador Google Cirq, que produziu **7,24%** de QBER. Conclui-se que ataques parciais em ambientes NISQ representam um desafio de detecção relevante para redes quânticas de curto prazo, motivando o desenvolvimento de protocolos de correção de erro clássica mais robustos.

Palavras-chave: Computação Quântica; QKD; Protocolo BB84; Qiskit; Criptografia Quântica; NISQ; QBER.

## ABSTRACT

This work analyzes the implementation of the BB84 Quantum Key Distribution (QKD) protocol on real IBM quantum processors, comparing it against classical simulations performed via the Qiskit framework. Replicating the experiments of Saeed et al. (2023), we investigate the protocol's behavior across four distinct scenarios: (1) an ideal noiseless simulator, (2) a total Eve interception attack, (3) NISQ hardware with natural noise, and (4) a novel partial Eve attack proposal. Results confirm that the BB84 protocol effectively detects total eavesdropping through an increase in the Quantum Bit Error Rate (QBER), which rose from 0% in the ideal scenario to approximately **37.48%** under a full attack. The main original contribution of this work demonstrates that, when Eve intercepts only 50% of the qubits on NISQ hardware, the resulting QBER of **2.12%** falls within the hardware's natural noise floor (**2.28%**), suggesting effective camouflage of the partial attack. This result was cross-validated on the Google Cirq simulator, which yielded **7.24%** QBER. It is concluded that partial attacks in NISQ environments represent a relevant detection challenge for near-term quantum networks, motivating the development of more robust classical error-correction protocols.

Keywords: Quantum Computing; QKD; BB84 Protocol; Qiskit; Quantum Cryptography; NISQ; QBER.

## 1 INTRODUÇÃO

A base da segurança da informação moderna está ancorada em problemas matemáticos complexos. Protocolos clássicos, como o RSA, confiam inteiramente na extrema dificuldade computacional de fatorar grandes números primos. O problema real surge com a iminência da computação quântica de larga escala: algoritmos como o de Shor provam matematicamente que computadores quânticos poderão quebrar essas chaves em tempo polinomial. É para solucionar essa vulnerabilidade fatal que a Distribuição de Chaves Quânticas (QKD - Quantum Key Distribution) ganha destaque. Em vez de depender de complexidade matemática, a QKD utiliza as leis fundamentais da física quântica para garantir uma segurança incondicional.

Este trabalho tem como objetivo central reproduzir e analisar a implementação proposta no artigo "An Analysis of QKD BB84 Protocol Implementation over Real IBM Quantum Processors vs. Simulation", de Saeed et al. (2023). Nossa proposta é demonstrar, na prática, como ocorre a troca de chaves criptográficas utilizando o protocolo BB84 e evidenciar como a presença de um interceptador (Eve) é naturalmente detectada pelo colapso da função de onda.

## 2 FUNDAMENTAÇÃO TEÓRICA

Para compreender o funcionamento do protocolo BB84, é necessário estabelecer os fundamentos físico-quânticos que o sustentam. Ao contrário do bit clássico, que assume o valor 0 ou 1 de forma determinística, o qubit pode existir em superposição de ambos os estados simultaneamente, representado pelo estado geral $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$, onde $\alpha$ e $\beta$ são amplitudes complexas que satisfazem $|\alpha|^2 + |\beta|^2 = 1$. Apenas no momento da medição o estado colapsa irreversivelmente para um dos valores clássicos, com probabilidades $|\alpha|^2$ e $|\beta|^2$, respectivamente.

O protocolo BB84 fundamenta-se na existência de duas bases de medição mutuamente não-ortogonais. A base retilínea ($+$) utiliza os estados computacionais $\{|0\rangle, |1\rangle\}$, enquanto a base diagonal ($\times$) utiliza os estados superpostos $\{|{+}\rangle, |{-}\rangle\}$, onde $|{+}\rangle = (|0\rangle + |1\rangle)/\sqrt{2}$ e $|{-}\rangle = (|0\rangle - |1\rangle)/\sqrt{2}$. A transição entre essas duas bases é realizada pela porta Hadamard (H): aplicada sobre $|0\rangle$, produz $|{+}\rangle$; aplicada sobre $|1\rangle$, produz $|{-}\rangle$; e, inversamente, aplicada sobre um estado da base diagonal, devolve o estado computacional correspondente. Quando Bob mede um qubit em uma base diferente da usada por Alice para codificá-lo, o resultado é completamente aleatório, com **50%** de probabilidade de erro.

A segurança do protocolo baseia-se em dois pilares da mecânica quântica. O Teorema da Não-Clonagem, demonstrado por Wootters e Zurek (1982), estabelece que é impossível criar uma cópia perfeita de um estado quântico desconhecido sem perturbá-lo. Complementarmente, o Princípio da Incerteza de Heisenberg garante que a tentativa de medir o estado de um qubit em uma base qualquer perturba irreversivelmente sua informação na base conjugada. Em conjunto, esses dois princípios tornam qualquer tentativa de interceptação fisicamente detectável: ao tentar medir os qubits em trânsito, Eve inevitavelmente altera seus estados, introduzindo erros mensuráveis na chave final.

O protocolo BB84 implementado em circuito quântico opera em quatro etapas. Na preparação, Alice inicializa $n$ registradores quânticos e clássicos. Cada bit clássico da sua chave secreta é codificado como qubit: o valor 0 é mapeado para o estado $|0\rangle$ e o valor 1 para o estado $|1\rangle$. Em seguida, portas Hadamard são aplicadas aleatoriamente em aproximadamente 50% dos qubits, transferindo-os da base retilínea para a base diagonal e compondo a sequência de bases de Alice. Na interceptação, o circuito de Eve insere medições em bases escolhidas aleatoriamente. Essa operação é fisicamente irreversível: ao medir, Eve força o colapso da função de onda, destruindo a superposição original. Como consequência direta do Teorema da Não-Clonagem e do Princípio da Incerteza, Eve não pode copiar os estados antes de medi-los tampouco restaurá-los ao estado original após a medição, tornando sua presença detectável por meio do aumento da QBER. Na medição, Bob aplica portas Hadamard nos qubits onde decidiu usar a base diagonal. Todos os qubits passam então por operadores de medição, colapsando os estados quânticos em bits clássicos armazenados nos registradores. Por fim, na reconciliação, Alice e Bob comparam publicamente as bases que utilizaram, via canal clássico autenticado. Os bits cujas bases não coincidem são descartados (processo de sifting), pois não carregam informação confiável. A taxa de erro dos bits restantes é calculada como a QBER; se esse valor ultrapassar o limiar estabelecido (neste trabalho, adotamos **0,11**, ou seja, **11%**), conclui-se que o canal foi comprometido, o circuito é descartado e o processo reiniciado desde o início. Caso contrário, os bits sobreviventes ao sifting formam a chave criptográfica compartilhada.

## 3 METODOLOGIA

Para colocar o experimento em prática e responder às questões estruturais da pesquisa, adotamos o ecossistema da IBM. Toda a nossa implementação foi desenvolvida na linguagem Python, utilizando o framework Qiskit, dispensando o uso de interfaces visuais arrastar-e-soltar, a fim de termos controle total sobre as lógicas de automação e medição.

O circuito base utilizado no experimento consiste em um registro de 4 qubits. O protocolo BB84 foi programado simulando três entidades: Alice (emissora), Bob (receptor) e Eve (espiã).

![[figures/fig0_circuito_bb84_base.pdf|Figura 1: Diagrama do circuito quântico base de 4 qubits gerado via Qiskit.]]

Para testar a resiliência do modelo, rodamos o experimento em múltiplos cenários, simulando o hardware perfeito e o processador quântico real da IBM Cloud com modelos de ruído NISQ. Para a nossa Nova Proposta, desenvolvemos um ataque tático onde Eve intercepta apenas 50% da transmissão (apenas nas linhas q0 e q1).

![[figures/fig4a_circuito_nossa_proposta.pdf|Figura 2: Diagrama do circuito evidenciando a interceptação parcial (Ataque nas linhas 0 e 1).]]

## 4 RESULTADOS E DISCUSSÃO

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

## 5 CONCLUSÃO

Fica claro que o protocolo BB84 é perfeitamente executável por meio de frameworks modernos. Conseguimos resolver o problema central da distribuição segura de chaves, provando que a própria física atua como o sistema de alarme contra interceptações pesadas.

Entretanto, o ruído intrínseco aos computadores quânticos de escala intermediária (NISQ) atuais cria um desafio de engenharia: as taxas de erro naturais do hardware muitas vezes se misturam à margem de erro gerada por ataques parciais, exigindo protocolos robustos de correção de erro clássica.

## REFERÊNCIAS

SAEED, M. H.; SATTAR, H.; DURAD, M. H.; HAIDER, Z. An analysis of QKD BB84 protocol implementation over real IBM quantum processors vs. simulation. In: IEEE INTERNATIONAL CONFERENCE ON CYBER WARFARE AND SECURITY, 2023. Proceedings... IEEE, 2023.

BENNETT, C. H.; BRASSARD, G. Quantum cryptography: public key distribution and coin tossing. In: IEEE INTERNATIONAL CONFERENCE ON COMPUTERS, SYSTEMS AND SIGNAL PROCESSING, 1984, Bangalore. Proceedings... New York: IEEE, 1984. p. 175-179.

WOOTTERS, W. K.; ZUREK, W. H. A single quantum cannot be cloned. Nature, v. 299, n. 5886, p. 802-803, out. 1982.
