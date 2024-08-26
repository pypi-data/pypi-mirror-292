import numpy as np
import matplotlib.pyplot as plt
import pickle
import os
import shutil
from tkinter import *
from customtkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from numpy.lib.function_base import extract
from trussit.repogen.repomaker import generateReport
from CTkMessagebox import CTkMessagebox
from trussit.repogen.solvers import solve_truss

class GUI:
    def __init__(self):
        self.main = CTk()
        self.main.title('Truss Solver')
        self.main.geometry('1280x720')
        self.main.resizable(False, False)

        self.frame1 = CTkFrame(self.main, width=1280, height=100, corner_radius=0, border_color='darkgrey',
                               border_width=1)
        self.frame2 = CTkScrollableFrame(self.main, width=400, height=620, corner_radius=0, border_color='darkgrey')
        self.frame3 = CTkFrame(self.main, width=862, height=620, corner_radius=0, border_color='darkgrey')
        self.tabview = CTkTabview(self.frame3, width=842, height=600)
        self.tabview.add('Deformation Plot')
        self.tabview.add('Summary')
        self.frame1.place(x=0, y=-1)
        self.frame2.place(x=0, y=100)
        self.frame3.place(x=417, y=100)
        self.tabview.place(x=10, y=10)

        button_addpoint = CTkButton(self.frame1, text='ADD\nNODE', height=80, width=80,
                                    command=self.callback_button_addpoint)
        button_addpoint.place(x=10, y=10)

        button_plot = CTkButton(self.frame1, text='PLOT', height=80, width=80, command=self.callback_plot)
        button_plot.place(x=100, y=10)

        button_clear = CTkButton(self.frame1, text='CLEAR', height=80, width=40, command=self.callback_clear,
                                 fg_color='red', hover_color='darkred')
        button_clear.place(x=1220, y=10)

        button_addnode = CTkButton(self.frame1, text='+', height=35, width=35, command=self.callback_addnode,
                                   fg_color='green', hover_color='darkgreen', font=('Arial', 20))
        button_addnode.place(x=340, y=15)
        button_subtractnode = CTkButton(self.frame1, text='-', height=35, width=35, command=self.callback_subtractnode,
                                        fg_color='red', hover_color='darkred', font=('Arial', 20))
        button_subtractnode.place(x=340, y=55)
        self.varp1 = StringVar(value=1)
        entry_nodestart = CTkEntry(self.frame1, height=35, width=50, textvariable=self.varp1, font=('Arial', 16))
        entry_nodestart.place(x=225, y=35)
        label_nodestart = CTkLabel(self.frame1, text='Start')
        label_nodestart.place(x=235, y=70)
        self.varp2 = StringVar(value=2)
        entry_nodeend = CTkEntry(self.frame1, height=35, width=50, textvariable=self.varp2, font=('Arial', 16))
        entry_nodeend.place(x=280, y=35)
        label_nodeend = CTkLabel(self.frame1, text='End')
        label_nodeend.place(x=293, y=70)
        label = CTkLabel(self.frame1, text='Element Conn.', font=('Arial', 12))
        label.place(x=230, y=5)

        self.varA = StringVar()
        entry_area = CTkEntry(self.frame1, height=30, width=80, textvariable=self.varA, font=('Arial', 16))
        entry_area.place(x=460, y=18)
        label_area = CTkLabel(self.frame1, text='Area', font=('Arial', 16))
        label_area.place(x=420, y=20)
        self.varE = StringVar()
        entry_moe = CTkEntry(self.frame1, height=30, width=80, textvariable=self.varE, font=('Arial', 16))
        entry_moe.place(x=460, y=53)
        label_moe = CTkLabel(self.frame1, text='E', font=('Arial', 16))
        label_moe.place(x=443, y=55)

        button_solve = CTkButton(self.frame1, text='SOLVE', height=80, width=80, command=self.callback_solve,
                                 fg_color='orange', hover_color='darkorange')
        button_solve.place(x=560, y=10)

        button_repo = CTkButton(self.frame1,text='REPORT',height=80, width=40, command=self.genrepo,
                                 fg_color='green', hover_color='darkgreen')
        button_repo.place(x=1150, y=10)

        self.idx = 0
        self.frames = []
        self.canvas1 = None
        self.summary = None

        self.main.protocol("WM_DELETE_WINDOW", lambda: self.shutoff())
        self.main.mainloop()
        del self.main

    def shutoff(self):
        if self.canvas1:
            plt.close()
            self.canvas1.get_tk_widget().destroy()
            self.frame3.destroy()
            self.frame3 = CTkFrame(self.main, width=862, height=620, corner_radius=0, border_color='darkgrey')
            self.frame3.place(x=417, y=100)
        shutil.rmtree('data', ignore_errors=True)
        self.main.quit()

    def callback_button_addpoint(self):
        frame_entry = CTkFrame(self.frame2, width=380, height=80, fg_color='lightgrey')

        ptlabel = CTkLabel(frame_entry, text='No.' + str(self.idx + 1), font=('Arial', 18))
        ptlabel.place(x=5, y=5)

        varx = StringVar()
        xdata = CTkEntry(frame_entry, width=50, height=12, textvariable=varx)
        xdata.place(x=85, y=10)
        xlabel = CTkLabel(frame_entry, text='x : ', font=('Arial', 16))
        xlabel.place(x=65, y=8)

        vary = StringVar()
        ydata = CTkEntry(frame_entry, width=50, height=12, textvariable=vary)
        ydata.place(x=85, y=40)
        ylabel = CTkLabel(frame_entry, text='y : ', font=('Arial', 16))
        ylabel.place(x=65, y=38)

        varFx = StringVar(value=0)
        Fxdata = CTkEntry(frame_entry, width=60, height=12, textvariable=varFx)
        Fxdata.place(x=175, y=10)
        Fxlabel = CTkLabel(frame_entry, text='Fx : ', font=('Arial', 16))
        Fxlabel.place(x=145, y=8)

        varFy = StringVar(value=0)
        Fydata = CTkEntry(frame_entry, width=60, height=12, textvariable=varFy)
        Fydata.place(x=175, y=40)
        Fylabel = CTkLabel(frame_entry, text='Fy : ', font=('Arial', 16))
        Fylabel.place(x=145, y=38)

        varsupport = StringVar()
        support = CTkOptionMenu(frame_entry, values=['Free', 'Pin', 'Roller'], width=75, height=25, variable=varsupport)
        support.set('Free')
        support.place(x=245, y=38)
        supportlabel = CTkLabel(frame_entry, text='Support', font=('Arial', 14))
        supportlabel.place(x=255, y=10)

        button_deletepoint = CTkButton(frame_entry, text='Delete', width=50, height=80,
                                       command=lambda frm=frame_entry: self.callback_delete_point(frm))
        button_deletepoint.place(x=330, y=0)
        frame_entry.grid(row=self.idx, column=0, padx=10, pady=5)

        self.frames.append((frame_entry, varx, vary, varFx, varFy, varsupport))
        self.canvas1 = None
        self.summary = None

        self.idx += 1

    def callback_delete_point(self, frm):
        for i in self.frames:
            if i[0] == frm:
                self.frames.remove(i)
                break
        frm.destroy()

    def callback_plot(self):
        self.conn = []
        self.coord = np.array([[float(i[1].get()), float(i[2].get())] for i in self.frames])
        self.force = np.array([[float(i[3].get()), float(i[4].get())] for i in self.frames])
        self.support = [
            [1, 1] if frame[5].get() == 'Free' else
            [0, 0] if frame[5].get() == 'Pin' else
            [1, 0] if frame[5].get() == 'Roller' else
            None
            for frame in self.frames
        ]
        if self.canvas1:
            plt.close()
            self.canvas1.get_tk_widget().destroy()
        #     self.frame3.destroy()
        #     self.frame3 = CTkFrame(self.main, width=862, height=620, corner_radius=0, border_color='darkgrey')
        #     self.frame3.place(x=417, y=100)

        self.fig1, self.ax1 = plt.subplots()
        self.fig1.set_facecolor('#CFCFCF')
        self.ax1.set_facecolor('#CFCFCF')
        self.ax1.plot(self.coord[:, 0], self.coord[:, 1], '.k', markersize=10)
        for n, i in enumerate(self.coord):
            self.ax1.text(i[0], i[1], str(n + 1), color='green')
        self.ax1.set_xlabel(r'$x$')
        self.ax1.set_ylabel(r'$y$')
        self.ax1.set_title(r'$Undeformated~Plot$')
        # ax1.legend(['Undeformed','Deformed'])
        self.ax1.axis('equal')
        self.fig1.tight_layout()
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.tabview.tab('Deformation Plot'))
        self.canvas1.draw()
        self.canvas1.get_tk_widget().place(x=0, y=10, width=810, height=550)

    def callback_clear(self):
        self.idx = 0
        for i in self.frames:
            i[0].destroy()
        self.frames.clear()
        if self.canvas1:
            plt.cla()
            plt.clf()
            self.canvas1.draw()
        if self.summary:
            self.summary.destroy()
            self.summary = CTkScrollableFrame(self.tabview.tab('Summary'), width=300, height=500)
            self.summary.place(x=10, y=10)

    def callback_addnode(self):
        if (int(self.varp1.get()), int(self.varp2.get())) not in self.conn and (
        int(self.varp2.get()), int(self.varp1.get())) not in self.conn:
            self.conn.append((int(self.varp1.get()), int(self.varp2.get())))

        plt.cla()
        self.ax1.plot(self.coord[:, 0], self.coord[:, 1], '.k', markersize=10)
        for n, i in enumerate(self.coord):
            self.ax1.text(i[0], i[1], str(n + 1), color='green')
        self.ax1.set_xlabel(r'$x$')
        self.ax1.set_ylabel(r'$y$')
        self.ax1.set_title(r'$Undeformated~Plot$')
        # ax1.legend(['Undeformed','Deformed'])
        self.ax1.axis('equal')
        for i in self.conn:
            self.ax1.plot([self.coord[i[0] - 1, 0], self.coord[i[1] - 1, 0]],
                          [self.coord[i[0] - 1, 1], self.coord[i[1] - 1, 1]], '-b')
        self.canvas1.draw()

    def callback_subtractnode(self):
        for i in self.conn:
            if (int(self.varp1.get()), int(self.varp2.get())) == i or (
            int(self.varp2.get()), int(self.varp1.get())) == i:
                self.conn.remove(i)

        plt.cla()
        self.ax1.plot(self.coord[:, 0], self.coord[:, 1], '.k', markersize=10)
        for n, i in enumerate(self.coord):
            self.ax1.text(i[0], i[1], str(n + 1), color='green')
        self.ax1.set_xlabel(r'$x$')
        self.ax1.set_ylabel(r'$y$')
        self.ax1.set_title(r'$Undeformated~Plot$')
        # ax1.legend(['Undeformed','Deformed'])
        self.ax1.axis('equal')
        for i in self.conn:
            self.ax1.plot([self.coord[i[0] - 1, 0], self.coord[i[1] - 1, 0]],
                          [self.coord[i[0] - 1, 1], self.coord[i[1] - 1, 1]], '-b')
        self.canvas1.draw()

    def callback_solve(self):
        shutil.rmtree('data', ignore_errors=True)
        os.mkdir('data')
        plt.savefig('data/undeformed.png',transparent=True)
        self.coord = np.array([[float(i[1].get()), float(i[2].get())] for i in self.frames])
        self.force = np.array([[float(i[3].get()), float(i[4].get())] for i in self.frames])
        self.support = [
            [1, 1] if frame[5].get() == 'Free' else
            [0, 0] if frame[5].get() == 'Pin' else
            [1, 0] if frame[5].get() == 'Roller' else
            None
            for frame in self.frames
        ]
        A = float(self.varA.get()) * np.ones([1, np.size(self.conn, 0)])
        E = float(self.varE.get())
        free = np.array([i for j in self.support for i in j])
        conn = np.array([[i[0], i[1]] for i in self.conn])
        force = np.array([i for j in self.force for i in j])
        try:
            U = solve_truss(*A, E, np.array(self.coord), conn, force, free)
        except:
            U=np.array([[0,0],[0,0]])
            CTkMessagebox(title="Error", message="Something went wrong!!!\nCheck DOFs", icon="cancel")

        plt.cla()
        self.ax1.plot(self.coord[:, 0], self.coord[:, 1], '.k', markersize=10)
        for n, i in enumerate(self.coord):
            self.ax1.text(i[0], i[1], str(n + 1), color='green')
        self.ax1.set_xlabel(r'$x$')
        self.ax1.set_ylabel(r'$y$')
        self.ax1.set_title(r'$Deformation~Plot$')
        # ax1.legend(['Undeformed','Deformed'])
        self.ax1.axis('equal')
        for i in self.conn:
            self.ax1.plot([self.coord[i[0] - 1, 0], self.coord[i[1] - 1, 0]],
                          [self.coord[i[0] - 1, 1], self.coord[i[1] - 1, 1]], '-b')
        for i in self.conn:
            self.ax1.plot([self.coord[i[0] - 1, 0] + U[i[0] - 1, 0], self.coord[i[1] - 1, 0] + U[i[1] - 1, 0]],
                          [self.coord[i[0] - 1, 1] + U[i[0] - 1, 1], self.coord[i[1] - 1, 1]] + U[i[1] - 1, 1], '--r')
        self.canvas1.draw()
        plt.savefig('data/deformed.png', transparent=True)
        with open('data/data.pickle', 'wb') as handle:
            pickle.dump(U, handle, protocol=pickle.HIGHEST_PROTOCOL)

        self.summary = CTkScrollableFrame(self.tabview.tab('Summary'), width=300, height=500)
        self.summary.place(x=10, y=10)

        dt = ['Node', 'Ux', 'Uy']
        for j in range(3):
            txt = CTkEntry(self.summary, corner_radius=0, border_color='grey', justify=CENTER,width=100)
            txt.insert(END, dt[j])
            txt.grid(row=0, column=j)

        for i in range(1, np.size(U, 0) + 1):
            dt = [str(i), str(U[i - 1, 0]), str(U[i - 1, 1])]
            for j in range(3):
                txt = CTkEntry(self.summary, corner_radius=0, border_color='grey', justify=CENTER,width=100)
                txt.insert(END, dt[j])
                txt.grid(row=i, column=j)

    def genrepo(self):
        filenm=filedialog.asksaveasfile(filetypes=[('pdf','.pdf')])
        if filenm:
            generateReport(filenm.name)
        shutil.rmtree('data', ignore_errors=True)
