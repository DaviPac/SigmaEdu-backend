Olá! Agente Professor da SigmaEdu. Sua dúvida sobre **Trigonometria**, focada em **Funções Trigonométricas**, foi identificada. Este é um tópico de nível "difícil" no ENEM, mas essencial para seu progresso.

Segue material focado para seu domínio:

***Observação Importante:*** *O banco de questões reais para este tópico não foi fornecido (`Base de Questões Encontradas para o assunto: []`). Para atender à sua solicitação, elaborei uma questão base simulada que representa bem o nível e estilo que você encontraria no ENEM para Funções Trigonométricas classificadas como "difíceis", porém buscando a abordagem "mais fácil" dentro dessa categoria, geralmente focada em modelagem e interpretação de parâmetros.*

---

### 1. Teoria Direcionada

As funções trigonométricas (seno e cosseno) são essenciais para modelar fenômenos periódicos, como ondas, ciclos de temperatura, batimentos cardíacos e marés. Compreender seus parâmetros é crucial para interpretá-las.

A forma geral de uma função trigonométrica sinusoidal é:
`f(t) = A + B * sen(Ct + D)` ou `f(t) = A + B * cos(Ct + D)`

Onde:
*   **A (Deslocamento Vertical / Valor Médio):** Representa o valor central em torno do qual a função oscila. É a média entre o valor máximo e o mínimo da função.
    *   `A = (Valor Máximo + Valor Mínimo) / 2`
*   **B (Amplitude):** Representa a metade da diferença entre o valor máximo e o mínimo. Indica o "quão alto" ou "quão baixo" a função se afasta do valor médio. O valor de B no termo `B * sen(...)` ou `B * cos(...)` é a amplitude. Se o valor do coeficiente B for negativo, ele inverte o gráfico, mas a amplitude continua sendo `|B|`.
    *   `|B| = (Valor Máximo - Valor Mínimo) / 2`
*   **C (Parâmetro de Período):** Afeta o período da função. O período (T) é o tempo necessário para um ciclo completo e é calculado por:
    *   `T = 2π / |C|`
    *   Consequentemente, `|C| = 2π / T`
*   **D (Deslocamento de Fase / Horizontal):** Determina o "início" do ciclo em relação ao eixo vertical.
    *   Uma função `y = B * cos(Ct)` tem seu valor máximo quando `Ct = 0`, ou seja, em `t=0`.
    *   Uma função `y = B * sen(Ct)` tem seu valor médio e está crescendo quando `Ct = 0`, ou seja, em `t=0`.
    *   Se o fenômeno começa no máximo ou no mínimo, a função cosseno é geralmente mais direta para usar sem deslocamento de fase `D`. Se começa no valor médio (e subindo ou descendo), a função seno pode ser mais conveniente.

**Passos para modelar um fenômeno periódico:**
1.  **Encontre o Valor Médio (A) e a Amplitude (B):** Use os valores máximo e mínimo fornecidos.
2.  **Encontre o Período (T) e o Parâmetro C:** Determine o tempo para um ciclo completo do fenômeno.
3.  **Escolha a Função (seno ou cosseno) e o Deslocamento de Fase (D):** Observe o comportamento da função no instante `t=0` ou em um instante de referência.

### 2. A Questão Base

> A altura da maré em uma cidade litorânea é um fenômeno periódico que pode ser modelado por uma função trigonométrica. Em um determinado dia, a maré atingiu sua altura máxima de 3,5 metros às 10h da manhã. Seis horas depois, às 16h, a maré atingiu sua altura mínima de 0,5 metros. Supondo que o padrão se repita de forma regular, qual função trigonométrica descreve a altura `h(t)` da maré em metros em função do tempo `t` em horas, considerando `t=0` como o instante das 10h da manhã?
>
> a) `h(t) = 2 + 1,5 * cos((π/12)t)`
> b) `h(t) = 2 + 1,5 * sen((π/6)t)`
> c) `h(t) = 2 + 1,5 * cos((π/6)t)`
> d) `h(t) = 1,5 + 2 * cos((π/6)t)`
> e) `h(t) = 2 + 1,5 * cos((π/6)(t - 10))`

### 3. Resolução Passo a Passo

Vamos analisar os dados e aplicar os conceitos de Funções Trigonométricas para encontrar a função correta.

1.  **Determinar o Valor Médio (A):**
    *   Altura Máxima = 3,5 m
    *   Altura Mínima = 0,5 m
    *   `A = (Valor Máximo + Valor Mínimo) / 2`
    *   `A = (3,5 + 0,5) / 2 = 4 / 2 = 2` metros.
    *   Isso significa que o deslocamento vertical da função é 2.

2.  **Determinar a Amplitude (B):**
    *   `B = (Valor Máximo - Valor Mínimo) / 2`
    *   `B = (3,5 - 0,5) / 2 = 3 / 2 = 1,5` metros.
    *   A amplitude da função é 1,5.

3.  **Determinar o Período (T) e o Parâmetro C:**
    *   Sabemos que a maré alta ocorre às 10h e a maré baixa às 16h. O tempo entre uma maré alta e uma maré baixa consecutivas é metade de um ciclo completo (meio período).
    *   Tempo decorrido = 16h - 10h = 6 horas.
    *   Portanto, `T/2 = 6` horas.
    *   O Período completo `T = 2 * 6 = 12` horas.
    *   Agora, calculamos o parâmetro C: `C = 2π / T`
    *   `C = 2π / 12 = π / 6`.

4.  **Escolher a Função (seno ou cosseno) e o Deslocamento de Fase (D):**
    *   O enunciado define `t=0` como o instante das 10h da manhã.
    *   Às 10h (`t=0`), a maré atingiu sua altura *máxima* (3,5 m).
    *   A função cosseno `cos(x)` começa em seu valor máximo (1) quando `x=0`. Isso se alinha perfeitamente com a condição inicial do problema.
    *   Portanto, uma função cosseno sem deslocamento de fase horizontal (ou seja, `D=0` se usarmos a forma `cos(Ct + D)`) é a escolha mais natural.

5.  **Montar a Função:**
    *   Usando a forma `h(t) = A + B * cos(Ct + D)` e substituindo os valores encontrados (A=2, B=1,5, C=π/6 e D=0):
    *   `h(t) = 2 + 1,5 * cos((π/6)t)`

6.  **Verificar com as Opções:**
    *   Comparando com as opções fornecidas, a função `h(t) = 2 + 1,5 * cos((π/6)t)` corresponde à **opção c)**.

**Resposta:** A função trigonométrica que descreve a altura da maré é `h(t) = 2 + 1,5 * cos((π/6)t)`.

### 4. Desafio de Fixação

> A temperatura diária em uma cidade segue um padrão periódico. Em um certo dia de verão, a temperatura mínima registrada foi de 18°C às 4h da manhã. Doze horas depois, às 16h, a temperatura atingiu seu valor máximo de 34°C. Qual função trigonométrica descreve a temperatura `T(h)` em graus Celsius em função do tempo `h` em horas, considerando `h=0` como o instante das 4h da manhã?
>
> a) `T(h) = 26 + 8 * cos((π/12)h)`
> b) `T(h) = 26 + 8 * sen((π/12)h)`
> c) `T(h) = 26 - 8 * cos((π/12)h)`
> d) `T(h) = 26 + 16 * cos((π/24)h)`
> e) `T(h) = 18 + 16 * sen((π/12)h)`