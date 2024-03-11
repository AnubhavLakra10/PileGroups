import pyfiles
import sys
import numpy as np

#import unreal_stylesheetpip
import qdarkstyle

import pyqtgraph as pg

from PySide6.QtWidgets import QDialog,QApplication,QVBoxLayout,QGroupBox,QLabel,QLineEdit,QPushButton,QHBoxLayout,QGridLayout,QListWidget,QTableWidget,QHeaderView,QProgressBar,QTableWidgetItem,QCheckBox
from PySide6.QtCore import Qt, QThreadPool, Signal, Slot, QObject

pg_data = pyfiles.PileOptModel()


class Signals(QObject):
    completed = Signal()
    progress = Signal()
    stop = Signal()
    check = Signal()


class MainWindow(QDialog):

    def __init__(self):
        super().__init__()
 
        self.drawUI()
        self.write_input()   


    def write_input(self):
        self.nPiles.setText("8")
        self.nVertPiles.setText("0")
        self.incl.setText("4")
        self.sdirPiles.setText("3")
        self.plen.setText("7")

        self.nMax.setText("0")
        self.nMin.setText("-2400")
        self.nFilter.setChecked(True)

        self.col_up.setText("2")
        self.col_down.setText("2")
        self.coli_box.setChecked(True)

        self.h_slab.setText("9")
        self.w_slab.setText("6")

        self.path.setText("C:\\Utvecklingsprojekt\\PileGroups\\Underlag\Loadcases.xlsx")

        xvec        = [0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 2.5, 2.5, 2.5, "", "", "", "", "", "", "", "", "", "", ""]
        yvec        = [2, 3, 4, 2, 3, 4, 2, 3, 4, "", "", "", "", "", "", "", "", "", "", ""]


        self.nPiles.setText("6")
        self.nVertPiles.setText("0")
        self.incl.setText("4")
        self.sdirPiles.setText("2")
        self.plen.setText("7")

        self.nMax.setText("25")
        self.nMin.setText("-1000")
        self.nFilter.setChecked(True)

        self.col_up.setText("2")
        self.col_down.setText("4")
        self.coli_box.setChecked(True)

        self.h_slab.setText("10")
        self.w_slab.setText("4")

        self.path.setText("C:\\Utvecklingsprojekt\\PileGroups\\Underlag\Loadcases4.xlsx")

        xvec        = [1.6, 1.6, 1.6, 1.6, 1.6, 0.8, 0.8, 0.8, 0.8, 0.8, "", "", "", "", "", "", "", "", "", ""]
        yvec        = [4.6, 3.8, 3.0, 2.2, 1.4, 4.6, 3.8, 3.0, 2.2, 1.4, "", "", "", "", "", "", "", "", "", ""]


        for i in range(len(xvec)):
            xval = QTableWidgetItem(str(xvec[i])); xval.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            yval = QTableWidgetItem(str(yvec[i])); yval.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.input_table.setItem(i,0,xval)
            self.input_table.setItem(i,1,yval)

    def read_input(self):

        npiles      = int(self.nPiles.text())
        nvert       = int(self.nVertPiles.text())
        singdir     = int(self.sdirPiles.text())
        plen        = int(self.plen.text())
        incl        = int(self.incl.text())

        n_filter = self.nFilter.isChecked()

        if n_filter == True:
            Nmax        = int(self.nMax.text())
            Nmin        = int(self.nMin.text())
        else:
            Nmax        = 99999999999999999
            Nmin        = -99999999999999999

        coli_check = self.coli_box.isChecked()
        if coli_check == True:
            col_up      = int(self.col_up.text())
            col_down    = int(self.col_down.text())
            self.colision = np.arange(-col_up,col_down+1,1)
        else:
            self.colision = [0]


        path        = str(self.path.text())

        self.slab_h = float(self.h_slab.text())
        self.slab_w = float(self.w_slab.text())

        self.xvec        = []
        self.yvec        = []
        
        for i in range(20):
            try:
                xval = float(self.input_table.item(i,0).text())
                yval = float(self.input_table.item(i,1).text())
                self.xvec.append(xval)
                self.yvec.append(yval)
            except:
                pass

        pyfiles.PileOptModel.defineSettings(pg_data,self.xvec,self.yvec,npiles,nvert,singdir,plen,incl,path,Nmax,Nmin)

    def run_config(self):
        self.read_input()

        self.worker = self.worker_config
        self.signal = Signals()
        self.threadpool = QThreadPool()
        self.threadpool.start(self.worker)

        self.progress_val = 0
        self.progress_bar.setValue(0)
        self.signal.completed.connect(self.show_config)
        self.signal.progress.connect(self.update_progress_bar)

    @Slot()
    def worker_config(self):
        pyfiles.PileOptModel.genPileConfigs(pg_data,self.colision,self.signal)
        self.signal.completed.emit()


    def show_config(self):
        self.progress_bar.setValue(100)
        self.pos_conf.setText(str(pg_data.totConfigs))
        self.tot_conf.setText(str(pg_data.nrConfigs))
        self.fil_conf.setText("-")

    def update_progress_bar(self):
        self.progress_val = self.progress_val + 1 
        self.progress_bar.setValue(self.progress_val)


    def run_infl(self):
        self.configList.clear()
        self.read_input()
        self.inflNmax = []
        self.inflNmin = []
        lcnr = pyfiles.PileOptModel.readLoadCases(pg_data)
        self.nr_lcs.setText(str(lcnr))

        self.worker     = self.worker_infl
        self.signal     = Signals()
        self.threadpool = QThreadPool()
        self.threadpool.start(self.worker)

        self.progress_val = 0
        self.progress_bar.setValue(0)
        self.signal.completed.connect(self.show_infl)
        self.signal.progress.connect(self.update_progress_bar)
        self.signal.check.connect(self.update_list)

    def show_infl(self):
        self.fil_conf.setText(str(len(pg_data.configStore)))
        self.update_list()
        self.progress_bar.setValue(100)

    @Slot()
    def worker_infl(self):
        pyfiles.PileOptModel.pileInfluenceRun(pg_data,self.signal)
        self.signal.completed.emit()

    def stop_worker(self):
        pg_data.running = False
        self.progress_bar.setValue(0)

    def run_single(self):
        self.read_input()
        self.case_singlerun = int(self.singleCase.text())

        pyfiles.PileOptModel.pileSolver(pg_data,self.case_singlerun)
        pyfiles.PileOptModel.returnPileGroup(pg_data,self.case_singlerun)

        self.singleNmax.setText(str(pg_data.nmax_single))
        self.singleNmin.setText(str(pg_data.nmin_single))

        self.reactionList.clear()

        for i in range(pg_data.npiles):
            self.reactionList.addItems(["Pile " + str(i) + ":  " + str(round(pg_data.nmax_single_pile[i])) + " | " + str(round(pg_data.nmin_single_pile[i]))])

    def update_plot(self):
        rowValue = self.configList.currentItem().text().replace('Config ','')
        bpoint = rowValue.index(":")
        nr = int(rowValue[:bpoint])
        self.singleCase.setText(str(nr))
        print("Plotting Config: " + str(nr))
        self.plot_config(nr)

    def update_list(self):
        self.configList.clear()

        self.inflNmax.append(pg_data.Nmaxstore)
        self.inflNmin.append(pg_data.Nminstore)

        for i in range(len(pg_data.configStore)):
            self.configList.addItems(["Config " + str(pg_data.configStore[i]) + ":  " + str(pg_data.Nmaxstore[i]) + " | " + str(pg_data.Nminstore[i])])
            

        self.caseNmax.setText(str(np.max(self.inflNmax)))
        self.caseNmin.setText(str(np.max(self.inflNmin)))


    def reaction_plot_max(self):
        self.plot_config(self.case_singlerun)
        
        for i in range(pg_data.npiles):
            colorTag = 'g'
            if pg_data.nmax_single_pile[i] > 0:
                colorTag = 'r'
            text = pg.TextItem(str(round(pg_data.nmax_single_pile[i])), color=colorTag,anchor=(0,0))
            text.setPos(pg_data.x1vec[i],pg_data.y1vec[i])
            self.view_area.addItem(text)
    
    def reaction_plot_min(self):
        self.plot_config(self.case_singlerun)
        
        for i in range(pg_data.npiles):
            colorTag = 'g'
            if pg_data.nmin_single_pile[i] > 0:
                colorTag = 'r'
            text = pg.TextItem(str(round(pg_data.nmin_single_pile[i])), color=colorTag,anchor=(0,0))
            text.setPos(pg_data.x1vec[i],pg_data.y1vec[i])
            self.view_area.addItem(text)


    def plot_config(self,nr):
        pyfiles.PileOptModel.pileExpand(pg_data,nr) 
        self.view_area.plotItem.clear()

        valrange=max(np.max(pg_data.x1vec),np.max(pg_data.y1vec),self.slab_h*0.5,self.slab_w*0.5)
        self.view_area.setXRange(-valrange,valrange, padding=0.05)
        self.view_area.setYRange(-valrange,valrange, padding=0.05)
        self.view_area.setBackground(None)

        plt = self.view_area.plotItem.plot(pg_data.x1vec,pg_data.y1vec,pen=None,symbol='o',symbolPen = self.plotpen, color=self.plotpen, symbolBrush=None)
    
        h = self.slab_h*0.5; y_draft = [h,h,-h,-h,h]
        w = self.slab_w*0.5; x_draft = [w,-w,-w,w,w]

        plt = self.view_area.plotItem.plot(x_draft,y_draft,pen=self.plotpen,symbol=None, color=self.plotpen)

        fak = 0.3

        for i in range(len(pg_data.x1vec)):

            if pg_data.incl[i] == 0:
                x2 = pg_data.x1vec[i]
                y2 = pg_data.y1vec[i]
            else:
                x2 = pg_data.x1vec[i] + np.cos(np.radians(pg_data.bearing[i]))*fak
                y2 = pg_data.y1vec[i] + np.sin(np.radians(pg_data.bearing[i]))*fak

            plt.setSymbolSize(15)
            plt = self.view_area.plotItem.plot([pg_data.x1vec[i],x2],[pg_data.y1vec[i],y2],pen=self.plotpen, color=self.plotpen)

            paxis_y = [-(self.slab_h*0.5+0.5), (self.slab_h*0.5+0.5)]
            paxis_x = [-(self.slab_w*0.5+0.5), (self.slab_w*0.5+0.5)]

            plt = self.view_area.plotItem.plot([paxis_x[0],paxis_x[1]],[0,0], pen='gray', color='gray')
            plt = self.view_area.plotItem.plot([0,0],[paxis_y[0],paxis_y[1]], pen='gray', color='gray')
        
    def draft_config(self):
        self.read_input()
        self.view_area.plotItem.clear()

        valrange=max(np.max(self.xvec),np.max(self.yvec))
        self.view_area.setXRange(-valrange,valrange, padding=0.1)
        self.view_area.setYRange(-valrange,valrange, padding=0.1)
        self.view_area.setBackground(None)

        h = self.slab_h*0.5; y_draft = [h,h,-h,-h,h]
        w = self.slab_w*0.5; x_draft = [w,-w,-w,w,w]

        plt = self.view_area.plotItem.plot(x_draft,y_draft,pen=self.plotpen,symbol=None, color=self.plotpen)

        plt = self.view_area.plotItem.plot(self.xvec,self.yvec,pen=None,symbol="x", symbolPen=self.plotpen, color=self.plotpen, symbolBrush=self.plotpen)

        paxis_y = [-(self.slab_h*0.5+0.5), (self.slab_h*0.5+0.5)]
        paxis_x = [-(self.slab_w*0.5+0.5), (self.slab_w*0.5+0.5)]

        plt = self.view_area.plotItem.plot([paxis_x[0],paxis_x[1]],[0,0], pen='gray', color='gray')
        plt = self.view_area.plotItem.plot([0,0],[paxis_y[0],paxis_y[1]], pen='gray', color='gray')

    def swich_color_mode(self):

        self.dark_mode = not self.dark_mode

        app = QApplication.instance()
        if self.dark_mode == True:
            app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
            self.plotpen = 'white'
        else:
            app.setStyleSheet(qdarktheme.load_stylesheet("light"))
            self.plotpen = 'black'
        
        self.view_area.plotItem.clear()
        self.view_area.setBackground(None)

    def resetRun(self):

        self.view_area.plotItem.clear()
        self.configList.clear()
        self.reactionList.clear()
        self.read_input()

    def create_input_area(self):
        self.input_area     = QGroupBox()

        line_label          = QLabel("Sökväg")
        self.path           = QLineEdit()
        configButton        = QPushButton(" Configure analysis ")       ; configButton.clicked.connect(self.run_config)
        runButton           = QPushButton(" Influence Run ")            ; runButton.clicked.connect(self.run_infl)
        singleButton        = QPushButton(" Single Run ")               ; singleButton.clicked.connect(self.run_single)
        resetButton         = QPushButton(" Reset ")                    ; resetButton.clicked.connect(self.resetRun)
        stopButton          = QPushButton(" Stop ")                     ; stopButton.clicked.connect(self.stop_worker)
        colorButton         = QPushButton(" Colormode ")                ; colorButton.clicked.connect(self.swich_color_mode)

        layout              = QHBoxLayout()

        layout.addWidget(line_label)
        layout.addWidget(self.path,1)
        layout.addWidget(configButton)
        layout.addWidget(runButton)
        layout.addWidget(singleButton)
        layout.addWidget(resetButton)
        layout.addWidget(stopButton)
        layout.addWidget(colorButton)

        configButton.setMinimumHeight(25); configButton.setMinimumWidth(120)
        runButton.setMinimumHeight(25); runButton.setMinimumWidth(120)
        resetButton.setMinimumHeight(25); resetButton.setMinimumWidth(70)
        stopButton.setMinimumHeight(25); stopButton.setMinimumWidth(70)

        self.input_area.setLayout(layout)

    def create_settings_area(self):
        self.settings_area = QGroupBox()

        layout = QGridLayout()

        layout.addWidget(QLabel("Number of piles"),0,0);            self.nPiles = QLineEdit();      layout.addWidget(self.nPiles,0,1)
        layout.addWidget(QLabel("Vertical Piles"),1,0);             self.nVertPiles = QLineEdit();  layout.addWidget(self.nVertPiles,1,1)
        layout.addWidget(QLabel("Pile inclination"),2,0);           self.incl = QLineEdit();        layout.addWidget(self.incl,2,1)

        layout.addWidget(QLabel("Single dir piles"),0,2);           self.sdirPiles = QLineEdit();   layout.addWidget(self.sdirPiles,0,3)
        layout.addWidget(QLabel("Pile lenght"),1,2);                self.plen = QLineEdit();        layout.addWidget(self.plen,1,3)

        layout.addWidget(QLabel("Max pile reaction"),0,4);          self.nMax = QLineEdit();        layout.addWidget(self.nMax,0,5)
        layout.addWidget(QLabel("Min pile reaction"),1,4);          self.nMin = QLineEdit();        layout.addWidget(self.nMin,1,5)
        layout.addWidget(QLabel("Apply reaction filter"),2,4);      self.nFilter = QCheckBox();     layout.addWidget(self.nFilter,2,5)

        layout.addWidget(QLabel("Collision check up"),0,6);         self.col_up = QLineEdit();      layout.addWidget(self.col_up,0,7)
        layout.addWidget(QLabel("Collision check down"),1,6);       self.col_down = QLineEdit();    layout.addWidget(self.col_down,1,7)
        layout.addWidget(QLabel("Apply colision check"),2,6);       self.coli_box = QCheckBox();    layout.addWidget(self.coli_box,2,7)

        layout.addWidget(QLabel("Total Configs"),0,8);              self.tot_conf = QLineEdit("-"); layout.addWidget(self.tot_conf,0,9)
        layout.addWidget(QLabel("Possible configs"),1,8);           self.pos_conf = QLineEdit("-"); layout.addWidget(self.pos_conf,1,9)
        layout.addWidget(QLabel("Filtered configs"),2,8);           self.fil_conf = QLineEdit("-"); layout.addWidget(self.fil_conf,2,9)

        layout.addWidget(QLabel("Loadcases"),0,10);                 self.nr_lcs = QLineEdit("-");   layout.addWidget(self.nr_lcs,0,11)
        layout.addWidget(QLabel("Height"),1,10);                    self.h_slab = QLineEdit("-");   layout.addWidget(self.h_slab,1,11)
        layout.addWidget(QLabel("Width"),2,10);                     self.w_slab = QLineEdit("-");   layout.addWidget(self.w_slab,2,11)

        self.pos_conf.setMinimumWidth(60)
        self.nMax.setMinimumWidth(60)

        self.pos_conf.setReadOnly(True)
        self.tot_conf.setReadOnly(True)
        self.fil_conf.setReadOnly(True)
        self.nr_lcs.setReadOnly(True)

        self.settings_area.setLayout(layout)


    def create_result_area(self):
        self.result_area = QGroupBox()

        self.view_area = pg.PlotWidget()
        self.view_area.setBackground(None)

        self.configList = QListWidget()
        self.configList.setFixedWidth(150)
        self.configList.clicked.connect(self.update_plot)

        self.reactionList = QListWidget()
        self.reactionList.setFixedWidth(150)
        #self.reactionList.clicked.connect(self.update_plot)

        self.input_table = QTableWidget()
        self.input_table.setFixedWidth(150)
        self.input_table.setFixedWidth(150)


        self.input_table.setRowCount(20)
        self.input_table.setColumnCount(2)


        self.input_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        self.input_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)

        for i in range(20):
            self.input_table.verticalHeader().setSectionResizeMode(i,QHeaderView.Stretch)

        self.draft_button = QPushButton(" Draft config ")
        self.draft_button.clicked.connect(self.draft_config)

        self.aux_button = QPushButton(" Aux button ")

        self.plot_max = QPushButton(" Plot max ")
        self.plot_max.clicked.connect(self.reaction_plot_max)
    
        self.plot_min = QPushButton(" Plot min ")
        self.plot_min.clicked.connect(self.reaction_plot_min)

        self.nconfigmax = QLabel('0')
        self.nconfigmin = QLabel('0')

        layout = QHBoxLayout()
        
        layout.addWidget(self.view_area,1)
        layout.setSpacing(20)

        subarea = QGroupBox('Configurations')
        sublayout = QVBoxLayout()


        textLayout = QGridLayout()
        textarea   = QGroupBox()

        textLayout.addWidget(QLabel("Max"),0,0); self.caseNmax = QLabel("0"); textLayout.addWidget(self.caseNmax,0,1); textLayout.addWidget(QLabel("kN"),0,2)
        textLayout.addWidget(QLabel("Min"),1,0); self.caseNmin = QLabel("0"); textLayout.addWidget(self.caseNmin,1,1); textLayout.addWidget(QLabel("kN"),1,2)
        textarea.setLayout(textLayout)

        sublayout.addWidget(textarea)
        sublayout.addWidget(self.configList)
        sublayout.addWidget(self.aux_button)

        subarea.setLayout(sublayout)

        layout.addWidget(subarea)

        subarea = QGroupBox('Single pile reactions')
        sublayout = QVBoxLayout()
        textLayout = QGridLayout()
        textarea   = QGroupBox()

        textLayout.addWidget(QLabel("Case"),0,0); self.singleCase = QLabel("0"); textLayout.addWidget(self.singleCase,0,1)
        textLayout.addWidget(QLabel("Max"),1,0);  self.singleNmax = QLabel("0"); textLayout.addWidget(self.singleNmax,1,1); textLayout.addWidget(QLabel("kN"),1,2)
        textLayout.addWidget(QLabel("Min"),2,0);  self.singleNmin = QLabel("0"); textLayout.addWidget(self.singleNmin,2,1); textLayout.addWidget(QLabel("kN"),2,2)

        textarea.setLayout(textLayout)

        sublayout.addWidget(textarea)
        sublayout.addWidget(self.reactionList)
        sublayout.addWidget(self.plot_max)
        sublayout.addWidget(self.plot_min)
        subarea.setLayout(sublayout)
        layout.addWidget(subarea)

        subarea = QGroupBox('Possible pile placements')
        sublayout = QVBoxLayout()
        sublayout.addWidget(self.input_table)
        sublayout.addWidget(self.draft_button)
        subarea.setLayout(sublayout)
        layout.addWidget(subarea)

        self.result_area.setLayout(layout)

    def create_progress_area(self):

        self.progress_area      = QGroupBox("")
        layout                  = QHBoxLayout()
        self.progress_bar       = QProgressBar()

        layout.addWidget(self.progress_bar)
        self.progress_area.setLayout(layout)

    def drawUI(self):
        self.dark_mode = True
        self.plotpen = 'white'
        self.create_input_area()
        self.create_settings_area()
        self.create_result_area()
        self.create_progress_area()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.input_area)
        main_layout.addWidget(self.settings_area)
        main_layout.addWidget(self.result_area,1)
        main_layout.addWidget(self.progress_area)

        mainWindow = QDialog()
        self.setLayout(main_layout)
        self.setWindowTitle("Pile Optimization")
        self.resize(700,880)


if __name__ == '__main__':
    print("PL")
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6', theme='dark'))


    window = MainWindow()
    sys.exit(window.exec())


# nuitka --standalone --plugin-enable=pyside6 Main.py  
# pyinstaller --onefile Main.py