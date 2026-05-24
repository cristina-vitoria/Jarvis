# Aula7

<!-- página 1 [OCR] -->
MC102 - Algoritmos e Progração de Computador

Prof. Alexandre Xavier Falcão

7º Aula: Comandos de repetição.

1 Comando for

O comando for é uma simplificação do comando while, onde a inicialização da variável de controle,
a expressão lógica envolvendo a variável de controle e a atualização da variável são especificadas no
próprio comando. Sua implementação é feita com o comando while, portanto seu comportamento é
o mesmo: após a inicialização, a expressão lógica é testada. Se for verdadeira, o bloco de comandos
é executado. Após execução, a variável de controle é atualizada, a expressão lógica é verificada, e o
processo se repete até que a expressão seja falsa.

for (inicialização; expressão; atualização)
{
bloco de comandos

>
Por exemplo, um programa para somar n números fica.

#include<stdio.h>

int main()
{
int n,i;
float soma,num;

printf ("Entre com a quantidade de números a serem somados: ");
scanf("%d" ,&n) ;

for (i=1, soma = 0.0; i <= n; i=i+i, soma = soma + num) {
printf("Digite o Ádo. número:",i);
scanf ("Wf",&num);

}

printf ("0 resultado da soma é %f\n",soma) ;

return (0) ;

}

Uma observação interessante é que a sintaxe para incrementar/decrementar e multiplicar/dividir
valores permite as seguintes variações.

<!-- página 2 [OCR] -->
mesmo que soma = soma + num; */
mesmo que prod = prod * num; */

soma += num; /*
prod *= num; /*

th try th th teh
oooogo

y /= 2; /* mesmo que y = y / 2; */
itt; /* mesmo que i = i+ 1; */
i--; /* mesmo que i = i - 1; */

Outro exemplo é um programa para calcular o maior entre n números lidos da entrada padrão.

#include <stdio.h>
#include <limits.h>

int main()
{

int i,n,num,maior;

printf ("Entre com a quantidade de números: ");
scanf("%d",&n) ;

maior = INT_MIN;
for(i=1; i <= n; i++) {

printf("Entre com um inteiro: ");

scanf ("hd", &num) ;

if (num > maior)

maior = num;

}
printf ("O maior inteiro lido foi %d\n",maior) ;
return(0);

}

Sabendo que o fatorial de um número inteiro n é nx (n — 1) x (n — 2)...1, faça um programa
para calcular o fatorial de um número lido da entrada padrão usando o comando for e apenas duas
variáveis.

O triângulo de Floyd é formado por n linhas de números consecutivos, onde cada linha contém
um número a mais que a linha anterior. Para imprimir o triângulo de Floyd precisamos aninhar um
for dentro do outro.

#include <stdio.h>

int main()
{

int 1,c,nl,i;

printf ("Entre com o número de linhas: ");
scanf ("Jd",&nl);

i=di;
for(l=1; 1 <= nl; 1++) 1

<!-- página 3 [OCR] -->
for(c=1; c<=1; ct+) {
printf("%2d ",i);
itt;

}

printf("\n");

return(0);

}

Outro exemplo que requer dois comandos for aninhados é a impressão de uma tabuada. Faça um
programa para imprimir uma tabuada com n linhas e n colunas.

Observe que existe uma relação entre a integral de uma função continua, sua aproximação pela
somatória de uma função discreta, e a implementação da somatória usando o comando for. Por
exemplo,

T=Tmax—do /2

/ art dd, =D (ax+b)dy, (1)

min T=Tmintde/2

onde Zmin < max, é uma aproximação para a integral da curva, a qual tem maior exatidão para
valores menores de dy > 0. Podemos implementar esta integral como:

#include<stdio.h>

int main()
{

float a,b,xmin,xmax,x,dx,integral;

printf("Entre com os coeficientes a e b da reta y=ax+b: \n");
scanf("Kf Z%f",&a,&b) ;

printf ("Entre com o intervalo [xmin,xmax] para cálculo de área: An");
scanf("%f %f",&xmin, &xmax) ;

printf("Entre com o incremento dx: \n");
scanf ("4f", &dx) ;

integral = 0.0;

for (x=xmin+dx/2.0; x <= xmax-dx/2.0; x=x+dx)
integral += (a*x+b)+dx;

printf ("integral %f\n",integral) ;

return(0);