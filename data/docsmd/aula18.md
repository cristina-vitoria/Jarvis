# Aula18

<!-- página 1 [OCR] -->
MC102 - Algoritmos e Progração de Computador

Prof. Alexandre Xavier Falcão

18º Aula: Recursão

1 Recursão

A solução de um problema é dita recursiva quando ela é escrita em função de si própria para
instâncias menores do problema. Considere, por exemplo, o problema de calcular a soma dos números
inteiros no intervalo [m,n], onde m,n € Zem<n.

A solução iterativa ém +(m +1) +(m+2)+...+n, que pode ser facilmente implementada com
a função abaixo:

int Soma(int m, int n)
{

int soma=0, i;

for (i=m; i <= n; i++)
soma += i;

return (soma) ;

}

A solução recursiva está diretamente ligada ao conceito de indução matemática. A indução
fraca usa como hipótese que a solução de um problema de tamanho t pode ser obtida a partir de
sua solução de tamanho t — 1. Por exemplo, se soubermos o resultado da soma de m até n— 1, basta
somar n a este resultado: Soma(m,n) = Soma(m,n — 1) + n. Neste caso, dizemos que a recursão
é decrescente. Podemos também obter o mesmo resultado somando m com a soma de m + 1 até
n: Soma(m,n) =m + Soma(m + 1,n). Neste caso, dizemos que a recursão é crescente. A solução
recursiva, portanto, pode ser implementada com funções do tipo:

tipo função(<parâmetros>)
t

<variáveis locais>

if (<condição de parada>)
{
<comandos finais>
return (valor);
} else {
<comandos iniciais>
<chamada recursiva>

<!-- página 2 [OCR] -->
<comandos finais>
return (valor);
}
}

No caso do exemplo acima temos:

e Solução crescente

int Soma(int m, int n)
{
if (m==n){
return(n) ;
} else {
return (m+Soma(m+1,n));
>
}

e Solução decrescente

int Soma(int m, int n)
{
if (m==n){
return(m) ;
} else {
return(Soma(m,n-1)+n) ;
>
}

Observe que nestes exemplos não precisamos de variáveis locais, nem de comandos iniciais e finais,
portanto podemos colocar a chamada recursiva no comando de retorno. As árvores de recursão
mostradas na Figura 1 ajudam a visualizar o comportamento dessas funções.

A indução forte usa outra hipótese: a solução de um problema de tamanho t depende de suas
soluções de tamanhos , para todo t’ < t. Esta estratégia também é denominada divisão e con-
quista. Por exemplo, podemos dizer que Soma(m,n) = Soma(m, =") + Soma(232 + 1,n). Ou
seja, o problema é dividido em subproblemas similares (divisão), os subproblemas são resolvidos re-
cursivamente (i.e. quando o problema chega a seu tamanho mínimo, ele é resolvido de forma direta),
e as soluções dos subproblemas são combinadas para gerar a solução do problema de tamanho maior
(conquista). Isto requer, porém, ao menos duas chamadas recursivas:

tipo função(<parâmetros>)
{

<variáveis locais>

if (<condição de parada>)
{

<comandos finais>

<!-- página 3 [OCR] -->
Recursao Crescente Recursao Decrescente

12,345
1,2,3,4,5 234,
5 15 iC »

1,2,3,4+5
1+ 2,3,4,5 12,3,
14 10

on Su 67
3445 9 1a
Ness chy

Figura 1: Árvores de recursão param = 1en=5.

return (valor);

} else {
<comandos iniciais>
<primeira chamada recursiva>
<segunda chamada recursiva>
<comandos finais>
return (valor);

}
>

No caso do exemplo acima temos:

int Soma(int m, int n)
{
if (m==n){
return (m) ;
} else {
return (Soma(m, (m+n) /2)+Soma((m+n)/2+1,n));
}
>

Mais uma vez, pelas mesmas razões acima, as chamadas recursivas podem ser feitas no comando de
retorno. A árvore de recursão é apresentada na Figura 2.

Observe que em todos os exemplos, as chamadas recursivas são para a própria função. Dizemos
então que a recursão é direta. Em alguns problemas (e.g. análise sintática do compilador), porém,
uma função A pode chamar uma função B que chama C, que chama ..., que chama A. Neste caso
dizemos que a recursão é indireta.

<!-- página 4 [OCR] -->
Recursao por Divisao e Conquista

15 1,2,3,4,5

ao

(AN EN

(YN, Ss,
a it

Figura 2: Árvore de recursão param=len=5.

2 Exercícios

1. Escreva uma função recursiva para calcular o fatorial de um número inteiro n. Note que o
fatorial de n pode ser definido de forma recursiva como:

sen=0
fato) (1 nxfat(n-1) sen>0 ”

2. Os termos de uma seqiiéncia de Fibonacci (e.g. (0,1,1,2,3,5,8,...) são definidos de forma

recursiva como:
n—1 sel<n<2

fibln) = { fib(n — 1) + fib(n — 2) sen > 2

Escreva uma função recursiva para retornar o n-ésimo termo desta sequência.

(2)