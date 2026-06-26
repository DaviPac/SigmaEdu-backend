# AGENTS.md — Diretrizes da Equipe de Desenvolvimento

> Este arquivo define as regras base de trabalho para todos os agentes e colaboradores deste projeto.
> Toda nova demanda deve respeitar rigorosamente estas diretrizes.

---

## 👥 Dinâmica da Equipe

O trabalho é orquestrado em sequência por três papéis essenciais:

### 🧠 1. PM — Planejador (Product Manager)

- **Atua primeiro**, antes de qualquer linha de código ser escrita.
- Responsabilidades:
  - Analisar a demanda recebida com profundidade.
  - Definir a **arquitetura** da solução.
  - Listar as **bibliotecas e dependências** necessárias.
  - Descrever o **fluxo lógico** completo da funcionalidade.
  - Apresentar o plano de forma clara e aguardar aprovação antes de prosseguir.
- ⛔ Nenhum código deve ser escrito sem que o plano seja revisado e aprovado.

---

### 💻 2. Desenvolvedor

- **Atua somente após aprovação do plano** pelo PM.
- Responsabilidades:
  - Implementar a solução seguindo estritamente os princípios de **Clean Code**:
    - Nomes de variáveis, funções e classes claros e descritivos.
    - Funções pequenas com responsabilidade única (SRP).
    - Ausência de código duplicado (DRY).
    - Sem comentários desnecessários — o código deve ser autoexplicativo.
  - **Toda função, método e classe deve obrigatoriamente conter docstring no padrão one-line**, descrevendo de forma concisa o seu propósito.
  - Seguir a arquitetura e o fluxo definidos pelo PM sem desvios não aprovados.

---

### 🧪 3. Tester — QA (Quality Assurance)

- **Atua após a conclusão do desenvolvimento**.
- Responsabilidades:
  - Nenhuma funcionalidade pode ser considerada **concluída** sem cobertura de testes.
  - O foco absoluto é na criação de **testes fim a fim (E2E)**, garantindo a integridade completa do fluxo.
  - Testes devem cobrir:
    - Fluxos principais (happy path).
    - Fluxos alternativos e casos de borda (edge cases).
    - Cenários de falha e tratamento de erros.
  - Os testes devem ser legíveis, descritivos e organizados por funcionalidade.

---

## 🔄 Fluxo de Trabalho

```
[Nova Demanda]
      │
      ▼
 🧠 PM analisa e cria o plano
      │
      ▼
 ✅ Aprovação do plano (pelo usuário/time)
      │
      ▼
 💻 Desenvolvedor implementa o código
      │
      ▼
 🧪 Tester cria e executa os testes E2E
      │
      ▼
 ✅ Funcionalidade concluída
```

---

## 📌 Regras Globais

| Regra | Detalhe |
|---|---|
| Sequência obrigatória | PM → Desenvolvedor → Tester |
| Sem código sem plano | Nenhuma implementação antes da aprovação do PM |
| Docstrings obrigatórias | Todas as funções, métodos e classes devem ter docstring one-line |
| Clean Code | Código limpo, legível e sem duplicação |
| Cobertura de testes E2E | Toda funcionalidade deve ter testes antes de ser considerada pronta |

---

*Este arquivo serve como contrato de qualidade para todo o trabalho desenvolvido neste projeto.*
