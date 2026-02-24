AN ANALYSIS OF QKD BB84 PROTOCOL IMPLEMENTATION OVER REAL IBM QUANTUM PROCESSORS VS. SIMULATION (UMA ANÁLISE DA IMPLEMENTAÇÃO DO PROTOCOLO QKD BB84 EM PROCESSADORES QUÂNTICOS REAIS IBM VS. SIMULAÇÃO)

João da Cruz de Natividade e Silva Neto¹, Alydson de Araujo Lustoza²

¹² Universidade Federal do Pará (UFPA), Belém, Pará, Brasil. joao.silva.neto@itec.ufpa.br; Alydsonlustoza@gmail.com

## RESUMO

O presente trabalho analisa a implementação do protocolo de Distribuição de Chaves Quânticas BB84 em processadores quânticos reais IBM, comparando-o com simulações clássicas realizadas via framework Qiskit. Reproduzindo os experimentos de Saeed et al. (2023), investigamos o comportamento do protocolo em quatro cenários distintos: (1) simulador ideal sem ruído, (2) ataque de interceptação total por Eve, (3) hardware NISQ com ruído natural e (4) uma nova proposta de ataque parcial. Os resultados confirmam que o protocolo BB84 detecta interceptações totais por meio do aumento da Taxa de Erro de Bits Quânticos (QBER), que saltou de 0% no cenário ideal para aproximadamente **25,32%** sob ataque total — muito acima do limiar crítico de 11%. O hardware NISQ com ruído natural produz uma QBER de **2,42%**. O ataque parcial de 50% dos qubits eleva a QBER para **14,36%**, ainda acima do limiar de detecção; resultado validado de forma cruzada no simulador Google Cirq, que produziu **15,89%** de QBER. A principal contribuição original deste trabalho é demonstrada na análise de escalabilidade com 16 qubits: um micro-ataque cirúrgico de **12,5%** dos qubits produz uma QBER de apenas **5,49%**, abaixo do limiar de 11%, alcançando camuflagem efetiva dentro do ruído natural do hardware NISQ. Conclui-se que micro-ataques cirúrgicos em ambientes NISQ representam um desafio de detecção crítico para redes quânticas de curto prazo, motivando o desenvolvimento de protocolos de reconciliação de informação e correção de erro clássica mais robustos.

Palavras-chave: Computação Quântica; QKD; Protocolo BB84; Qiskit; Criptografia Quântica; NISQ; QBER.

## ABSTRACT

This work analyzes the implementation of the BB84 Quantum Key Distribution (QKD) protocol on real IBM quantum processors, comparing it against classical simulations performed via the Qiskit framework. Replicating the experiments of Saeed et al. (2023), we investigate the protocol's behavior across four distinct scenarios: (1) an ideal noiseless simulator, (2) a total Eve interception attack, (3) NISQ hardware with natural noise, and (4) a novel partial Eve attack proposal. Results confirm that the BB84 protocol effectively detects total eavesdropping through an increase in the Quantum Bit Error Rate (QBER), which rose from 0% in the ideal scenario to approximately **25.32%** under a full attack — well above the critical 11% threshold. NISQ hardware with natural noise produces a QBER of **2.42%**. The 50% partial qubit attack raises the QBER to **14.36%**, still above the detection threshold; this result was cross-validated on the Google Cirq simulator, which yielded **15.89%** QBER. The main original contribution of this work is demonstrated in the 16-qubit scalability analysis: a surgical micro-attack on **12.5%** of qubits produces a QBER of only **5.49%**, below the 11% threshold, achieving effective camouflage within the natural noise floor of NISQ hardware. It is concluded that surgical micro-attacks in NISQ environments represent a critical detection challenge for near-term quantum networks, motivating the development of more robust information reconciliation and classical error-correction protocols.

Keywords: Quantum Computing; QKD; BB84 Protocol; Qiskit; Quantum Cryptography; NISQ; QBER.

## 1 INTRODUÇÃO

A base da segurança da informação moderna está ancorada em problemas matemáticos complexos. Protocolos clássicos, como o RSA, confiam inteiramente na extrema dificuldade computacional de fatorar grandes números primos. O problema real surge com a iminência da computação quântica de larga escala: algoritmos como o de Shor provam matematicamente que computadores quânticos poderão quebrar essas chaves em tempo polinomial. É para solucionar essa vulnerabilidade fatal que a Distribuição de Chaves Quânticas (QKD - Quantum Key Distribution) ganha destaque. Em vez de depender de complexidade matemática, a QKD utiliza as leis fundamentais da física quântica para garantir uma segurança incondicional.

