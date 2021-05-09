# import libs
import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# define class
class MainWindow(QWidget):
    
    # initialize
    def __init__(self):
        
        # class intialize
        super().__init__()

        # define title
        self.setWindowTitle('사진속 얼굴 태깅 어플리케이션')

        # position
        self.left = 500
        self.top = 200
        self.width = 400
        self.height = 500
        self.setGeometry(self.left, self.top, self.width, self.height)

        # make, connect buttons
        self.btn1 = QPushButton('사진 업로드', self)
        self.btn1.clicked.connect(self.getPhotoPath)
        self.btn2 = QPushButton('btn2', self)
        self.btn3 = QPushButton('btn3', self)
        self.btn4 = QPushButton('btn4', self)
        self.btn5 = QPushButton('btn5', self)
        self.btn6 = QPushButton('btn6', self)

        # button 1 to 3
        hbox1 = QHBoxLayout()
        for btn in [self.btn1, self.btn2, self.btn3]:
            hbox1.addWidget(btn)
        self.setLayout(hbox1)
        btns1 = QWidget()
        btns1.setLayout(hbox1)

        # button 4 to 6
        hbox2 = QHBoxLayout()
        for btn in [self.btn4, self.btn5, self.btn6]:
            hbox2.addWidget(btn)
        self.setLayout(hbox2)
        btns2 = QWidget()
        btns2.setLayout(hbox2)

        # whole buttons
        btnvbox = QVBoxLayout()
        btnvbox.addWidget(btns1)
        btnvbox.addWidget(btns2)
        self.setLayout(btnvbox)
        btns=QWidget()
        btns.setLayout(btnvbox)

        # label
        self.label = QLabel("이미지가 여기에 업로드됩니다", self)
        self.label.move(20, 20)

        # label and buttons
        vbox = QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addWidget(btns)
        self.setLayout(vbox)

    # show
    def loadImage(self):
        self.pixmap = QPixmap(self.imagepath)
        pixmap_resized = self.pixmap.scaled(400, 200)
        self.label.setPixmap(pixmap_resized)

    # select
    def getPhotoPath(self):
        fname = QFileDialog.getOpenFileName(self, 'open file', './img')
        self.imagepath = fname[0]
        self.loadImage()


# activate
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec_()
