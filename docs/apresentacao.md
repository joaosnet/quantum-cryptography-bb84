# Roteiro Completo para Apresentação - QKD BB84 (Submissão COBENGE)

**Instruções para o NotebookLM:** Utilize este texto para gerar uma apresentação de 15 slides. O texto contém descrições visuais detalhadas dos gráficos e circuitos em vez de imagens diretas. Por favor, mantenha o tom académico e utilize as descrições para sugerir layouts ou criar diagramas representativos.

## Slide 1: Capa (Obrigatório)

- **Título Original:** An Analysis of QKD BB84 Protocol Implementation over Real IBM Quantum Processors vs. Simulation
    
- **Título Traduzido:** Uma Análise da Implementação do Protocolo QKD BB84 em Processadores Quânticos Reais IBM vs. Simulação
    
- **Subtítulo:** Replicação do Estudo e Nova Proposta de Ataque Parcial em Hardware NISQ
    
- **Autor:** [Inserir o Teu Nome]
    

## Slide 2: Introdução - A Ameaça Quântica à Criptografia

- **Tópico:** O Problema a ser Resolvido
    
- **Conteúdo:** A segurança atual da internet (protocolos como RSA e ECC) baseia-se na dificuldade de fatorar grandes números primos. Com o avanço da computação quântica e a aplicação do Algoritmo de Shor, a quebra destas chaves matemáticas passará a ocorrer em tempo polinomial. O fim da criptografia clássica é uma questão de tempo.
    
- **Ideia Visual:** Um cadeado digital a ser quebrado por um átomo ou símbolo quântico.
    

## Slide 3: Introdução - A Solução BB84

- **Tópico:** A Física substitui a Matemática
    
- **Conteúdo:** A Distribuição de Chaves Quânticas (QKD) não resolve equações; ela utiliza a Mecânica Quântica. O protocolo BB84, criado em 1984, codifica a chave em estados de polarização de fótons (qubits).
    
- **O Grande Trunfo:** O Teorema da Não-Clonagem. É fisicamente impossível copiar um estado quântico desconhecido. Qualquer tentativa de interceptação (espionagem) altera o estado do sistema irreversivelmente, deixando um rastro claro.
    

## Slide 4: Metodologia - O Fluxo de Alice, Bob e Eve

- **Tópico:** Como a informação viaja
    
- **Conteúdo:**
    
    - **Alice (Emissora):** Gera bits aleatórios e aplica bases aleatórias (Retilínea ou Diagonal) para enviá-los.
        
    - **Bob (Receptor):** Mede os fótons utilizando as suas próprias bases aleatórias.
        
    - **Sifting:** Eles comparam publicamente _apenas_ as bases que usaram. Onde coincidem, a chave é formada.
        
    - **Eve (Espiã):** Se tentar ler a chave no meio do caminho, ela colapsa a função de onda e introduz erros (QBER).
        

## Slide 5: Metodologia - Ferramentas de Implementação

- **Tópico:** Ambiente de Desenvolvimento e Chip Quântico
    
- **Conteúdo:** * **Framework:** 100% Python e IBM Qiskit. Sem interfaces gráficas (IBM Composer), garantindo controlo algorítmico total.
    
    - **Processador Quântico:** O artigo base utilizou o `ibmqx2`. Na nossa implementação, emulamos o hardware real utilizando o `qasm_simulator` equipado com o modelo de ruído `qiskit_aer.noise`, aplicando erros depolarizantes de 5% para replicar com fidelidade a decoerência térmica da Era NISQ.
        

## Slide 6: Metodologia - O Circuito Quântico Base (Replicação)

- **Tópico:** Qual foi o circuito utilizado?
    
- **Descrição Visual do Circuito para o NotebookLM:** Um diagrama de circuito quântico com 4 linhas horizontais (q0, q1, q2, q3). No início, blocos azuis (Portas X) atuam como "NOT" para codificar os bits 1. A seguir, blocos vermelhos (Portas H de Hadamard) criam a superposição (Base Diagonal). No final, blocos cinzentos com medidores representam o Bob colapsando os estados de volta para bits clássicos (linha dupla inferior).
    
- **Conteúdo:** O circuito de 4 qubits demonstra a preparação de Alice (Portas X e H) e a medição de Bob, isoladas por barreiras virtuais simulando o canal de fibra óptica.
    

## Slide 7: Metodologia - A Nossa Proposta (O Circuito do Ataque Parcial)

- **Tópico:** Evoluindo o modelo original
    
- **Descrição Visual do Circuito para o NotebookLM:** O mesmo circuito anterior de 4 linhas, mas com uma zona intermediária "grampeada". Na metade do circuito, as linhas q0 e q1 possuem blocos de medição seguidos por novas Portas H, representando a interceptação e re-preparação por parte da espiã Eve. As linhas q2 e q3 passam intocadas, representando a furtividade.
    
- **Conteúdo:** O artigo base assume que Eve ataca 100% do canal. A nossa proposta injeta um "Ataque Parcial", onde Eve interceta apenas 50% dos qubits, testando a sensibilidade do sistema num ambiente já ruidoso.
    