Este trabalho tem como objetivo central reproduzir e analisar a implementação proposta no artigo "An Analysis of QKD BB84 Protocol Implementation over Real IBM Quantum Processors vs. Simulation", de Saeed et al. (2023). Nossa proposta é demonstrar, na prática, como ocorre a troca de chaves criptográficas utilizando o protocolo BB84 e evidenciar como a presença de um interceptador (Eve) é naturalmente detectada pelo colapso da função de onda. Como contribuição original, investigamos os limites dessa detecção ao escalar o experimento para 16 qubits e aplicar um micro-ataque cirúrgico que se camufla no ruído natural do hardware NISQ.

## 2 FUNDAMENTAÇÃO TEÓRICA

Para compreender o funcionamento do protocolo BB84, é necessário estabelecer os fundamentos físico-quânticos que o sustentam. Ao contrário do bit clássico, que assume o valor 0 ou 1 de forma determinística, o qubit pode existir em superposição de ambos os estados simultaneamente, representado pelo estado geral $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$, onde $\alpha$ e $\beta$ são amplitudes complexas que satisfazem $|\alpha|^2 + |\beta|^2 = 1$. Apenas no momento da medição o estado colapsa irreversivelmente para um dos valores clássicos, com probabilidades $|\alpha|^2$ e $|\beta|^2$, respectivamente.

O protocolo BB84 fundamenta-se na existência de duas bases de medição mutuamente não-ortogonais. A base retilínea ($+$) utiliza os estados computacionais $\{|0\rangle, |1\rangle\}$, enquanto a base diagonal ($\times$) utiliza os estados superpostos $\{|{+}\rangle, |{-}\rangle\}$, onde $|{+}\rangle = (|0\rangle + |1\rangle)/\sqrt{2}$ e $|{-}\rangle = (|0\rangle - |1\rangle)/\sqrt{2}$. A transição entre essas duas bases é realizada pela porta Hadamard (H): aplicada sobre $|0\rangle$, produz $|{+}\rangle$; aplicada sobre $|1\rangle$, produz $|{-}\rangle$; e, inversamente, aplicada sobre um estado da base diagonal, devolve o estado computacional correspondente. Quando Bob mede um qubit em uma base diferente da usada por Alice para codificá-lo, o resultado é completamente aleatório, com **50%** de probabilidade de erro.

A segurança do protocolo baseia-se em dois pilares da mecânica quântica. O Teorema da Não-Clonagem, demonstrado por Wootters e Zurek (1982), estabelece que é impossível criar uma cópia perfeita de um estado quântico desconhecido sem perturbá-lo. Complementarmente, o Princípio da Incerteza de Heisenberg garante que a tentativa de medir o estado de um qubit em uma base qualquer perturba irreversivelmente sua informação na base conjugada. Em conjunto, esses dois princípios tornam qualquer tentativa de interceptação fisicamente detectável: ao tentar medir os qubits em trânsito, Eve inevitavelmente altera seus estados, introduzindo erros mensuráveis na chave final.

O protocolo BB84 implementado em circuito quântico opera em quatro etapas. Na preparação, Alice inicializa $n$ registradores quânticos e clássicos. Cada bit clássico da sua chave secreta é codificado como qubit: o valor 0 é mapeado para o estado $|0\rangle$ e o valor 1 para o estado $|1\rangle$. Em seguida, portas Hadamard são aplicadas aleatoriamente em aproximadamente 50% dos qubits, transferindo-os da base retilínea para a base diagonal e compondo a sequência de bases de Alice. Na interceptação, o circuito de Eve insere medições em bases escolhidas aleatoriamente. Essa operação é fisicamente irreversível: ao medir, Eve força o colapso da função de onda, destruindo a superposição original. Como consequência direta do Teorema da Não-Clonagem e do Princípio da Incerteza, Eve não pode copiar os estados antes de medi-los tampouco restaurá-los ao estado original após a medição, tornando sua presença detectável por meio do aumento da QBER. Na medição, Bob aplica portas Hadamard nos qubits onde decidiu usar a base diagonal. Todos os qubits passam então por operadores de medição, colapsando os estados quânticos em bits clássicos armazenados nos registradores. Por fim, na reconciliação, Alice e Bob comparam publicamente as bases que utilizaram, via canal clássico autenticado. Os bits cujas bases não coincidem são descartados (processo de sifting), pois não carregam informação confiável. A taxa de erro dos bits restantes é calculada como a QBER; se esse valor ultrapassar o limiar estabelecido (neste trabalho, adotamos **0,11**, ou seja, **11%**), conclui-se que o canal foi comprometido, o circuito é descartado e o processo reiniciado desde o início. Caso contrário, os bits sobreviventes ao sifting formam a chave criptográfica compartilhada.

