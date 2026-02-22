# An Analysis of QKD BB84 Protocol Implementation over Real IBM Quantum Processors vs. Simulation (Uma Análise da Implementação do Protocolo QKD BB84 em Processadores Quânticos Reais IBM vs. Simulação)

## 1. Introdução

A base da segurança da informação moderna está ancorada em problemas matemáticos complexos. Protocolos clássicos, como o RSA, confiam inteiramente na extrema dificuldade computacional de fatorar grandes números primos. O problema real surge com a iminência da computação quântica de larga escala: algoritmos como o de Shor provam matematicamente que computadores quânticos poderão quebrar essas chaves em tempo polinomial. É para solucionar essa vulnerabilidade fatal que a Distribuição de Chaves Quânticas (QKD - _Quantum Key Distribution_) ganha destaque. Em vez de depender de complexidade matemática, a QKD utiliza as leis fundamentais da física quântica para garantir uma segurança incondicional.

Este trabalho tem como objetivo central reproduzir e analisar a implementação proposta no artigo "An Analysis of QKD BB84 Protocol Implementation over Real IBM Quantum Processors vs. Simulation" (Uma Análise da Implementação do Protocolo QKD BB84 em Processadores Quânticos Reais IBM vs. Simulação), de Saeed et al. (2023). Nossa proposta é demonstrar, na prática, como ocorre a troca de chaves criptográficas utilizando o protocolo BB84 e evidenciar como a presença de um interceptador (Eve) é naturalmente detectada pelo colapso da função de onda.

## 2. Metodologia

Para colocar o experimento em prática e responder às questões estruturais da pesquisa, adotamos o ecossistema da IBM. Toda a nossa implementação foi desenvolvida na linguagem Python, utilizando o framework Qiskit, dispensando o uso de interfaces visuais arrastar-e-soltar como o IBM Quantum Composer, a fim de termos controle total sobre as lógicas de automação e medição.

O circuito base utilizado no experimento consiste em um registro de 4 qubits. O protocolo BB84 foi programado simulando três entidades: Alice (emissora), Bob (receptor) e Eve (espiã). O fluxo metodológico seguiu as seguintes etapas:

1. **Codificação (Alice):** Alice gera uma sequência aleatória de 4 bits. Em seguida, ela escolhe bases aleatórias (Retilínea, operando com estados $|0\rangle$ e $|1\rangle$, ou Diagonal, aplicando portas lógicas Hadamard, $H$, para criar superposição). Esses qubits são injetados no canal quântico.
    
2. **Medição (Bob):** No outro extremo, Bob recebe os qubits e também aplica bases aleatórias para medi-los.
    
3. **Peneiramento (Sifting):** Alice e Bob comparam publicamente quais bases usaram (mas nunca os resultados das medições). Os bits onde as bases coincidiram formam a chave final segura.
    

Para testar a resiliência do modelo, rodamos o experimento em dois cenários. O primeiro foi feito localmente utilizando o simulador clássico do Qiskit (`qasm_simulator`), que nos forneceu um ambiente livre de ruídos para validação lógica. Em seguida, analisamos o comportamento desses mesmos circuitos quando submetidos a um processador quântico real da IBM Cloud (como o hardware `ibmqx2` referenciado no artigo base, sujeito a ruído térmico e erros de porta lógica).

_[Inserir aqui a Imagem gerada: circuito_bb84.png. Sugestão de legenda: Figura 1 - Diagrama do circuito quântico de 4 qubits gerado via Qiskit.]_

## 3. Resultados e Discussão

Ao executar nosso código no simulador clássico sem qualquer interferência externa, o comportamento da distribuição de chaves foi perfeito. Quando comparamos as bases de Alice e Bob, nos casos em que ambos escolheram o mesmo alinhamento, a probabilidade de leitura correta do estado foi cravada, dividindo-se perfeitamente entre os estados esperados da chave.

O cenário muda drasticamente quando forçamos a inserção de "Eve" no código. Simulamos a espiã interceptando os qubits no meio do trajeto, aplicando suas próprias bases de medição aleatórias e reenviando as partículas para Bob. Devido ao Teorema da Não-Clonagem da mecânica quântica, a simples tentativa de leitura por parte de Eve colapsa o estado original. Como resultado nos histogramas do Qiskit, a taxa de erro nos bits que deveriam ser idênticos entre Alice e Bob saltou de 0% para aproximadamente 25% (Quantum Bit Error Rate - QBER). Essa alteração violenta na distribuição de probabilidade é a "prova física" de que a linha foi grampeada.

_[Inserir aqui os histogramas: histograma_sem_eve.png e histograma_com_eve.png lado a lado. Sugestão de legenda: Figura 2 - Comparativo da distribuição de probabilidades entre um canal limpo e um canal interceptado no qasm_simulator.]_

Ao analisar o paralelismo com os dados do processador quântico real (hardware NISQ), observamos um desafio prático: a máquina real introduz erros próprios devido à decoerência quântica. Diferente do simulador perfeito, o chip físico gera um "ruído de fundo", criando pequenas probabilidades de estados errôneos mesmo sem a presença de um espião. Contudo, os picos de sinal verdadeiro ainda se mantêm estatisticamente distinguíveis do ruído natural, validando o protocolo.

## 4. Conclusão

Ao final da nossa implementação, fica claro que o protocolo BB84 não é apenas uma teoria elegante, mas uma ferramenta perfeitamente executável por meio de frameworks como o Qiskit. Conseguimos resolver o problema central da distribuição segura de chaves, provando que a própria física atua como o sistema de alarme contra interceptações.

Apesar do sucesso do experimento, é importante destacar as limitações atuais da tecnologia. A nossa execução restringiu-se a um registro de 4 qubits como prova de conceito, enquanto redes QKD reais exigiriam escalar isso para centenas de qubits (512+). Além disso, o ruído intrínseco aos computadores quânticos de escala intermediária (NISQ) atuais, como a família `ibmqx`, cria um desafio de engenharia: as taxas de erro naturais do hardware muitas vezes se misturam à margem de erro que denotaria uma espionagem, exigindo a implementação de protocolos robustos de correção de erro e amplificação de privacidade antes que esses sistemas dominem o mercado corporativo.

## Referências Bibliográficas

[1] SAEED, M. H.; SATTAR, H.; DURAD, M. H.; HAIDER, Z. "An Analysis of QKD BB84 Protocol Implementation over Real IBM Quantum Processors vs. Simulation". IEEE, 2023. [2] BENNETT, C. H.; BRASSARD, G. "Quantum cryptography: Public key distribution and coin tossing". Proceedings of IEEE International Conference on Computers, Systems and Signal Processing, 1984. [3] WOOTTERS, W. K.; ZUREK, W. H. "A single quantum cannot be cloned". Nature, vol. 299, no. 5886, pp. 802-803, 1982.