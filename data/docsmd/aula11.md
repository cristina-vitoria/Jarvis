# Aula11

<!-- página 1 -->
# MC102 - Algoritmos e Progra¸c˜ao de Computador
Prof. Alexandre Xavier Falc˜ao
11◦Aula: Opera¸c˜oes com Vetores
## 1
## Opera¸c˜oes com vetores
Uma das aplica¸c˜oes para vetores ´e a representa¸c˜ao de sinais e fun¸c˜oes discretas. Em telecomunica¸c˜oes,
por exemplo, ´e muito comum obter amostras de um sinal el´etrico, que representa um trecho de um
sinal de voz, e armazen´a-las em um vetor. O processamento do sinal no computador ´e essencialmente
uma seq¨uˆencia de opera¸c˜oes aplicadas ao vetor. O sinal processado pode ent˜ao ser transformado de
volta em sinal el´etrico, e por sua vez transformado em som.
1.1
Reﬂex˜ao
Seja f1(x) um sinal discreto deﬁnido no intervalo de inteiros [0, n) = 0, 1, . . . , n −1. Assumimos que
f1(x) = 0 fora deste intervalo. A reﬂex˜ao f2(x) = f1(−x) do sinal em torno da origem ´e um sinal
deﬁnido no intervalo (−n, 0], com valores nulos fora deste intervalo (Figura 1). Muito embora as
amostras desses sinais estejam deﬁnidas em intervalos diferentes do eixo x, ambos s˜ao armazenados
em vetores com n posi¸c˜oes, cujos ´ındices variam de 0 a n −1. O problema consiste em encontrar
primeiro a rela¸c˜ao entre x e os ´ındices i e j dos vetores de f1[i] e f2[j], que ´e diferente para cada
caso, e depois encontrar a rela¸c˜ao entre i e j. Para f1[i], i = x = 0, 1, . . . , n −1, mas para f2[j],
j = −x + n −1 e x = −n + 1, −n + 2, . . . , 0.
Ent˜ao, a rela¸c˜ao entre i e j ´e j = −i + n −1,
i = 0, 1, . . . , n −1, j = n −1, n −2, . . . , 0; e a reﬂex˜ao implica em fazer f2[−i + n −1] ←f1[i].
...
−n+1
−1
−2
x
f2(x)=f1(−x)
x
f1(x)
...
n−1
...
...
f1[i],i=0,1, ..., n−1.
f2[j],j=0,1,...,n−1.
Figura 1: Reﬂex˜ao de um sinal discreto.

<!-- página 2 -->
#include <stdio.h>
#define N 100
int main()
{
float f1[N],f2[N];
int i,n;
printf("Entre com o n´umero de amostras\n");
scanf("%d",&n);
printf("Entre com os valores das amostras\n");
for (i=0; i < n; i++)
scanf("%f",&f1[i]);
/* calcula a reflex~ao */
for (i=0; i < n; i++)
f2[-i+n-1] = f1[i];
printf("Vetor resultante\n");
for (i=0; i < n; i++)
printf("%5.2f ",f2[i]);
printf("\n");
return(0);
}
1.2
Convolu¸c˜ao
A convolu¸c˜ao entre dois sinais discretos f1(x), x ∈[0, n1), e f2(x), x ∈[0, n2), ´e um terceiro sinal
discreto f3(x), x ∈[0, n1 + n2 −1), com n1 + n2 −1 amostras (Figura 2).
f3(x)
=
x′=+∞
X
x′=−∞
f1(x′)f2(x −x′).
(1)
O sinal f3(x) ´e calculado pela soma do produto entre f1(x′)f2(x −x′) ao deslizarmos f2(x −x′) sobre
o eixo x′ para cada deslocamento x. No entanto, f3(x) ̸= 0 apenas para x ∈[0, n1 + n2 −1). Sendo i,
j, k os ´ındices dos vetores f1[i], f2[j] e f3[k], respectivamente, temos que x′ = i, x = k, e x −x′ = j
(i.e., j = k −i).
A convolu¸c˜ao pode ser usada para ﬁltrar o sinal, suavizando transi¸c˜oes abruptas (e.g. f2(x) =
{1, 2, 1}), detectando transi¸c˜oes abruptas (e.g. f2(x) = {−1, 2, −1}), ou real¸cando essas transi¸c˜oes
(e.g. f2(x) = {1, −1}). Na maioria dos casos, no entanto, usa-se f2(x + n2/2) deslocada para que
a origem x = 0 ﬁque na amostra do meio. Isto apenas desloca o sinal f3(x) para f3(x + n2/2), n˜ao
afetando o algoritmo nem o conte´udo do vetor.