## 3 METODOLOGIA

Para colocar o experimento em prática e responder às questões estruturais da pesquisa, adotamos o ecossistema da IBM. Toda a nossa implementação foi desenvolvida na linguagem Python, utilizando o framework Qiskit, dispensando o uso de interfaces visuais arrastar-e-soltar, a fim de termos controle total sobre as lógicas de automação e medição. O ambiente de execução foi o Google Colaboratory (Colab), que oferece acesso gratuito a GPUs e integração nativa com os serviços IBM Quantum.

O circuito base utilizado no experimento consiste em um registro de 4 qubits. O protocolo BB84 foi programado simulando três entidades: Alice (emissora), Bob (receptor) e Eve (espiã).

![[figures/fig0_circuito_bb84_base.pdf|Figura 1: Diagrama do circuito quântico base de 4 qubits gerado via Qiskit.]]

Para testar a resiliência do modelo, rodamos o experimento em múltiplos cenários, simulando o hardware perfeito e o processador quântico real da IBM Cloud com modelos de ruído NISQ. Para a nossa Nova Proposta, desenvolvemos um ataque tático onde Eve intercepta apenas 50% da transmissão (apenas nas linhas q0 e q1).

![[figures/fig4a_circuito_nossa_proposta.pdf|Figura 2: Diagrama do circuito evidenciando a interceptação parcial (Ataque nas linhas 0 e 1).]]

O ambiente de desenvolvimento e execução utilizado ao longo de todos os experimentos é ilustrado na Figura 3, que registra a execução do código no Google Colaboratory.

![[figures/fig8_colab.png|Figura 3: Ambiente de execução no Google Colaboratory com saída do protocolo BB84.]]

## 4 RESULTADOS E DISCUSSÃO

### 4.1 Módulo 1 — Experimento Clássico com 4 Qubits

Ao executar nosso código no simulador clássico sem qualquer interferência externa, o comportamento da distribuição de chaves foi perfeito. O estado $|0101\rangle$ foi medido com probabilidade de **100%**, resultando em uma QBER de **0%**.

![[figures/fig1_simulador_ideal.pdf|Figura 4: Cenário 1 - Distribuição de probabilidade perfeita em ambiente simulado ideal (QBER = 0%).]]

O cenário muda drasticamente quando forçamos a inserção de Eve no código com interceptação total. Devido ao Teorema da Não-Clonagem da mecânica quântica, o colapso da função de onda espalha a probabilidade de forma quase uniforme entre quatro estados ($|0100\rangle$, $|0101\rangle$, $|0110\rangle$ e $|0111\rangle$), cada um com aproximadamente **25%**. A QBER saltou de 0% para **25,32%** — mais do que o dobro do limiar crítico de 11%, tornando Eve imediatamente detectável.

![[figures/fig2_simulador_eve_total.pdf|Figura 5: Cenário 2 - Colapso da função de onda após ataque de força bruta total de Eve (QBER = 25,32%).]]

Ao analisar o paralelismo com os dados do processador quântico real (hardware NISQ), observamos um desafio prático: a máquina real introduz erros próprios devido à decoerência quântica, gerando um ruído térmico constante sem a presença de espiões. O estado $|0101\rangle$ ainda domina com **90,6%** de probabilidade, resultando em um QBER natural de **2,42%** — valor confortavelmente abaixo do limiar de 11% e tratado como ruído aceitável pelos protocolos de segurança.

![[figures/fig3_hardware_natural.pdf|Figura 6: Cenário 3 - Ruído natural e decoerência introduzidos pelo hardware físico NISQ (QBER = 2,42%).]]

Quando executamos a Nossa Proposta (Ataque Parcial de 50% dos qubits), a distribuição de probabilidade se dividiu entre os estados $|0100\rangle$ (**47,8%**) e $|0101\rangle$ (**46,1%**). O ruído do ataque elevou a QBER para **14,36%**, valor que ultrapassa o limiar de 11% — Eve ainda seria detectada, mas com margem consideravelmente menor do que no ataque total.

![[figures/fig4_hardware_ataque_parcial.pdf|Figura 7: Cenário 4 - Nossa Proposta de Ataque Parcial no hardware da IBM Qiskit (QBER = 14,36%).]]

Para garantir a validade científica do ataque, aplicamos validação cruzada recriando a mesma arquitetura de intrusão no ecossistema de software da Google (Cirq), com estados dominantes em **44,5%** e **43,2%**, obtendo resultados compatíveis com QBER de **15,89%** — confirmando que o ataque de 50% permanece acima do limiar de detecção em ambas as plataformas.