## Slide 8: Resultados - O Simulador Ideal (Sem Eve)

- **Tópico:** A Perfeição Teórica
    
- **Descrição Visual do Gráfico para o NotebookLM:** Um gráfico de barras simples. Apenas uma única barra azul gigante atingindo 100% (1.000) no estado "0101". O resto do gráfico está completamente vazio.
    
- **Conteúdo:** Em ambiente controlado e ideal (sem ruído e sem espiões), o protocolo BB84 funciona com precisão absoluta. O Bob recebe 100% da informação correta que Alice enviou (QBER = 0%).
    

## Slide 9: Resultados - O Ataque Total no Ambiente Ideal

- **Tópico:** Replicando a Deteção do Artigo Original
    
- **Descrição Visual do Gráfico para o NotebookLM:** Um gráfico com várias barras vermelhas espalhadas. Em vez de uma barra em "0101", a probabilidade dividiu-se, mostrando barras com valores à volta de 12% a 13% em vários estados diferentes.
    
- **Conteúdo:** Quando a Eve aplica a força bruta e interceta 100% dos qubits, o Teorema da Não-Clonagem destrói a chave. A taxa de erro (QBER) sobe drasticamente para níveis teóricos de ~25% ou mais. A intrusão é gritante e impossível de ignorar.
    

## Slide 10: Resultados - A Realidade do Hardware NISQ

- **Tópico:** O Inimigo Silencioso: O Ruído Natural
    
- **Descrição Visual do Gráfico para o NotebookLM:** Um gráfico de barras azuis. Há uma barra principal enorme (cerca de 0.90), mas ao contrário do cenário ideal, o fundo está cheio de barras minúsculas (cerca de 0.04) em estados incorretos.
    
- **Conteúdo:** Na vida real, os chips quânticos atuais (Era NISQ) sofrem interferências térmicas e radiação. Mesmo **sem qualquer espião**, a chave sofre uma degradação natural, gerando uma taxa de erro intrínseca entre 5% e 10%.
    

## Slide 11: Resultados - A Nossa Proposta (Ataque Parcial)

- **Tópico:** O Perigo da Camuflagem
    
- **Descrição Visual do Gráfico para o NotebookLM:** Um gráfico de barras cor-de-laranja. O estado principal caiu bastante (para cerca de 0.48), e surgiram picos secundários quase tão altos quanto o original (0.47), com pequenos ruídos ao redor.
    
- **Conteúdo:** Quando introduzimos o Ataque Parcial num ambiente NISQ (com ruído), a espiã eleva o erro em apenas ~12.5%. A grande descoberta é que este ataque não destrói totalmente o sinal. Ele cria uma assinatura que pode ser facilmente confundida pelo administrador do sistema como "apenas mais ruído do hardware".
    

## Slide 12: Resultados - Comparativo Final de QBER

- **Tópico:** A Taxa de Erro Quântico Lado a Lado
    
- **Descrição Visual do Gráfico para o NotebookLM:** Um gráfico de 4 barras largas comparativas: Barra 1 (Simulador Ideal) em 0.00%. Barra 2 (Ataque Total) disparada nos 37.82%. Barra 3 (Hardware com Ruído) baixinha nos 2.48%. Barra 4 (Ataque Parcial) perigosamente no meio, com 26.35%.
    
- **Conteúdo:** A comparação direta prova que, em simulação ideal, qualquer ataque é óbvio. Mas no hardware ruidoso, um ataque tático aproxima muito as margens de erro, exigindo algoritmos de calibração extremamente precisos para não aprovar chaves roubadas.
    

## Slide 13: Conclusão - Limitações do Estudo

- **Tópico:** Quais são as limitações atuais?
    
- **Conteúdo:** * **Escala de Hardware:** Operámos num registro de apenas 4 qubits como prova de conceito laboratorial. O uso prático (como proteger dados bancários) exigirá mais de 512 qubits totalmente coerentes.
    
    - **A Barreira NISQ:** Os computadores "Noisy Intermediate-Scale Quantum" ainda são demasiado instáveis. A decoerência é o maior obstáculo atual para a implementação comercial pura do BB84.
        

## Slide 14: Conclusão - O Caminho para a Computação Quântica

- **Tópico:** Soluções Paliativas e o Futuro
    
- **Conteúdo:** O trabalho de replicar o IEEE com o Qiskit comprova que o software já está preparado para o futuro. Contudo, enquanto não atingirmos a computação tolerante a falhas (Fault-Tolerant), as redes QKD terão de usar rotinas clássicas pesadas de **Correção de Erros (Reconciliation)** e **Amplificação de Privacidade** no pós-processamento para filtrar a interferência da máquina (e dos espiões camuflados nela).
    

## Slide 15: Fecho e Discussão

- **Tópico:** Agradecimentos e Q&A
    
- **Conteúdo:** * "A Física assegura as fundações da nossa privacidade; o desafio atual é meramente um problema de engenharia."
    
    - Agradecimento à banca do COBENGE e ao professor orientador.
        
    - Abertura para perguntas (Defesa dos gráficos gerados via Qiskit).