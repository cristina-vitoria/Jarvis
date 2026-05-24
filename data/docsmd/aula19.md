# Aula19

<!-- página 1 [OCR] -->
MC102 - Algoritmos e Progração de Computador

Prof. Alexandre Xavier Falcão

19º Aula: Recursão (cont.)

1 Ordenação por indução fraca

Os algoritmos de ordenação de sequências por seleção, inserção, e permutação podem ser implemen-
tados usando indução fraca. Na ordenação por inserção, ordenamos a sequência até a penúltima
posição e inserimos o último elemento na posição correta da sequência ordenada. Na ordenação por
seleção, selecionamos o maior elemento, colocamos ele na última posição e depois repetimos o processo
para a subsequência terminada no penúltimo. Na ordenação por permutação, o processo é similar.
Os elementos são permutados até que o maior seja o último, e depois repetimos o processo para a
subseqiiéncia terminada no penúltimo.

Por exemplo, a função abaixo ordena de forma recursiva um vetor v de inteiros e de tamanho n
por inserção.

void Insercao(int *v, int n)
{

int i,j; /* varidveis locais */

/* A condição de parada é não fazer nada. Caso contrário: */
if (n>1)1
/* comandos iniciais: vazio */
/* chamada recursiva */
Insercao(v,n-1);
/* comandos finais: insere o último elemento na posição correta. */
i=n-2; j=n-1;
while ( (i >= 0) && (v[i]l > v[j])){
troca(&v [il] ,&v[j]);
i==; jos
>
}

2 Ordenação por indução forte

A vantagem da indução forte é reduzir a complexidade da ordenação de O(n?) para O(nlogn). O
algoritmo mais simples nesta linha é o merge — sort. Este algoritmo subdivide a sequência em duas,
ordena de forma recursiva cada parte, e depois intercala as partes ordenadas.

<!-- página 2 [OCR] -->
/* Considerando que o vetor está ordenado do inicio até o meio e do
meio + 1 até o final, intercala seus elementos para que fique
ordenado do início ao fim. */

void Intercala(int *v, int inicio, int meio, int fim)
{
int i,j,k,vaux[N]; /* Ordenação requer memória auxiliar do mesmo
tamanho da entrada. */

i=inicio;
j=meio+1;
k=inicio;

while ((i<=meio) &&(j<=fim)){
if (vlil <= v[j]{
vaux[k]=v[il;
it+; k++;
Jelsef
vaux [k]=v[j];
jtt; k++;
}
}
for(i=i; i <= meio; i++,k++)
vaux [k]=v [i];
for(j=j; j <= fim; j++,k++)
vaux [k]=v[j];
/* copia de volta para v */
for (i=inicio; i <= fim; i++)
v[il=vaux [i];

}

void MergeSort(int *v, int inicio, int fim)
{

int meio; /* variável local */

/* A condição de parada é não fazer nada. Caso contrário: */
if (inicio < fim) {

/* comando inicial: calcula o meio */

meio = (iniciot+fim)/2;

/* chamadas recursivas */

MergeSort (v,inicio,meio) ;

MergeSort (v,meio+1 ,fim) ;

/* comando final: intercalação */

Intercala(v,inicio,meio,fim);

<!-- página 3 [OCR] -->
Uma desvantagem do algoritmo acima, porém, é a necessidade de memória auxiliar, na função
de intercalação, do mesmo tamanho da entrada. Isto pode ser um problema para sequências muito
grandes.

Outro algoritmo que usa indução forte, tem complexidade O(n log n) no caso médio, e O(n?) no
pior caso, mas não requer memória auxiliar é o quick — sort. Este algoritmo particiona a sequência
em duas partes de tal forma que todos os elementos da primeira parte são menores ou iguais aos da
segunda. A seqiiéncia é ordenada repetindo-se este processo de forma recursiva para cada parte.

void QuickSort(int *v, int inicio, int fim)
{
int p;

if (inicio < fim){
p = Particiona(v,inicio,fim) ;
QuickSort (v,inicio,p);
QuickSort (v,p+i,fim);
}
>

3 Exercícios

1. Escreva as funções de ordenação de forma recursiva, por seleção e por permutação, de um vetor
v com n elementos.

2. Escreva uma função recursiva para ordenar v por partição. Isto é, complete o código do quick —
sort.