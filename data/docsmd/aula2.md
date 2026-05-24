# Aula2

<!-- página 1 [OCR] -->
MC102 - Algoritmos e Progração de Computador

Prof. Alexandre Xavier Falcão

2º Aula: Variáveis simples, atribuições e operações matemáticas

1 Variáveis simples

Variáveis simples armazenam números e caracteres na memória principal. A forma de armazena-
mento depende do conteúdo. Variáveis que armazenam números inteiros, por exemplo, consideram 1
bit para o sinal e os demais para o valor do número. Por exemplo, uma variável inteira com b bits
pode armazenar valores de —20-1) a 2-1) — 1 ou valores sem sinal de 0 a 2° — 1. Essas variáveis são
declaradas da seguinte forma.

int main()

t

int a; /* pode armazenar apenas números inteiros com no máximo 4 bytes,
incluindo o sinal. Isto é, valores de -2147483648 a 2147483647. */

unsigned int b; /* pode armazenar apenas números inteiros sem sinal com no
máximo 4 bytes. Isto é, valores de
O a 4294967295. */

short c; /* pode armazenar apenas números inteiros com no máximo 2 bytes,
incluindo o sinal. Isto é, valores de -32768 a 32767. */

unsigned short d; /* pode armazenar apenas números inteiros sem sinal
com no máximo 2 bytes. Isto é, valores de 0 a
65535. */

float e; /* pode armazenar números reais com no máximo 4 bytes,
incluindo o sinal. A forma de armazenamento permite
representar números nos intervalos de -2 x 107(-38) a -2 x
10°(38) e de 2 x 107(-38) a 2 x 10°(38). */

double f; /* pode armazenar números reais com no máximo 8 bytes,
incluindo o sinal. A forma de armazenamento permite
representar números nos intervalos de -2 x 107(-308) a -2 x
10-(308) e de 2 x 10"(-308) a 2 x 107(308). */

char g; /* pode armazenar caracteres alfanuméricos com no máximo 1

<!-- página 2 [OCR] -->
byte, incluindo o sinal no caso de número inteiro. Isto é,
valores como ’a’, ’X’, ’%’ e números de -128 a 127.*/

unsigned char h; /* pode armazenar caracteres alfanuméricos com no máximo 1
byte, incluindo o sinal no caso de número inteiro. Isto é,
valores como ’a’, ’X’, ’%’ e números de 0 a 255.*/

}

Alguns sistemas operacionais consideram apenas 2 bytes para o tipo int. Neste caso, o tipo long
estende para 4 bytes. O comando sizeof(tipo) permite saber quantos bytes são ocupados um dado
tipo de variável (e.g. sizeof (int) = 4 bytes).

Os nomes das variáveis podem ter tamanhos maiores, contendo caracteres alfanuméricos, mas não
podem conter caracteres e nem constituírem palavras reservadas pela linguagem para outros fins.

2 Atribuições

O operador “=” é usado para indicar uma atribuição de valor à variável. Todo comando de declaração

de variável ou de atribuição deve ser finalizado com “;”. Exemplos:

int main

t

int a;

unsigned int b;
short c;
unsigned short d;
float e;

double f;

char g;
unsigned char h;

= 10; /* correto */

= -6; /* errado */

= 100000; /* errado */

= 33000; /* certo */

= -80000.657; /* certo */

= 30 /* errado */

'a?; /* certo */

= a; /* errado, a menos que
= 200; /* certo */

=ºB?; /* certo */

““a”? fosse do tipo char */

“Prima ho gocp
i]

Declarações e atribuições também podem aparecer da seguinte forma:

int main()

{

<!-- página 3 [OCR] -->
int a=10,b=-30; /* na mesma linha, separadas por ‘‘,’’. */
float c;
char d=’4’; /* estou me referindo ao caracter 4 e não ao número. */

c=a; /* converte para float e copia valor 10.0 para ‘‘c’’. */

c=a+1.8; /* atribui valor 11.8 para ‘‘c’’. */

b = c; /* converte para int truncando a parte decimal e copia 11
para ‘‘c??. */

b=a+b; /* soma 10 e 11, e copia 21 para. b */
a= 10+ b; c = b*40.5; /* devemos evitar de escrever vários comenados
em uma mesma linha. */

}

Note que as atribuições só podem ser feitas após a declaração da variável. Podemos também usar um
tipo de variável entre parênteses, para fazer com que o resultado da expressão seja convertido para
o tipo especificado antes da atribuição. Exemplos:

int main()
{

int a;

= (int) (2.5*7.2); /* calcula o produto e depois converte para inteiro. */

a
}
3 Operações aritméticas e expressões

Operações aritméticas podem ser combinadas formando expressões. Existe uma regra de prioridade
da multiplicação e divisão (mesma prioridade) sobre soma e subtração (mesma prioridade), e a ordem
de execução para operadores de mesma prioridade é da esquerda para direita. Exemplos:

int main()

{
int a=20,b=10;
float c=1.5,d;

d
d

c*b/a; /* atribui 0.75 para ‘‘d’? */

c*(b/a); /* atribui 0.0 para ‘‘d’’, pois a divisão entre
inteiros resulta em um inteiro. A divisão só resulta
em número real se ao menos um dos operandos for
real, porém isto não adianta nada se o resultado for
atribuído a uma variável inteira. Os parênteses
forçam a execução da operação de divisão antes da
multiplicação. */

d = b-a*c; /* atribui -20.0 para ““d?” */

d = (b-c)*a; /* atribui 170.0 para ‘‘d’’ */

<!-- página 4 [OCR] -->
Note que a melhor forma de garantir o resultado esperado é usar parênteses. A prioridade de execução
neste caso é da expressão mais interna para a mais externa.

int main()

{
int a=20,b=10;
float c=1.5,d;

d = (((a+5)*10)/2)+b; /* atribui 135 para ‘‘d’’ */
}

4 Exercício

Sabendo que as fórmulas de conversão de temperatura de Celsius para Fahrenheit e vice-versa são

c = E = 3295, ()
= OC + 32, (2)

escreva dois programas em C, um para converter de Celsius para Fahrenheit e outro para fazer o
caminho inverso.