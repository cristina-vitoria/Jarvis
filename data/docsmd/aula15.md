# Aula15

<!-- página 1 -->
# MC102 - Algoritmos e Progra¸c˜ao de Computador
Prof. Alexandre Xavier Falc˜ao
15◦Aula: Registros
## 1
## Registros
Sabemos que vari´aveis compostas s˜ao aquelas que agrupam um certo n´umero de elementos em um
´unico identiﬁcador. No caso de vetores e matrizes, todos os elementos agrupados s˜ao do mesmo tipo
e, portanto, dizemos que s˜ao vari´aveis compostas homogˆeneas.
Em muitas situa¸c˜oes, por´em, desejamos agrupar vari´aveis de tipos diferentes. Um exemplo ´e o
caso em que agrupamos dados sobre uma pessoa/objeto (e.g. RA, nome, e notas de um aluno). O
conceito de registro permite criar um identiﬁcador ´unico associado a todos esses dados. Portanto,
um registro ´e uma vari´avel composta heterogˆenea e seus elementos s˜ao chamados campos.
Diferentes tipos de registro podem ser criados com campos diferentes. Para deﬁnir um tipo de reg-
istro, n´os usamos o comando typedef struct. O programa abaixo deﬁne um tipo de registro, Aluno,
uma vari´avel deste tipo, armazena dados nos seus campos e depois imprime os dados armazenados.
#include <stdio.h>
#include <string.h>
typedef struct _aluno {
int
RA;
char
nome[50];
float nota[3];
} Aluno;
int main()
{
Aluno a; /* vari´avel do tipo Aluno */
a.RA
= 909090;
strcpy(a.nome,"Jose Maria");
a.nota[0] = 3.0;
a.nota[1] = 10.0;
a.nota[2] = 7.0;
printf("%6d %s %5.2f %5.2f %5.2f\n",a.RA,a.nome,a.nota[0],a.nota[1],a.nota[2]);
return 0;
}
Observe que cada campo do registro ´e uma vari´avel de qualquer tipo v´alido, incluindo um outro
registro, vetor, matriz, etc.

<!-- página 2 -->
#include <stdio.h>
typedef struct _ponto {
float x;
float y;
} Ponto;
typedef struct _reta {
Ponto p1;
Ponto p2;
} Reta;
typedef struct _curva { /* pontos consecutivos s~ao interligados
por segmentos de reta. */
Ponto pt[100];
int npts;
} Curva;
int main()
{
Reta r;
Curva c;
int i;
/* ler os pontos da reta */
scanf("%f %f",&r.p1.x,&r.p1.y);
scanf("%f %f",&r.p2.x,&r.p2.y);
/* ler os pontos da curva */
scanf("%d",&c.npts);
for (i=0; i < c.npts; i++)
scanf("%f %f",&c.pt[i].x,&c.pt[i].y);
/* complete o programa para que ele verifique se existe
intersec¸c~ao entre a curva e a reta. */
return 0;
}
Vetores de registros podem ser usados para armazenar base de dados (ou parte da base) em
mem´oria. O programa abaixo ilustra o armazenamento de uma mini base com 5 nomes e 5 telefones.
#include <stdio.h>

<!-- página 3 -->
typedef struct _agenda {
char nome[50];
int
telefone;
} Agenda;
int main()
{
Agenda amigo[5];
char nome_aux[50];
int i,comp;
printf("Entre com os nomes\n");
for (i=0; i < 100; i++) {
fgets(nome_aux,49,stdin);
comp = strlen(nome_aux);
strncpy(amigo[i].nome,nome_aux,comp-1); /* elimina \n */
amigo[i].nome[comp-1] = ’\0’; /* insere \0 por garantia */
}
printf("Entre com os telefones\n");
for (i=0; i < 5; i++)
fscanf(stdin,"%d",&amigo[i].telefone);
for (i=0; i < 5; i++)
fprintf(stdout,"%s: %d\n",amigo[i].nome,amigo[i].telefone);
return 0;
}
## 2
## Exerc´ıcios
1. Complete o programa acima para c´alculo de intersec¸c˜oes entre a reta e a curva.
2. O centro de gravidade (xg, yg) de um conjunto de pontos (xi, yi), i = 0, 1, . . . , n −1, ´e deﬁnido
por:
xg
=
Pi=n−1
i=0
xi
n
yg
=
Pi=n−1
i=0
yi
n
.
Fa¸ca um programa para ler os pontos de uma curva e calcular seu centro de gravidade.
3. Fa¸ca um programa para armazenar 20 nomes e 20 telefones em um vetor de registros, colocar
os elementos do vetor em ordem crescente de nome, e depois imprimir o vetor ordenado.