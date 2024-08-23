
""" Ventana principal del visor de variables """


"========================================================"

import tkinter as tk
# Depura: visor_vari.
from visor_vari.mas_bajo_nivel.variables_valores import ini
from visor_vari.control import ver_registro

"========================================================"

class E_lenguaje_quipus:

    "......... Inicializando .........."

    def __init__(self, acaso, sup_vent):
        
        self.acaso= acaso
        self.ventana= sup_vent
        self.iniciotekinte()

    def iniciotekinte(self):

        if self.acaso == True:
            
            ini.objeto_tk= tk.Toplevel(self.ventana)
            
            ini.objeto_tk.geometry("200x25")
            ini.objeto_tk.title ("diseñemos programas")

            self.primer_marco= tk.LabelFrame(ini.objeto_tk, bd= 0)
            self.primer_marco.pack(expand= True, fill= tk.BOTH)

            self.boton_muestra()

        else:
            objeto= tk.Tk()
            ini.objeto_tk= objeto
            
            objeto.geometry("200x25")
            objeto.title ("diseñemos programas")

            self.primer_marco= tk.LabelFrame(objeto, bd= 0)
            self.primer_marco.pack(expand= True, fill= tk.BOTH)
            
            self.boton_muestra()
            
            objeto.mainloop()
    
    def boton_muestra (self):
        
        self.panel_control= tk.LabelFrame(self.primer_marco)
        self.panel_control.pack(anchor= "w")

        boton_para_crear_nuevo_carapter= tk.Button (self.panel_control, text= "mostrar carapteres", command= self.mirar_las_varis)
        boton_para_crear_nuevo_carapter.config(padx= 24)
        boton_para_crear_nuevo_carapter.pack ()

    def mirar_las_varis(self):
        ver_registro(tk)

def gentil(ventana= False, macro= None):
    E_lenguaje_quipus(ventana, macro)

