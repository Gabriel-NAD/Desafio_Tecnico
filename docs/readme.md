# Lógica de Raciocínio

Este documento descreve a linha de pensamento na ordem em que as decisões foram surgindo.
Cada seção separa **o que foi pensado inicialmente** do que ficou **definido após análise**.

---

# 1. Linha Cronológica de Pensamento

## 1.1 Primeiros Passos Pensados
- **Ler a documentação fornecida**, entendendo o proposto, os requisitos e as restrições.
- **Abrir imediatamente um arquivo de rascunho** para anotar ideias brutas sobre arquitetura e fluxo.
- **Estudar as bibliotecas exigidas** (OpenCV e Flask no Python; OpenCV no C++), já que não são ferramentas totalmente dominadas.
- **Avaliar design patterns** para estruturar o pipeline.
  - *Primeira ideia*: Factory + Command + Proxy — mas, ao analisar melhor, ficou claro que isso seria mais complexo do que necessário.
- **Considerar diferentes arquiteturas** (monolito, microserviços).
  - *Primeira impressão*: talvez microserviços ajudassem a isolar partes, mas rapidamente percebeu-se que seria overengineering para o escopo.
- **Criar um plano de tarefas no GitHub**, possivelmente pensando em Scrum.
  - Mas, ao revisar, ficou claro que Scrum não se aplica, já que o trabalho é individual e curto.
- **Iniciar pela versão Python**, por familiaridade recente.
- **Depois portar para C++** mantendo a equivalência lógica.
- **Pensar em possíveis features de bônus** desde cedo.




 
## 1.2 Primeiros Passos Praticos

- **Kanban com datas separadas para o projeto definindo escopo
- **Definir logica de commits + issues
- **
---

# 2. Decisões Definidas Após Análise

## 2.1 Design Pattern
Após reavaliar:

- **Padrão escolhido**: **Factory + Chain of Responsibility**
- Motivos:
  - O pipeline é naturalmente dividido em etapas;
  - CoR permite trocar ou reorganizar passos facilmente;
  - Factory instancia cada etapa do pipeline sem acoplamento forte;
  - Facilita portar a mesma arquitetura para C++.

**Conclusão:** é o padrão ideal para pipelines de processamento de imagem.

---

## 2.2 Arquitetura
- Microserviços = **overengineering** para apenas 1 pessoa e escopo pequeno.
- Monolito puro = simples demais (dificulta modularidade, principalmente para o bônus).
- **Decisão Final:**  
  → **Monolito Modular**  
  Estrutura organizada por camadas + módulos separados para:
  - pipeline  
  - adapters (API / CLI)  
  - utilidades  
  - estrutura compartilhada (interfaces, erros, DTOs)

Isso mantém complexidade baixa e reutilização alta.

---

## 2.3 Gestão de Tarefas
- Scrum não faz sentido com 1 pessoa e prazo de ~3 dias efetivos.
- **Decisão:** utilizar apenas:
  - Issues no GitHub
  - Kanban simples
  - Commits bem documentados com histórico claro

---

# 3. Definições Técnicas

## 3.1 Questões Iniciais do Problema
Ideias surgidas ao ler o enunciado:

- Como receber e validar imagens? Tipos possíveis: PNG, JPG (PDF = ignorado, pois não faz parte do escopo original).
- Correção de perspectiva: pensar em algoritmos low-level → **DLT (Direct Linear Transform)** é o caminho natural.
- Artefatos brancos: suspeitas iniciais:
  - ruído sal e pimenta  
  - artefatos de interpolação  
  - linhas duplicadas pós-warp  

Soluções consideradas:
- mediana
- gaussiano leve
- interpolação com Lanczos4
- morfologia (open/close)

---

## 3.2 Pipeline Proposto (definido)
1. **Rotação**
2. **Remoção de artefatos brancos**
3. **Correção de perspectiva (DLT)**
4. **Alinhamento de retângulos** (opcional, mas aumenta eficiência)
5. **Normalização e saída**

---

# 4. Implementação Exigida

## Python
- Python 3  
- OpenCV  
- API HTTP com Flask  
- A API deve:
  - receber uma imagem via POST  
  - processar via pipeline  
  - retornar o binário para outra rota  

## C++
- C++  
- OpenCV  
- Execução via bash  
- Makefile completo  

---

# 5. Bônus

- Opcional: criar bindings das funções C++ escolher entre:
  - ctypes  
  - Cython   

- Implementar uma **funcionalidade extra** útil ao pipeline.

---

# 6. Regras e Observações
- Proibido usar ferramentas de alto nível que façam o trabalho automaticamente.
- Deve existir histórico completo do desenvolvimento via commits.
- Documentar cada etapa para facilitar entendimento do pipeline.


