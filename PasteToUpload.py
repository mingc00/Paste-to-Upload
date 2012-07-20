import sys
import urllib
import urllib2
import json
import re
from PySide.QtGui import QFont, QLabel, QLineEdit, QMainWindow, QApplication, QKeySequence
from PySide.QtCore import QBuffer, QByteArray, QIODevice, QThread, Qt

# Your Imgur API developer key
API_KEY = ''


class PasteToUpload(QMainWindow):

    def __init__(self):
        super(PasteToUpload, self).__init__()
        self.initUI()

    def initUI(self):
        self.resize(290, 150)
        self.setWindowTitle('PasteToUpload')
        font = QFont('Helvetica', 16)
        self.label = QLabel('Ctrl+V', self)
        self.edit = QLineEdit(self)
        self.label.setFont(font)
        self.label.move(45, 25)
        self.edit.move(45, 85)
        self.label.setFixedWidth(250)
        self.edit.setFixedWidth(200)
        self.edit.setReadOnly(True)
        self.edit.setFocusPolicy(Qt.NoFocus)
        self.show()

    def __sendPost(self, base64):
        value = {
            'key': API_KEY,
            'image': base64
        }
        data = urllib.urlencode(value)
        f = urllib2.urlopen(
            url='http://api.imgur.com/2/upload.json',
            data=data
        )
        return json.load(f)

    def keyPressEvent(self, e):
        if e.matches(QKeySequence.Paste):
            clipboard = QApplication.clipboard()
            mimeData = clipboard.mimeData()
            if mimeData.hasImage():
                image = clipboard.image()
                byteArray = QByteArray()
                buf = QBuffer(byteArray)
                buf.open(QIODevice.WriteOnly)
                image.save(buf, "PNG")
                self.label.setText('Uploading')
                self.thread = NetThread(str(byteArray.toBase64()))
                self.thread.finished.connect(self.onThreadEnd)
                self.thread.start()
            else:
                self.label.setText('No picture in clipboard')

    def onThreadEnd(self):
        url = self.thread.getResult()
        self.edit.setText(url)
        QApplication.clipboard().setText(url)
        self.label.setText('Finish (URL in clipboard)')


class NetThread(QThread):
    """docstring for NetThread"""
    def __init__(self, base64):
        super(NetThread, self).__init__()
        self.base64 = base64

    def run(self):
        value = {
            'key': API_KEY,
            'image': self.base64
        }
        data = urllib.urlencode(value)
        f = urllib2.urlopen(
            url='http://api.imgur.com/2/upload.json',
            data=data
        )
        response = json.load(f)
        urlRaw = response[u'upload'][u'links'][u'original']
        self.__url = re.sub(r'\\/', '/', urlRaw)

    def getResult(self):
        return self.__url


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ptu = PasteToUpload()
    sys.exit(app.exec_())
