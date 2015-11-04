# smd_gui

""" Suspension length and force plots - matplotlib
    Cartoon - Tkinter Canvas"""

import tkinter as Tk

from numpy import arange, sin, pi

# matplotlib including mpl into tkinter bits
import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler

from matplotlib.figure import Figure


# "internal" import of config (global vars)
import smd_cfg


class SuspPlot():
    """ matplotlib plots"""

    #TODO: change the init to blank plot
        #  then def a new fn which plots telem data from the relevant Suspension.record

                      #(arr, arr, arr, tk frame)
    def __init__(self, car, root):

                     
        self.all_struts = car.all_struts
        self.applied_force = car.applied_force
        self.opposite_applied_force = car.opposite_applied_force

        #TODO: check, is this iffy, cleaner way possible?
        self.lst_of_applied_forces = [self.applied_force, self.opposite_applied_force]
        self.root = root

        self.my_frame = Tk.Frame (self.root, width = 600, height = 400, background = "white") ##TODO - check this is displaying

        self.f = Figure(figsize=(5,4), dpi=100)
        self.a = self.f.add_subplot(311) #length vs time
        self.b = self.f.add_subplot(312) #force on road vs time
        self.c = self.f.add_subplot(313) #app force vs time

        self.lst_of_colours = ["r", "b"]
        self.i = 0
        for strut in self.all_struts:
            self.a.plot(strut.record["time"], strut.record["length"], self.lst_of_colours[self.i])
            self.i = self.i+1
        

        self.a.set_xlabel("time/s") 
        self.a.set_ylabel("Length /m")
        self.a.set_title("Suspension Length Plot")


        self.i = 0
        for strut in self.all_struts:
            self.b.plot(strut.record["time"], strut.record["force_on_road"], self.lst_of_colours[self.i])
            self.i = self.i+1
            
        self.b.set_xlabel("time/s")
        self.b.set_ylabel("Force /N")
        self.b.set_title("Suspension Force Plot")

    
        self.i = 0
        for strut in self.all_struts:
            #DEBUGGING
            print( "len of time =", len(strut.record["time"]) )
            print( "len of lst applied forces =", len(self.lst_of_applied_forces[self.i]) )

            #special case when model not yet run (i.e. program first opened)
            #plot 0,0 i.e. nothing proper, jsut on epoint on origin
            if len(strut.record["time"]) != len(self.lst_of_applied_forces[self.i]):
                print("lists in smd_gui not same length to plot")
                
                    
            else:     
                self.c.plot(strut.record["time"], self.lst_of_applied_forces[self.i], self.lst_of_colours[self.i])

            self.i = self.i+1
        
        self.c.set_xlabel("time/s")
        self.c.set_ylabel("Force /N")
        self.c.set_title("Applied Force Plot (load transfer etc)")


        # a tk.Drawing Area
        self.canvas = FigureCanvasTkAgg(self.f, master=self.my_frame)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)  ###TODO - Tk has no attr "TOP"... maybe try packing to Frame

        self.toolbar = NavigationToolbar2TkAgg( self.canvas, self.my_frame )
        self.toolbar.update()
        #self.canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1) 

        ##TODO:  may need to put all this in a frame, frame has self. root as master, then canvas has self. frame as master
        ## then in main prog outside of this class, can .pack or .grid the frame as a whole to position everything in one go


class SuspDisplay():
    """TKinter cartoon of 2 suspension struts"""

    #TODO: again, pass in array of all struts, init shoudl draw start positins only                                     

    def __init__(self, car, root):

            #TODO : DONE-CHECK might be better to make things like max_time global between modules
            # can't just "global" this, need a config.py module
            # http://effbot.org/pyfaq/how-do-i-share-global-variables-across-modules.htm
        
        self.all_struts = car.all_struts
        
        #global max_time  #TODO: unnecessary to create "self" version of globals.
        #self.max_time = smd_config.max_time

        #global time_step
        #self.time_step = smd_config.time_step


        
        
        self.root = root
        self.my_frame = Tk.Frame (self.root, width = 600, height = 500)
        
        self.my_canvas = Tk.Canvas(self.my_frame, width = 600, height = 500, background = "white" )

        self.ground_height = 100 # number of pixels for bottom of strut leg line

        self.body_length = 500 # in pix##TODO: follow this up, deleting numbers in expressions, replace with this var
        self.scale = 200 # scale strut length by this number of pix
        
        for strut in self.all_struts:
            strut.line = StrutLine(strut, self)
            

            #TODOTODOTODO, similar techinque to input gui each strut "has-a" input box.
            # in this case, each strut "has-a" visual representation ( a line)

        self.susp_line_1 = self.my_canvas.create_line( 100, 500, 100, (500-self.susp_length_1), fill = "red", width = 20 ) 
        self.susp_line_2 = self.my_canvas.create_line( 500, 500, 500, (500-self.susp_length_2), fill = "blue", width = 20 )

        self.body_line = self.my_canvas.create_line( 100, (500-self.susp_length_1), 500, (500-self.susp_length_2), fill = "black", width = 10)

        self.my_canvas.grid(row = 0, column =0)

        self.anim_button = Tk.Button(master = self.my_frame, text = "Animate", height = 6, width = 12, \
                                     activebackground = "red", repeatdelay = 500, repeatinterval = 25, \
                                     command = self.animate)
        self.anim_button.grid(row = 1, column = 0)

        
# TODO: again, import strut1.record etc and plot data from here.
    def animate(self): 

        #TODO, as above, check if some things best as class vars.
        
        #careful, can't have 1 ms redraw freq, of monitor is not 1000 Hz!!!
        anim_frame_freq = 20 #ms between frame updates
    
        for index in range(0, int(smd_cfg.max_time/smd_cfg.time_step),1):

            if (index%anim_frame_freq == 0):
            
                self.susp_length_1 = 200*(self.lst_length_1[index])
                self.susp_length_2 = 200*(self.lst_length_2[index])

                #delay between animating (i.e. framerate)

                self.my_canvas.after(anim_frame_freq) #
                
                self.my_canvas.coords(self.susp_line_1, 100, 500, 100, 500-self.susp_length_1 )
                self.my_canvas.coords(self.susp_line_2, 500, 500, 500, 500-self.susp_length_2 )
                self.my_canvas.coords(self.body_line, 100, (500-self.susp_length_1), 500, (500-self.susp_length_2))
                self.my_canvas.update()

        # OBSOLETE cmd line interface anim, before gui button coded
        #while True:
         #   animate_keypress = input("enter n to quit or any other key to animate")
          #  if(animate_keypress == "n"):
           #     break
            #else:
             #   SuspDisplay.animate(self)

class StrutLine(): # the line that represents a strut in the animation TODO: fully implement

    def __init__ (self, strut, master):

        self.strut = strut
        self.master = master

        # TODO: clean up temp bodge since matplotlib and tk canvas lines use shorthand or full colour name
        # maybe a dict in the cfg file "common name - tk name- mpl name" numpy array probably better.

        if self.strut.colour == "r":
            self.colour = "red"
        elif strut.colour == "b":
            self.colour = "blue"

        # TODO: only want x "plus body length if rear strut""
        #DEBUG - when prog first started, record.["length"] = []
        print("SMD_GUI strut len =", self.strut.record["length"]) 
        self.line = self.master.my_canvas.create_line( self.master.ground_height, self.master.body_length,
                                                       self.master.ground_height, (self.master.scale*(self.master.body_length-self.strut.record["length"][0])),
                                                       fill = self.colour, width = 20 )


        #####need getter and setter etc
    
