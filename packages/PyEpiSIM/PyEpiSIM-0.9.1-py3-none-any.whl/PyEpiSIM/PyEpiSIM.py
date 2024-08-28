import tkinter
import time
import numpy as np
import tkinter as tk
# from tkinter import ttk
import ttkbootstrap as ttk
import tkinter.font as tkFont
import math
import webbrowser
import sys
import pandas as pd
#from comtypes.safearray import numpy
from sympy import *
from decimal import Decimal
import time
import scipy.io
from PIL import Image, ImageTk
from .PyEpiSIM_funcAsse import *  #PyEpiSIM's algorithm code
import os

def general(frame_General):
    print("general")
    tk.Label(frame_General, text="Parameter setting:", font=('Times New Roman',14,'bold')).place(x=52, y=10, anchor='nw')
    frame_Ps = tk.Frame(frame_General, height=250, width=900, relief='ridge', borderwidth=1)
    frame_Ps.place(relx=0.5, rely=0.06, anchor='n')

    global defaultcase, defaultcontrol, defaultsnps, defaultmodel, defaultuMAF, defaultlMAF
    tk.Label(frame_Ps, text="Cases:", font=('Times New Roman',11)).place(x=100, y=40, anchor='nw')
    defaultcase = tk.StringVar(value='1000')
    caseVal = tk.Entry(frame_Ps, textvariable=defaultcase).place(x=170, y=40, anchor='nw')
    tk.Label(frame_Ps, text="Controls:", font=('Times New Roman',11)).place(x=400, y=40, anchor='nw')
    defaultcontrol = tk.StringVar(value='1000')
    controlVal = tk.Entry(frame_Ps, textvariable=defaultcontrol).place(x=470, y=40, anchor='nw')
    tk.Label(frame_Ps, text="SNPs:", font=('Times New Roman',11)).place(x=100, y=90, anchor='nw')
    defaultsnps = tk.StringVar(value='100')
    snpslVal = tk.Entry(frame_Ps, textvariable=defaultsnps).place(x=170, y=90, anchor='nw')
    tk.Label(frame_Ps, text="Models:", font=('Times New Roman',11)).place(x=400, y=90, anchor='nw')
    defaultmodel = tk.StringVar(value='1')
    modelsVal = tk.Entry(frame_Ps, textvariable=defaultmodel).place(x=470, y=90, anchor='nw')
    tk.Label(frame_Ps, text="MAFs:").place(x=100, y=140, anchor='nw')
    tk.Label(frame_Ps, text="Upper bound of MAFs:", font=('Times New Roman',11)).place(x=120, y=180, anchor='nw')
    defaultuMAF = tk.StringVar(value='0.5')
    uMAFVal = tk.Entry(frame_Ps, textvariable=defaultuMAF).place(x=270, y=180, anchor='nw')
    tk.Label(frame_Ps, text="Lower bound of MAFs:", font=('Times New Roman',11)).place(x=470, y=180, anchor='nw')
    defaultlMAF = tk.StringVar(value='0.05')
    lMAFVal = tk.Entry(frame_Ps, textvariable=defaultlMAF).place(x=620, y=180, anchor='nw')


def public(frame_public):
    print("public")
    tk.Label(frame_public, text="Parameter setting:", font=('Times New Roman',14,'bold')).place(x=52, y=10, anchor='nw')
    frame_Ps = tk.Frame(frame_public, height=250, width=900, relief='ridge', borderwidth=1)
    frame_Ps.place(relx=0.5, rely=0.06, anchor='n')

    global public_modelSec, public_var2, public_lb2, public_var3, public_lb3
    public_modelSec = tkinter.StringVar()
    modelChosen = ttk.Combobox(frame_Ps, textvariable=public_modelSec,state = "readonly")  # #创建下拉菜单
    modelChosen.place(x=80, y=20)
    modelChosen["value"] = df["title"].tolist()     
    modelChosen.bind("<<ComboboxSelected>>", public_Act1)
    modelChosen.bind("<<ComboboxSelected>>", lambda event:public_Act3(event, frame_Ps), add='+')
    modelChosen.current(0)
    public_var2 = tk.StringVar()
    public_var2.set(("Select a Model",))
    public_lb2 = tk.Listbox(frame_Ps, listvariable=public_var2)
    public_lb2.place(x=80, y=60, width=165,height=150,anchor='nw')
    public_lb2.bind("<<ListboxSelect>>", public_Act2)
    public_var3 = tk.StringVar()
    public_var3.set(("Model Description",))
    public_lb3 = tk.Listbox(frame_Ps, listvariable=public_var3)
    public_lb3.place(x=350, y=20, width=165, height=190,anchor='nw')

    def Add1():
        print("Public_Add")
        public_add_start_time = time.time()
        global CurrentModelNum
        global ModelInfo   # ModelInfo[ith model][Model 1st parameter]
        defaultmodelValue = float(defaultmodel.get())
        if defaultmodelValue > CurrentModelNum:
            add1['state'] = tk.NORMAL
            CurrentModelNum += 1
            ModelInfo.append([1])
            rightshow.insert(tk.INSERT, '==========' + '\n')
            rightshow.insert(tk.INSERT, 'Current Model:  ' + str(CurrentModelNum) + '\n') 
            rightshow.insert(tk.INSERT, 'Type:  Public' + '\n') 
            if public_modelSec.get() == "Select":
                rightshow.insert(tk.INSERT, 'Error! (Penetrance)' + '\n') 
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            else:
                ModelInfo[CurrentModelNum-1].append([]) # Store the combined genotype penetrance of each epistatic model
                for each_str in public_var3.get().replace('(', '').replace(')', '').replace("'",'').split(', '):
                    if each_str:
                        ModelInfo[CurrentModelNum-1][1].append(each_str)
                for each_index in ModelInfo[CurrentModelNum-1][1]:
                    rightshow.insert(tk.INSERT, each_index + '\n')
            
            kSNP = int(len(ModelInfo[CurrentModelNum-1][1])**(1/3))
            ModelInfo[CurrentModelNum-1].append(kSNP)
            rightshow.insert(tk.INSERT, 'k-SNP: ' + str(kSNP) + '\n')

            ModelInfo[CurrentModelNum-1].append([])
            for i in range(kSNP):
                MAF = float(globals()['Public_mafVal'+str(i+1)].get())
                if (MAF <= 0) or (MAF > 0.5):
                    rightshow.insert(tk.INSERT, 'Error! (MAF of SNP)' + '\n')
                    CurrentModelNum -= 1
                    ModelInfo.pop()
                    return
                else:
                    ModelInfo[CurrentModelNum-1][3].append(MAF)
                    rightshow.insert(tk.INSERT, 'SNP_' + str(i+1) + ': ' + str(MAF) + '\n')
                
            rightshow.insert(tk.INSERT, 'Add OK!' + '\n')    
            print(ModelInfo)
            public_add_end_time = time.time()
            print('public add time cost : %.6f second' %(public_add_end_time-public_add_start_time))
        else: 
            add1['state'] = tk.DISABLED
    
    add1 = tk.Button(frame_Ps, text='Add', font=('Times New Roman', 16,'bold'), width=10, height=1, command=Add1)
    add1.configure(bg="gray")
    add1.place(x=600, y=150, anchor='nw')
    return modelChosen

def public_Act1(event):
    if public_modelSec.get() == "Select":
        public_var2.set(['Select a Model'])    
    elif public_modelSec.get() == "Single-SNP":
        public_var2.set(df["Single-SNP"].tolist())
    elif public_modelSec.get() == "Two-SNP":
        public_var2.set(df["Two-SNP"].tolist())
    elif public_modelSec.get() == "Three-SNP":
        public_var2.set(df["Three-SNP"].tolist())
    elif public_modelSec.get() == "Four-SNP":
        public_var2.set(df["Four-SNP"].tolist())
    else: public_var2.set([])

