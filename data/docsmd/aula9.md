# Aula9

<!-- página 1 -->
# MC102 - Algoritmos e Progra¸c˜ao de Computador
Prof. Alexandre Xavier Falc˜ao
9◦Aula: Vetores
## 1
## Vetores
At´e agora, vimos que uma vari´avel simples est´a associada a uma posi¸c˜ao de mem´oria e qualquer
referˆencia a ela signiﬁca um acesso ao conte´udo de um peda¸co de mem´oria, cujo tamanho depende de
seu tipo. Nesta aula iremos ver um dos tipos mais simples de estrutura de dados, denominada vetor,
que nos possibilitar´a associar um identiﬁcador a um conjunto de vari´aveis simples de um mesmo tipo.
Naturalmente, precisaremos de uma sintaxe apropriada para acessar cada vari´avel deste conjunto de
forma precisa.
int main()
{
tipo identificador[n´umero de vari´aveis];
}
Antes de iniciarmos, considere que desejamos ler 10 notas de alunos e imprimir as notas acima
da m´edia. Note que para executar a tarefa, precisamos calcular a m´edia primeiro e depois comparar
cada nota com a m´edia. Portanto, precisamos armazenar cada nota em uma vari´avel. Agora imagine
que a turma tem 100 alunos. Como criar 100 vari´aveis sem tornar o acesso a elas algo complicado de
se programar?
Um vetor ´e um conjunto de posi¸c˜oes consecutivas de mem´oria, identiﬁcadas por um mesmo nome,
individualizadas por ´ındices e cujo conte´udo ´e do mesmo tipo. Assim, o conjunto de 10 notas pode ser
associado a apenas um identiﬁcador, digamos nota, que passar´a a identiﬁcar n˜ao apenas uma ´unica
posi¸c˜ao de mem´oria, mas 10.
int main()
{
float nota[10]; /* vetor de 10 vari´aveis do tipo float */
}
A referˆencia ao conte´udo da n-´esima vari´avel ´e indicada pela nota¸c˜ao nota[n −1], onde n ´e uma
express˜ao inteira ou uma vari´avel inteira.
A nota de valor 7.0 na Figura 1, que est´a na quarta posi¸c˜ao da seq¨uˆencia de notas ´e obtida como
nota[3]. Assim, um programa para resolver o problema acima ﬁca:
#include <stdio.h>
int main()

<!-- página 2 -->
{
float nota[10],media=0.0;
int i;
printf("Entre com 10 notas\n");
for (i=0; i < 10; i++) {
scanf("%f",&nota[i]);
media += nota[i];
}
media /= 10.0;
printf("media %5.2f\n",media);
for (i=0; i < 10; i++) {
if (nota[i] > media)
printf("nota[%d]=%5.2f\n",i,nota[i]);
}
return 0;
}
2.5
4.5
9.0
5.5
7.0
8.3
8.7
9.3
10.0
9.0
Figura 1: Vetor de 10 notas representado pelo identiﬁcador nota.
O identiﬁcador ´e uma vari´avel do tipo apontador, cujo conte´udo ´e o endere¸co de mem´oria do
primeiro elemento do vetor. Considere, por exemplo, o trecho de c´odigo abaixo.
int main()
{
int v[5]={7,2,1,4,10}; // inicializa¸c~ao
printf("Endereco de v[0]: %d=%d\n",&v[0],v);
printf("Conteudo de v[0]: %d=%d\n",v[0],*v);
printf("Conteudo de v[1]: %d=%d\n",v[1],*(v+1));
printf("Conteudo de v[4]: %d=%d\n",v[4],*(v+4));
printf("Endereco de v[4]: %d=%d\n",&v[4],(v+4));
return 0;
}
Na mem´oria, os elementos do vetor s˜ao armazenados um ap´os o outro. O endere¸co de v[i] pode ser
obtido por &v[i] ou (v + i), j´a que v guarda o endere¸co de v[0] e, portanto, (v + i) guarda o endere¸co
de v[i]. Ao somarmos (v + i), pulamos na mem´oria i ∗sizeof(int) bytes a partir do endere¸co de v[0].

