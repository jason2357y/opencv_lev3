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
        self.btn6 = QPushButton('이름 태그', self)
        self.btn6.clicked.connect(self.createTagNameWindow)

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
        fname = QFileDialog.getOpenFileName(self, 'open file', './images')
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

    def createTagNameWindow(self):
        self.tagnamewin = TagNameWindow()
        self.tagnamewin.setWidgets(self)
        self.tagnamewin.show()


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

            img_edited.save('./images/img_edited.png', 'PNG')
            mainwindow.imagepath = './images/img_edited.png'
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

        # label obj(main)
        self.mlabel = SquareLabel(mainwindow.label.pixmap(), mainwindow.imgwidth, mainwindow.imgheight, mainwindow.flist)

        # buttons
        self.btnAddFace = QPushButton('얼굴 추가', self)
        self.btnAddFace.clicked.connect(lambda: self.mlabel.addFace())
        self.btnOK = QPushButton('확인', self)
        self.btnOK.clicked.connect(lambda: self.finishFace(mainwindow))

        # layout(buttons)
        vbox = QVBoxLayout()
        vbox.addWidget(self.btnAddFace)
        vbox.addWidget(self.btnOK)
        vbox.setContentsMargins(0, 0, 0, 0)

        # set layout
        btns_widget = QWidget()
        btns_widget.setLayout(vbox)
        vbox.setContentsMargins(0, 0, 0, 0)

        # set main window layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.mlabel)
        hbox.addWidget(btns_widget)
        hbox.setContentsMargins(0,0,0,0)
        self.setLayout(hbox)

    # close window
    def finishFace(self, mainwindow):
        mainwindow.label.setPixmap(self.mlabel.pixmap_resized)
        self.close()


# label
class SquareLabel(QLabel):
    # initialize
    def __init__(self, pixmap, w, h, faceList):
        super().__init__()
        self.pixmap = pixmap
        self.pixmap_resized = self.pixmap.scaled(w, h)
        self.setPixmap(self.pixmap_resized)
        self.left_clicking = False
        self.faceList = faceList

        painter = QPainter(self.pixmap_resized)
        painter.setPen(QPen(QColor(200, 200, 200), 3))
        for f in faceList.face_list:
            print(f.x, f.y, f.w, f.h)
            painter.drawEllipse(f.x, f.y, f.w, f.h)

        self.setPixmap(self.pixmap_resized)

    def mousePressEvent(self, event):
        # print('mousePressEvent', event.x(), event.y(), event.button())
        if event.button() == 1:
            self.startX = event.x()
            self.startY = event.y()
            self.left_clicking = True

    def mouseReleaseEvent(self, event):
        # print('mouseReleaseEvent', event.x(), event.y(), event.button())
        if event.button() == 1:
            self.finishX = event.x()
            self.finishY = event.y()

    def mouseMoveEvent(self, event):
        # print('mouseMoveEvent', event.x(), event.y())
        if self.left_clicking:
            self.pixmap_temp = self.pixmap_resized.copy()

            painter = QPainter(self.pixmap_temp)
            painter.setPen(QPen(QColor('green'), 3))
            r=int(((self.startX-event.x())**2+(self.startY-event.y())**2)**0.5)
            painter.drawEllipse(self.startX-r, self.startY-r, 2*r, 2*r)

            self.setPixmap(self.pixmap_temp)

    # draw face
    def addFace(self):
        print('addFace clicked')
        try:
            r = int(((self.startX - self.finishX) ** 2 + (self.startY - self.finishY) ** 2) ** 0.5)
            x, y, w, h = self.startX-r, self.startY-r, 2*r, 2*r
            self.faceList.append_face(x,y,w,h)
            painter =QPainter(self.pixmap_resized)
            painter.setPen(QPen(QColor(200, 200, 200), 3))
            painter.drawEllipse(x,y,w,h)

            self.setPixmap(self.pixmap_resized)
        except AttributeError:
            pass

# name tagging window
class TagNameWindow(MainWindow):
    # initialize
    def __init__(self):
        super().__init__()
    # create widget
    def setWidgets(self, mainwindow):
        self.setGeometry(self.left, self.top, 200, 300)
        self.mlabel = TaggingLabel(mainwindow.label.pixmap(), mainwindow.width, mainwindow.height, mainwindow.flist)

        self.btnSave = QPushButton('저장', self)
        self.btnSave.clicked.connect(lambda : self.mlabel.saveFile())
        self.btnOK = QPushButton('확인', self)
        self.btnOK.clicked.connect(lambda : self.finishTag(mainwindow))

        vbox = QVBoxLayout()
        vbox.addWidget(self.btnSave)
        vbox.addWidget(self.btnOK)

        buttons_widget = QWidget()
        buttons_widget.setLayout(vbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.mlabel)
        hbox.addWidget(buttons_widget)
        self.setLayout(hbox)
    # close window
    def finishTag(self, mainwindow):
        mainwindow.label.setPixmap(self.mlabel.pixmap_temp)
        self.close()

# label
class TaggingLabel(SquareLabel):
    def __init__(self, pixmap, w, h, faceList):
        super().__init__(pixmap, w, h, faceList)

    # input name
    def mousePressEvent(self, event):
        for f in self.faceList.face_list:
            if int((f.w**2+f.h**2)**0.5) >= int(((f.x-event.x())**2+(f.y-event.y())**2)**0.5):
                print('얼굴 아이디:', f.id, f.name)
                text, okPressed = QInputDialog.getText(self,'입력창', '이름', QLineEdit.Normal)
                if okPressed and text != '':
                    f.name = text
                self.drawNames()
                break

    def mouseReleaseEvent(self, event):
        pass
    def mouseMoveEvent(self, event):
        pass
    # draw
    def drawNames(self):
        self.pixmap_temp = self.pixmap_resized.copy()
        painter = QPainter(self.pixmap_temp)
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        for f in self.faceList.face_list:
            painter.drawText(f.x, f.y - 5, f.name)
        painter.end()
        self.setPixmap(self.pixmap_temp)
    # save
    def saveFile(self):
        text, okPressed = QInputDialog.getText(self, '파일이름입력창', '파일명', QLineEdit.Normal)
        if okPressed:
            self.pixmap_temp.save(text + '.jpg', 'JPG')

# activate
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    win.setWidgets()
    app.exec_()
