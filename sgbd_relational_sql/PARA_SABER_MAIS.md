## **Para saber mais: principais tipos de dados em SQL**

Ao criar a tabela Livros percebemos que é preciso definir não só o nome dos campos, mas também o seu tipo. Abaixo encontra-se uma tabela com os principais comandos para definição de tipos utilizados na linguagem SQL.

Lembrando que alguns SGBD’s possuem comandos diferenciados para a mesma finalidade, um exemplo disso é a indicação de uma cadeia de caracteres, pois em alguns sistemas usa-se `char` e em outros é usado o comando `character` ambos para tipificar como texto.

<table>
    <thead>
        <tr>
            <th><strong>Categoria</strong></th>
            <th><strong>Descrição</strong></th>
            <th><strong>Exemplo</strong></th>
            <th><strong>Comando</strong></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Numéricos exatos</td>
            <td>Inteiros de vários tamanhos que podem ser formatados</td>
            <td>9.78 pode ser definida como <code>decimal(3,2)</code> 9 é número inteiro é do tipo <code>int</code>.</td>
            <td>int, smallint, decimal(i,j), numeric(i,j), dec(i,j)</td>
        </tr>
        <tr>
            <td>Numéricos aproximados</td>
            <td>Números de ponto flutuante com precisão</td>
            <td>7.90 é do tipo float</td>
            <td>float ou real, double precision</td>
        </tr>
        <tr>
            <td>Cadeias de caracteres</td>
            <td>Textos de tamanhos fixos</td>
            <td>“modelagem” é char(9)</td>
            <td>char(n) ou character(n)</td>
        </tr>
        <tr>
            <td></td>
            <td>Texto de tamanho variável</td>
            <td></td>
            <td>varchar(n) ou char varying(n) ou character varying(n)</td>
        </tr>
        <tr>
            <td>Valores lógicos</td>
            <td>Termos que representa verdadeiro ou falso</td>
            <td></td>
            <td>true, false ou unknown</td>
        </tr>
        <tr>
            <td>Datas</td>
            <td>Datas, dias, mês, anos.</td>
            <td>Calendário lunar, calendário comercial</td>
            <td>Date DD-MM-YYYY ou YYYY-MM-DD-</td>
        </tr>
        <tr>
            <td></td>
            <td>Tempo</td>
            <td>10:59:13 é tipo HH:MM:SS</td>
            <td>HH:MM:SS, timestamp</td>
        </tr>
    </tbody>
</table>

Mesmo com o padrão ANSI, cada SGBD tem seu manual com mais detalhes sobre tipos específicos.
