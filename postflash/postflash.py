#!/usr/bin/env python


import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
import re
from collections import OrderedDict
import csv
import os
import argparse as ap

from .__init__ import __code__,__version__,__author__,__email__


# History
# Summer 2016.  Began project.  RER
# Winter 2016.  Updated to be more python 3 compatible.  added argparse. RER
# Summer 2017.  added limit popup box. RER


class PopupWindow(object):
    def __init__(self,master,default):
        self.value=default
        self.top=tk.Toplevel(master)
        self.top.wm_title("Background Limit")
        
        self.frame=ttk.Frame(self.top)
        self.frame.pack()
        self.l=ttk.Label(self.frame,text="Enter Flash limit (e\u207b)")
        self.l.pack()
        self.e=ttk.Entry(self.frame)
        self.e.insert(tk.END,self.value)
        self.e.pack()
        self.b=ttk.Button(self.frame,text='ok',command=self.cleanup)
        self.b.pack()
    def cleanup(self):
        self.value=float(self.e.get())
        self.top.destroy()

class Postflash(ttk.Frame):
    def blink(self):
        if self.blink_data['visible']:
            self.l['foreground']=self.blink_data['off_color']
        else:
            self.l['foreground']=self.blink_data['on_color']
        self.blink_data['visible']=not self.blink_data['visible']
        self.blink_data['to_blink']=self.after(self.blink_data['rate'],\
                                               self.blink)

    def stop(self):
        self.after_cancel(self.blink_data['to_blink'])
        self.blink_data['visible']=True
        self.l['text']=''

    def bind_compute(self,event):
        self.compute()


    def compute(self,ignore=False):

        # get the exptime
        exptime=self.e.get()
        try: 
            exptime=float(exptime)
        except ValueError:
            if not ignore:
                mb.showerror("Invalid Value","Exposure time must be a number.",\
                             parent=self)
            return

        # get the filter and sky settings
        filt=self.filter.get()
        sky=self.sky.get()        

        if self.data[filt][sky]=='':
            mb.showerror("Invalid Table","Sky background not known.",\
                             parent=self)
            return

        # get the sky brightness
        skyvalue=float(self.data[filt][sky])

        # turn off blinking
        self.stop()

        # compute flash
        flash=self.limit-(skyvalue/1000.)*exptime
        if flash < 0:
            self.l['text']='No Flash Required'
            self.l['foreground']='black'
        else:
            self.l['text']='Required: '+"{:4.1f}".format(flash)+u' e\u207b'
            self.blink()

    def __about__(self):
        mb.showinfo("About "+__code__,__code__+"\nVersion: "+__version__+'\n'+\
                        "Author: "+__author__+'\nEmail: '+__email__,parent=self)

    def __help__(self):
        mb.showinfo("Help "+__code__,"Postflash estimates are computed using Table 2 of Baggett & Anderson (2012).\nhttp://www.stsci.edu/hst/wfc3/documents/ISRs/WFC3-2012-12.pdf",parent=self)


    def __quit__(self):
        quit()

    def __getlimit__(self):
        pu=PopupWindow(self.root,self.limit)
        self.root.wait_window(pu.top)
        self.limit=pu.value
        
        
    def __init__(self,datafile,root=None,def_filt='f438w',limit=12.):
        ttk.Frame.__init__(self,root)

        # save some data and pack the main GUI
        self.limit=limit
        self.pack()


        # set some stuff to the main window
        root.wm_title(__code__)
        root.bind('<Return>',self.bind_compute)
        root.bind('<KP_Enter>',self.bind_compute)

        # do the menu bar info
        menubar=tk.Menu(self)
        filemenu=tk.Menu(menubar,tearoff=0)
        filemenu.add_command(label="About",command=self.__about__)
        filemenu.add_separator()
        filemenu.add_command(label="Quit",command=self.__quit__)
        menubar.add_cascade(label="File",menu=filemenu)
        editmenu=tk.Menu(menubar,tearoff=0)
        editmenu.add_command(label="Limit",command=self.__getlimit__)
        menubar.add_cascade(label="Menu",menu=editmenu)
        
        helpmenu=tk.Menu(menubar,tearoff=0)
        helpmenu.add_command(label='Help',command=self.__help__)
        menubar.add_cascade(label='Help',menu=helpmenu)
        root.config(menu=menubar)

     
        # variable to pick the filter
        self.filter=tk.StringVar()
        

        # set properties of blink
        self.blink_data={}
        self.blink_data['to_blink']=1           #tried =None, but fails
        self.blink_data['off_color']='#e9e9e9'  # gray
        self.blink_data['on_color']='#FF0000'   # red
        self.blink_data['rate']=300             # time in ms
        self.blink_data['visible']=True         # do we show it

        main=ttk.Frame(root)
        main.pack()

        # build a notebook for the filter types
        nb=ttk.Notebook(main)
        lp=ttk.Frame(nb)
        wp=ttk.Frame(nb)
        xp=ttk.Frame(nb)
        mp=ttk.Frame(nb)
        np=ttk.Frame(nb)
        filter_frames={'lp':lp,'w':wp,'x':xp,'m':mp,'n':np}

        nb.add(lp,text='Long')
        nb.add(wp,text='Wide')
        nb.add(xp,text='X-wide')
        nb.add(mp,text='Medium')
        nb.add(np,text='Narrow')
        nb.pack()

        # to count the number of filters per type
        count=[0,0,0,0,0]
        n=5       # maximum number in a column

        # read the data
        self.data=OrderedDict()

        # Nor's idea about hardcoding
