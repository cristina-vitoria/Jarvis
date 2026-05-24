# Aula12

<!-- página 1 -->
# MC102 - Algoritmos e Progra¸c˜ao de Computador
Prof. Alexandre Xavier Falc˜ao
12◦Aula: Vetores Multidimensionais
## 1
## Vetores Multidimensionais
Vetores tamb´em podem possuir m´ultiplas dimens˜oes, se declararmos um identiﬁcador que ´e um vetor
de vetores de vetores de vetores ....
#define N1 10
#define N2 8
.
.
.
#define Nn 50
int main()
{
tipo identificador[N1][N2]...[Nn]
}
No caso bidimensional, por exemplo, o identiﬁcador ´e chamado matriz e corresponde ao que
entendemos no ensino b´asico por matriz (ver Figura 1). Na mem´oria, uma matriz m[3][2] ﬁca como
ilustrado na Figura 2.
#define NLIN 80
#define NCOL 100
int main()
{
int m[NLIN][NCOL];
}
Matrizes podem ser utilizadas para c´alculos envolvendo ´algebra linear, para armazenar imagens, e
muitas outras aplica¸c˜oes. O programa abaixo, por exemplo, soma duas matrizes e apresenta a matriz
resultante na tela.
#include <stdio.h>
#define N 20

<!-- página 2 -->
NCOL−1
## ...
## ...
## ...
## ...
NLIN−1
Figura 1: Matriz m[NLIN][NCOL] de vari´aveis inteiras.
m[1]
m[2]
m[0]
m[2][0]
m[2][1]
m
m[0][0]
m[0][1]
m[1][0]
m[1][1]
Figura 2: Matriz m[3][2] de vari´aveis inteiras.
int main()
{
int m1[N][N],m2[N][N],m3[N][N];
int l,c,nlin,ncol;
printf("Entre com os n´umeros de linhas e colunas das matrizes\n");
scanf("%d %d",&nlin,&ncol); /* assumindo que nlin e ncol < 20 */
printf("Entre com os elementos da matriz 1\n");
for (l=0; l < nlin; l++)
for (c=0; c < ncol; c++)
scanf("%d",&m1[l][c]);
printf("Entre com os elementos da matriz 2\n");
for (l=0; l < nlin; l++)
for (c=0; c < ncol; c++)
scanf("%d",&m2[l][c]);

<!-- página 3 -->
/* soma as matrizes */
for (l=0; l < nlin; l++)
for (c=0; c < ncol; c++)
m3[l][c] = m1[l][c] + m2[l][c];
/* imprime o resultado */
printf("Resultado: \n");
for (l=0; l < nlin; l++) {
for (c=0; c < ncol; c++)
printf("%2d ",m3[l][c]);
printf("\n");
}
return(0);
}
Outro exemplo ´e a multiplica¸c˜ao de matrizes.
#include <stdio.h>
#define N 20
int main()
{
int m1[N][N],m2[N][N],m3[N][N];
int l,c,i,nlin1,ncol1,nlin2,ncol2,nlin3,ncol3;
printf("Entre com os n´umeros de linhas e colunas da matriz 1\n");
scanf("%d %d",&nlin1,&ncol1); /* assumindo que nlin1 e ncol1 < 20 */
printf("Entre com os elementos da matriz a\n");
for (l=0; l < nlin1; l++)
for (c=0; c < ncol1; c++)
scanf("%d",&m1[l][c]);
printf("Entre com os n´umeros de linhas e colunas da matriz 2\n");
scanf("%d %d",&nlin2,&ncol2); /* assumindo que nlin2 e ncol2 < 20 */
if (ncol1 != nlin2){
printf("Erro: N´umero de colunas da matriz 1 est´a diferente\n");
printf("
do n´umero de linhas da matriz 2\n");
exit(-1);
}
printf("Entre com os elementos da matriz 2\n");

<!-- página 4 -->
for (l=0; l < nlin2; l++)
for (c=0; c < ncol2; c++)
scanf("%d",&m2[l][c]);
nlin3 = nlin1;
ncol3 = ncol2;
/* multiplica as matrizes */
for (l=0; l < nlin3; l++)
for (c=0; c < ncol3; c++) {
m3[l][c] = 0;
for (i=0; i < nlin2; i++)
m3[l][c] = m3[l][c] + m1[l][i]*m2[i][c];
}
/* imprime o resultado */
printf("Resultado: \n");
for (l=0; l < nlin3; l++) {
for (c=0; c < ncol3; c++)
printf("%2d ",m3[l][c]);
printf("\n");
}
return(0);
}
## 2
## Lineariza¸c˜ao de Matrizes
Matrizes tamb´em podem ser representadas na forma unidimensional (isto ´e muito comum em processa-
mento de imagens, por exemplo). Considere a matriz da ﬁgura 1. Podemos armazenar seus elementos
da esquerda para direita e de cima para baixo iniciando em [0, 0] at´e [NLIN −1, NCOL −1] em
um vetor de NLIN × NCOL vari´aveis. Para saber o ´ındice i do elemento do vetor correspondente
a vari´avel m[l, c] da matriz, fazemos i = l ∗NCOL + c. O processo inverso ´e dado por c = i%NCOL
e l = i/NCOL. A Figura 3 ilustra a lineariza¸c˜ao de uma matriz m[3][2] em um vetor v[6].
## 3
## Exerc´ıcios
Consulte os livros de ´algebra linear e:
1. Escreva um programa para calcular a transposta de uma matriz.
2. Escreva um programa para calcular o determinante de uma matriz.
3. Escreva um programa para inverter uma matriz.

<!-- página 5 -->
i = c + l*ncol, ncol=2
c = i % ncol
l = i / ncol
m[0][0]
m[0][1]
m[1][0]
m[1][1]
m[2][0]
m[2][1]
m[l][c]
c
l
v[0]
v[3]
v[2]
v[1]
v[5]
v[4]
v[i]
v[i] = m[l][c]
Figura 3: Matriz m[3][2] linearizada em vetor v[6], onde v[i] = m[l][c].