# Aula3

<!-- página 1 [OCR] -->
MC102 - Algoritmos e Progração de Computador

Prof. Alexandre Xavier Falcão

3º Aula: Variáveis simples, atribuições, e operações matemáticas.

1 Constantes

Assim como variáveis, constantes são usadas para armazenar números e caracteres. Porém, não
podemos modificar o conteúdo de uma constante durante a execução do programa. Exemplos:

#define PI 3.1415926536 /* atribui 3.1415926536 para PI */
#define MSG "O Conteúdo de a é " /* atribui o texto para MSG */
#define Epsilon 1E-05 /* atribui 0.00001 para Epsilon */

int main()

{
float dois_PI;

dois PI = 2*PI; /* atribui 6.2831853072 para "a" */
printf("%s %5.2f\n" ,MSG,dois_PI); /* imprime "0 conteúdo de a é 6.28"
na tela */

2 Definindo novos tipos

Podemos usar o comando typedef para definir novos tipos de variáveis ou abreviar tipos existentes.

typedef enum {false,true} bool; /* o tipo bool só armazena 0/false e 1/true */
typedef unsigned char uchar; /* o tipo uchar é o mesmo que unsigned char */
int main()
{

bool vi,v2; /* tipo boleano ou variável lógica */

uchar a=10;

vi = true; /* o mesmo que atribuir 1 para vi */
v2 = false; /* o mesmo que atribuir O para v2 */
printf("%d %d Z%d\n",vi,v2,a); /* imprime na tela 1 0 10 */

<!-- página 2 [OCR] -->
3 Operações lógicas e expressões

Os caracteres “&&”, “||”, “!” indicam as seguintes operações lógicas: and, or e not, respectiva-
mente. Essas operações quando aplicadas a variáveis lógicas reproduzem os resultados apresentados
na Figura 1, dependendo do conteúdo das variáveis.

vl v2 vl and v2 vl v2 | vl or v2 vl not v1
true true true true true true true false
true false | false true false | true false | true
false | true false false | true true
false | false | false false | false | false

Figura 1: Operações lógicas

typedef enum {false,true} bool;
int main()
{

bool vi,v2,v3;

vi = true;

v2 = false;

v3 = vi&&v2; /* atribui false para ‘‘v3’? */

v3 = villv2; /* atribui true para ‘‘v3’? */

v3 = !vi; /* atribui false para ‘‘v3’? */

v3 = ((vig&v2) | |(!v2)); /* atribui true para ‘‘v3’? */

4 Funções matemáticas e resto da divisão inteira

Note que um programa consiste de uma sequência de comandos apresentada na função principal
(main). Quando várias tarefas são necessárias, as sequências de comandos dessas tarefas podem ser
agrupadas em outras funções. Esta forma de organização dos programas evita confusão na depuração
do programa e provê uma melhor apresentação do código fonte. Estas funções podem ser chamadas a
partir da função principal e devem retornar o resultado da tarefa correspondente, para que as demais
tarefas possam ser executadas. A própria função main deve retornar o valor 0, quando termina
com sucesso. Várias funções matemáticas, por exemplo, são disponibilizadas para o programador na
linguagem C.

<!-- página 3 [OCR] -->
#include <math.h> /* Para usar as funções matemáticas precisamos
incluir suas definições, que estão em math.h. */

tidefine PI 3.1415926536

int main()

{
double a,b;
int c,d,e;
a= 1.0;
b = exp(a); /* atribui 2.718282 para b */
a = 4.0;
a = pow(a,3.0); /* atribui 64.0 para a */
b = 10g10(100); /* atribui 2.000000 para b */
a = sin(PI/4.0); /* atribui 0.707107 para a */
c= 5;
d = 3;
e = c/d; /* atribui 1 para c - divisão inteira */
e = cid; /* atribui 2 para e - resto da divisão inteira */
return(0);
}

Além de incluir as definições de math.h, as funções matemáticas precisam ser compiladas e incorpo-
radas ao programa executável. Isto é feito com o comando “gec exemplo.c -o exemplo -Im”. Outros
exemplos de funções matemáticas são: raíz quadrada sqrt (x), cosseno cos(x), arco tangente atan(x),
logarítmo Neperiano In(x), e arredondamento round(x). Essas funções podem ser encontradas em
qualquer manual da linguagem C ou através do comando man para aqueles que usam linux.

5 Endereço das variáveis

Toda variável x tem um endereço na memória que pode ser acessado com &z. Este endereço é
necessário em algumas funções de entrada de dados, que veremos a sequir.