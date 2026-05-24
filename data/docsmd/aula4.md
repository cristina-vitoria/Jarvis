# Aula4

<!-- página 1 [OCR] -->
MC102 - Algoritmos e Progração de Computador

Prof. Alexandre Xavier Falcão

4º Aula: Entrada de dados padrão e saída de dados padrão.

Comandos de entrada e saída são usados para fornecer números e caracteres que serão armazenados
em variáveis na memória primária. Vamos aprender, inicialmente, apenas os comandos scanf e printf
de leitura e escrita, respectivamente.

1 Entrada padrão de dados

O teclado é o dispositivo padrão para entrada de dados. O comando scanf ler números e caracteres
digitados no teclado da seguinte forma:

scanf ("%d" ,&a) ;

hy?

onde “a” é uma variável inteira e “&a” é o endereço em memória da variável “a”.

Cada tipo de variável requer um símbolo específico de conversão. Por exemplo, “%d” indica
conversão da entrada para um valor inteiro. O símbolo “%d” pode ser usado com variáveis int, short,
unsigned short, unsigned char; o símbolo “%u” é usado para unsigned int; o símbolo “%c” para char;
o símbolo “%s” para char e cadeias de caracteres; o símbolo “%f” para float; e o símbolo “%lf” para

double. Exemplo:

#include<stdio.h> /* Deve ser incluída para scanf e printf */

int main()

{
int a;
float b;
char c;
double d;
unsigned int e;
unsigned char f;
short g;
unsigned short h;

printf("Digite um inteiro: ");
scanf ("%d" ,&a) ;

printf("Digite um float: ");
scanf("/f",&b) ;

printf ("Digite um caracter: ");

<!-- página 2 [OCR] -->
scanf(" Kc",&c); /* Kc só funcionou com espaço em branco na
frente. Outra opção é usar hs */

printf ("Digite um double: ");

scanf("41f",&d) ;

printf("Digite um inteiro sem sinal: ");

scanf ("%u" ,&e) ;

printf("Digite um inteiro sem sinal de 0 a 255: ");

scanf("/d" ,&f) ;

printf("Digite um short: ");

scanf("%d" ,&g) ;

printf("Digite um short sem sinal: ");

scanf("%d" ,&h) ;

return(0);

2 Saída padrão de dados

A tela é o dispositivo padrão para saída de dados. O comando printf apresenta números e caracteres
na tela da seguinte forma:

printf("%d",a); /* Mostra o conteúdo da variável ‘‘a’’. */

A simbologia de conversão é a mesma usada no scanf. Esta saída também pode ser formatada
indicando o número de dígitos do número.

#include<stdio.h> /* Deve ser incluída para scanf e printf */

int main()
{
int a=9,b=800;
float c=20.9176,d=-1.4219;

/* An pula linha, 3 indica o número de dígitos (incluindo o sinal,
se houver), 5 indica o número de dígitos total (incluindo o
sinal, se houver) e 2 o número de dígitos após o ponto. */

printf("\n a=%3d,\n b=%3d,\n c=%5.2f, An d=%45.2f.\n",a,b,c,d);
return(0);

}

A saida do programa sera:

a= 9, /* alinha pela direita com espaços em branco à esquerda do número. */
b=800,

c= 20.92, /* arredonda para cima. */

d= -1.42. /* arredonda para baixo. */

<!-- página 3 [OCR] -->
3 Exercícios

1. Escreva um programa para converter temperaturas de Celsius para Farenheit usando a entrada
padrão e a saída padrão para obter e mostrar as temperaturas, respectivamente. Repita o
exercício para converter de Farenheit para Celsius.

2. Escreva um programa para trocar os conteúdos de duas variáveis inteiras, x e y, usando uma
terceira variável z. Leia os valores de x e y da entrada padrão e apresente os resultados na saída
padrão. Repita o exercício sem usar a terceira variável z.