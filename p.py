# import libs
import sys
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt5.QtWidgets import *
from PIL import Image
import cv2
import math


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
        self.imgwidth = 400
        self.imgheight = 500

        self.delclicked = False

    def setWidgets(self):
        # generate, connect buttons
        self.btn1 = QPushButton('사진 업로드', self)
        self.btn1.clicked.connect(self.getPhotoPath)
        self.btn2 = QPushButton('이미지 편집', self)
        self.btn2.clicked.connect(self.createEditingWindow)
        self.btn3 = QPushButton('얼굴 찾기', self)
        self.btn3.clicked.connect(self.findFace)
        self.btn4 = QPushButton('얼굴 삭제', self)
        self.btn4.clicked.connect(self.delFace)
        self.btn5 = QPushButton('얼굴 추가', self)
        self.btn5.clicked.connect(self.createAddFaceWindow)
        self.btn6 = QPushButton('btn6', self)

        # button 1 to 3
        hbox1 = QHBoxLayout()
        for btn in (self.btn1, self.btn2, self.btn3):
            hbox1.addWidget(btn)
        self.setLayout(hbox1)
        btns1 = QWidget()
        btns1.setLayout(hbox1)

        # button 4 to 6
        hbox2 = QHBoxLayout()
        for btn in (self.btn4, self.btn5, self.btn6):
            hbox2.addWidget(btn)
        self.setLayout(hbox2)
        btns2 = QWidget()
        btns2.setLayout(hbox2)

        # whole buttons
        btnvbox = QVBoxLayout()
        btnvbox.addWidget(btns1)
        btnvbox.addWidget(btns2)
        self.setLayout(btnvbox)
        btns = QWidget()
        btns.setLayout(btnvbox)

        # label
        self.label = QLabel("이미지가 여기에 업로드됩니다", self)
        self.label.move(20, 20)

        # label and buttons
        vbox = QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addWidget(btns)
        self.setLayout(vbox)
        vbox.setContentsMargins(0, 0, 0, 0)

    # show
    def loadImage(self):
        self.pixmap = QPixmap(self.imagepath)
        pixmap_resized = self.pixmap.scaled(self.imgwidth, self.imgheight)
        self.label.setPixmap(pixmap_resized)

    # select
    def getPhotoPath(self):
        fname = QFileDialog.getOpenFileName(self, 'open file', './img')
        self.originalpath = self.imagepath = fname[0]
        self.loadImage()

    # open edit window
    def createEditingWindow(self):
        self.editwin = EditWindow()
        self.editwin.setWidgets(self)
        self.editwin.show()

    # draw face
    def findFace(self):
        # find faces
        self.flist = FaceList()
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        img = cv2.imread(self.imagepath, cv2.IMREAD_COLOR)
        img = cv2.resize(img, (self.imgwidth, self.imgheight))
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(img_gray, 1.1, 4).tolist()

        # add to flist
        for x, y, w, h in faces:
            print(x, y, w, h)
            self.flist.append_face(x, y, h, w)
            cv2.circle(img, (x + w // 2, y + h // 2), (h + w) // 4, (200, 200, 200), 2)

        self.showImage(img)

    # show
    def showImage(self, img):
        height, width, color = img.shape
        bytesPerLine = 3 * width
        image = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.image = image.rgbSwapped()
        self.label.setPixmap(QPixmap.fromImage(self.image))

    # delete face at picture
    def delFace(self):
        if self.label.pixmap() is None:
            print('사진이 업로드 되지 않았습니다')
        elif self.flist is None or self.flist.count_face() == 0:
            print('탐색된 얼굴이 없습니다')
        else:
            print('어느 위치를 지우시겠습니까? 원하는 위치를 클릭해 주세요.')
            self.delclicked = True

    # when clicked
    def mousePressEvent(self, event):
        diag = math.inf
        
        # if enabled
        if self.delclicked is True:
            cnt = -1
            print('(%d, %d)' % (event.x(), event.y()))
            for i in self.flist.face_list:
                centx = i.x + (i.w / 2)
                centy = i.y + (i.h / 2)

                # is in cricle
                if diag > abs(math.sqrt(((centx - event.x()) ** 2) + ((centy - event.y()) ** 2))):  # closest
                    diag = abs(math.sqrt(((centx - event.x()) ** 2) + ((centy - event.y()) ** 2)))
                    faceid = i.id
                    cnt += 1

            t = self.flist.face_list[cnt]
            condition = diag <= (t.w + t.h) / 4  # distance <= radius

            # delete
            if condition:
                print('removing face id: %d' % faceid)
                self.flist.remove_face(faceid)
                img = cv2.imread(self.imagepath)
                img = cv2.resize(img, (self.imgwidth, self.imgheight))

                for f in self.flist.face_list:  # draw
                    print(f.x, f.y, f.w, f.h, f.name, f.id)
                    cv2.circle(img, (f.x + f.w // 2, f.y + f.h // 2), (f.w + f.h) // 4, (200, 200, 200), 2)

                self.showImage(img)
            self.delclicked = False
            
    # open faceadd window
    def createAddFaceWindow(self):
        self.addfacewin = AddFaceWindow()
        self.addfacewin.setWidgets(self)
        self.addfacewin.show()


# editing window
class EditWindow(QWidget):
    # initialize
    def __init__(self):
        super().__init__()
        self.setWindowTitle('사진속 얼굴 태깅 어플리케이션')

        # pos
        self.left = 500
        self.top = 200
        self.width = 400
        self.height = 500
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.imgwidth = 400
        self.imgheight = 300

    # generate widgets
    def setWidgets(self, mainwindow):

        # width, heighth
        self.label_width = QLabel('너비 바꾸기')
        self.text_width = QLineEdit('width', self)
        self.label_height = QLabel('높이 바꾸기')
        self.text_height = QLineEdit('height', self)

        # color
        self.label_color = QLabel('사진색 바꾸기')
        self.radiobtn1 = QRadioButton('원본')
        self.radiobtn2 = QRadioButton('회색 계열')
        self.radiobtn3 = QRadioButton('적색 계열')
        self.radiobtn4 = QRadioButton('황색 계열')
        self.radiobtn5 = QRadioButton('녹색 계열')
        self.radiobtn6 = QRadioButton('청색 계열')
        self.radiobtn1.setChecked(True)
        self.radiochecked = '원본'

        # connect radiobuttons
        self.radiobtn1.toggled.connect(self.btnstate)
        self.radiobtn2.toggled.connect(self.btnstate)
        self.radiobtn3.toggled.connect(self.btnstate)
        self.radiobtn4.toggled.connect(self.btnstate)
        self.radiobtn5.toggled.connect(self.btnstate)
        self.radiobtn6.toggled.connect(self.btnstate)

        # confirm
        self.btn_okay = QPushButton('확인', self)
        self.btn_okay.clicked.connect(lambda: self.editImage(mainwindow))

        # layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.label_width)
        vbox.addWidget(self.text_width)
        vbox.addWidget(self.label_height)
        vbox.addWidget(self.text_height)
        vbox.addWidget(self.label_color)
        vbox.addWidget(self.radiobtn1)
        vbox.addWidget(self.radiobtn2)
        vbox.addWidget(self.radiobtn3)
        vbox.addWidget(self.radiobtn4)
        vbox.addWidget(self.radiobtn5)
        vbox.addWidget(self.radiobtn6)
        vbox.addWidget(self.btn_okay)
        self.setLayout(vbox)

    # change image
    def editImage(self, mainwindow):
        try:
            imgwidth_edited = self.text_width.text()
            imgheight_edited = self.text_height.text()
            mainwindow.imgwidth = int(imgwidth_edited)
            mainwindow.imgheight = int(imgheight_edited)
            image = Image.open(mainwindow.originalpath)

            # change color
            if self.radiochecked == '회색 계열':
                img_edited = image.convert('L')

            if self.radiochecked == '적색 계열':
                red = (
                    1.00, 0.36, 0.18, 0,
                    0.11, 0.72, 0.07, 0,
                    0.02, 0.12, 0.95, 0)
                img_edited = image.convert('RGB', red)
            if self.radiochecked == '황색 계열':
                yellow = (
                    0.90, 0.36, 0.18, 0,
                    0.11, 0.72, 0.07, 0,
                    0.02, 0.12, 0.04, 0)
                img_edited = image.convert('RGB', yellow)
            if self.radiochecked == '녹색 계열':
                green = (
                    0.41, 0.36, 0.18, 0,
                    0.50, 0.72, 0.07, 0,
                    0.02, 0.12, 0.95, 0)
                img_edited = image.convert('RGB', green)
            if self.radiochecked == '청색 계열':
                blue = (
                    0.31, 0.36, 0.18, 0,
                    0.40, 0.72, 0.07, 0,
                    0.60, 0.12, 0.95, 0)
                img_edited = image.convert('RGB', blue)
            if self.radiochecked == '원본':
                img_edited = image

            img_edited.save('./img/img_edited.png', 'PNG')
            mainwindow.imagepath = './img/img_edited.png'
            mainwindow.loadImage()
            self.close()
        except ValueError:
            QMessageBox.question(self, '에러', '너비나 높이가 숫자가 아닙니다', QMessageBox.Ok)

    # return color in text
    def btnstate(self):
        radiobtn = self.sender()
        self.radiochecked = radiobtn.text()


# list of face
class FaceList:
    # initialize
    def __init__(self):
        self.face_list = []
        self.next_id = 0

    # add
    def append_face(self, x, y, h, w):
        self.face_list.append(Face(x, y, w, h, '', self.next_id))
        self.next_id += 1

    # count
    def count_face(self):
        len(self.face_list)

    # delete
    def remove_face(self, ind):
        cnt = 0
        for i in self.face_list:
            if i.id == ind:
                del self.face_list[cnt]
            cnt += 1


# face object
class Face:
    # set instance attribute
    def __init__(self, x, y, w, h, name, id):
        self.x, self.y, self.w, self.h, self.name, self.id = x, y, w, h, name, id

# add face
class AddFaceWindow(MainWindow):
    # initialize
    def __init__(self):
        super().__init__()
        
    # generate widgets
    def setWidgets(self, mainwindow):
        # pos
        self.setGeometry(self.left, self.top, 200, 300)

        #label obj(main)
        self.mlabel = SquareLabel(mainwindow.imagepath, mainwindow.imgwidth, mainwindow.imgheight)

        # buttons
        self.btnAddFace = QPushButton('얼굴 추가', self)
        self.btnOK = QPushButton('확인', self)

        # layout(buttons)
        vbox = QVBoxLayout()
        vbox.addWidget(self.btnAddFace)
        vbox.addWidget(self.btnOK)

        # set layout
        btns_widget = QWidget()
        btns_widget.setLayout(vbox)

        #set main window layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.mlabel)
        hbox.addWidget(btns_widget)
        self.setLayout(hbox)


# label
class SquareLabel(QLabel):
    #initialize
    def __init__(self, imgpath, w, h):
        super().__init__()
        self.pixmap = QPixmap(imgpath)
        self.pixmap_resized = self.pixmap.scaled(w,h)
        self.setPixmap(self.pixmap_resized)
        self.left_clicking=False
        
        painter=QPainter(self.pixmap_resized)
        painter.setPen(QPen(QColor('gray'), 2))
        for f in faceList.face_list:
            print(f.x, f.y, f.w, f.h)
            painter.drawEllipse(f.x, f.y, f.w, f.h)
        
        self.setPixmap(self.pixmap_resized)
        
        def mousePressEvent(self, event):
            print('mousePressEvent', event.x(), event.y(), event.button())
            
        def mouseReleaseEvent(self, event):
            print('mouseReleaseEvent', event.x(), event.y(), event.button())
            
        def mouseMoveEvent(self, event):
            print('mouseMoveEvent', event.x(), event.y())
            
        


# activate
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    win.setWidgets()
    app.exec_()
