# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 17:07:51 2019

@author: Sean
"""

import sys
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFileDialog, QMainWindow
from mainForm import Ui_MainWindow
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np


class PyQtMainEntry(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.camera = cv2.VideoCapture(0)
        self.is_camera_opened = False
        
        # 定时器: 30ms捕获一帧
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._queryFrame)
        self._timer.setInterval(30)


    def btnOpenCamera_Clicked(self):
        self.is_camera_opened = not self.is_camera_opened    # 应该是为了实现取反，但是亲测不行，使用 not 关键字
        if self.is_camera_opened:
            self.btnOpenCamera.setText('关闭摄像头')
            self._timer.start()
        else:
            self.btnOpenCamera.setText('打开摄像头')
            self._timer.stop()
            
            self.setupUi(self)
    
    def btnCapture_Clicked(self):
        if not self.is_camera_opened:
            return
        
        self.captured = self.frame
#        print(self.captured.shape)
        rows, cols, channels = self.captured.shape
        bytesPerLine = channels * cols
        # Qt显示图片时，需要先转换成QImage类型
        QImg = QImage(self.captured.data, cols, rows, bytesPerLine, QImage.Format_RGB888)
        self.label_2.setPixmap(QPixmap.fromImage(QImg).scaled(
                self.label_2.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
    
    def btnReadImage_Clicked(self):
        #打开文件选取对话框, 注意：只能加载纯英文路径图片
        filename, _ = QFileDialog.getOpenFileName(self, '打开图片')
        if filename:
            self.captured = cv2.imread(str(filename))
            # BGR --> RGB
            self.captured = cv2.cvtColor(self.captured, cv2.COLOR_BGR2RGB)
            rows, cols, channels = self.captured.shape
            bytesPerLine = channels*cols
            QImg = QImage(self.captured.data, cols, rows, bytesPerLine, QImage.Format_RGB888)
            self.label_2.setPixmap(QPixmap.fromImage(QImg).scaled(
                self.label_2.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
    
    def btnGray_Clicked(self):
        # 如果没有捕获图片，则不执行操作
        if not hasattr(self, "captured"):
            return
        self.gray = cv2.cvtColor(self.captured, cv2.COLOR_RGB2GRAY)
        rows, columns = self.gray.shape
        bytesPerLine = columns
        # 灰度图是单通道，所以需要用Format_Indexed8
        QImg = QImage(self.gray.data, columns, rows, bytesPerLine, QImage.Format_Indexed8)
        self.label_3.setPixmap(QPixmap.fromImage(QImg).scaled(
            self.label_3.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
    
    def btnThreshold_Clicked(self):
        '''
        Otsu自动阈值分割
        '''
        if not hasattr(self, "captured"):
            return
        self.gray = cv2.cvtColor(self.captured, cv2.COLOR_BGR2GRAY)
        _, self.threshold = cv2.threshold(self.gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        rows, columns = self.threshold.shape
        bytesPerLine = columns
        # 阈值分割图也是单通道，也需要用Format_Indexed8
        QImg = QImage(self.threshold.data, columns, rows, bytesPerLine, QImage.Format_Indexed8)
        self.label_3.setPixmap(QPixmap.fromImage(QImg).scaled(
            self.label_3.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
    
    @QtCore.pyqtSlot()
    def _queryFrame(self):
        # 循环捕获图片
        ret, self.frame = self.camera.read()
        img_rows, img_cols, channels = self.frame.shape
        bytesPerLine = channels*img_cols
        
        cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB, self.frame)
        QImg = QImage(self.frame.data, img_cols, img_rows, bytesPerLine, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(QImg).scaled(
            self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = PyQtMainEntry()
    window.show()
    sys.exit(app.exec_())
    window.camera.release()