# Aula5

<!-- página 1 [OCR] -->
MC102 - Algoritmos e Progração de Computador

Prof. Alexandre Xavier Falcão

5º Aula: Comando condicional.

Em muitas tarefas de programação, desejamos que o computador execute instruções diferentes,
dependendo de alguma condição lógica. Por exemplo, no cálculo das raízes de uma equação de
segundo grau, teremos instruções diferentes para raízes imaginárias e para raízes reais.

1 Estrutura condicional simples

Um comando condicional simples é aquele que permite a escolha de um grupo de instruções (bloco
de comandos) quando uma determinada condição lógica é satisfeita.

if (expressão) {
bloco de comandos

}

#include<stdio.h>

int main()
{

int a,b;
printf("Digite a eb: ");

scanf("4d 4d",&a,&b); /* podemos ler mais de uma variável por linha,
deixando um espaço em branco entre os números. */

if (a > b) { /* 0 bloco de comandos deve ser delimitado por
chaves. Neste caso, como temos um único comando, as

chaves são opcionais. A instrução só será executada,

caso o valor de ‘‘a’’ seja maior que o valor de

“bp”? (ou b < a). */

printf("%d é maior que %d\n",a,b);

if (a<=b) /* ou b >= a */
printf("%d é menor ou igual a %d\n",a,b);

if (a == b) /* NUNCA FAÇA a=b */

<!-- página 2 [OCR] -->
printf ("4d é igual a %d\n",a,b);

if (a != b)
printf("%d é diferente de %d\n",a,b);

return(0);

}

A condição lógica também pode ser resultado de uma expressão lógica mais complicada.

#include<stdio.h>

int main()
{

int a,b,c;

printf("Digite a, b, e c: ");
scanf("%d Kd %d" ,&a,&b,&c);

if ((a > b)&&(b > c))
printf("%d é maior que Kd e hdin",a,b,c);

if (((a == b)&&(b < c)) II
(Ca == c)&&(c < b))){
printf("%d é igual a kd e menor que %d\n",a,b,c);
printf("ou hd é igual a kd e menor que %d\n",a,c,b);
}

return (0) ;

2 Estrutura condicional composta

Um comando condicional composto é aquele que permite a escolha de um bloco de comandos, quando
uma determinada condição é satisfeita, e de um outro bloco de comandos quando a condição não é
satisfeita.

if (expressão) {
bloco 1 de comandos
} else {
bloco 2 de comandos

}

#include<stdio.h>

int main()

{

<!-- página 3 [OCR] -->
int a,b;

printf("Digite ae b: ");
scanf ("4d 4d" ,&a,&b) ;

if (a>b) {

printf("%d é maior que %d\n",a,b);

+ else { /* Essas chaves são opcionais, pois o bloco
tem um único comando.*/

printf("%d é menor ou igual a %d\n",a,b);

}

return (0) ;

}
Note que, um bloco de comandos pode ter outros comandos condicionais.

#include<stdio.h>

int main()
{

int a,b,c;

printf("Digite a, b, ec: ");
scanf ("4d hd fd" ,&a,k&b,&c) ;

if (a > b) { /* Neste caso, as chaves são obrigatórias. */
printf("%d é maior que %d\n",a,b);
if (b > c)
printf("%d é maior que %d\n",b,c);
else /* b <= c */
printf("%d é menor ou igual a %d\n",b,c);
} else { /* a <= b */
printf("%d é menor ou igual a %d\n",a,b);
if (b < c)
printf("%d é menor que %d\n",b,c);
else /* b >= c */
printf("%d é maior ou igual a %d\n",b,c);

return(0);

3 Exercícios

1. Escreva um único programa para converter entre Celsius e Farenheit, e vice-versa.

2. Escreva um programa para calcular o maior número entre três números lidos.