<!-- página 3 -->
v
v[4]=10
v[1]=2
v[0]=7
v=200
Figura 2: Como o vetor ﬁca armazenado na mem´oria. Os n´umeros ao lado indicam o endere¸co de
mem´oria na pilha. As vari´aveis e os respectivos conte´udos s˜ao indicados nas gavetas.
## 2
## Busca em Vetores
Um problema comum quando se manipula vetores ´e a necessidade de encontrar um elemento com um
dado valor. Uma forma trivial de fazer este acesso ´e percorrer do ´ındice inicial ao ´ındice ﬁnal todos
os elementos do vetor at´e achar o elemento desejado. Esta forma de busca ´e chamada linear, pois no
pior caso o n´umero de compara¸c˜oes necess´arias ´e igual ao n´umero de elementos no vetor.
2.1
Busca Linear
Suponha, por exemplo, que desejamos saber se existe uma nota x no vetor lido.
#include <stdio.h>
int main()
{
float nota[11],x; /* vetor criado com uma posi¸c~ao a mais */
int i;
printf("Entre com 10 notas\n");
for (i=0; i < 10; i++) {
scanf("%f",&nota[i]);
}
while(1) {
printf("Digite a nota procurada ou -1 para sair do programa\n");

<!-- página 4 -->
scanf("%f",&x);
if (x==-1.0)
break;
/* busca linear */
nota[10] = x; /* elemento sentinela */
i = 0;
while (nota[i] != x) /* busca com sentinela */
i++;
if (i < 10)
printf("nota %5.2f encontrada na posi¸c~ao %d\n",nota[i],i);
else
printf("nota %5.2f n~ao encontrada\n",x);
}
return 0;
}
Imagine agora que nosso vetor tem tamanho 1024. O que podemos fazer para reduzir o n´umero de
compara¸c˜oes? Quanto maior for a quantidade de informa¸c˜ao sobre os dados, mais vantagens podemos
tirar para agilizar os algoritmos.
2.2
Busca Bin´aria
A busca bin´aria ,por exemplo, reduz o n´umero de compara¸c˜oes de n para log2(n) no pior caso, onde n
´e o tamanho do vetor. Ou seja, um vetor de tamanho 1024 = 210 requer no pior caso 10 compara¸c˜oes.
No entanto, a busca bin´aria requer que o vetor esteja ordenado. Esta ordena¸c˜ao tamb´em tem um
custo a ser considerado, mas se vamos fazer v´arias buscas, este custo pode valer a pena. A id´eia
b´asica ´e que a cada itera¸c˜ao do algoritmo, podemos eliminar a metade dos elementos no processo de
busca. Vamos supor, por exemplo, que o vetor de notas est´a em ordem crescente.
#include <stdio.h>
typedef enum {false,true} bool;
int main()
{
float nota[10],x;
int i,pos,inicio,fim;
bool achou;
printf("Entre com 10 notas em ordem crescente\n");
for (i=0; i < 10; i++) {
scanf("%f",&nota[i]);

<!-- página 5 -->
}
while(1) {
printf("Digite a nota procurada ou -1 para sair do programa\n");
scanf("%f",&x);
if (x==-1.0)
break;
/* busca bin´aria */
inicio = 0;
fim
= 9;
achou
= false;
while ((inicio <= fim)&&(!achou)){
pos = (inicio+fim)/2;
if (x < nota[pos])
fim = pos-1;
else
if (x > nota[pos])
inicio = pos + 1;
else
achou = true;
}
if (achou)
printf("nota %5.2f encontrada na posi¸c~ao %d\n",nota[pos],pos);
else
printf("nota %5.2f n~ao encontrada\n",x);
}
return 0;
}
Algoritmos para ordenar vetores ser˜ao vistos na pr´oxima aula.