<!-- página 3 -->
#include <stdio.h>
#define N1 100
#define N2 9
#define N3 110
int main()
{
float f1[N1],f2[N2],f3[N3];
int i,j,k,n1,n2,n3;
printf("Entre com o n´umero de amostras\n");
scanf("%d",&n1);
printf("Entre com os valores das amostras\n");
for (i=0; i < n1; i++)
scanf("%f",&f1[i]);
printf("Entre com o n´umero de coeficientes do filtro\n");
scanf("%d",&n2);
printf("Entre com os valores dos coeficientes\n");
for (i=0; i < n2; i++) /* ler f2 sem reflex~ao */
scanf("%f",&f2[i]);
n3 = n1+n2-1;
/* calcula a convolu¸c~ao */
for (k=0; k < n3; k++) {
f3[k]=0.0;
for (i=0; i < n1; i++){
j = k-i; // reflexao
if ((j >= 0)&&(j < n2))
f3[k] += f1[i]*f2[j];
}
}
printf("Vetor resultante\n");
for (k=0; k < n3; k++)
printf("%5.2f ",f3[k]);
printf("\n");
return 0;
}

<!-- página 4 -->
f3(x)
x
x´
−1
f2(−x´)
f1(x´)
x´
x´
f2(x´)
x´
x
x−1
f2(x−x´)
Figura 2: Convolu¸c˜ao entre sinais discretos.
1.3
Correla¸c˜ao e correla¸c˜ao circular
A correla¸c˜ao entre dois sinais discretos ´e deﬁnida como
f3(x)
=
x′=+∞
X
x′=−∞
f1(x′)f2(x + x′).
(2)
Sua implementa¸c˜ao ´e muito parecida com a da convolu¸c˜ao, exceto que j = i + k. A correla¸c˜ao ´e
normalmente usada para alinhar (registrar) dois sinais, minimizando a distˆancia entre eles. Neste
caso, por´em, ela deve ser calculada de forma circular. Supondo que f1(x) e f2(x) possuem o mesmo
n´umero n de amostras (caso contr´ario, podemos completar com zeros o sinal com menos amostras),
a correla¸c˜ao circular ´e deﬁnida por:
f3(x)
=
x′=n−1
X
x′=0
f1(x′)f2((x + x′)%n).
(3)
Note que, f3(x) ̸= 0 para x ∈[0, n), e os ´ındices i, j, k de f1[i], f2[j], e f3[k] ﬁcam x = k, x′ = i,
e j = (i + k)%n. O valor m´aximo de f3(x) representa o deslocamento circular x necess´ario para o
alinhamento de f2(x) com f1(x).

<!-- página 5 -->
#include <stdio.h>
#define N 100
int main()
{
float f1[N],f2[N],f3[N];
int i,j,k,n,imax;
printf("Entre com o n´umero de amostras dos sinais\n");
scanf("%d",&n);
printf("Entre com os valores das amostras do 1o. sinal\n");
for (i=0; i < n; i++)
scanf("%f",&f1[i]);
printf("Entre com os valores das amostras do 2o. sinal\n");
for (i=0; i < n; i++)
scanf("%f",&f2[i]);
/* calcula a correla¸c~ao circular */
for (k=0; k < n; k++) {
f3[k]=0.0;
for (i=0; i < n; i++){
f3[k] += f1[i]*f2[(i+k)%n];
}
}
printf("Vetor resultante\n");
for (i=0; i < n; i++)
printf("%5.2f ",f3[i]);
printf("\n");
/* alinha o vetor f2 com f1 */
imax = 0;
for (i=1; i < n; i++) /* encontra o m´aximo */
if (f3[i] > f3[imax])
imax = i;
for (i=0; i < n; i++) /* alinha f2 copiando o resultado para f3 */
f3[i] = f2[(i+imax)%n];
printf("Vetor alinhado\n");
for (i=0; i < n; i++)
printf("%5.2f ",f3[i]);
printf("\n");
return 0;
}

<!-- página 6 -->
## 2
## Exerc´ıcios
1. O histograma de um sinal discreto f(x) com n amostras e L valores inteiros no intervalo [0, L−1]
´e uma fun¸c˜ao discreta h(l), l = 0, 1, . . . , L −1, onde h(l) ´e o n´umero de ocorrˆencias do valor
f(x) = l, para x = 0, 1, . . . , n−1. Escreva um programa para calcular o histograma de um sinal
discreto.
2. Seja p[i], i = 0, 1, . . . , n −1, um vetor que armazena em cada posi¸c˜ao i o coeﬁciente ai de um
polinˆomio de grau n −1: a0 + a1x1 + . . . + an−1xn−1. Fa¸ca um programa para ler um dado
polinˆomio em p e avaliar seus valores para diferentes valores de x lidos da entrada padr˜ao.