# Aula21

<!-- página 1 [OCR] -->
MC102 - Algoritmos e Progração de Computador

Prof. Alexandre Xavier Falcão

21º Aula: Alocação dinâmica de memória (cont.)

1 Alocando memória para matrizes

No caso de vetores multidimensionais (e.g. matrizes), devemos alocar um vetor de apontadores,
ie. um apontador por linha, e depois um vetor de elementos para cada linha. Assim como fizemos
para Figura, podemos entender uma matriz como uma estrutura abstrata com operações de criação,
destruição, transposição, leitura e impressão. O programa abaixo ilustra esses conceitos para 0 caso
de matriz representada por um registro. Fica como exercício modificá-lo para representar a matriz
como apontador para registro, assim como fizemos na aula de alocação de memória para vetores.

#include <stdio.h>
#include <malloc.h>

typedef struct matriz (
float **elem; /* matriz de elementos do tipo float */
int nlin,ncol; /* números de linhas e colunas */

> Matriz;

Matriz CriaMatriz(int nlin, int ncol);
Matriz LeMatriz();

Matriz TranspoeMatriz(Matriz m1);
void ImprimeMatriz(Matriz m);

void DestroiMatriz(Matriz m);

Matriz CriaMatriz(int nlin, int ncol)
{

Matriz m;

int 1;

m.elem = (float **)calloc(nlin,sizeof (float *)); /* aloca vetor de
apontadores para
variáveis do
tipo float */
if (m.elem != NULL){
for (1=0; 1 < nlin; 1++)
m.elem[1] = (float *)calloc(ncol,sizeof(float)); /* aloca vetor
de variáveis

<!-- página 2 [OCR] -->
do tipo
float */

m.nlin = nlin;
ncol;

m.ncol

return(m); /* retorna cópia do registro */

}

Matriz LeMatriz()

{
int 1,c,nlin,ncol;
Matriz m;

scanf("%d %d" ,&nlin, &ncol) ;
m = CriaMatriz(nlin,ncol);
for (1=0; 1 < m.nlin; 1++)
for (c=0; c < m.ncol; c++)
scanf("%f",&m.elem[1] [c]);
return (m) ;

}

Matriz TranspoeMatriz(Matriz m1)
{

int l,c;

Matriz m2;

m2 = CriaMatriz(mi.ncol,mi.nlin);
for (1=0; 1 < m2.nlin; 1++)
for (c=0; c < m2.ncol; c++)
m2.elem[1][c] = mi.elem[cl [1];
return (m2) ;

}
void ImprimeMatriz(Matriz m)
{

int 1,c;

for (1=0; 1 < m.nlin; 1++){
for (c=0; c < m.ncol; c++)
printf("%f ",m.elem[1] [c]);
printf("\n");
}
}

<!-- página 3 [OCR] -->
void DestroiMatriz (Matriz m)

t
int 1;

if (m.elem != NULL) {
for (1=0; 1 < m.nlin; 1++) /* desaloca espago do vetor de
variáveis de cada linha */
if (m.elem[1] != NULL)
free(m.elem[1]);
free(m.elem); /* desaloca espaço do vetor de apontadores */
}
}

int main()
{

Matriz mi,m2;

mi = LeMatriz();

m2 = TranspoeMatriz(m1) ;
ImprimeMatriz (m2) ;
DestroiMatriz(m1) ;
DestroiMatriz(m2) ;

return 0;

2 Outras formas de manipulação de apontadores duplos

O programa abaixo ilustra outras formas de manipulação de apontadores duplos, que costumam
confundir bastante os programadores.

#include <malloc.h>
/*----- 1. Manipulação com alocação e desalocação dinâmicas de memória ----*/

float **CriaMatriz(int nlin, int ncol); /* Aloca memória para matriz
representada por apontador
duplo */

void DestroiMatriz(float ***m, int nlin); /* Desaloca memória
atribuindo NULL ao
conteúdo de m. Isto
requer passar o
endereço de m para a
função, pontanto m é um
apontador de apontador

<!-- página 4 [OCR] -->
duplo. Ou seja,
apontador triplo. */

float **CriaMatriz(int nlin, int ncol)
{

float **m=NULL;

int 1;

m = (float **)calloc(nlin, sizeof (float *));
if (m != NULL)
for (1=0; 1 < nlin; 1++)
m[1]=(float *) calloc(ncol,sizeof(float));
return (m) ;

}

void DestroiMatriz(float **+*m, int nlin)
{

int 1;

if (**m != NULL) {
if Cem != NULL) {
for (1=0; 1 < nlin; 1++)
free((*m) [1]);
free(*m) ;
*m = NULL;

void TranspoeMatriz(float m1[2][3], float m2[3][2]) /* passagem por
referéncia */
{

int 1,c;

for (1=0; 1 < 3; 1++)
for (c=0; c < 2; c++)
m2[1][c] = mt[c] [1];

<!-- página 5 [OCR] -->
int main()
{
float **m=NULL;
float mi [2] [3]={{1,2,3},{4,5,6}}; /* inicializa por linha */
float m2[3] [2];
int 1,c;

m = CriaMatriz(2,3);
printf ("Ydlo",m);
DestroiMatriz(&m,2);
printf ("hdin",m);
/* -------------------------- */
for (1=0; 1< 2; 1++) {
for (c=0; c < 3; c++)
printf ("%f ",mi [1] [cl);
printf ("hn");
}
TranspoeMatriz(m1,m2) ;
for (1=0; 1 < 3; 1++) {
for (c=0; c < 2; c++)
printf("%f ",m2[1][c]);
printf("\n");
}

return 0;