def public_Act2(event):
    if public_modelSec.get() == "Select" and  public_lb2.get(public_lb2.curselection()) == "Select a Model":
        public_var3.set(['Model Description'])
    elif public_modelSec.get() == "Single-SNP" and  public_lb2.get(public_lb2.curselection()) == "Model 1":
        public_var3.set(df["Single-SNP*Model1"].tolist())
    elif public_modelSec.get() == "Single-SNP" and  public_lb2.get(public_lb2.curselection()) == "Model 2":
        public_var3.set(df["Single-SNP*Model2"].tolist())
    elif public_modelSec.get() == "Single-SNP" and public_lb2.get(public_lb2.curselection()) == "Model 3":
        public_var3.set(df["Single-SNP*Model3"].tolist())
    elif public_modelSec.get() == "Single-SNP" and public_lb2.get(public_lb2.curselection()) == "Model 4":
        public_var3.set(df["Single-SNP*Model4"].tolist())
    elif public_modelSec.get() == "Single-SNP" and public_lb2.get(public_lb2.curselection()) == "Model 5":
        public_var3.set(df["Single-SNP*Model5"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "Model 1":
        public_var3.set(df["Two-SNP*Model1"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "Model 2":
        public_var3.set(df["Two-SNP*Model2"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "Model 3":
        public_var3.set(df["Two-SNP*Model3"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "Model 4":
        public_var3.set(df["Two-SNP*Model4"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "Model 5":
        public_var3.set(df["Two-SNP*Model5"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "Model 6":
        public_var3.set(df["Two-SNP*Model6"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "Model 7":
        public_var3.set(df["Two-SNP*Model7"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "Model 8":
        public_var3.set(df["Two-SNP*Model8"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "Model 9":
        public_var3.set(df["Two-SNP*Model9"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "Model 10":
        public_var3.set(df["Two-SNP*Model10"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "Model 11":
        public_var3.set(df["Two-SNP*Model11"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "DME-1":
        public_var3.set(df["Two-SNP*DME-1"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "DME-2":
        public_var3.set(df["Two-SNP*DME-2"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "DME-3":
        public_var3.set(df["Two-SNP*DME-3"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "DME-4":
        public_var3.set(df["Two-SNP*DME-4"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "DME-5":
        public_var3.set(df["Two-SNP*DME-5"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "DME-6":
        public_var3.set(df["Two-SNP*DME-6"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "DME-7":
        public_var3.set(df["Two-SNP*DME-7"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "DME-8":
        public_var3.set(df["Two-SNP*DME-8"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "DME-9":
        public_var3.set(df["Two-SNP*DME-9"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "DME-10":
        public_var3.set(df["Two-SNP*DME-10"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "DME-11":
        public_var3.set(df["Two-SNP*DME-11"].tolist())
    elif public_modelSec.get() == "Two-SNP" and public_lb2.get(public_lb2.curselection()) == "DME-12":
        public_var3.set(df["Two-SNP*DME-12"].tolist())
    elif public_modelSec.get() == "Three-SNP" and public_lb2.get(public_lb2.curselection()) == "Model 1":
        public_var3.set(df["Three-SNP*Model1"].tolist())
    elif public_modelSec.get() == "Three-SNP" and public_lb2.get(public_lb2.curselection()) == "Model 2":
        public_var3.set(df["Three-SNP*Model2"].tolist())
    elif public_modelSec.get() == "Three-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-1":
        public_var3.set(df["Three-SNP*Bush-1"].tolist())
    elif public_modelSec.get() == "Three-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-2":
        public_var3.set(df["Three-SNP*Bush-2"].tolist())
    elif public_modelSec.get() == "Three-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-3":
        public_var3.set(df["Three-SNP*Bush-3"].tolist())
    elif public_modelSec.get() == "Three-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-4":
        public_var3.set(df["Three-SNP*Bush-4"].tolist())
    elif public_modelSec.get() == "Three-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-5":
        public_var3.set(df["Three-SNP*Bush-5"].tolist())
    elif public_modelSec.get() == "Three-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-6":
        public_var3.set(df["Three-SNP*Bush-6"].tolist())
    elif public_modelSec.get() == "Three-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-7":
        public_var3.set(df["Three-SNP*Bush-7"].tolist())
    elif public_modelSec.get() == "Three-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-8":
        public_var3.set(df["Three-SNP*Bush-8"].tolist())
    elif public_modelSec.get() == "Three-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-9":
        public_var3.set(df["Three-SNP*Bush-9"].tolist())
    elif public_modelSec.get() == "Three-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-10":
        public_var3.set(df["Three-SNP*Bush-10"].tolist())
    elif public_modelSec.get() == "Four-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-11":
        public_var3.set(df["Four-SNP*Bush-11"].tolist())
    elif public_modelSec.get() == "Four-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-12":
        public_var3.set(df["Four-SNP*Bush-12"].tolist())
    elif public_modelSec.get() == "Four-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-13":
        public_var3.set(df["Four-SNP*Bush-13"].tolist())
    elif public_modelSec.get() == "Four-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-14":
        public_var3.set(df["Four-SNP*Bush-14"].tolist())
    elif public_modelSec.get() == "Four-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-15":
        public_var3.set(df["Four-SNP*Bush-15"].tolist())
    elif public_modelSec.get() == "Four-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-16":
        public_var3.set(df["Four-SNP*Bush-16"].tolist())
    elif public_modelSec.get() == "Four-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-17":
        public_var3.set(df["Four-SNP*Bush-17"].tolist())
    elif public_modelSec.get() == "Four-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-18":
        public_var3.set(df["Four-SNP*Bush-18"].tolist())
    elif public_modelSec.get() == "Four-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-19":
        public_var3.set(df["Four-SNP*Bush-19"].tolist())
    elif public_modelSec.get() == "Four-SNP" and public_lb2.get(public_lb2.curselection()) == "Bush-20":
        public_var3.set(df["Four-SNP*Bush-20"].tolist())
    else: public_var3.set([])

def public_Act3(event, frame_Ps):
    defaultmaf1 = tk.StringVar(value='0.05')
    defaultmaf2 = tk.StringVar(value='0.05')
    defaultmaf3 = tk.StringVar(value='0.05')
    defaultmaf4 = tk.StringVar(value='0.05')
    global Public_mafVal1
    global Public_mafVal2
    global Public_mafVal3
    global Public_mafVal4
    global Public_maflabel
    try:
        Public_maflabel.destroy()
        Public_mafVal1.destroy()
        Public_mafVal2.destroy()
        Public_mafVal3.destroy()
        Public_mafVal4.destroy()
    except:
        pass    
    if public_modelSec.get() == "Single-SNP":
        Public_maflabel = tk.Label(frame_Ps, text="MAFs of the Model: ", font=('Times New Roman',11))
        Public_maflabel.place(x=600, y=30, anchor='nw')
        Public_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
        Public_mafVal1.place(x=600, y=70, width=30,anchor='nw')
    elif public_modelSec.get() == "Two-SNP":
        Public_maflabel = tk.Label(frame_Ps, text="MAFs of the Model: ", font=('Times New Roman',11))
        Public_maflabel.place(x=600, y=30, anchor='nw')
        Public_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
        Public_mafVal1.place(x=600, y=70, width=30,anchor='nw')
        Public_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
        Public_mafVal2.place(x=650, y=70, width=30,anchor='nw')
    elif public_modelSec.get() == "Three-SNP":
        Public_maflabel = tk.Label(frame_Ps, text="MAFs of the Model: ", font=('Times New Roman',11))
        Public_maflabel.place(x=600, y=30, anchor='nw')
        Public_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
        Public_mafVal1.place(x=600, y=70, width=30,anchor='nw')
        Public_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
        Public_mafVal2.place(x=650, y=70, width=30,anchor='nw')
        Public_mafVal3 = tk.Entry(frame_Ps, textvariable=defaultmaf3)
        Public_mafVal3.place(x=700, y=70, width=30,anchor='nw')
    elif public_modelSec.get() == "Four-SNP":
        Public_maflabel = tk.Label(frame_Ps, text="MAFs of the Model: ", font=('Times New Roman',11))
        Public_maflabel.place(x=600, y=30, anchor='nw')
        Public_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
        Public_mafVal1.place(x=600, y=70, width=30,anchor='nw')
        Public_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
        Public_mafVal2.place(x=650, y=70, width=30,anchor='nw')
        Public_mafVal3 = tk.Entry(frame_Ps, textvariable=defaultmaf3)
        Public_mafVal3.place(x=700, y=70, width=30,anchor='nw')
        Public_mafVal4 = tk.Entry(frame_Ps, textvariable=defaultmaf4)
        Public_mafVal4.place(x=750, y=70, width=30,anchor='nw')


def restricted1(frame_Restricted1):
    print("restricted1")
    tk.Label(frame_Restricted1, text="Parameter setting:", font=('Times New Roman',14,'bold')).place(x=52, y=10, anchor='nw')
    frame_Ps = tk.Frame(frame_Restricted1, height=250, width=900, relief='ridge', borderwidth=1)
    frame_Ps.place(relx=0.5, rely=0.06, anchor='n')

    global restricted1_modelSec, restricted1_var2, restricted1_lb2, restricted1_var3, restricted1_lb3
    restricted1_modelSec = tkinter.StringVar()
    modelChosen = ttk.Combobox(frame_Ps, textvariable=restricted1_modelSec, state="readonly")  
    modelChosen.place(x=80, y=20)
    modelChosen["value"] = df1["title"].tolist()
    modelChosen.bind("<<ComboboxSelected>>", restricted1_Act1)
    modelChosen.bind("<<ComboboxSelected>>", lambda event:restricted1_Act3(event, frame_Ps), add='+')
    modelChosen.current(0)
    restricted1_var2 = tk.StringVar()
    restricted1_var2.set(("Select a Model",))
    restricted1_lb2 = tk.Listbox(frame_Ps, listvariable=restricted1_var2)
    restricted1_lb2.place(x=80, y=60, width=165,height=150,anchor='nw')
    restricted1_lb2.bind("<<ListboxSelect>>", restricted1_Act2)
    restricted1_var3 = tk.StringVar()
    restricted1_var3.set(("Model Description",))
    restricted1_lb3 = tk.Listbox(frame_Ps, listvariable=restricted1_var3)
    restricted1_lb3.place(x=300, y=20, width=165, height=190,anchor='nw')
    #右边
    tk.Label(frame_Ps, text="The proportion of cases:", font=('Times New Roman',11)).place(x=520, y=20, anchor='nw')
    defaultp = tk.StringVar(value='0.10')
    proVal = tk.Entry(frame_Ps, textvariable=defaultp)
    proVal.place(x=690, y=20, anchor='nw')
    tk.Label(frame_Ps, text="Heritability of the Model:", font=('Times New Roman',11)).place(x=520, y=50, anchor='nw')
    defaulth = tk.StringVar(value='0.0097')
    hVal = tk.Entry(frame_Ps, textvariable=defaulth)
    hVal.place(x=690, y=50, anchor='nw')

    def Add2():
        print("Res1_Add")
        res1_add_start_time = time.time()
        global CurrentModelNum
        global ModelInfo
        defaultmodelValue = float(defaultmodel.get())
        if defaultmodelValue > CurrentModelNum:
            add2['state'] = tk.NORMAL
            CurrentModelNum += 1
            ModelInfo.append([2])
            rightshow.insert(tk.INSERT, '==========' + '\n')
            rightshow.insert(tk.INSERT, 'Current Model:  ' + str(CurrentModelNum) + '\n') 
            rightshow.insert(tk.INSERT, 'Type:  Restricted (1)' + '\n') 
            if restricted1_modelSec.get() == "Select":
                rightshow.insert(tk.INSERT, 'Error! (Penetrance)' + '\n') 
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            else:
                ModelInfo[CurrentModelNum-1].append([])
                for each_str in restricted1_var3.get()[1:-1].replace("'",'').split(', '):
                    if each_str:
                        ModelInfo[CurrentModelNum-1][1].append(each_str)
                for each_index in ModelInfo[CurrentModelNum-1][1]:
                    rightshow.insert(tk.INSERT, each_index + '\n')
            
            kSNP = int(len(ModelInfo[CurrentModelNum-1][1])**(1/3))
            ModelInfo[CurrentModelNum-1].append(kSNP)
            rightshow.insert(tk.INSERT, 'k-SNP: ' + str(kSNP) + '\n')

            ModelInfo[CurrentModelNum-1].append([])
            for i in range(kSNP):
                MAF = float(globals()['Res1_mafVal'+str(i+1)].get())
                if (MAF <= 0) or (MAF > 0.5):
                    rightshow.insert(tk.INSERT, 'Error! (MAF of SNP)' + '\n')
                    CurrentModelNum -= 1
                    ModelInfo.pop()
                    return
                else:
                    ModelInfo[CurrentModelNum-1][3].append(MAF)
                    rightshow.insert(tk.INSERT, 'MAF_' + str(i+1) + ': ' + str(MAF) + '\n')
            PD = float(proVal.get())
            if (PD <= 0) or (PD > 1):
                rightshow.insert(tk.INSERT, 'Error! (PD)' + '\n')
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            else:
                ModelInfo[CurrentModelNum-1].append(PD)
                rightshow.insert(tk.INSERT, 'PD: ' + str(PD) + '\n')
            H2 = float(hVal.get())
            if (H2 <= 0) or (H2 > 1):
                rightshow.insert(tk.INSERT, 'Error! (H2)' + '\n')
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            else:
                ModelInfo[CurrentModelNum-1].append(H2)
                rightshow.insert(tk.INSERT, 'H2: ' + str(H2) + '\n')
            print(ModelInfo)
            
            RTable=RelativeRisk(ModelInfo,CurrentModelNum)
            if len(RTable) < 1:
                rightshow.insert(tk.INSERT, 'NO Explicit Solution!' + '\n')
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            else:
                rightshow.insert(tk.INSERT, 'Add OK!' + '\n')    
                res1_add_end_time = time.time()
                print('res1 add time cost : %.6f second' %(res1_add_end_time-res1_add_start_time))
        else: 
            add2['state'] = tk.DISABLED

    add2 = tk.Button(frame_Ps, text='Add', font=('Times New Roman', 16,'bold'), width=10, height=1, command=Add2)
    add2.configure(bg="gray")
    add2.place(x=600, y=165, anchor='nw')

def restricted1_Act1(event):
    if restricted1_modelSec.get() == "Select":
        restricted1_var2.set(['Select a Model']) 
    elif restricted1_modelSec.get() == "Single-SNP":
        restricted1_var2.set(df1["Single-SNP"].tolist())
    elif restricted1_modelSec.get() == "Two-SNP":
        restricted1_var2.set(df1["Two-SNP"].tolist())
    elif restricted1_modelSec.get() == "Three-SNP":
        restricted1_var2.set(df1["Three-SNP"].tolist())
    elif restricted1_modelSec.get() == "Four-SNP":
        restricted1_var2.set(df1["Four-SNP"].tolist())
    else: restricted1_var2.set([])

def restricted1_Act2(event):
    if restricted1_modelSec.get() == "Select" and  restricted1_lb2.get(restricted1_lb2.curselection()) == "Select a Model":
        restricted1_var3.set(['Model Description'])
    elif restricted1_modelSec.get() == "Single-SNP" and restricted1_lb2.get(restricted1_lb2.curselection()) == "Model 1":
        restricted1_var3.set(df1["Single-SNP*Model1"].tolist())
    elif restricted1_modelSec.get() == "Single-SNP" and  restricted1_lb2.get(restricted1_lb2.curselection()) == "Model 2":
        restricted1_var3.set(df1["Single-SNP*Model2"].tolist())
    elif restricted1_modelSec.get() == "Two-SNP" and restricted1_lb2.get(restricted1_lb2.curselection()) == "Model 1":
        restricted1_var3.set(df1["Two-SNP*Model1"].tolist())
    elif restricted1_modelSec.get() == "Two-SNP" and restricted1_lb2.get(restricted1_lb2.curselection()) == "Model 2":
        restricted1_var3.set(df1["Two-SNP*Model2"].tolist())
    elif restricted1_modelSec.get() == "Two-SNP" and restricted1_lb2.get(restricted1_lb2.curselection()) == "Model 3":
        restricted1_var3.set(df1["Two-SNP*Model3"].tolist())
    else: restricted1_var3.set([])

def restricted1_Act3(event, frame_Ps):
    defaultmaf1 = tk.StringVar(value='0.3')
    defaultmaf2 = tk.StringVar(value='0.3')
    defaultmaf3 = tk.StringVar(value='0.4')
    defaultmaf4 = tk.StringVar(value='0.4')
    global Res1_mafVal1
    global Res1_mafVal2
    global Res1_mafVal3
    global Res1_mafVal4
    global Res1_maflabel
    try:
        Res1_maflabel.destroy()
        Res1_mafVal1.destroy()
        Res1_mafVal2.destroy()
        Res1_mafVal3.destroy()
        Res1_mafVal4.destroy()
    except:
        pass
    if restricted1_modelSec.get() == "Single-SNP":
        Res1_maflabel = tk.Label(frame_Ps, text="MAFs of the Model: ", font=('Times New Roman',11))
        Res1_maflabel.place(x=520, y=80, anchor='nw')
        Res1_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
        Res1_mafVal1.place(x=550, y=110, width=30,anchor='nw')
    elif restricted1_modelSec.get() == "Two-SNP":
        Res1_maflabel = tk.Label(frame_Ps, text="MAFs of the Model: ", font=('Times New Roman',11))
        Res1_maflabel.place(x=520, y=80, anchor='nw')
        Res1_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
        Res1_mafVal1.place(x=550, y=110, width=30,anchor='nw')
        Res1_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
        Res1_mafVal2.place(x=600, y=110, width=30,anchor='nw')
    elif restricted1_modelSec.get() == "Three-SNP":
        Res1_maflabel = tk.Label(frame_Ps, text="MAFs of the Model: ", font=('Times New Roman',11))
        Res1_maflabel.place(x=520, y=80, anchor='nw')
        Res1_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
        Res1_mafVal1.place(x=550, y=110, width=30,anchor='nw')
        Res1_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
        Res1_mafVal2.place(x=600, y=110, width=30,anchor='nw')
        Res1_mafVal3 = tk.Entry(frame_Ps, textvariable=defaultmaf3)
        Res1_mafVal3.place(x=650, y=110, width=30,anchor='nw')
    elif restricted1_modelSec.get() == "Four-SNP":
        Res1_maflabel = tk.Label(frame_Ps, text="MAFs of the Model: ", font=('Times New Roman',11))
        Res1_maflabel.place(x=520, y=80, anchor='nw')
        Res1_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
        Res1_mafVal1.place(x=550, y=110, width=30,anchor='nw')
        Res1_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
        Res1_mafVal2.place(x=600, y=110, width=30,anchor='nw')
        Res1_mafVal3 = tk.Entry(frame_Ps, textvariable=defaultmaf3)
        Res1_mafVal3.place(x=650, y=110, width=30,anchor='nw')
        Res1_mafVal4 = tk.Entry(frame_Ps, textvariable=defaultmaf4)
        Res1_mafVal4.place(x=700, y=110, width=30,anchor='nw')


def restricted2(frame_Restricted2):
    print("restricted2")
    tk.Label(frame_Restricted2, text="Parameter setting:", font=('Times New Roman',14,'bold')).place(x=52, y=10, anchor='nw')
    frame_Ps = tk.Frame(frame_Restricted2, height=250, width=900, relief='ridge', borderwidth=1)
    frame_Ps.place(relx=0.5, rely=0.06, anchor='n')

    global restricted2_modelSec, restricted2_var2, restricted2_lb2, restricted2_var3, restricted2_lb3
    restricted2_modelSec = tkinter.StringVar()
    # modelSec = tkinter.StringVar()
    modelChosen = ttk.Combobox(frame_Ps, textvariable=restricted2_modelSec, state="readonly")
    modelChosen.place(x=80, y=20)
    modelChosen["value"] = df1["title"].tolist()
    modelChosen.bind("<<ComboboxSelected>>", restricted2_Act1)
    modelChosen.bind("<<ComboboxSelected>>", lambda event:restricted2_Act3(event, frame_Ps), add='+')
    modelChosen.current(0)
    restricted2_var2 = tk.StringVar()
    restricted2_var2.set(("Select a Model",))
    restricted2_lb2 = tk.Listbox(frame_Ps, listvariable=restricted2_var2)
    restricted2_lb2.place(x=80, y=60, width=165,height=150,anchor='nw')
    restricted2_lb2.bind("<<ListboxSelect>>", restricted2_Act2)
    restricted2_var3 = tk.StringVar()
    restricted2_var3.set(("Model Description",))
    restricted2_lb3 = tk.Listbox(frame_Ps, listvariable=restricted2_var3)
    restricted2_lb3.place(x=300, y=20, width=165, height=190,anchor='nw')
    tk.Label(frame_Ps, text="The proportion of cases:", font=('Times New Roman',11)).place(x=520, y=20, anchor='nw')
    defaultp = tk.StringVar(value='0.05')
    proVal = tk.Entry(frame_Ps, textvariable=defaultp)
    proVal.place(x=690, y=20, anchor='nw')
    tk.Label(frame_Ps, text="Marginal effect size of\n the first SNP(AA-Aa):", font=('Times New Roman',11)).place(x=520, y=50, anchor='nw')
    defaulth = tk.StringVar(value='0.306')
    hVal = tk.Entry(frame_Ps, textvariable=defaulth)
    hVal.place(x=690, y=60, anchor='nw')

    def Add_res2():
        print("Res2_Add")
        res2_add_start_time = time.time()
        global CurrentModelNum
        global ModelInfo
        defaultmodelValue = float(defaultmodel.get())
        if defaultmodelValue > CurrentModelNum:
            add_res2['state'] = tk.NORMAL
            CurrentModelNum += 1
            ModelInfo.append([3])
            rightshow.insert(tk.INSERT, '==========' + '\n')
            rightshow.insert(tk.INSERT, 'Current Model:  ' + str(CurrentModelNum) + '\n') 
            rightshow.insert(tk.INSERT, 'Type:  Restricted (2)' + '\n') 
            if restricted2_modelSec.get() == "Select":
                rightshow.insert(tk.INSERT, 'Error! (Penetrance)' + '\n') 
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            else:
                ModelInfo[CurrentModelNum-1].append([])
                for each_str in restricted2_var3.get()[1:-1].replace("'",'').split(', '):
                    if each_str:
                        ModelInfo[CurrentModelNum-1][1].append(each_str)
                for each_index in ModelInfo[CurrentModelNum-1][1]:
                    rightshow.insert(tk.INSERT, each_index + '\n')
            
            kSNP = int(len(ModelInfo[CurrentModelNum-1][1])**(1/3))
            ModelInfo[CurrentModelNum-1].append(kSNP)
            rightshow.insert(tk.INSERT, 'k-SNP: ' + str(kSNP) + '\n')

            ModelInfo[CurrentModelNum-1].append([])
            for i in range(kSNP):
                MAF = float(globals()['Res2_mafVal'+str(i+1)].get())
                if (MAF <= 0) or (MAF > 0.5):
                    rightshow.insert(tk.INSERT, 'Error! (MAF of SNP)' + '\n')
                    CurrentModelNum -= 1
                    ModelInfo.pop()
                    return
                else:
                    ModelInfo[CurrentModelNum-1][3].append(MAF)
                    rightshow.insert(tk.INSERT, 'MAF_' + str(i+1) + ': ' + str(MAF) + '\n')
            PD = float(proVal.get())
            if (PD <= 0) or (PD > 1):
                rightshow.insert(tk.INSERT, 'Error! (PD)' + '\n')
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            else:
                ModelInfo[CurrentModelNum-1].append(PD)
                rightshow.insert(tk.INSERT, 'PD: ' + str(PD) + '\n')
            lamda = float(hVal.get())
            if (lamda <= 0):
                rightshow.insert(tk.INSERT, 'Error! (lamda)' + '\n')
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            else:
                ModelInfo[CurrentModelNum-1].append([])
                ModelInfo[CurrentModelNum-1].append(lamda)
                rightshow.insert(tk.INSERT, 'lamda: ' + str(lamda) + '\n')
            print(ModelInfo)
            print(lamda)

            RTable=RelativeRisk(ModelInfo,CurrentModelNum)
            print('RTable', RTable)
            if len(RTable) < 1:
                rightshow.insert(tk.INSERT, 'NO Explicit Solution!' + '\n')
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            else:
                rightshow.insert(tk.INSERT, 'Add OK!' + '\n')   
                res2_add_end_time = time.time()
                print('res2 add time cost : %.6f second' %(res2_add_end_time-res2_add_start_time))
        else: 
            add_res2['state'] = tk.DISABLED

    add_res2 = tk.Button(frame_Ps, text='Add', font=('Times New Roman', 16,'bold'), width=10, height=1, command=Add_res2)
    add_res2.configure(bg="gray")
    add_res2.place(x=600, y=165, anchor='nw')

def restricted2_Act1(event):
    if restricted2_modelSec.get() == "Select":
        restricted2_var2.set(['Select a Model']) 
    elif restricted2_modelSec.get() == "Single-SNP":
        restricted2_var2.set(df1["Single-SNP"].tolist())
    elif restricted2_modelSec.get() == "Two-SNP":
        restricted2_var2.set(df1["Two-SNP"].tolist())
    elif restricted2_modelSec.get() == "Three-SNP":
        restricted2_var2.set(df1["Three-SNP"].tolist())
    elif restricted2_modelSec.get() == "Four-SNP":
        restricted2_var2.set(df1["Four-SNP"].tolist())
    else: restricted2_var2.set([])

def restricted2_Act2(event):
    if restricted2_modelSec.get() == "Select" and  restricted2_lb2.get(restricted2_lb2.curselection()) == "Select a Model":
        restricted2_var3.set(['Model Description'])
    elif restricted2_modelSec.get() == "Single-SNP" and restricted2_lb2.get(restricted2_lb2.curselection()) == "Model 1":
        restricted2_var3.set(df1["Single-SNP*Model1"].tolist())
    elif restricted2_modelSec.get() == "Single-SNP" and restricted2_lb2.get(restricted2_lb2.curselection()) == "Model 2":
        restricted2_var3.set(df1["Single-SNP*Model2"].tolist())
    elif restricted2_modelSec.get() == "Two-SNP" and restricted2_lb2.get(restricted2_lb2.curselection()) == "Model 1":
        restricted2_var3.set(df1["Two-SNP*Model1"].tolist())
    elif restricted2_modelSec.get() == "Two-SNP" and restricted2_lb2.get(restricted2_lb2.curselection()) == "Model 2":
        restricted2_var3.set(df1["Two-SNP*Model2"].tolist())
    elif restricted2_modelSec.get() == "Two-SNP" and restricted2_lb2.get(restricted2_lb2.curselection()) == "Model 3":
        restricted2_var3.set(df1["Two-SNP*Model3"].tolist())
    else: restricted2_var3.set([])

def restricted2_Act3(event, frame_Ps):
    defaultmaf1 = tk.StringVar(value='0.4')
    defaultmaf2 = tk.StringVar(value='0.4')
    defaultmaf3 = tk.StringVar(value='0.4')
    defaultmaf4 = tk.StringVar(value='0.4')
    global Res2_mafVal1
    global Res2_mafVal2
    global Res2_mafVal3
    global Res2_mafVal4
    global Res2_maflabel
    try:
        Res2_maflabel.destroy()
        Res2_mafVal1.destroy()
        Res2_mafVal2.destroy()
        Res2_mafVal3.destroy()
        Res2_mafVal4.destroy()
    except:
        pass
    if restricted2_modelSec.get() == "Single-SNP":
        Res2_maflabel = tk.Label(frame_Ps, text="MAFs of the Model", font=('Times New Roman',11))
        Res2_maflabel.place(x=520, y=95, anchor='nw')
        Res2_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
        Res2_mafVal1.place(x=550, y=125, width=30,anchor='nw')
    elif restricted2_modelSec.get() == "Two-SNP":
        Res2_maflabel = tk.Label(frame_Ps, text="MAFs of the Model", font=('Times New Roman',11))
        Res2_maflabel.place(x=520, y=95, anchor='nw')
        Res2_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
        Res2_mafVal1.place(x=550, y=125, width=30,anchor='nw')
        Res2_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
        Res2_mafVal2.place(x=600, y=125, width=30,anchor='nw')
    elif restricted2_modelSec.get() == "Three-SNP":
        Res2_maflabel = tk.Label(frame_Ps, text="MAFs of the Model", font=('Times New Roman',11))
        Res2_maflabel.place(x=520, y=95, anchor='nw')
        Res2_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
        Res2_mafVal1.place(x=550, y=125, width=30,anchor='nw')
        Res2_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
        Res2_mafVal2.place(x=600, y=125, width=30,anchor='nw')
        Res2_mafVal3 = tk.Entry(frame_Ps, textvariable=defaultmaf3)
        Res2_mafVal3.place(x=650, y=125, width=30,anchor='nw')
    elif restricted2_modelSec.get() == "Four-SNP":
        Res2_maflabel = tk.Label(frame_Ps, text="MAFs of the Model", font=('Times New Roman',11))
        Res2_maflabel.place(x=520, y=95, anchor='nw')
        Res2_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
        Res2_mafVal1.place(x=550, y=125, width=30,anchor='nw')
        Res2_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
        Res2_mafVal2.place(x=600, y=125, width=30,anchor='nw')
        Res2_mafVal3 = tk.Entry(frame_Ps, textvariable=defaultmaf3)
        Res2_mafVal3.place(x=650, y=125, width=30,anchor='nw')
        Res2_mafVal4 = tk.Entry(frame_Ps, textvariable=defaultmaf4)
        Res2_mafVal4.place(x=700, y=125, width=30,anchor='nw')

#res（3）
def restricted3(frame_Restricted3):
    print("restricted3")

    tk.Label(frame_Restricted3, text="Parameter setting:", font=('Times New Roman', 14, 'bold')).place(x=52, y=10,
                                                                                                       anchor='nw')
    frame_Ps = tk.Frame(frame_Restricted3, height=250, width=900, relief='ridge', borderwidth=1)
    frame_Ps.place(relx=0.5, rely=0.06, anchor='n')

    global restricted3_modelSec, restricted3_var2, restricted3_lb2, restricted3_var3, restricted3_lb3, pohdefaultp
    restricted3_modelSec = tkinter.StringVar()
    modelChosen = ttk.Combobox(frame_Ps, textvariable=restricted3_modelSec, state="readonly")
    modelChosen.place(x=80, y=20)
    modelChosen["value"] = df2["title"].tolist()
    modelChosen.bind("<<ComboboxSelected>>", restricted3_Act1)
    modelChosen.bind("<<ComboboxSelected>>", lambda event: restricted3_Act3(event, frame_Ps), add='+')
    modelChosen.current(0)
    restricted3_var2 = tk.StringVar()
    restricted3_var2.set(("Select a Model",))
    restricted3_lb2 = tk.Listbox(frame_Ps, listvariable=restricted3_var2)
    restricted3_lb2.place(x=80, y=60, width=165, height=150, anchor='nw')
    restricted3_lb2.bind("<<ListboxSelect>>", restricted3_Act2)
    restricted3_var3 = tk.StringVar()
    restricted3_var3.set(("Model Description",))
    restricted3_lb3 = tk.Listbox(frame_Ps, listvariable=restricted3_var3)
    restricted3_lb3.place(x=300, y=20, width=165, height=190, anchor='nw')

    tk.Label(frame_Ps, text="Fix Prevalence or Heritability:", font=('Times New Roman', 11)).place(x=520, y=20, anchor='nw')
    global fix_Select
    fix_Select = tkinter.StringVar()
    fixVal = ttk.Combobox(frame_Ps, textvariable=fix_Select, state="readonly")
    fixVal.place(x=550, y=60, width=130, height=25)
    fixVal["value"] = ('Select', 'Prevalence', 'Heritability')
    fixVal.bind("<<ComboboxSelected>>", restricted3_Act4)
    pohdefaultp = tk.StringVar(value=' ')
    pohVal = tk.Entry(frame_Ps, textvariable=pohdefaultp)
    pohVal.place(x=710, y=60, width=50, height=25, anchor='nw')

    def Add_res3():
        print("Res3_Add")
        res3_add_start_time = time.time()
        global CurrentModelNum
        global ModelInfo
        defaultmodelValue = float(defaultmodel.get())
        if defaultmodelValue > CurrentModelNum:
            add_res3['state'] = tk.NORMAL
            CurrentModelNum += 1
            ModelInfo.append([4])
            rightshow.insert(tk.INSERT, '==========' + '\n')
            rightshow.insert(tk.INSERT, 'Current Model:  ' + str(CurrentModelNum) + '\n')
            rightshow.insert(tk.INSERT, 'Type:  Restricted (3)' + '\n')
            if restricted3_modelSec.get() == "Select":
                rightshow.insert(tk.INSERT, 'Error! (Penetrance)' + '\n')
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            else:
                ModelInfo[CurrentModelNum - 1].append([])
                for each_str in restricted3_var3.get()[1:-1].replace("'", '').split(', '):
                    if each_str:
                        ModelInfo[CurrentModelNum - 1][1].append(each_str)
                for each_index in ModelInfo[CurrentModelNum - 1][1]:
                    rightshow.insert(tk.INSERT, each_index + '\n')

            kSNP = int(len(ModelInfo[CurrentModelNum - 1][1]) ** (1 / 3))
            if kSNP == 6: kSNP = 5
            ModelInfo[CurrentModelNum - 1].append(kSNP)
            rightshow.insert(tk.INSERT, 'k-SNP: ' + str(kSNP) + '\n')

            ModelInfo[CurrentModelNum - 1].append([])
            for i in range(kSNP):
                MAF = float(globals()['Res3_mafVal' + str(i + 1)].get())
                if (MAF <= 0) or (MAF > 0.5):
                    rightshow.insert(tk.INSERT, 'Error! (MAF of SNP)' + '\n')
                    CurrentModelNum -= 1
                    ModelInfo.pop()
                    return
                else:
                    ModelInfo[CurrentModelNum - 1][3].append(MAF)
                    rightshow.insert(tk.INSERT, 'MAF_' + str(i + 1) + ': ' + str(MAF) + '\n')

            #
            if fix_Select.get() == 'Heritability':
                ModelInfo[CurrentModelNum - 1].append(2)
                Her = float(pohVal.get())
                if (Her <= 0) or (Her > 1):
                    rightshow.insert(tk.INSERT, 'Error! (Her)' + '\n')
                    CurrentModelNum -= 1
                    ModelInfo.pop()
                    return
                else:
                    ModelInfo[CurrentModelNum - 1].append(Her)
                    rightshow.insert(tk.INSERT, 'Heritability: ' + str(Her) + '\n')
                print('ModelInfo', ModelInfo)
                PTable = find_max_prevalence(ModelInfo[CurrentModelNum - 1])
                print('PTable', PTable)
                if len(PTable) < 1:
                    rightshow.insert(tk.INSERT, 'NO Explicit Solution!' + '\n')
                    CurrentModelNum -= 1
                    ModelInfo.pop()
                    return
                else:
                    rightshow.insert(tk.INSERT, 'Add OK!' + '\n')
                    res3_add_end_time = time.time()
                    print('res3 add time cost : %.6f second' %(res3_add_end_time-res3_add_start_time))

            elif fix_Select.get() == 'Prevalence':
                ModelInfo[CurrentModelNum - 1].append(1)
                Pre = float(pohVal.get())
                Her = float(pohVal.get())
                if (Pre <= 0) or (Pre > 1):
                    rightshow.insert(tk.INSERT, 'Error! (Pre)' + '\n')
                    CurrentModelNum -= 1
                    ModelInfo.pop()
                    return
                else:
                    ModelInfo[CurrentModelNum - 1].append(Pre)
                    rightshow.insert(tk.INSERT, 'Prevalence: ' + str(Pre) + '\n')
                print('ModelInfo', ModelInfo)
                PTable = find_max_heritability(ModelInfo[CurrentModelNum - 1])
                print('PTable', PTable)
                if len(PTable) < 1:
                    rightshow.insert(tk.INSERT, 'NO Explicit Solution!' + '\n')
                    CurrentModelNum -= 1
                    ModelInfo.pop()
                    return
                else:
                    rightshow.insert(tk.INSERT, 'Add OK!' + '\n')   
                    res3_add_end_time = time.time()
                    print('res3 add time cost : %.6f second' %(res3_add_end_time-res3_add_start_time))
            else:
                rightshow.insert(tk.INSERT, 'Error! (Fix Prevalence or Heritability)' + '\n')
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
        else:
            add_res3['state'] = tk.DISABLED

    add_res3 = tk.Button(frame_Ps, text='Add', font=('Times New Roman', 16, 'bold'), width=10, height=1, command=Add_res3)
    add_res3.configure(bg="gray")
    add_res3.place(x=600, y=165, anchor='nw')

def restricted3_Act1(event):
    if restricted3_modelSec.get() == "Select":
        restricted3_var2.set(['Select a Model'])
    elif restricted3_modelSec.get() == "Two-SNP":
        restricted3_var2.set(df2["Two-SNP"].tolist())
    elif restricted3_modelSec.get() == "Three-SNP":
        restricted3_var2.set(df2["Three-SNP"].tolist())
    elif restricted3_modelSec.get() == "Four-SNP":
        restricted3_var2.set(df2["Four-SNP"].tolist())
    elif restricted3_modelSec.get() == "Five-SNP":
        restricted3_var2.set(df2["Five-SNP"].tolist())
    else:
        restricted3_var2.set([])

def restricted3_Act2(event):
    if restricted3_modelSec.get() == "Select" and restricted3_lb2.get(restricted3_lb2.curselection()) == "Select a Model":
        restricted3_var3.set(['Model Description'])

    elif restricted3_modelSec.get() == "Two-SNP" and restricted3_lb2.get(restricted3_lb2.curselection()) == "additive_2":
        restricted3_var3.set(df2["Two-SNP*additive_2"].tolist())
    elif restricted3_modelSec.get() == "Two-SNP" and restricted3_lb2.get(restricted3_lb2.curselection()) == "multiplicative_2":
        restricted3_var3.set(df2["Two-SNP*multiplicative_2"].tolist())
    elif restricted3_modelSec.get() == "Two-SNP" and restricted3_lb2.get(restricted3_lb2.curselection()) == "threshold_2":
        restricted3_var3.set(df2["Two-SNP*threshold_2"].tolist())
    elif restricted3_modelSec.get() == "Three-SNP" and restricted3_lb2.get(restricted3_lb2.curselection()) == "additive_3":
        restricted3_var3.set(df2["Three-SNP*additive_3"].tolist())
    elif restricted3_modelSec.get() == "Three-SNP" and restricted3_lb2.get(restricted3_lb2.curselection()) == "multiplicative_3":
        restricted3_var3.set(df2["Three-SNP*multiplicative_3"].tolist())
    elif restricted3_modelSec.get() == "Three-SNP" and restricted3_lb2.get(restricted3_lb2.curselection()) == "threshold_3":
        restricted3_var3.set(df2["Three-SNP*threshold_3"].tolist())
    elif restricted3_modelSec.get() == "Four-SNP" and restricted3_lb2.get(restricted3_lb2.curselection()) == "additive_4":
        restricted3_var3.set(df2["Four-SNP*additive_4"].tolist())
    elif restricted3_modelSec.get() == "Four-SNP" and restricted3_lb2.get(restricted3_lb2.curselection()) == "multiplicative_4":
        restricted3_var3.set(df2["Four-SNP*multiplicative_4"].tolist())
    elif restricted3_modelSec.get() == "Four-SNP" and restricted3_lb2.get(restricted3_lb2.curselection()) == "threshold_4":
        restricted3_var3.set(df2["Four-SNP*threshold_4"].tolist())
    elif restricted3_modelSec.get() == "Five-SNP" and restricted3_lb2.get(restricted3_lb2.curselection()) == "additive_5":
        restricted3_var3.set(df2["Five-SNP*additive_5"].tolist())
    elif restricted3_modelSec.get() == "Five-SNP" and restricted3_lb2.get(restricted3_lb2.curselection()) == "multiplicative_5":
        restricted3_var3.set(df2["Five-SNP*multiplicative_5"].tolist())
    elif restricted3_modelSec.get() == "Five-SNP" and restricted3_lb2.get(restricted3_lb2.curselection()) == "threshold_5":
        restricted3_var3.set(df2["Five-SNP*threshold_5"].tolist())
    else:
        restricted3_var3.set([])


def restricted3_Act3(event, frame_Ps):
    defaultmaf1 = tk.StringVar(value='0.4')
    defaultmaf2 = tk.StringVar(value='0.4')
    defaultmaf3 = tk.StringVar(value='0.4')
    defaultmaf4 = tk.StringVar(value='0.4')
    defaultmaf5 = tk.StringVar(value='0.4')
    global Res3_mafVal1
    global Res3_mafVal2
    global Res3_mafVal3
    global Res3_mafVal4
    global Res3_mafVal5
    global Res3_maflabel
    try:
        Res3_maflabel.destroy()
        Res3_mafVal1.destroy()
        Res3_mafVal2.destroy()
        Res3_mafVal3.destroy()
        Res3_mafVal4.destroy()
        Res3_mafVal5.destroy()
    except:
        pass
    if restricted3_modelSec.get() == "Single-SNP":
        Res3_maflabel = tk.Label(frame_Ps, text="MAFs of the Model", font=('Times New Roman', 11))
        Res3_maflabel.place(x=520, y=95, anchor='nw')
        Res3_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
        Res3_mafVal1.place(x=550, y=125, width=30, anchor='nw')
    elif restricted3_modelSec.get() == "Two-SNP":
        Res3_maflabel = tk.Label(frame_Ps, text="MAFs of the Model", font=('Times New Roman', 11))
        Res3_maflabel.place(x=520, y=95, anchor='nw')
        Res3_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
        Res3_mafVal1.place(x=550, y=125, width=30, anchor='nw')
        Res3_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
        Res3_mafVal2.place(x=600, y=125, width=30, anchor='nw')
    elif restricted3_modelSec.get() == "Three-SNP":
        Res3_maflabel = tk.Label(frame_Ps, text="MAFs of the Model", font=('Times New Roman', 11))
        Res3_maflabel.place(x=520, y=95, anchor='nw')
        Res3_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
        Res3_mafVal1.place(x=550, y=125, width=30, anchor='nw')
        Res3_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
        Res3_mafVal2.place(x=600, y=125, width=30, anchor='nw')
        Res3_mafVal3 = tk.Entry(frame_Ps, textvariable=defaultmaf3)
        Res3_mafVal3.place(x=650, y=125, width=30, anchor='nw')
    elif restricted3_modelSec.get() == "Four-SNP":
        Res3_maflabel = tk.Label(frame_Ps, text="MAFs of the Model", font=('Times New Roman', 11))
        Res3_maflabel.place(x=520, y=95, anchor='nw')
        Res3_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
        Res3_mafVal1.place(x=550, y=125, width=30, anchor='nw')
        Res3_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
        Res3_mafVal2.place(x=600, y=125, width=30, anchor='nw')
        Res3_mafVal3 = tk.Entry(frame_Ps, textvariable=defaultmaf3)
        Res3_mafVal3.place(x=650, y=125, width=30, anchor='nw')
        Res3_mafVal4 = tk.Entry(frame_Ps, textvariable=defaultmaf4)
        Res3_mafVal4.place(x=700, y=125, width=30, anchor='nw')
    elif restricted3_modelSec.get() == "Five-SNP":
        Res3_maflabel = tk.Label(frame_Ps, text="MAFs of the Model", font=('Times New Roman', 11))
        Res3_maflabel.place(x=520, y=95, anchor='nw')
        Res3_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
        Res3_mafVal1.place(x=550, y=125, width=30, anchor='nw')
        Res3_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
        Res3_mafVal2.place(x=600, y=125, width=30, anchor='nw')
        Res3_mafVal3 = tk.Entry(frame_Ps, textvariable=defaultmaf3)
        Res3_mafVal3.place(x=650, y=125, width=30, anchor='nw')
        Res3_mafVal4 = tk.Entry(frame_Ps, textvariable=defaultmaf4)
        Res3_mafVal4.place(x=700, y=125, width=30, anchor='nw')
        Res3_mafVal5 = tk.Entry(frame_Ps, textvariable=defaultmaf5)
        Res3_mafVal5.place(x=750, y=125, width=30, anchor='nw')

#This is the default value in the newly added box that is linked to the selection of Prevalence or Heritage
def restricted3_Act4(event):
            if fix_Select.get() == "Select":
                pohdefaultp.set(['0'])
            elif fix_Select.get() == "Prevalence":
                pohdefaultp.set(['0.2'])
            elif fix_Select.get() == "Heritability":
                pohdefaultp.set(['0.02'])
            else:
                pohdefaultp.set([])

#Pure(1)
def Pure(frame_Pure):
    print("Pure1")
    tk.Label(frame_Pure, text="Parameter setting:", font=('Times New Roman',14,'bold')).place(x=52, y=10, anchor='nw')
    frame_Ps = tk.Frame(frame_Pure, height=250, width=900, relief='ridge', borderwidth=1)
    frame_Ps.place(relx=0.5, rely=0.06, anchor='n')

    tk.Label(frame_Ps, text="Search veracity:", font=('Times New Roman',11)).place(x=50, y=20, anchor='nw')
    defaults = tk.StringVar()
    sVal = ttk.Combobox(frame_Ps, textvariable=defaults)
    sVal.place(x=220, y=20, width=145, height=25)
    sVal["value"] = ('0.1', '0.01', '0.001')
    sVal.current(0)
    tk.Label(frame_Ps, text="The proportion of cases:", font=('Times New Roman',11)).place(x=50, y=60, anchor='nw')
    defaultp = tk.StringVar(value='0.05')
    proVal = tk.Entry(frame_Ps, textvariable=defaultp)
    proVal.place(x=220, y=60, anchor='nw')
    tk.Label(frame_Ps, text="Heritability of the Model:", font=('Times New Roman',11)).place(x=50, y=100, anchor='nw')
    defaulth = tk.StringVar(value='0.0526')
    hVal = tk.Entry(frame_Ps, textvariable=defaulth)
    hVal.place(x=220, y=100, anchor='nw')
    tk.Label(frame_Ps, text="MAFs of the Model:", font=('Times New Roman',11)).place(x=50, y=140, anchor='nw')
    defaultmaf1 = tk.StringVar(value='0.5')
    defaultmaf2 = tk.StringVar(value='0.5')
    mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
    mafVal1.place(x=220, y=140, width=50, anchor='nw')
    mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
    mafVal2.place(x=280, y=140, width=50, anchor='nw')
    # #Search function, uses step size exhaustive search, and can only be of order 2, so MAF can only have two
    def Search():
        print('Search')
        pure1_search_start_time = time.time()
        rightshow.insert(tk.INSERT, '\n')
        rightshow.insert("insert", '=== Search ====\n')
        Veracity_val = float(sVal.get())
        rightshow.insert(tk.INSERT, 'Veracity: ' + str(Veracity_val) + '\n') 
        # PD :The proportion of cases
        PD_var = Decimal(proVal.get())
        if ((abs(PD_var) != PD_var) or (PD_var > 1) or (PD_var == 0)):
            rightshow.insert(tk.INSERT, 'Error! (PD)') 
            return
        else:
            rightshow.insert(tk.INSERT, 'PD: ' + str(PD_var) + '\n') 
        # H2
        H2_var = Decimal(hVal.get())
        if ((abs(H2_var) != H2_var) or (H2_var > 1) or (H2_var == 0)):
            rightshow.insert(tk.INSERT, 'Error! (H2)') 
            return
        else:
            rightshow.insert(tk.INSERT, 'H2: ' + str(H2_var) + '\n')
        # MAF1
        MAF1_var = Decimal(mafVal1.get())
        if ((abs(MAF1_var) != MAF1_var) or (MAF1_var > 0.5) or (MAF1_var == 0)):
            rightshow.insert(tk.INSERT, 'Error! (MAF of SNP1)') 
            return
        else:
            rightshow.insert(tk.INSERT, 'SNP_1: ' + str(MAF1_var) + '\n')
        # MAF2
        MAF2_var = Decimal(mafVal2.get())
        if ((abs(MAF2_var) != MAF2_var) or (MAF2_var > 0.5) or (MAF2_var == 0)):
            rightshow.insert(tk.INSERT, 'Error! (MAF of SNP2)') 
            return
        else:
            rightshow.insert(tk.INSERT, 'SNP_2: ' + str(MAF2_var) + '\n')
        search['state'] = 'disabled'
        rightshow.insert(tk.INSERT, 'Search......\n')        
        rightshow.insert(tk.INSERT, '-- iter -- 0%')        
        time.sleep(0.0000000001)
        tag = 1
        iTag = 0
        Model = ['Select a Model']
        global Penetrance
        Penetrance = ['Penetrance']
        for f11 in np.arange(0, 1, Veracity_val):
            for f22 in np.arange(0, 1, Veracity_val):
                for f33 in np.arange(0, 1, Veracity_val):
                    iTag += 1
                    if (math.floor((1+1/Veracity_val)**3/50) != 0) \
                        and ((iTag % (math.floor((1+1/Veracity_val)**3/50))) == 0) \
                        and (Veracity_val == 0.1):
                        rightshow.delete("end-1c linestart", "end")
                        rightshow.insert(tk.INSERT, '\n')
                        rightshow.insert("end", '-- iter -- ' + str(round(iTag/((1+1/Veracity_val)**3)*100,4)) + '%') 
                        time.sleep(0.0000000001)
                    elif (math.floor((1+1/Veracity_val)**3/50000) != 0) \
                        and ((iTag % (math.floor((1+1/Veracity_val)**3/50000))) == 0) \
                        and (Veracity_val == 0.01):
                        rightshow.delete("end-1c linestart", "end")
                        rightshow.insert(tk.INSERT, '\n')
                        rightshow.insert("end", '-- iter -- ' + str(round(iTag/((1+1/Veracity_val)**3)*100,4)) + '%') 
                        time.sleep(0.0000000001)
                    elif (math.floor((1+1/Veracity_val)**3/400000) != 0) \
                        and ((iTag % (math.floor((1+1/Veracity_val)**3/400000))) == 0) \
                        and (Veracity_val == 0.005):
                        rightshow.delete("end-1c linestart", "end")
                        rightshow.insert(tk.INSERT, '\n')
                        rightshow.insert("end", '-- iter -- ' + str(round(iTag/((1+1/Veracity_val)**3)*100,4)) + '%') 
                        time.sleep(0.0000000001)
                    num, Pure=PureEpistasis(float(MAF1_var),float(MAF2_var),float(PD_var),float(H2_var),float(f11),float(f22),float(f33),float(Veracity_val))
                    for i in range(num):
                        tag += 1
                        Model.append('Model' + str(tag-1))
                        Penetrance.append(Pure[i])

        rightshow.delete("end-1c linestart", "end")
        rightshow.insert(tk.INSERT, '\n')
        rightshow.insert("end", '-- iter -- 100%')
        rightshow.insert(tk.INSERT, '\n')
        rightshow.insert("end", 'Search OK!')
        rightshow.insert(tk.INSERT, '\n')
        pure1_search_end_time = time.time()
        print('pure1 search time cost : %.6f second' %(pure1_search_end_time-pure1_search_start_time))
        time.sleep(0.0000000001)
        pure_var2.set(Model)
        for k in range(len(Penetrance)-1):
            Penetrance_save=numpy.array(Penetrance[k+1], dtype=object)
            Penetrance[k+1] = Penetrance_save
        Penetrance_array = numpy.array(Penetrance)
        Penetrance_out = Penetrance_array.reshape(Penetrance_array.shape[0],1)
        scipy.io.savemat('PureEpistasis_python.mat', mdict = {'Penetrance':Penetrance_out})
        # print(Model, Penetrance_out)
        search['state'] = 'normal'
    search = tk.Button(frame_Ps, text='Search', font=('Times New Roman', 16,'bold'), width=10, height=1, command=lambda:thread_it(Search))
    search.configure(bg="gray")
    search.place(x=150, y=180, anchor='nw')

    def pure_Act1(event):
        for i in pure_lb2.curselection():
            if i > 0:
                Penetrance_show = []
                for each_array in Penetrance[i]:
                    Penetrance_show.append(each_array[0][0])
                pure_var3.set((Penetrance_show))
    pure_var2 = tk.StringVar()
    pure_var2.set(("Select a Model",))
    pure_lb2 = tk.Listbox(frame_Ps, listvariable=pure_var2)
    pure_lb2.place(x=460, y=20, width=165, height=140, anchor='nw')
    pure_lb2.bind("<<ListboxSelect>>", pure_Act1)
    pure_var3 = tk.StringVar()
    pure_var3.set(("Model Description",))
    pure_lb3 = tk.Listbox(frame_Ps, listvariable=pure_var3)
    pure_lb3.place(x=670, y=20, width=165, height=140, anchor='nw')

    def Add4():
        print("Pure_Add")
        pure1_add_start_time = time.time()
        global CurrentModelNum
        global ModelInfo
        defaultmodelValue = float(defaultmodel.get())
        if defaultmodelValue > CurrentModelNum:
            add4['state'] = tk.NORMAL
            CurrentModelNum += 1
            ModelInfo.append([5])
            rightshow.insert(tk.INSERT, '==========' + '\n')
            rightshow.insert(tk.INSERT, 'Current Model:  ' + str(CurrentModelNum) + '\n') 
            rightshow.insert(tk.INSERT, 'Type:  Pure(1)' + '\n') 
            for i in pure_lb2.curselection():
                if i > 0:
                    ModelInfo[CurrentModelNum-1].append([])
                    for each_str in pure_var3.get()[1:-1].replace("'",'').split(', '):
                        if each_str:
                            ModelInfo[CurrentModelNum-1][1].append(each_str)
                    for each_index in ModelInfo[CurrentModelNum-1][1]:
                        rightshow.insert(tk.INSERT, each_index + '\n')
                else:
                    rightshow.insert(tk.INSERT, 'Error! (Penetrance)' + '\n') 
                    CurrentModelNum -= 1
                    ModelInfo.pop()
                    return
            
            kSNP = int(len(ModelInfo[CurrentModelNum-1][1])**(1/3))
            ModelInfo[CurrentModelNum-1].append(kSNP)
            rightshow.insert(tk.INSERT, 'k-SNP: ' + str(kSNP) + '\n')

            ModelInfo[CurrentModelNum-1].append([])
            MAF1 = float(Decimal(mafVal1.get()))
            if (MAF1 <= 0) or (MAF1 > 0.5):
                rightshow.insert(tk.INSERT, 'Error! (MAF of SNP)' + '\n')
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            else:
                ModelInfo[CurrentModelNum-1][3].append(MAF1)
                rightshow.insert(tk.INSERT, 'SNP_1' + ': ' + str(MAF1) + '\n')
            MAF2 = float(Decimal(mafVal2.get()))
            if (MAF2 <= 0) or (MAF2 > 0.5):
                rightshow.insert(tk.INSERT, 'Error! (MAF of SNP)' + '\n')
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            else:
                ModelInfo[CurrentModelNum-1][3].append(MAF2)
                rightshow.insert(tk.INSERT, 'SNP_2' + ': ' + str(MAF2) + '\n')
            print(ModelInfo)
            rightshow.insert(tk.INSERT, 'Add OK!' + '\n')    
            pure1_add_end_time = time.time()
            print('pure1 add time cost : %.6f second' %(pure1_add_end_time-pure1_add_start_time))
        else: 
            add4['state'] = tk.DISABLED
    add4 = tk.Button(frame_Ps, text='Add', font=('Times New Roman', 16,'bold'), width=10, height=1, command=Add4)
    add4.configure(bg="gray")
    add4.place(x=590, y=180, anchor='nw')


#pure(2)
def Pure2(frame_Pure2):
    print("Pure2")
    tk.Label(frame_Pure2, text="Parameter setting:", font=('Times New Roman', 14, 'bold')).place(x=52, y=10, anchor='nw')
    frame_Ps = tk.Frame(frame_Pure2, height=250, width=900, relief='ridge', borderwidth=1)
    frame_Ps.place(relx=0.5, rely=0.06, anchor='n')

    tk.Label(frame_Ps, text="Choosing the order:", font=('Times New Roman', 11)).place(x=50, y=20, anchor='nw')
    global order_Select
    order_Select = tkinter.StringVar()
    sVal = ttk.Combobox(frame_Ps, textvariable=order_Select, state = "readonly")
    sVal.place(x=220, y=20, width=100, height=25)
    sVal["value"] = ('Select','2', '3', '4', '5')
    sVal.bind("<<ComboboxSelected>>", lambda event: pure2_Act1(event, frame_Ps), add='+')
    sVal.current(0)

    tk.Label(frame_Ps, text="The proportion of cases:", font=('Times New Roman', 11)).place(x=50, y=60, anchor='nw')
    defaultp = tk.StringVar(value='0.05')
    proVal = tk.Entry(frame_Ps, textvariable=defaultp)
    proVal.place(x=220, y=60, anchor='nw')

    tk.Label(frame_Ps, text="Heritability of the Model:", font=('Times New Roman', 11)).place(x=50, y=100, anchor='nw')
    defaulth = tk.StringVar(value='0')
    hVal = tk.Entry(frame_Ps, textvariable=defaulth)
    hVal.place(x=220, y=100, anchor='nw')

    Pure2_Penlabel = tk.Label(frame_Ps, text="Penetrance_show: ", font=('Times New Roman', 11))
    Pure2_Penlabel.place(x=550, y=10, anchor='nw')
    pure2_var2 = tk.StringVar()
    pure2_lb2 = tk.Listbox(frame_Ps, listvariable=pure2_var2)
    pure2_lb2.place(x=550, y=35, width=190, height=120, anchor='nw')

    def pure2_Act1(event, frame_Ps):
        defaultmaf1 = tk.StringVar(value='0.2')
        defaultmaf2 = tk.StringVar(value='0.2')
        defaultmaf3 = tk.StringVar(value='0.3')
        defaultmaf4 = tk.StringVar(value='0.3')
        defaultmaf5 = tk.StringVar(value='0.4')
        global Pure2_mafVal1
        global Pure2_mafVal2
        global Pure2_mafVal3
        global Pure2_mafVal4
        global Pure2_mafVal5
        global Pure2_maflabel
        try:
            Pure2_maflabel.destroy()
            Pure2_mafVal1.destroy()
            Pure2_mafVal2.destroy()
            Pure2_mafVal3.destroy()
            Pure2_mafVal4.destroy()
            Pure2_mafVal5.destroy()
        except:
            pass
        if order_Select.get() == "2":
            Pure2_maflabel = tk.Label(frame_Ps, text="MAFs of the Model: ", font=('Times New Roman', 11))
            Pure2_maflabel.place(x=50, y=140, anchor='nw')
            Pure2_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
            Pure2_mafVal1.place(x=220, y=140, width=30, anchor='nw')
            Pure2_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
            Pure2_mafVal2.place(x=260, y=140, width=30, anchor='nw')
        elif order_Select.get() == "3":
            Pure2_maflabel = tk.Label(frame_Ps, text="MAFs of the Model: ", font=('Times New Roman', 11))
            Pure2_maflabel.place(x=50, y=140, anchor='nw')
            Pure2_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
            Pure2_mafVal1.place(x=220, y=140, width=30, anchor='nw')
            Pure2_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
            Pure2_mafVal2.place(x=260, y=140, width=30, anchor='nw')
            Pure2_mafVal3 = tk.Entry(frame_Ps, textvariable=defaultmaf3)
            Pure2_mafVal3.place(x=300, y=140, width=30, anchor='nw')
        elif order_Select.get() == "4":
            Pure2_maflabel = tk.Label(frame_Ps, text="MAFs of the Model: ", font=('Times New Roman', 11))
            Pure2_maflabel.place(x=50, y=140, anchor='nw')
            Pure2_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
            Pure2_mafVal1.place(x=220, y=140, width=30, anchor='nw')
            Pure2_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
            Pure2_mafVal2.place(x=260, y=140, width=30, anchor='nw')
            Pure2_mafVal3 = tk.Entry(frame_Ps, textvariable=defaultmaf3)
            Pure2_mafVal3.place(x=300, y=140, width=30, anchor='nw')
            Pure2_mafVal4 = tk.Entry(frame_Ps, textvariable=defaultmaf4)
            Pure2_mafVal4.place(x=340, y=140, width=30, anchor='nw')
        elif order_Select.get() == "5":
            Pure2_maflabel = tk.Label(frame_Ps, text="MAFs of the Model: ", font=('Times New Roman', 11))
            Pure2_maflabel.place(x=50, y=140, anchor='nw')
            Pure2_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
            Pure2_mafVal1.place(x=220, y=140, width=30, anchor='nw')
            Pure2_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
            Pure2_mafVal2.place(x=260, y=140, width=30, anchor='nw')
            Pure2_mafVal3 = tk.Entry(frame_Ps, textvariable=defaultmaf3)
            Pure2_mafVal3.place(x=300, y=140, width=30, anchor='nw')
            Pure2_mafVal4 = tk.Entry(frame_Ps, textvariable=defaultmaf4)
            Pure2_mafVal4.place(x=340, y=140, width=30, anchor='nw')
            Pure2_mafVal5 = tk.Entry(frame_Ps, textvariable=defaultmaf5)
            Pure2_mafVal5.place(x=380, y=140, width=30, anchor='nw')

   #calulation
    def Count2():
        print("Pure2_Count2")
        pure2_count_start_time = time.time()
        rightshow.insert(tk.INSERT, '\n')
        rightshow.insert("insert", '=== Pure2_Count2 ====\n')
        order_val = int(sVal.get())
        PD_var = Decimal(proVal.get())
        H2_var = Decimal(hVal.get())
        MAF_list = []
        for i in range(order_val):
            MAF = float(globals()['Pure2_mafVal'+str(i+1)].get())
            MAF_list.append(MAF)
        x_result, v, pd, h = pure2_calculation(MAF_list,float(PD_var),float(H2_var), order_val)
        if v == 0:
            rightshow.insert(tk.INSERT, 'There is no solution to the problem defined.') 
        else:
            x_result_show = [float('{:.6f}'.format(i)) for i in x_result]
            pure2_var2.set(str(x_result_show).replace('[', '').replace(']', '').replace(',', ''))
            rightshow.insert("end", 'Count OK!')
            rightshow.insert(tk.INSERT, '\n')
            pure2_count_end_time = time.time()
            print('pure2 count time cost : %.6f second' %(pure2_count_end_time-pure2_count_start_time))
    count2 = tk.Button(frame_Ps, text='Count', font=('Times New Roman', 16, 'bold'), width=10, height=1, command=Count2)
    count2.configure(bg="gray")
    count2.place(x=170, y=180, anchor='nw')

    def Add_pure2():
        print("Pure2_Add")
        pure2_add_start_time = time.time()
        global CurrentModelNum
        global ModelInfo
        defaultmodelValue = float(defaultmodel.get())
        if defaultmodelValue > CurrentModelNum:
            addpure2['state'] = tk.NORMAL
            CurrentModelNum += 1
            ModelInfo.append([6])
            rightshow.insert(tk.INSERT, '==========' + '\n')
            rightshow.insert(tk.INSERT, 'Current Model:  ' + str(CurrentModelNum) + '\n')
            rightshow.insert(tk.INSERT, 'Type:  Pure(2)' + '\n')
            if pure2_var2:
                ModelInfo[CurrentModelNum-1].append([])
                for each_str in pure2_var2.get()[1:-1].replace("'",'').split(', '):
                    if each_str:
                        ModelInfo[CurrentModelNum-1][1].append(float(each_str))
                for each_index in ModelInfo[CurrentModelNum-1][1]:
                    rightshow.insert(tk.INSERT, str(each_index) + '\n')
            else:
                rightshow.insert(tk.INSERT, 'Error! (Penetrance)' + '\n') 
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            # order
            order_val = int(sVal.get())
            ModelInfo[CurrentModelNum-1].append(order_val)            
            rightshow.insert(tk.INSERT, 'order: ' + str(order_val) + '\n')
            # MAF
            ModelInfo[CurrentModelNum-1].append([])
            for i in range(order_val):
                MAF = float(globals()['Pure2_mafVal'+str(i+1)].get())
                if (MAF <= 0) or (MAF > 0.5):
                    rightshow.insert(tk.INSERT, 'Error! (MAF of SNP)' + '\n')
                    CurrentModelNum -= 1
                    ModelInfo.pop()
                    return
                else:
                    ModelInfo[CurrentModelNum-1][3].append(MAF)
                    rightshow.insert(tk.INSERT, 'MAF_' + str(i+1) + ': ' + str(MAF) + '\n')

            # PD :The proportion of cases
            PD_var = float(proVal.get())
            if ((abs(PD_var) != PD_var) or (PD_var > 1) or (PD_var == 0)):
                rightshow.insert(tk.INSERT, 'Error! (PD)')
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            else:
                ModelInfo[CurrentModelNum-1].append(PD_var)
                rightshow.insert(tk.INSERT, 'PD: ' + str(PD_var) + '\n') 
            # H2
            H2_var = float(hVal.get())
            if H2_var != 0:
                rightshow.insert(tk.INSERT, 'Error! (H2)') 
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            else:
                ModelInfo[CurrentModelNum-1].append(H2_var)
                rightshow.insert(tk.INSERT, 'H2: ' + str(H2_var) + '\n')
            rightshow.insert(tk.INSERT, 'Add OK!' + '\n')  
            pure2_add_end_time = time.time()
            print('pure2 add time cost : %.6f second' %(pure2_add_end_time-pure2_add_start_time))
            print(ModelInfo)
        else:
            addpure2['state'] = tk.DISABLED
    addpure2 = tk.Button(frame_Ps, text='Add', font=('Times New Roman', 16, 'bold'), width=10, height=1, command=Add_pure2)
    addpure2.configure(bg="gray")
    addpure2.place(x=590, y=180, anchor='nw')


#pure(3)
def Pure3(frame_Pure3):
    print("Pure3")
    tk.Label(frame_Pure3, text="Parameter setting:", font=('Times New Roman', 14, 'bold')).place(x=52, y=10, anchor='nw')
    frame_Ps = tk.Frame(frame_Pure3, height=250, width=900, relief='ridge', borderwidth=1)
    frame_Ps.place(relx=0.5, rely=0.06, anchor='n')
    tk.Label(frame_Ps, text="Choosing the order:", font=('Times New Roman', 11)).place(x=50, y=20, anchor='nw')
    global order_Select1
    order_Select1 = tkinter.StringVar()
    sVal = ttk.Combobox(frame_Ps, textvariable=order_Select1, state = "readonly")
    sVal.place(x=220, y=20, width=100, height=25)
    sVal["value"] = ('Select','2', '3', '4', '5')
    sVal.bind("<<ComboboxSelected>>", lambda event: pure3_Act1(event, frame_Ps), add='+')
    sVal.current(0)
    tk.Label(frame_Ps, text="The proportion of cases:", font=('Times New Roman', 11)).place(x=50, y=60, anchor='nw')
    defaultp = tk.StringVar(value='0.05')
    proVal = tk.Entry(frame_Ps, textvariable=defaultp)
    proVal.place(x=220, y=60, anchor='nw')
    tk.Label(frame_Ps, text="Heritability of the Model:", font=('Times New Roman', 11)).place(x=50, y=100, anchor='nw')
    defaulth = tk.StringVar(value='0.2')
    hVal = tk.Entry(frame_Ps, textvariable=defaulth)
    hVal.place(x=220, y=100, anchor='nw')
    Pure3_Penlabel = tk.Label(frame_Ps, text="Penetrance_show: ", font=('Times New Roman', 11))
    Pure3_Penlabel.place(x=550, y=10, anchor='nw')
    pure3_var2 = tk.StringVar()
    pure3_lb2 = tk.Listbox(frame_Ps, listvariable=pure3_var2)
    pure3_lb2.place(x=550, y=35, width=190, height=120, anchor='nw')

    def pure3_Act1(event, frame_Ps):
        defaultmaf1 = tk.StringVar(value='0.2')
        defaultmaf2 = tk.StringVar(value='0.2')
        defaultmaf3 = tk.StringVar(value='0.3')
        defaultmaf4 = tk.StringVar(value='0.3')
        defaultmaf5 = tk.StringVar(value='0.4')
        global Pure3_mafVal1
        global Pure3_mafVal2
        global Pure3_mafVal3
        global Pure3_mafVal4
        global Pure3_mafVal5
        global Pure3_maflabel
        try:
            Pure3_maflabel.destroy()
            Pure3_mafVal1.destroy()
            Pure3_mafVal2.destroy()
            Pure3_mafVal3.destroy()
            Pure3_mafVal4.destroy()
            Pure3_mafVal5.destroy()
        except:
            pass
        if order_Select1.get() == "2":
            Pure3_maflabel = tk.Label(frame_Ps, text="MAFs of the Model: ", font=('Times New Roman', 11))
            Pure3_maflabel.place(x=50, y=140, anchor='nw')
            Pure3_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
            Pure3_mafVal1.place(x=220, y=140, width=30, anchor='nw')
            Pure3_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
            Pure3_mafVal2.place(x=260, y=140, width=30, anchor='nw')
        elif order_Select1.get() == "3":
            Pure3_maflabel = tk.Label(frame_Ps, text="MAFs of the Model: ", font=('Times New Roman', 11))
            Pure3_maflabel.place(x=50, y=140, anchor='nw')
            Pure3_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
            Pure3_mafVal1.place(x=220, y=140, width=30, anchor='nw')
            Pure3_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
            Pure3_mafVal2.place(x=260, y=140, width=30, anchor='nw')
            Pure3_mafVal3 = tk.Entry(frame_Ps, textvariable=defaultmaf3)
            Pure3_mafVal3.place(x=300, y=140, width=30, anchor='nw')
        elif order_Select1.get() == "4":
            Pure3_maflabel = tk.Label(frame_Ps, text="MAFs of the Model: ", font=('Times New Roman', 11))
            Pure3_maflabel.place(x=50, y=140, anchor='nw')
            Pure3_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
            Pure3_mafVal1.place(x=220, y=140, width=30, anchor='nw')
            Pure3_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
            Pure3_mafVal2.place(x=260, y=140, width=30, anchor='nw')
            Pure3_mafVal3 = tk.Entry(frame_Ps, textvariable=defaultmaf3)
            Pure3_mafVal3.place(x=300, y=140, width=30, anchor='nw')
            Pure3_mafVal4 = tk.Entry(frame_Ps, textvariable=defaultmaf4)
            Pure3_mafVal4.place(x=340, y=140, width=30, anchor='nw')
        elif order_Select1.get() == "5":
            Pure3_maflabel = tk.Label(frame_Ps, text="MAFs of the Model: ", font=('Times New Roman', 11))
            Pure3_maflabel.place(x=50, y=140, anchor='nw')
            Pure3_mafVal1 = tk.Entry(frame_Ps, textvariable=defaultmaf1)
            Pure3_mafVal1.place(x=220, y=140, width=30, anchor='nw')
            Pure3_mafVal2 = tk.Entry(frame_Ps, textvariable=defaultmaf2)
            Pure3_mafVal2.place(x=260, y=140, width=30, anchor='nw')
            Pure3_mafVal3 = tk.Entry(frame_Ps, textvariable=defaultmaf3)
            Pure3_mafVal3.place(x=300, y=140, width=30, anchor='nw')
            Pure3_mafVal4 = tk.Entry(frame_Ps, textvariable=defaultmaf4)
            Pure3_mafVal4.place(x=340, y=140, width=30, anchor='nw')
            Pure3_mafVal5 = tk.Entry(frame_Ps, textvariable=defaultmaf5)
            Pure3_mafVal5.place(x=380, y=140, width=30, anchor='nw')


    def Count3():
        print("Pure3_Count2")
        pure3_count_start_time = time.time()
        rightshow.insert(tk.INSERT, '\n')
        rightshow.insert("insert", '=== Pure3_Count3 ====\n')
        order_val = int(sVal.get())
        PD_var = Decimal(proVal.get())
        H2_var = Decimal(hVal.get())
        MAF_list = []
        for i in range(order_val):
            MAF = float(globals()['Pure3_mafVal'+str(i+1)].get())
            MAF_list.append(MAF)
        x_result, v, pd, h = pure3_calculation(MAF_list,float(PD_var),float(H2_var), order_val)
        if v == 0:
            rightshow.insert(tk.INSERT, 'There is no solution to the problem defined.') 
        else:
            x_result_show = [float('{:.6f}'.format(i)) for i in x_result]
            pure3_var2.set(str(x_result_show).replace('[', '').replace(']', '').replace(',', ''))
            rightshow.insert("end", 'Count OK!')
            rightshow.insert(tk.INSERT, '\n')
            pure3_count_end_time = time.time()
            print('pure3 count time cost : %.6f second' %(pure3_count_end_time-pure3_count_start_time))
    count3 = tk.Button(frame_Ps, text='Count', font=('Times New Roman', 16, 'bold'), width=10, height=1, command=Count3)
    count3.configure(bg="gray")
    count3.place(x=170, y=180, anchor='nw')

    def Add_pure3():
        print("Pure3_Add")
        pure3_add_start_time = time.time()
        global CurrentModelNum
        global ModelInfo
        defaultmodelValue = float(defaultmodel.get())
        if defaultmodelValue > CurrentModelNum:
            addpure3['state'] = tk.NORMAL
            CurrentModelNum += 1
            ModelInfo.append([7])
            rightshow.insert(tk.INSERT, '==========' + '\n')
            rightshow.insert(tk.INSERT, 'Current Model:  ' + str(CurrentModelNum) + '\n')
            rightshow.insert(tk.INSERT, 'Type:  Pure(3)' + '\n')
            if pure3_var2:
                ModelInfo[CurrentModelNum-1].append([])
                for each_str in pure3_var2.get()[1:-1].replace("'",'').split(', '):
                    if each_str:
                        ModelInfo[CurrentModelNum-1][1].append(float(each_str))
                for each_index in ModelInfo[CurrentModelNum-1][1]:
                    rightshow.insert(tk.INSERT, str(each_index) + '\n')
            else:
                rightshow.insert(tk.INSERT, 'Error! (Penetrance)' + '\n') 
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            # order
            order_val = int(sVal.get())
            ModelInfo[CurrentModelNum-1].append(order_val)            
            rightshow.insert(tk.INSERT, 'order: ' + str(order_val) + '\n')
            # MAF
            ModelInfo[CurrentModelNum-1].append([])
            for i in range(order_val):
                MAF = float(globals()['Pure3_mafVal'+str(i+1)].get())
                if (MAF <= 0) or (MAF > 0.5):
                    rightshow.insert(tk.INSERT, 'Error! (MAF of SNP)' + '\n')
                    CurrentModelNum -= 1
                    ModelInfo.pop()
                    return
                else:
                    ModelInfo[CurrentModelNum-1][3].append(MAF)
                    rightshow.insert(tk.INSERT, 'MAF_' + str(i+1) + ': ' + str(MAF) + '\n')
            # PD :The proportion of cases
            PD_var = float(proVal.get())
            if ((abs(PD_var) != PD_var) or (PD_var > 1) or (PD_var == 0)):
                rightshow.insert(tk.INSERT, 'Error! (PD)')
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            else:
                ModelInfo[CurrentModelNum-1].append(PD_var)
                rightshow.insert(tk.INSERT, 'PD: ' + str(PD_var) + '\n') 
            # H2
            H2_var = float(hVal.get())
            if H2_var == 0:
                rightshow.insert(tk.INSERT, 'Error! (H2)') 
                CurrentModelNum -= 1
                ModelInfo.pop()
                return
            else:
                ModelInfo[CurrentModelNum-1].append(H2_var)
                rightshow.insert(tk.INSERT, 'H2: ' + str(H2_var) + '\n')
            rightshow.insert(tk.INSERT, 'Add OK!' + '\n') 
            pure3_add_end_time = time.time()
            print('pure3 add time cost : %.6f second' %(pure3_add_end_time-pure3_add_start_time))
            print(ModelInfo)
        else:
            addpure3['state'] = tk.DISABLED
    addpure3 = tk.Button(frame_Ps, text='Add', font=('Times New Roman', 16, 'bold'), width=10, height=1, command=Add_pure3)
    addpure3.configure(bg="gray")
    addpure3.place(x=590, y=180, anchor='nw')


def Epistasis(frame_Epistasis):
    print("Epistasis")
    ss = ttk.Style()
    ss.configure('Two.TNotebook.Tab', font=('Times New Roman', 16,'bold'), anchor='n')
    ss.configure('Two.TNotebook', tabposition='sw')
    # ss.map("Two.TNotebook.Tab", background=[("selected", 'red')], foreground=[("selected", 'green')])
    ss.map("Two.TNotebook.Tab", foreground=[("selected", 'blue')])
    note = ttk.Notebook(frame_Epistasis,style='Two.TNotebook')
    note.place(relx=0, rely=0, relwidth=1, relheight=1)
    global im3, ph3
    im3 = Image.open(os.path.join(data_dir, 'empty.jpg')).resize((90, 40))
    ph3 = ImageTk.PhotoImage(im3)

    frame_public = tk.Frame(note)
    note.add(frame_public, text='Public', image=ph3, compound='center')
    res1 = public(frame_public)
    res1.current(0)
    frame_Restricted1 = tk.Frame(note)
    note.add(frame_Restricted1, text='Restricted(1)', image=ph3, compound='center')
    restricted1(frame_Restricted1)
    frame_Restricted2 = tk.Frame(note)
    note.add(frame_Restricted2, text='Restricted(2)', image=ph3, compound='center')
    restricted2(frame_Restricted2)
    #res(3)
    frame_Restricted3 = tk.Frame(note)
    note.add(frame_Restricted3, text='Restricted(3)', image=ph3, compound='center')
    restricted3(frame_Restricted3)
    frame_Pure = tk.Frame(note)
    note.add(frame_Pure, text='Pure(1)', image=ph3, compound='center')
    Pure(frame_Pure)
    #Pure(2)
    frame_Pure2 = tk.Frame(note)
    note.add(frame_Pure2, text='Pure(2)', image=ph3, compound='center')
    Pure2(frame_Pure2)
    #Pure(3)
    frame_Pure3 = tk.Frame(note)
    note.add(frame_Pure3, text='Pure(3)', image=ph3, compound='center')
    Pure3(frame_Pure3)

def LD(frame_LD):
    print("LD")
    tk.Label(frame_LD, text="Parameter setting:", font=('Times New Roman',14,'bold')).place(x=52, y=10, anchor='nw')
    frame_Ps = tk.Frame(frame_LD, height=250, width=900, relief='ridge', borderwidth=1)
    frame_Ps.place(relx=0.5, rely=0.06, anchor='n')
    
    global avgLd, pos1, Maf1, pos2, Maf2, LdLevel
    tk.Label(frame_Ps, text="Average of Adjacent LD:", font=('Times New Roman',11)).place(x=50, y=20, anchor='nw')
    avgLd = tk.StringVar(value='0')
    caseVal = tk.Entry(frame_Ps, textvariable=avgLd).place(x=230, y=20, anchor='nw')
    tk.Label(frame_Ps, text="Specified Special LD:", font=('Times New Roman',11)).place(x=50, y=60, anchor='nw')
    tk.Label(frame_Ps, text="Position of the frist SNP:", font=('Times New Roman',11)).place(x=70, y=90, anchor='nw')
    pos1 = tk.StringVar(value='50')
    snpslVal = tk.Entry(frame_Ps, textvariable=pos1).place(x=250, y=90, anchor='nw')
    tk.Label(frame_Ps, text="MAF of the first SNP:", font=('Times New Roman',11)).place(x=450, y=90, anchor='nw')
    Maf1= tk.StringVar(value='0.5')
    modelsVal = tk.Entry(frame_Ps, textvariable=Maf1).place(x=630, y=90, anchor='nw')
    tk.Label(frame_Ps, text="Position of the second SNP:", font=('Times New Roman',11)).place(x=70, y=120, anchor='nw')
    pos2 = tk.StringVar(value='90')
    uMAFVal = tk.Entry(frame_Ps, textvariable=pos2).place(x=250, y=120, anchor='nw')
    tk.Label(frame_Ps, text="MAF of the second SNP:", font=('Times New Roman',11)).place(x=450, y=120, anchor='nw')
    Maf2 = tk.StringVar(value='0.5')
    lMAFVal = tk.Entry(frame_Ps, textvariable=Maf2).place(x=630, y=120, anchor='nw')
    tk.Label(frame_Ps, text="The LD leveL:", font=('Times New Roman',11)).place(x=70, y=150, anchor='nw')
    LdLevel = tk.StringVar(value='0.5')
    ldVal = tk.Entry(frame_Ps, textvariable=LdLevel).place(x=250, y=150, anchor='nw')
    b1 = tk.Button(frame_Ps, text='Specify', font=('Times New Roman', 16,'bold'), width=10, height=1, command=Specify)
    b1.configure(bg="gray")
    b1.place(x=350, y=190, anchor='nw')

def Specify():
    LD_specify_start_time = time.time()
    global LdSpecifyClickTime, LDInfor, HightLD, bool_LD
    avgLdValue= float(avgLd.get())
    Maf1Value = float(Maf1.get())
    Maf2Value = float(Maf2.get())
    defaultsnpsValue = float(defaultsnps.get())
    pos1Value = float(pos1.get())
    pos2Value = float(pos2.get())
    LdLevelValue = float(LdLevel.get())

    if Maf1Value > Maf2Value:
        HightLD = Maf2Value * (1 - Maf1Value) / (Maf1Value * (1 - Maf2Value))
    else:
        HightLD = Maf1Value * (1 - Maf2Value) / (Maf2Value * (1 - Maf1Value))
    if HightLD < LdLevelValue:
        bool_LD = 0
    else:
        bool_LD = 1

    if avgLdValue > 1 or avgLdValue <=0:
        rightshow.insert("insert", 'Error info avgLdValue \n')
        return
    elif 0 >= Maf1Value > 0.5:
        rightshow.insert("insert", 'Error info Maf1Value \n')
        return
    elif 0 >= Maf2Value > 0.5:
        rightshow.insert("insert", 'Error info Maf2Value \n')
        return

    elif bool_LD == 0:
        rightshow.insert("insert", 'The Hight LD level ' + str(HightLD)+ '\n')
        return
    elif LdLevelValue <= 0:
        rightshow.insert("insert", 'Error info defaultldValue \n')
        return
    elif pos1Value > defaultsnpsValue:
        rightshow.insert("insert", 'Error Position 1 \n')
        return
    elif pos2Value > defaultsnpsValue:
        rightshow.insert("insert", 'Error Position 2 \n')
        return
    # elif LdSpecifyClickTime != 0:
    else:
        pos1ValueList.append(pos1Value)
        pos2ValueList.append(pos2Value)
        print("***********")
        # if pos1ValueList[0] == pos1Value and len(pos1ValueList) > 1 :
        if len(set(pos1ValueList)) < len(pos1ValueList):
            rightshow.insert("insert", 'Error Pos1 same with before \n')
            pos1ValueList.remove(pos1ValueList[-1])
            pos2ValueList.remove(pos2ValueList[-1])
            return
        # elif pos2ValueList[0] == pos2Value and len(pos2ValueList) > 1 :
        elif len(set(pos2ValueList)) < len(pos2ValueList):
            rightshow.insert("insert", 'Error Pos2 same with before  \n')
            pos1ValueList.remove(pos1ValueList[-1])
            pos2ValueList.remove(pos2ValueList[-1])
            return
        else:
            LdSpecifyClickTime += 1
            rightshow.insert("insert", "==== LD" + str(LdSpecifyClickTime) + " ==== \n")
            rightshow.insert("insert", "Position 1: " + str(pos1Value) + " \n")
            rightshow.insert("insert", "Position 2: " + str(pos2Value) + " \n")
            rightshow.insert("insert", "MAF 1: " + str(Maf1Value) + " \n")
            rightshow.insert("insert", "MAF 2: " + str(Maf2Value) + " \n")
            rightshow.insert("insert", "LD level:  " + str(LdLevelValue) + " \n")
            LD_specify_end_time = time.time()
            print('LD specify time cost : %.6f second' %(LD_specify_end_time-LD_specify_start_time))
            LDInfor.append({'Position 1':str(pos1Value), 'Position 2':str(pos2Value), 'MAF 1':str(Maf1Value), 'MAF 2':str(Maf2Value), 'LD level':str(LdLevelValue)})
        print(pos1ValueList)
        print(pos2ValueList)
        print(LDInfor)

def Outputs(frame_Outputs):
    print("Outputs")
    tk.Label(frame_Outputs, text="Parameter setting:", font=('Times New Roman',14,'bold')).place(x=52, y=10, anchor='nw')
    frame_Ps = tk.Frame(frame_Outputs, height=250, width=900, relief='ridge', borderwidth=1)
    frame_Ps.place(relx=0.5, rely=0.06, anchor='n')

    global defaultdata, var1C1, var2C2, defaultsnp, var1C3, var2C4, defaultrep
    tk.Label(frame_Ps, text="FileName of chromosome data: ", font=('Times New Roman',11)).place(x=50, y=40, anchor='nw')
    defaultdata = tk.StringVar(value='chromosome')
    dataVal = tk.Entry(frame_Ps, textvariable=defaultdata).place(x=250, y=40, anchor='nw')
    var1C1 = tk.IntVar()
    var1C1.set('0')
    var2C2 = tk.IntVar()
    var2C2.set('0')
    c1 = tk.Checkbutton(frame_Ps, text='chromosome data(.txt)', font=('Times New Roman',11), variable=var1C1, onvalue=1, offvalue=0,
                        command=outputSelction("chromosome data")).place(x=50, y=80, anchor='nw')
    c2 = tk.Checkbutton(frame_Ps, text='chromosome data(.mat)', font=('Times New Roman',11), variable=var2C2, onvalue=1, offvalue=0,
                        command=outputSelction("chromosome data")).place(x=50, y=120, anchor='nw')
    tk.Label(frame_Ps, text="FileName of SNP data: ", font=('Times New Roman',11)).place(x=450, y=40, anchor='nw')
    defaultsnp= tk.StringVar(value='SNP')
    snpVal = tk.Entry(frame_Ps, textvariable=defaultsnp).place(x=600, y=40, anchor='nw')
    var1C3 = tk.IntVar()
    var1C3.set('0') 
    var2C4 = tk.IntVar()
    var2C4.set('1')
    c3 = tk.Checkbutton(frame_Ps, text='SNP data(.txt)', font=('Times New Roman',11), variable=var1C3, onvalue=1, offvalue=0,
                        command=outputSelction("snp txt")).place(x=450, y=80, anchor='nw')
    c4 = tk.Checkbutton(frame_Ps, text='SNP data(.mat)', font=('Times New Roman',11), variable=var2C4, onvalue=1, offvalue=0,
                        command=outputSelction("snp mat")).place(x=450, y=120, anchor='nw')

    tk.Label(frame_Ps, text="Repeat simulation number:", font=('Times New Roman',11)).place(x=50, y=180, anchor='nw')
    defaultrep= tk.StringVar(value='1')
    repVal = tk.Entry(frame_Ps, textvariable=defaultrep).place(x=250, y=180, anchor='nw')

def outputSelction(type):
    print(type)

def Preset():
    print("Preset")

def Simulation(Case_Num, Control_Num, SNP_Num, L_MAF, H_MAF, Aver_LD, LDInfo, FileName, FileFormat, ModelInformation, RepeatNumValue):
    print('------------------------------------------Simulation---------------------------------------------------------')
    # print(Case_Num, Control_Num, SNP_Num, L_MAF, H_MAF, Aver_LD, LDInfo, FileName, FileFormat, ModelInformation, RepeatNumValue)
    Adj_LD_Level = generateAdjLD(SNP_Num, Aver_LD)
    rightshow.insert(tk.INSERT, 'generate adjacent LD OK!' + '\n')
    time.sleep(0.0000000001)

    MAF, Adj_LD_Level = generateMAF(SNP_Num, L_MAF, H_MAF, LDInfo, ModelInformation, Adj_LD_Level)
    rightshow.insert(tk.INSERT, 'generate MAF OK!' + '\n')
    time.sleep(0.0000000001)

    Match, Tag = Match_LD_MAF(Adj_LD_Level, MAF)
    if Match == 0:
        rightshow.insert(tk.INSERT, 'Match MAF and LD OK!' + '\n')
    else:
        rightshow.insert(tk.INSERT, 'Error: Match MAF and LD!' + '\n')
        return
    time.sleep(0.0000000001)
    # 
    TotalBytes = 560000000
    if TotalBytes < (SNP_Num * 2):
        rightshow.insert(tk.INSERT, 'Error: Too many SNP!' + '\n')
        return
    TotalRow = math.floor(TotalBytes/SNP_Num)
    if TotalRow % 2 != 0:
        TotalRow -= 1
    SNP_Iter_Num = [0 for index in range(math.ceil((Case_Num + Control_Num) / TotalRow))]
    for i in range(len(SNP_Iter_Num)-1):
        SNP_Iter_Num[i] = TotalRow
    SNP_Iter_Num[len(SNP_Iter_Num)-1] =(Case_Num+Control_Num)-TotalRow * (len(SNP_Iter_Num) - 1)


    Chr_Iter_Num =[0 for index in range(math.ceil(2*(Case_Num + Control_Num)/TotalRow))]
    for i in range(len(Chr_Iter_Num)-1):
        Chr_Iter_Num[i] = TotalRow
    Chr_Iter_Num[len(Chr_Iter_Num)-1] = 2 * (Case_Num+Control_Num)-TotalRow * (len(Chr_Iter_Num)- 1)

    if len(Chr_Iter_Num) != 1:
        FileFormat[0][1] = 0
        if FileFormat[0][0] == 0:
            FileFormat[0][0] = 1
    if len(SNP_Iter_Num) != 1:
        FileFormat[1][1] = 0
        if FileFormat[1][0] == 0:
            FileFormat[1][0] = 1
    rightshow.insert(tk.INSERT, 'Transaction probability...' + '\n')
    rightshow.insert(tk.INSERT, '-- iter -- 0%')
    time.sleep(0.0000000001)
    # 
    Trans = np.zeros((2,SNP_Num-1))
    for i in range(SNP_Num-1):
        Trans[0][i] = R2Equation(Adj_LD_Level[i], MAF[i], MAF[i+1])[0]
        Trans[1][i] = R2Equation(Adj_LD_Level[i], MAF[i], MAF[i+1])[1]
        if i % 50 == 0:
            rightshow.delete("end-1c linestart", "end")
            rightshow.insert(tk.INSERT, '\n')
            rightshow.insert("end", '-- iter -- ' + str(i*100/SNP_Num) + '%') 
            time.sleep(0.0000000001)
    # print('Trans', Trans)
    rightshow.delete("end-1c linestart", "end")
    rightshow.insert(tk.INSERT, '\n')
    rightshow.insert("end", '-- iter -- ' + str(100) + '%' + '\n') 
    rightshow.insert(tk.INSERT, 'Transaction probability OK!' + '\n')
    time.sleep(0.0000000001)

    # LD_Tag
    LD_Tag = np.zeros((2,SNP_Num))
    LDNum = len(LDInfo)
    if LDNum > 0:
        for i in range(LDNum):
            if int(float(LDInfo[i]['Position 1'])) > int(float(LDInfo[i]['Position 2'])):
                LD_Tag[0][int(float(LDInfo[i]['Position 1']))] = int(float(LDInfo[i]['Position 2']))
                LD_Tag[1][int(float(LDInfo[i]['Position 1']))] = float(LDInfo[i]['LD level'])
            else:
                LD_Tag[0][int(float(LDInfo[i]['Position 2']))] = int(float(LDInfo[i]['Position 1']))
                LD_Tag[1][int(float(LDInfo[i]['Position 2']))] = float(LDInfo[i]['LD level'])
    # print('LD_Tag', LD_Tag)

    # simulate
    for RepeatNum in range(RepeatNumValue):
        if RepeatNumValue == 1:
            rightshow.insert(tk.INSERT, 'simulate ...' + '\n')
        else:
            rightshow.insert(tk.INSERT, 'simulate [' + str(RepeatNum+1) + ']' + '\n')
        rightshow.insert(tk.INSERT, '-- iter -- 0%')
        time.sleep(0.0000000001)
        Current_Control_Num = 0  # It is the control number of simulated data (the number of samples that do not affect complex diseases)
        Current_Case_Num = 0 # It is the number of cases in simulated data (the number of samples affecting complex diseases, with the last column being 1)

        SNP_simulate = np.zeros((SNP_Iter_Num[0], SNP_Num+1))
        SNP_times =0
         #Here is a simulation of chromosomes
        for ChrIter in range(len(Chr_Iter_Num)):
            Chr_simulate = np.zeros((Chr_Iter_Num[ChrIter],SNP_Num)) # 4000*100 int [0,1]
            CurrentRow = 1
            while CurrentRow <= Chr_Iter_Num[ChrIter]:
                #print('CurrentRow',CurrentRow)
                Chr_simulate[CurrentRow-1, 0] = int(GenerateAllele(0, MAF[0], 0, -1))
                for i in range(SNP_Num-1):
                    if LD_Tag[0][i+1] == 0:
                        Chr_simulate[CurrentRow-1, i+1] = int(GenerateAllele(Trans[0][i], MAF[i], Trans[1][i], Chr_simulate[CurrentRow-1, i]))
                    else:
                        aToB, AToB = R2Equation(LD_Tag[1][i+1], MAF[int(LD_Tag[0][i+1])], MAF[i+1])
                        Chr_simulate[CurrentRow-1, i+1] = int(GenerateAllele(aToB, MAF[int(LD_Tag[0][i+1])], AToB, Chr_simulate[CurrentRow-1, int(LD_Tag[0][i+1])]))
               #The following is a simulation of SNP samples, where the addition of two chromosomes results in one SNP
                if CurrentRow % 2 == 0:
                    for j in range(SNP_Num):
                        if (ChrIter+1) % 2 == 1:
                            SNP_simulate[int(CurrentRow/2-1), j] = int(Chr_simulate[CurrentRow-1, j]+Chr_simulate[CurrentRow-2, j])
                        else:
                            SNP_simulate[int(TotalRow/2+CurrentRow/2), j] = int(Chr_simulate[CurrentRow-1, j]+Chr_simulate[CurrentRow-2, j])

                    SNP_times = int(SNP_times)
                    #Mark this SNP,Status == 1 is case，at this point, the last column is 1
                    # Status == 0 is control
                    Status = StatusDecision(SNP_simulate[SNP_times, :SNP_Num], ModelInformation)
                    if Status == 1:#case
                        if Current_Case_Num < Case_Num:
                            SNP_simulate[SNP_times, SNP_Num] = Status  # Column SNP_Num of row SNP_times
                            Current_Case_Num = Current_Case_Num + 1
                            rightshow.delete("end-1c linestart", "end")
                            rightshow.insert(tk.INSERT, '\n')
                            rightshow.insert("end", '-- iter -- ' + str(100*(Current_Case_Num+Current_Control_Num)/(Case_Num+Control_Num)) + '%')
                            time.sleep(0.0000000001)
                        else:
                            CurrentRow -= 2
                    else:#Status == 0,Control,
                        if Current_Control_Num < Control_Num:
                            SNP_simulate[SNP_times, SNP_Num] = Status
                            Current_Control_Num = Current_Control_Num + 1
                            rightshow.delete("end-1c linestart", "end")
                            rightshow.insert(tk.INSERT, '\n')
                            rightshow.insert("end", '-- iter -- ' + str(100*(Current_Case_Num+Current_Control_Num)/(Case_Num+Control_Num)) + '%') 
                            time.sleep(0.0000000001)
                        else:
                            CurrentRow -= 2                        
                    if (ChrIter+1) % 2 == 0:
                        SNPNUMBER = CurrentRow/2 + Chr_Iter_Num[ChrIter-2]/2
                        SNP_times = CurrentRow/2 + Chr_Iter_Num[ChrIter-2]/2
                    else:
                        SNPNUMBER = CurrentRow/2
                        SNP_times = CurrentRow/2
                    if SNP_Iter_Num[math.ceil((ChrIter+1)/2)-1] == SNPNUMBER:
                        if FileFormat[1][1] == 1:
                            rightshow.insert(tk.INSERT, '\n')
                            rightshow.insert(tk.INSERT, 'save SNP data (.mat)...' + '\n')
                            time.sleep(0.0000000001)
                            if RepeatNumValue == 1:
                                Name = FileName[1] + '.mat'
                            else:
                                Name = FileName[1] + '_' + str(RepeatNum+1) + '.mat'
                            scipy.io.savemat(Name, mdict = {'SNP_simulate':SNP_simulate})
                        if FileFormat[1][0] == 1:
                            rightshow.insert(tk.INSERT, '\n')
                            rightshow.insert(tk.INSERT, 'save SNP data (.txt)...' + '\n')
                            time.sleep(0.0000000001)
                            if RepeatNumValue == 1:
                                Name = FileName[1] + '.txt'
                            else:
                                Name = FileName[1] + '_' + str(RepeatNum+1) + '.txt'
                            np.savetxt('SNP_simulate.txt', np.c_[SNP_simulate],fmt='%d',delimiter='\t')
                        if len(SNP_Iter_Num) > 1:
                            SNP_simulate = np.zeros((Chr_Iter_Num[ChrIter],SNP_Num))
                CurrentRow += 1
            if FileFormat[0][1] == 1:
                rightshow.insert(tk.INSERT, 'save Chromosome data (.mat)...' + '\n')
                time.sleep(0.0000000001)
                if RepeatNumValue == 1:
                    Name = FileName[0] + '.mat'
                else:
                    Name = FileName[0] + '_' + str(RepeatNum+1) + '.mat'
                scipy.io.savemat(Name, mdict = {'Chr_simulate':Chr_simulate})
            if FileFormat[0][0] == 1:
                rightshow.insert(tk.INSERT, 'save Chromosome data (.txt)...' + '\n')
                time.sleep(0.0000000001)
                if RepeatNumValue == 1:
                    Name = FileName[0] + '.txt'
                else:
                    Name = FileName[0] + '_' + str(RepeatNum+1) + '.txt'
                np.savetxt('Chr_simulate.txt', np.c_[Chr_simulate],fmt='%d',delimiter='\t')

    rightshow.insert(tk.INSERT, '===========================' + '\n')
    rightshow.insert(tk.INSERT, '====== Simulation OK ======' + '\n')
    rightshow.insert(tk.INSERT, '===========================' + '\n')
    time.sleep(0.0000000001)
    # vertify
    rightshow.insert(tk.INSERT, 'vertify data ...' + '\n')
    time.sleep(0.0000000001)
    if (FileFormat[0][1] == 1) and (FileFormat[1][1] == 1):
        # SNP_simulate  Chr_simulate
        rightshow.insert(tk.INSERT, '=== Cases:  ' + str(SNP_simulate[:,-1].tolist().count(1)) + '\n')
        # Controls
        rightshow.insert(tk.INSERT, '=== Controls:  ' + str(SNP_simulate[:,-1].tolist().count(0)) + '\n')
        # SNPs
        rightshow.insert(tk.INSERT, '=== SNPs:  ' + str(SNP_simulate.shape[1]-1) + '\n')
        UpperBound, LowerBound = BoundMAFs(Chr_simulate)
        # Upper bound of MAFs
        rightshow.insert(tk.INSERT, '=== Upper bound of MAFs:  ' + str(UpperBound) + '\n')
        # Lower bound of MAFs
        rightshow.insert(tk.INSERT, '=== Lower bound of MAFs:  ' + str(LowerBound) + '\n')
        # Average of Adjacent LD
        rightshow.insert(tk.INSERT, '=== Adjacent LD:  ' + str(MeanAdjLD(Chr_simulate)) + '\n')
        time.sleep(0.0000000001)
        # LDInfo
        rightshow.insert(tk.INSERT, '=== LD Information:' + '\n')
        for i in range(len(LDInfo)):
            rightshow.insert(tk.INSERT, '= LD:  ' + str(i) + '\n')
            rightshow.insert(tk.INSERT, 'Position 1:  ' + str(LDInfo[i]['Position 1']) + '\n')
            rightshow.insert(tk.INSERT, 'Position 2:  ' + str(LDInfo[i]['Position 2']) + '\n')
            rightshow.insert(tk.INSERT, 'MAF 1:  ' + str((Chr_simulate[:,int(float(LDInfo[i]['Position 1']))].tolist().count(1))/(Chr_simulate.shape[0])) + '\n')
            rightshow.insert(tk.INSERT, 'MAF 2:  ' + str((Chr_simulate[:,int(float(LDInfo[i]['Position 2']))].tolist().count(1))/(Chr_simulate.shape[0])) + '\n')
            rightshow.insert(tk.INSERT, 'LD Level:  ' + str(ComputerLD(np.vstack((Chr_simulate[:,int(float(LDInfo[i]['Position 1']))],Chr_simulate[:,int(float(LDInfo[i]['Position 2']))])))) + '\n')
        time.sleep(0.0000000001)
        # MD Information
        rightshow.insert(tk.INSERT, '=== MD Information:' + '\n')
        for i in range(len(ModelInformation)):
            rightshow.insert(tk.INSERT, '= MD:  ' + str(i) + '\n')
            rightshow.insert(tk.INSERT, 'k_way:  ' + str(ModelInformation[i][0]) + '\n')
            rightshow.insert(tk.INSERT, 'Positions:' + '\n')
            for j in range(int(ModelInformation[i][0])):
                rightshow.insert(tk.INSERT, str(ModelInformation[i][3][j]) + '\n')
            rightshow.insert(tk.INSERT, 'MAFs:' + '\n')
            for j in range(int(ModelInformation[i][0])):
                rightshow.insert(tk.INSERT, str((Chr_simulate[:,int(ModelInformation[i][3][j])].tolist().count(1))/(Chr_simulate.shape[0])) + '\n')
            UnUsedPara2, pvalue = PenetranceCal(ModelInformation, i, SNP_simulate)
            rightshow.insert(tk.INSERT, 'Chi-2 P-value::  ' + str(pvalue) + '\n')
        time.sleep(0.0000000001)
    else:
        rightshow.insert(tk.INSERT, 'Too many to vertify or no need!' + '\n')

def Simulate_Button():
    InforHandles = {'Cases':defaultcase, 'Controls':defaultcontrol, 'SNPs':defaultsnps, 'Models':defaultmodel, \
        'Upper bound of MAFs':defaultuMAF, 'Lower bound of MAFs':defaultlMAF, 'Average of Adjacent LD':avgLd}

    FileHandles = [defaultdata, var1C1, var2C2, defaultsnp, var1C3, var2C4]
    RepeatNum = defaultrep.get()
    # code biginning
    # bS['state'] = tk.DISABLED
    rightshow.insert(tk.INSERT, '==========================' + '\n')
    rightshow.insert(tk.INSERT, '======= Parameters =======' + '\n')
    rightshow.insert(tk.INSERT, '==========================' + '\n')
    simulate_start_time = time.time()
    # %%%%%% General
    rightshow.insert(tk.INSERT, '%%%%%% General' + '\n')
    for i in range(4):
        num = float(list(InforHandles.values())[i].get())
        if np.round(num) < 0:
            rightshow.insert(tk.INSERT, 'Error! (' + list(InforHandles.keys())[i] + ')' + '\n')
            bS['state'] = tk.NORMAL
            return
    TotalBytes = 560000000
    OneBytes = 8
    if (TotalBytes/OneBytes) < (float(list(InforHandles.values())[2].get())*2):
        rightshow.insert(tk.INSERT, 'Error: Too many SNP! <' + str(int(TotalBytes/OneBytes)) + '\n')
        bS['state'] = tk.NORMAL
        return 
    if (TotalBytes/OneBytes) < (float(list(InforHandles.values())[0].get())):
        rightshow.insert(tk.INSERT, 'Error: Too many Cases!' + '\n')
        bS['state'] = tk.NORMAL
        return 
    if (TotalBytes/OneBytes) < (float(list(InforHandles.values())[1].get())):
        rightshow.insert(tk.INSERT, 'Error: Too many Controls!' + '\n')
        bS['state'] = tk.NORMAL
        return 
    num = float(list(InforHandles.values())[4].get())
    if (num < 0) or (num > 0.5):
        rightshow.insert(tk.INSERT, 'Error! (Upper bound of MAFs)' + '\n')
        bS['state'] = tk.NORMAL
        return         
    num = float(list(InforHandles.values())[5].get())
    if (num < 0) or (num > float(list(InforHandles.values())[4].get())):
        rightshow.insert(tk.INSERT, 'Error! (Lower bound of MAFs)' + '\n')
        bS['state'] = tk.NORMAL
        return
    num = float(list(InforHandles.values())[6].get())
    if (num < 0) or (num > 1):
        rightshow.insert(tk.INSERT, 'Error! (Average of Adjacent LD)' + '\n')
        bS['state'] = tk.NORMAL
        return
    show_str = []
    for each_key in list(InforHandles.keys()):
        show_str.append(each_key + ': ')
    for index, each_value in enumerate(list(InforHandles.values())):
        show_str[index] = show_str[index] + each_value.get() + '\n'
        rightshow.insert(tk.INSERT, show_str[index])
    if np.round(float(RepeatNum)) < 0:
        rightshow.insert(tk.INSERT, 'Error! (Repeat Number)' + '\n')
        bS['state'] = tk.NORMAL
        return 
    else:
        rightshow.insert(tk.INSERT, 'Repeat Number: ' + str(RepeatNum) + '\n')
    # %%%%%% LD Information
    rightshow.insert(tk.INSERT, '\n')
    rightshow.insert(tk.INSERT, '%%%%%% LD Information' + '\n')
    RowLD = len(LDInfor)
    rightshow.insert(tk.INSERT, '=== Specify LD:  ' + str(RowLD) + '\n')
    factorTag = [0 for index in range(int(InforHandles['SNPs'].get()))]
    for i in range(RowLD):
        rightshow.insert(tk.INSERT, '= LD: ' + str(i+1) + '\n')
        rightshow.insert(tk.INSERT, 'Position 1: ' + str(LDInfor[i]['Position 1']) + '\n')
        factorTag[int(float(LDInfor[i]['Position 1']))] = 1
        rightshow.insert(tk.INSERT, 'Position 2: ' + str(LDInfor[i]['Position 2']) + '\n')
        factorTag[int(float(LDInfor[i]['Position 2']))] = 1
        rightshow.insert(tk.INSERT, 'MAF 1: ' + str(LDInfor[i]['MAF 1']) + '\n')
        rightshow.insert(tk.INSERT, 'MAF 2: ' + str(LDInfor[i]['MAF 2']) + '\n')
        rightshow.insert(tk.INSERT, 'LD Level: ' + str(LDInfor[i]['LD level']) + '\n')
    # %%%%%% Model Information
    rightshow.insert(tk.INSERT, '\n')
    rightshow.insert(tk.INSERT, '%%%%%% Model Information' + '\n')
    global ModelInformation
    RowModel = len(ModelInfo)
    ModelInformation = [[] for index in range(RowModel)]
    if RowModel != int(InforHandles['Models'].get()):
        rightshow.insert(tk.INSERT, 'No enough model!' + '\n')
        bS['state'] = tk.NORMAL
        return
    else:
        rightshow.insert(tk.INSERT, '=== Models:  ' + str(RowModel) + '\n')

    for i in range(RowModel):
        #  MD、k_way、MAFs
        rightshow.insert(tk.INSERT, '= MD: ' + str(i+1) + '\n')
        rightshow.insert(tk.INSERT, 'k_way: ' + str(ModelInfo[i][2]) + '\n')
        ModelInformation[i].append(ModelInfo[i][2])
        rightshow.insert(tk.INSERT, 'MAFs: ' + '\n')
        ModelInformation[i].append([])
        for each_MAFs in ModelInfo[i][3]:
            rightshow.insert(tk.INSERT, str(each_MAFs) + '\n')
            ModelInformation[i][1].append(each_MAFs)
        # Penetrance
        rightshow.insert(tk.INSERT, 'Penetrance: ' + '\n')
        ModelInformation[i].append([])            

        if (ModelInfo[i][0] == 1):                             ######### pubilc
            for each_Penetrance in ModelInfo[i][1]:
                if len(str(each_Penetrance).split(': ')) == 2:
                    Penetrance_show = float('{:.6f}'.format(float(str(each_Penetrance).split(': ')[1])))
                    print(Penetrance_show)
                    rightshow.insert(tk.INSERT, str(Penetrance_show) + '\n')
                    ModelInformation[i][2].append(float(str(each_Penetrance).split(': ')[1]))
                else:
                    Penetrance_show = float('{:.6f}'.format(float(str(each_Penetrance).split(':')[1])))
                    print(Penetrance_show)
                    rightshow.insert(tk.INSERT, str(Penetrance_show) + '\n')
                    ModelInformation[i][2].append(float(str(each_Penetrance).split(':')[1]))


        elif (ModelInfo[i][0] == 2) or (ModelInfo[i][0] == 3):  ######### res1\res2
            RTable = RelativeRisk(ModelInfo, i+1)
            # print(RTable)
            for j in range(3**ModelInfo[i][2]):
                Penetrance_show = float('{:.6f}'.format(RTable[j]))
                rightshow.insert(tk.INSERT, str(Penetrance_show) + '\n')
                ModelInformation[i][2].append(RTable[j])

        elif (ModelInfo[i][0] == 4):                            ########## res3
            if ModelInfo[i][4] == 2:
                PTable = find_max_prevalence(ModelInfo[i])
            elif ModelInfo[i][4] == 1:
                PTable = find_max_heritability(ModelInfo[i])
            # print(pTable)
            for j in range(3**ModelInfo[i][2]):
                Penetrance_show = float('{:.6f}'.format(PTable[j]))
                rightshow.insert(tk.INSERT, str(Penetrance_show) + '\n')
                ModelInformation[i][2].append(PTable[j])

        if (ModelInfo[i][0] == 5):                               ########## pure1
            for each_Penetrance in ModelInfo[i][1]:
                if len(str(each_Penetrance).split(': ')) == 2:
                    Penetrance_show = float('{:.6f}'.format(float(str(each_Penetrance).split(': ')[1])))
                    rightshow.insert(tk.INSERT, str(Penetrance_show) + '\n')
                    ModelInformation[i][2].append(float(str(each_Penetrance).split(': ')[1]))
                else:
                    Penetrance_show = float('{:.6f}'.format(float(str(each_Penetrance).split(':')[1])))
                    rightshow.insert(tk.INSERT, str(Penetrance_show) + '\n')
                    ModelInformation[i][2].append(float(str(each_Penetrance).split(':')[1]))

        elif (ModelInfo[i][0] == 6) or (ModelInfo[i][0] == 7):   ########## pure2 和 pure3
            for each_Penetrance in ModelInfo[i][1]:
                Penetrance_show = float('{:.6f}'.format(each_Penetrance))
                rightshow.insert(tk.INSERT, str(Penetrance_show) + '\n')
            ModelInformation[i][2] = ModelInfo[i][1]

                                                                 #### Positions
        rightshow.insert(tk.INSERT, 'Positions: ' + '\n')
        ModelInformation[i].append([])
        for k in range(ModelInfo[i][2]):
            factor, factorTag = NewPosition(factorTag)
            rightshow.insert(tk.INSERT, str(factor+1) + '\n')
            ModelInformation[i][3].append(factor)

    # %%%%%% File Information
    rightshow.insert(tk.INSERT, '\n')
    rightshow.insert(tk.INSERT, '%%%%%% File Information' + '\n')
    rightshow.insert(tk.INSERT, '== chromosome: ' + str(FileHandles[0].get()) + '\n')
    rightshow.insert(tk.INSERT, '.txt: ' + str(FileHandles[1].get()) + '\n')
    rightshow.insert(tk.INSERT, '.mat: ' + str(FileHandles[2].get()) + '\n')
    rightshow.insert(tk.INSERT, '== SNP: ' + str(FileHandles[3].get()) + '\n')
    rightshow.insert(tk.INSERT, '.txt: ' + str(FileHandles[4].get()) + '\n')
    rightshow.insert(tk.INSERT, '.mat: ' + str(FileHandles[5].get()) + '\n')
    FileName = [str(FileHandles[0].get()), str(FileHandles[3].get())]
    FileFormat = [[int(FileHandles[1].get()), int(FileHandles[2].get())], [int(FileHandles[4].get()), int(FileHandles[5].get())]]
    # %%%%%% simulation
    rightshow.insert(tk.INSERT, '\n')
    rightshow.insert(tk.INSERT, '%%%%%% simulation' + '\n')
    time.sleep(0.0000000001)
    print(ModelInformation)
    Simulation(int(defaultcase.get()), int(defaultcontrol.get()), int(defaultsnps.get()), float(defaultlMAF.get()), \
        float(defaultuMAF.get()), float(avgLd.get()), LDInfor, FileName, FileFormat, ModelInformation, int(RepeatNum))
    # Simulation(Case_Num,Control_Num,SNP_Num,L_MAF,H_MAF,Aver_LD,LDInfo,FileName,FileFormat,ModelInformation,hListBoxHandle,RepeatNumValue)
    rightshow.insert(tk.INSERT, '===========================' + '\n')
    rightshow.insert(tk.INSERT, '=========== END ===========' + '\n')
    rightshow.insert(tk.INSERT, '===========================' + '\n')
    simulate_end_time = time.time()
    print('simulate time cost : %.6f second' %(simulate_end_time-simulate_start_time))
    bS['state'] = tk.NORMAL
    rightshow_text = rightshow.get("0.0","end")
    # print(rightshow_text)
    with open('log.txt', 'a+', encoding='utf-8') as f:
        f.write(rightshow_text)
        f.close()

#close window
def Close():
    print("Close")
    sys.exit()

def Help():
    print("Help")
    # The path here is the absolute path where you placed help.mht
    webbrowser.open("help.mht")

def Init_interface(window):
    s = ttk.Style()
    s.configure('One.TNotebook.Tab', font=('Times New Roman',25,'bold'), width=15, anchor='n')
    s.configure('One.TNotebook', tabposition='nw')
    note = ttk.Notebook(window,style='One.TNotebook', padding=10)
    note.pack(fill=tk.BOTH, expand=True)
    global im1, ph1,im2, ph2,current_dir,data_dir
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, 'data')
    im1 = Image.open(os.path.join(data_dir, 'photo.jpg')).resize((80, 80))
    ph1 = ImageTk.PhotoImage(im1)
    im2 = Image.open(os.path.join(data_dir, 'empty.jpg')).resize((150, 80))
    ph2 = ImageTk.PhotoImage(im2)
    frame_PyepiSIM = tk.Frame(note, relief='ridge', borderwidth=1)
    note.add(frame_PyepiSIM, text='', image=ph1, compound='center', state='disabled')
    frame_General = tk.Frame(note, relief='ridge', borderwidth=1)
    note.add(frame_General, text='General', image=ph2, compound='center')
    general(frame_General)
    frame_Epistasis = tk.Frame(note, relief='ridge')
    note.add(frame_Epistasis, text='Epistasis', image=ph2, compound='center')
    Epistasis(frame_Epistasis)
    frame_LD = tk.Frame(note, relief='ridge', borderwidth=1)
    note.add(frame_LD, text='LD', image=ph2, compound='center')
    LD(frame_LD)
    frame_Outputs = tk.Frame(note, relief='ridge', borderwidth=1)
    note.add(frame_Outputs, text='Outputs', image=ph2, compound='center')
    Outputs(frame_Outputs)
    
    global rightshow, bS
    tk.Label(window, text="Command Prompt Window:", font=('Times New Roman',14,'bold')).place(x=70, y=410, anchor='nw')
    rightshow = tk.scrolledtext.ScrolledText(window, width=127,height=12)
    rightshow.place(x=70, y=445, anchor='nw')
    bS = tk.Button(window, text='Simulate', font=('Times New Roman', 16,'bold'), width=10, height=1, command=lambda:thread_it(Simulate_Button))
    bS.configure(bg="gray")
    bS.place(x=260, y=680, anchor='nw')
    bH = tk.Button(window, text='Help', font=('Times New Roman', 16,'bold'), width=10, height=1, command=Help)
    bH.configure(bg="gray")
    bH.place(x=460, y=680, anchor='nw')
    bC = tk.Button(window, text='Close', font=('Times New Roman', 16,'bold'), width=10, height=1, command=Close)
    bC.configure(bg="gray")
    bC.place(x=660, y=680, anchor='nw')

def run():
    window = tk.Tk()
    window.title('PyepiSIM')
    window.geometry('1040x800')

    EpistVar = tk.StringVar()
    defaults = tk.StringVar()

    global CurrentModelNum
    global ModelInfo
    CurrentModelNum = 0
    ModelInfo = []
    LdSpecifyClickTime = 0
    bool_LD = 0
    HightLD = 0
    # 获取当前模块的路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, 'data')

    # 读取 Excel 文件
    global df, df1, df2
    df = pd.read_excel(os.path.join(data_dir, 'public.xlsx'), na_filter=False)
    df1 = pd.read_excel(os.path.join(data_dir, 'restricted.xlsx'), na_filter=False)
    df2 = pd.read_excel(os.path.join(data_dir, 'restricted3.xlsx'), na_filter=False)
    # global df, df1, df2
    # df = pd.read_excel(r"./data/public.xlsx",na_filter=False)
    # df1 = pd.read_excel(r"./data/restricted.xlsx", na_filter=False)
    # df2 = pd.read_excel(r"./data/restricted3.xlsx", na_filter=False)
    # Store Position of first SNP under the LD button
    global pos1ValueList,pos2ValueList,LDInfor
    pos1ValueList = []
    # Store Position of sencond SNP under the LD button
    pos2ValueList = []
    LDInfor = []
    Init_interface(window)
    window.mainloop()
if  __name__ == "__main__":
    run()