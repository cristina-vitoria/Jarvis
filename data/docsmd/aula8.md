# Aula8

<!-- página 1 [OCR] -->
MC102 - Algoritmos e Progração de Computador

Prof. Alexandre Xavier Falcão

8º Aula: Comando Switch.

1 Comando Switch

Frequentemente desejamos evitar aninhar vários comandos if para tratar múltiplas condições. O
comando switch faz este papel verificando o conteúdo de variáveis dos tipos int, char, unsigned int,
unsigned short, short, e unsigned char.

switch (variável) {

case conteúdol:
bloco de comandos
break;

case conteúdo2:
bloco de comandos
break;

case conteúdon:
bloco de comandos
break;

default:
bloco de comandos

}
Suponha, por exemplo, um programa que faz o papel de uma calculadora.

#include <stdio.h>
#include <math.h>

#define PI 3.1415926536
int main()
{

double a,b,c;

char opt;

do {

<!-- página 2 [OCR] -->
printf ("Digite a opção desejada\n") ;
printf("*: multiplicag&o\n") ;
printf("/: divisdo\n");

printf("+: adig&o\n");

printf("-: subtragdo\n") ;

printf("r: raiz quadrada\n") ;
printf("p: poténcia\n") ;

printf("t: tangente\n");

printf("a: arco tangente\n");
printf("x: sair do programa\n") ;

scanf(" %c",&opt) ;

switch(opt) {
case ’*?:
printf("Digite os dois operandos: ");
scanf("%1f Klf",&a,&b);
c=axb;
printf("\n\n %8.41£*%8.41f=%8.41f\n\n",a,b,c);
break;
case ’/?:
printf("Digite os dois operandos: ");
scanf("%1f Klf",&a,&b);
if (b!=0.0)f{
c = a/b;
printf("\n\n %8.41£/%8.41£=%8.41£\n\n",a,b,c);
Jelsef
printf ("inin Operai$Ã£o invA<lida\n\n") ;
}
break;
case ?+?:
printf("Digite os dois operandos: ");
scanf("%1f %1f",&%a,&b) ;
c = atb;
printf ("nin %8.41f+7%8.41f=%8.41f\n\n",a,b,c) ;
break;
case ?-?:
printf("Digite os dois operandos: ");
scanf("%1f Klf",&a,&b);
c=a-b;
printf ("nin %8.41f-%8.41f=%8 .41f\n\n ",a,b,c);
break;
case ’r’:
printf("Digite o número: ");
scanf("%1f",&a);
if (a >= 0)

<!-- página 3 [OCR] -->
c=sgrt(a);
printf ("nin sqrt (%8.41f)=%8.41f\n\n",a,c);
Jelset
c=sgrt(-a);
printf ("inn sqrt (%8.41£)=%8.41f i\n\n",a,c);
}
break;
case ’p’:
printf("Digite os dois operandos: ");
scanf("4,lf %1f",&a,&b) ;
c = pow(a,b);
printf("\n\n pow(%48.41f ,48.41£)=%8.41f\n\n ",a,b,c);
break;
case ’t’:
printf("Digite o ângulo em graus: ");
scanf ("Ylf",&a);
if (((int)a)%90==0.0)
{
b = ((int)a)%360;
if (b < 0.0)
b = 360.0 + b;
if (b==270)
printf("\n\n tan(%f)=-infinito\n\n" ,a);
else
printf (nin tan(/f)=+infinito\n\n",a) ;
telse{
b = PI*a/180.0;
c = tan(b);
printf("\n\n tan(48.41f)=%8.41f\n\n ",a,c);
}
break;
case ’a’:
printf("Digite o arco: ");
scanf("%1f" ,&a) ;
c = atan(a);
c = c*180.0/PI;
printf("\n\n atan(48.41f)=48.41f graus\n\n",a,c);
break;
case ’x’:
break;
default:
printf ("inn Opção invdlida\n\n") ;
}
} while (opt != ’x’);

return(0);

<!-- página 4 [OCR] -->
Continue o programa acrescentando outras funções.
Outro exemplo é a geração de menus de programas que envolvem vários comandos switch aninha-
dos.

#include <stdio.h>

int main()
{
char opti,opt2;

do

{
printf("Digite a opção desejada:\n");
printf("0 - Conta corrente\n");
printf("1 - Aplicagdes\n") ;
printf("2 - Cancelar a operag&o\n") ;
scanf(" Kc",&opt1);

switch(opti) {
case ’0’:

do {
printf("Digite a opção desejada:\n");
printf("0 - Saldo da conta corrente\n") ;
printf("1 - Extrato da conta corrente\n");
printf("2 - Saque da conta corrente\n");
printf("3 - Voltar para o menu principal\n") ;
printf("4 - Cancelar operag4o\n") ;
scanf(" %c",&opt2) ;

switch(opt2) {

case ’0’:
printf("\n\n Imprime saldo\n\n") ;
break;

case ’1’:
printf("\n\n Imprime extrato\n\n");
break;

case ’2’:
printf("\n\n Digite o valor do saque\n\n") ;
break;

case '3”:
break;

case 74’:
opt2='3";

<!-- página 5 [OCR] -->
optl='2";
break;
default:
printf ("nin Opção invdlida\n\n") ;
}
} while(opt2 != ’3’);
break;

case ?1º:

do {
printf("Digite a opção desejada:\n");
printf("0 - Saldo da aplicag&o\n") ;
printf("1 - Extrato da aplicag&o\n");
printf("2 - Saque da aplicaçãoin");
printf("3 - Voltar para o menu principal\n") ;
printf ("4 - Cancelar operag&o\n") ;
scanf(" 4c", &opt2) ;

switch(opt2) {

case ’0’:
printf("\n\n Imprime saldo\n\n");
break;

case 71’:
printf("\n\n Imprime extrato\n\n") ;
break;

case ’2’:
printf("\n\n Digite o valor do saque\n\n");
break;

case '3?:
break;

case 74’:
opt2='3";
opti="2";

break;

default:
printf ("inin Opção invdlida\n\n") ;

} while(opt2 != 23º);
break;

case ’2?:
break;

default:
break;

<!-- página 6 [OCR] -->
}
} while (opti!=’2’);

return (0);

}