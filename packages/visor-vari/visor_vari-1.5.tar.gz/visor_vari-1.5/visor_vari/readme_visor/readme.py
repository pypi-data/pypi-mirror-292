
print("\
\n\
Para que pueda emplear la libreria visor_vari \n\
usted deberia traer la clase Super_tabla del \n\
modulo 'variables_valores' que se encuentra en \n\
la ruta: visor_vari.mas_bajo_nivel \n\
o en su defecto traerse el objeto 'refer' de ese \n\
modulo, que es un objeto ya formado alli. \n\
\n\
Con ese objeto usted podra guardar su variable \n\
en cualquier instancia. A usted, la libreria le \n\
proporciona (81) instancias para guardar diferentes \n\
valores. \n\
Comprendida desde 'self.selda_0' \n\
hasta 'self.selda_80' \n\
Sirvase usar la que usted prefiera \n\
\n\
Cuando quiera ver sus datos recogidos \n\
(en cierto punto de la ejecucion de su programa) \n\
deberá hacer la llamada a la funcion 'gentil' \n\
que se encuentra en el modulo 'visorquipus' \n\
del mismo paquete 'visor_vari'. \n\
Por supuesto, tambien deberá hacer \n\
esta importacion antes, en su propio modulo. \n\
la funcion 'gentil' no recibe agumentos. \n\
\n\
''' Ejemplo de ejecución ''' \n\
\n\
from visor_vari.mas_bajo_nivel.variables_valores import refer \n\
from visor_vari.visorquipus import gentil \n\
\n\
a= 10 \n\
b= 15 \n\
\n\
refer.selda_0= a \n\
refer.selda_1= b \n\
\n\
gentil() \n\
\n\
refer.selda_0= 43   # Se modifica el valor internamente \n\
                    # quizas al presionarse un boton. \n\
\n\
c= 17               # Se hacen presente otros valores \n\
refer.selda_41= c   # y... tambien se quieren ver. \n\
\n\
gentil() \n\
\n\
Como podra darse cuenta 'visor_vari' aqui, detecta los \n\
cambios que puedan darse en 'self.selda_0' que es \n\
en su programa la variable 'a'. \n\
En la linea donde se le asigna el valor (43) a esa variable \n\
estamos dando a entender \n\
que la variable podria modificarse (internamente) \n\
Porque... por ejemplo: \n\
En el trayecto de ejecucion del programa \n\
se ejecuto una funcion que la modifico, o porque se \n\
refresco (reseteo la variable) al haber entrado a \n\
una seccion que hace tal cosa, o porque usted se \n\
encuentra usando tkinter y quedo la ventana (tk) \n\
esperando una entrada y usted presiono algun boton \n\
que ingreso ese valor (43) a la variable. \n\
yo coloco el 'refer.selda_0= 43' solo para \n\
indicar el cambio. \n\
Pero es su programa como tal, el que se encuentra \n\
realizando cambios, \n\
que usted por supuesto quiere ver con mayor detalle. \n\
Esos cambios podra verlos posteriormente \n\
en la segunda llamada a la funcion 'gentil' en este ejemplo. \n\
\n\
La funcion gentil como usted sabra \n\
podra llamarla cuantas veces quiera.\n\
\n\
Para efectos practicos... donde necesite \n\
hacer revicion de alguna variable coloque \n\
'gentil()', pero antes de eso una funcion. \n\
Que debera crear usted, con el nombre que \n\
usted mismo quiera y en ella, haga las \n\
actualizaciones del objeto/imagen refer. \n\
Por ejemplo, la de: \n\
selda_0= x \n\
selda_1= y \n\
selda_2= z \n\
... \n\
Esto garantizara \n\
que se le este mostrando, \n\
la configuracion de las variables, \n\
para este momento de la ejecucion, \n\
en este caso practico. \n\
Pero trabajar asi con 'viso_vari' le permite tambien, \n\
que la funcion, la pueda usar en otros puntos. Sin\n\
tener que indicar una por una, las variables que\n\
se quieran ver. \n\
Evitando asi, hacer indistinguible su propio codigo \n\
del de visor_vari \n\
")

