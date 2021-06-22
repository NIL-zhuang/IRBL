import os
import sys
import datetime

from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import (QPushButton, QLineEdit, QTextEdit, QWidget, QHBoxLayout, QVBoxLayout, QApplication)
from PyQt5 import QtCore, QtGui, QtWidgets

import init
import runall
import tryGUI


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1128, 744)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.BHG = QtWidgets.QPushButton(self.centralwidget)
        self.BHG.setGeometry(QtCore.QRect(230, 350, 151, 71))
        self.BHG.setObjectName("BHG")
        self.terminal = QtWidgets.QTextEdit(self.centralwidget)
        self.terminal.setGeometry(QtCore.QRect(430, 100, 681, 561))
        self.terminal.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.terminal.setObjectName("terminal")
        self.Preprocess = QtWidgets.QPushButton(self.centralwidget)
        self.Preprocess.setGeometry(QtCore.QRect(70, 270, 311, 61))
        self.Preprocess.setObjectName("Preprocess")
        self.Quit = QtWidgets.QPushButton(self.centralwidget)
        self.Quit.setGeometry(QtCore.QRect(70, 540, 311, 61))
        self.Quit.setObjectName("Quit")
        self.Calculate = QtWidgets.QPushButton(self.centralwidget)
        self.Calculate.setGeometry(QtCore.QRect(280, 440, 101, 61))
        self.Calculate.setObjectName("Calculate")
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(460, 20, 251, 51))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setObjectName("title")
        self.copyright = QtWidgets.QLabel(self.centralwidget)
        self.copyright.setGeometry(QtCore.QRect(20, 690, 191, 16))
        self.copyright.setObjectName("copyright")
        self.date = QtWidgets.QTextEdit(self.centralwidget)
        self.date.setGeometry(QtCore.QRect(1003, 680, 111, 31))
        self.date.setReadOnly(True)
        self.date.setObjectName("date")
        self.date.insertPlainText(datetime.datetime.now().strftime('%Y-%m-%d'))
        self.aerfa = QtWidgets.QLabel(self.centralwidget)
        self.aerfa.setGeometry(QtCore.QRect(80, 360, 31, 21))
        self.aerfa.setObjectName("aerfa")
        self.samplerate_4 = QtWidgets.QLabel(self.centralwidget)
        self.samplerate_4.setGeometry(QtCore.QRect(70, 460, 91, 21))
        self.samplerate_4.setObjectName("samplerate_4")
        self.beta = QtWidgets.QLabel(self.centralwidget)
        self.beta.setGeometry(QtCore.QRect(80, 400, 31, 21))
        self.beta.setObjectName("beta")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(1040, 80, 71, 16))
        self.label_6.setObjectName("label_6")
        self.chooseData = QtWidgets.QPushButton(self.centralwidget)
        self.chooseData.setGeometry(QtCore.QRect(80, 190, 121, 51))
        self.chooseData.setCheckable(False)
        self.chooseData.setObjectName("chooseData")
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(70, 250, 311, 16))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setGeometry(QtCore.QRect(70, 510, 311, 16))
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.samplerate = QtWidgets.QSpinBox(self.centralwidget)
        self.samplerate.setGeometry(QtCore.QRect(190, 460, 31, 22))
        self.samplerate.setObjectName("samplerate")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(230, 460, 21, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.samplerate_2 = QtWidgets.QSpinBox(self.centralwidget)
        self.samplerate_2.setGeometry(QtCore.QRect(130, 360, 31, 22))
        self.samplerate_2.setObjectName("samplerate_2")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(170, 360, 21, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.samplerate_3 = QtWidgets.QSpinBox(self.centralwidget)
        self.samplerate_3.setGeometry(QtCore.QRect(130, 400, 31, 22))
        self.samplerate_3.setObjectName("samplerate_3")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(170, 400, 21, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(230, 190, 151, 51))
        self.textEdit.setObjectName("textEdit")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(230, 170, 161, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(6)
        font.setUnderline(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.chooseData.clicked.connect(self.choose_data)
        self.Preprocess.clicked.connect(self.preprocess)
        self.BHG.clicked.connect(self.bhg)
        #self.Calculate.clicked.connect(self.evaluate())

        self.Quit.clicked.connect(MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.BHG.setText(_translate("MainWindow", "BHG"))
        self.terminal.setHtml(_translate("MainWindow",
                                         "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                         "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                         "p, li { white-space: pre-wrap; }\n"
                                         "</style></head><body style=\" font-family:\'SimSun\'; font-size:9.07563pt; font-weight:400; font-style:normal;\">\n"
                                         "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9.07563pt;\"><br /></p></body></html>"))
        self.Preprocess.setText(_translate("MainWindow", "Preprocess"))
        self.Quit.setText(_translate("MainWindow", "Quit"))
        self.Calculate.setText(_translate("MainWindow", "Calculate"))
        self.title.setText(_translate("MainWindow", "IRBL  System"))
        self.copyright.setText(_translate("MainWindow", "copyright@2021 -khyyyds"))
        self.aerfa.setText(_translate("MainWindow", "α"))
        self.samplerate_4.setText(_translate("MainWindow", "sample rate"))
        self.beta.setText(_translate("MainWindow", "β"))
        self.label_6.setText(_translate("MainWindow", "<Window>"))
        self.chooseData.setText(_translate("MainWindow", "选择数据集"))
        self.label_8.setText(_translate("MainWindow", "%"))
        self.label_9.setText(_translate("MainWindow", "%"))
        self.label_10.setText(_translate("MainWindow", "%"))
        self.label.setText(_translate("MainWindow", "当前有swt、aspectj、eclipse可选"))

    def choose_data(self):
        self.terminal.moveCursor(QTextCursor.End)
        self.terminal.insertPlainText('Choose data...\n')
        proj = self.textEdit.text()
        init.set_proj(proj)
        self.terminal.insertPlainText(proj + ' is chosen as the project file.\n\n')

    def preprocess(self):
        self.terminal.moveCursor(QTextCursor.End)
        self.terminal.insertPlainText('Preprocessing...\n')
        runall.preprocessAll()
        self.terminal.insertPlainText('Finished preprocessing. Now you have the data to make BHG!\n\n')

    def bhg(self):
        alphaCal = int(self.samplerate_2.text()) / 100
        betaCal = int(self.samplerate_3.text()) / 100
        self.terminal.moveCursor(QTextCursor.End)
        self.terminal.insertPlainText('Making the matrix...\n')
        runall.bbSim()
        self.terminal.insertPlainText('Finished bbSim\n')
        runall.bsSim()
        self.terminal.insertPlainText('Finished bsSim\n')
        runall.ssSim()
        self.terminal.insertPlainText('Finished ssSim\n')
        self.terminal.insertPlainText('Computing the BHG matrix with alpha ' +
                                      str(alphaCal) + ' and beta ' + str(betaCal)+'\n')
        runall.edgeCombination(alphaCal, betaCal)
        self.terminal.insertPlainText('Work out! Use the BHG to get your result!\n\n')

    def evaluate(self):
        self.terminal.moveCursor(QTextCursor.End)
        self.terminal.insertPlainText('Calculating the result...\n')
        self.terminal.insertPlainText('This will be a long time, please don\'t close the system.\n')
        runall.fullEvaluate(100)
        self.terminal.insertPlainText('Finished the evaluate.\n\n')
'''
    def putout(self):
        self.terminal.moveCursor(QTextCursor.End)
        self.terminal.insertPlainText('test putout\n')
        tryGUI.easyTry()
'''



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(w)
    w.show()
    sys.exit(app.exec_())