![[figures/fig5_google_cirq_parcial.pdf|Figura 8: Cenário 5 - Nossa Proposta validada de forma cruzada no simulador Google Cirq (QBER = 15,89%).]]

O gráfico comparativo abaixo sumariza o impacto do QBER em cada cenário, evidenciando a linha de alarme de 11% e posicionando cada cenário em relação ao limiar de aborto do protocolo.

![[figures/fig6_diferencas_qber.pdf|Figura 9: Comparativo de QBER para todos os cenários, com destaque para o limiar crítico de 11%.]]

### 4.2 Módulo 2 — Análise de Escalabilidade e Micro-Ataque com 16 Qubits

Para investigar o comportamento do protocolo em escala maior e extrair a contribuição central deste trabalho, escalamos o experimento para **16 qubits** e testamos três sub-cenários: ruído NISQ natural, ataque agressivo de 50% e micro-ataque cirúrgico de 12,5%.

Os resultados confirmam a tendência observada no Módulo 1: um ataque agressivo de **50%** dos qubits (8 de 16) eleva a QBER para **16,06%**, ainda acima do limiar de detecção. Entretanto, o cenário do **micro-ataque de 12,5%** (apenas 2 de 16 qubits interceptados) revela o verdadeiro limite do protocolo BB84 em hardware NISQ: a QBER resultante foi de apenas **5,49%**, abaixo do limiar crítico de 11%.

Este é o achado central da pesquisa: **ao limitar o escopo da interceptação a 12,5% dos qubits transmitidos, Eve consegue roubar frações da chave quântica sem jamais acionar os alarmes de decoerência do protocolo BB84**. O ruído introduzido pelo micro-ataque se camufla perfeitamente dentro do patamar de ruído natural do hardware NISQ (2,42%), tornando a intrusão estatisticamente indistinguível de erros honestos de hardware.

![[figures/fig7_escala_microataque.pdf|Figura 10: Módulo 2 — Análise de escalabilidade com 16 qubits: QBER para ruído natural, ataque de 50% (16,06%) e micro-ataque de 12,5% (5,49%).]]

## 5 CONCLUSÃO

Fica claro que o protocolo BB84 é perfeitamente executável por meio de frameworks modernos. Conseguimos resolver o problema central da distribuição segura de chaves, provando que a própria física atua como o sistema de alarme contra interceptações pesadas: um ataque total produz QBER de 25,32% e um ataque parcial de 50% ainda gera 14,36% — ambos acima do limiar de 11%, sendo prontamente detectados e fazendo Eve falhar.

Entretanto, o verdadeiro achado deste trabalho está na análise de escalabilidade com 16 qubits. O ruído intrínseco dos computadores quânticos de escala intermediária (NISQ) cria uma janela de vulnerabilidade explorável: ao aplicar um micro-ataque cirúrgico sobre apenas **12,5%** dos qubits, Eve consegue manter a QBER em **5,49%** — abaixo do limiar de detecção e indistinguível do ruído natural de hardware. Este resultado demonstra matematicamente que, em ambientes NISQ, ataques parciais e suficientemente pequenos podem roubar frações da chave quântica sem disparar qualquer alarme.

Esta descoberta tem implicações diretas para a segurança de redes quânticas de curto prazo: os protocolos de reconciliação de informação e amplificação de privacidade precisam ser recalibrados para limites QBER mais conservadores, considerando o patamar de ruído do hardware utilizado. O desenvolvimento de protocolos de correção de erro clássica mais robustos, capazes de distinguir ruído de hardware de micro-ataques, constitui a principal direção de trabalhos futuros.

## REFERÊNCIAS

SAEED, M. H.; SATTAR, H.; DURAD, M. H.; HAIDER, Z. An analysis of QKD BB84 protocol implementation over real IBM quantum processors vs. simulation. In: IEEE INTERNATIONAL CONFERENCE ON CYBER WARFARE AND SECURITY, 2023. Proceedings... IEEE, 2023.

BENNETT, C. H.; BRASSARD, G. Quantum cryptography: public key distribution and coin tossing. In: IEEE INTERNATIONAL CONFERENCE ON COMPUTERS, SYSTEMS AND SIGNAL PROCESSING, 1984, Bangalore. Proceedings... New York: IEEE, 1984. p. 175-179.

WOOTTERS, W. K.; ZUREK, W. H. A single quantum cannot be cloned. Nature, v. 299, n. 5886, p. 802-803, out. 1982.