#        self.data["f200lp"]= [79.5,105.6,75.8,161.6,135.3,110.7]
#        self.data["f218w"]= [0.8,0.1,1.6,1.6,1.6,1.7]
#        self.data["f225w"]= [1.0,1.0,2.5,2.6,2.5,3.5]
#        self.data["f275w"]= [1.0,0.8,2.2,2.5,2.3,2.8]
#        self.data["f280n"]= [1.5,0.0,1.5,1.5,1.5,1.5]
#        self.data["f300x"]= [1.5,2.8,4.0,4.9,4.4,6.2]
#        self.data["f336w"]= [4.5,2.1,2.9,4.9,3.9,3.6]
#        self.data["f343n"]= [1.5,1.2,2.3,3.4,2.9,2.7]
#        self.data["f350lp"]= [89.7,105.2,74.6,162.6,136.2,106.7]
#        self.data["f373n"]= [2.1,0.3,1.7,1.9,1.8,1.8]
#        self.data["f390m"]= [2.4,2.6,2.6,3.9,3.6,3.1]
#        self.data["f390w"]= [9.1,9.4,8.1,15.8,13.7,10.9]
#        self.data["f395n"]= [2.9,0.7,2.0,2.6,2.5,2.2]
#        self.data["f410m"]= [3.8,2.6,3.3,5.4,4.9,4.1]
#        self.data["f438w"]= [9.1,9.3,8.1,15.6,13.7,10.8]
#        self.data["f467m"]= [3.8,4.3,4.5,8.0,7.1,5.8]
#        self.data["f469n"]= [1.8,0.7,2.0,2.6,2.5,2.2]
#        self.data["f475w"]= [19.1,26.3,20.,41.2,35.8,27.8]
#        self.data["f475x"]= [29.1,42.3,31.2,65.6,56.5,43.8]
#        self.data["f487n"]= [3.5,1.1,2.3,3.2,2.9,2.6]
#        self.data["f502n"]= [2.5,1.3,2.4,3.4,3.2,2.8]
#        self.data["f547m"]= [12.9,14.2,11.4,23.0,19.9,15.7]
#        self.data["f555w"]= [35.0,35.9,26.8,56.2,48.3,37.5]
#        self.data["f600lp"]= [37.9,57.3,40.9,89.9,74.0,58.8]
#        self.data["f606w"]= [37.9,55.1,40.0,85.6,72.5,56.6]
#        self.data["f621m"]= [13.9,15.9,12.5,25.8,21.8,17.4]
#        self.data["f625w"]= [29.1,36.5,26.9,57.3,48.3,38.0]
#        self.data["f631n"]= [None,None,0.9,2.0,1.7,1.3]
#        self.data["f645n"]= [2.9,1.9,2.8,4.4,3.9,3.4]
#        self.data["f656n"]= [3.2,0.4,1.7,2.1,2.0,1.9]
#        self.data["f657n"]= [5.0,2.8,3.4,5.8,5.1,4.3]
#        self.data["f658n"]= [3.4,0.6,1.9,2.5,2.3,2.1]
#        self.data["f665n"]= [2.4,3.1,3.6,6.2,5.4,4.6]
#        self.data["f673n"]= [6.2,2.7,3.4,5.6,4.9,4.2]
#        self.data["f680n"]= [4.3,8.5,7.4,14.6,12.3,10.0]
#        self.data["f689m"]= [13.5,15.4,12.2,25.2,21.1,16.9]
#        self.data["f763m"]= [8.6,13.0,10.5,21.6,18.0,14.5]
#        self.data["f775w"]= [21.5,23.6,17.7,38.0,31.3,25.1]
#        self.data["f814w"]= [23.2,30.1,22.1,48.1,39.4,31.6]
#        self.data["f845m"]= [None,None,6.4,14.5,11.7,9.3]
#        self.data["f850lp"]= [11.5,8.8,7.5,15.2,12.5,10.3]
#        self.data["f953n"]= [2.4,0.4,1.8,2.1,2.0,1.9]
#        h = {}
#        h["filt"]= 0
#        h["data average"] = 1
#        h["low zodi"] = 2
#        h["high zodi"] = 3
#        h["high earth"] = 4
#        h["high airglow"] = 5
#        k =  dic.keys()
#        k.sort()
#        print k
#        print dic["f775w"][h["high zodi"]]


        # read the CSV file
        with open(datafile) as f:
            csvReader=csv.reader(f)
            fields=next(csvReader)
            for row in csvReader:
                temp=OrderedDict(zip(fields,row))
                filt=temp.pop('filt')
                self.data[filt]=temp

        # set default
        self.filter.set(def_filt)
        pattern=re.compile("[a-z][0-9][0-9][0-9]*")
        for filt in self.data:

            # get the filter type (wide vs. narrow)
            filter_type=pattern.split(filt)[1]

            # get properites of the pane
            group=filter_frames[filter_type]
            index=nb.index(group)

            # where to place the button
            r=count[index] % n
            c=count[index] // n
            count[index]+=1

            
            # draw the button
            ttk.Radiobutton(group,text=filt,variable=self.filter,value=filt).\
                grid(row=r,column=c)

            # select the default
            if filt == def_filt:
                nb.select(index)

        # build a new group for the data
        group=ttk.Frame(main,padding=2)       

        # stuff for the sky type
        ttk.Label(group,text="Sky type:").grid(row=0,column=0,sticky='E')
        self.sky_type=tk.StringVar()
        self.sky=ttk.Combobox(group,textvariable=self.sky_type,\
                              postcommand=lambda: self.compute(ignore=True))
        self.sky['values']=list(self.data[def_filt].keys())
        self.sky.current(0)
        self.sky.state(['readonly'])
        self.sky.grid(row=0,column=1,sticky='W')

        # stuff for the exposure time
        l=ttk.Label(group,text="exp time (s)")
        self.e=ttk.Entry(group)
        l.grid(row=1,column=0,sticky='E')
        self.e.grid(row=1,column=1,sticky='W')
        group.pack()
        self.e.focus_set()

        # build flashing output text        
        row=ttk.Frame(main,padding=2)
        self.l=ttk.Label(row,font="-weight bold")
        self.l.pack()
        row.pack()


        # build the buttons at the end
        row=ttk.Frame(main,padding=2)
        ttk.Button(row,text="compute",command=self.compute).grid(row=0,column=0)
        ttk.Button(row,text="stop",command=self.stop).grid(row=0,column=1)
        ttk.Button(row,text="quit",command=self.__quit__).grid(row=0,column=2)
        row.pack()

        self.root=root   
        

def main():

    # build default data file
    path=os.path.dirname(os.path.abspath(__file__))

    datafile=os.path.join(path,'postflash.csv')

    # parse arguments
    parser=ap.ArgumentParser(description="Compute UVIS Postflash")
    parser.add_argument('-b','--background',
                        type=ap.FileType('r'),\
                        help='full path to CSV file for backgrounds',\
                        default=datafile)
    args=parser.parse_args()


    # start the GUI
    root=tk.Tk()
    app=Postflash(args.background.name,root=root)
    app.mainloop()


if __name__=='__main__':
    main()
    
