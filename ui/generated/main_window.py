# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QTabWidget, QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(900, 620)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.dialogueTab = QWidget()
        self.dialogueTab.setObjectName(u"dialogueTab")
        self.gridLayout_2 = QGridLayout(self.dialogueTab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.statusLabel = QLabel(self.dialogueTab)
        self.statusLabel.setObjectName(u"statusLabel")

        self.verticalLayout.addWidget(self.statusLabel)

        self.showWindow = QTextEdit(self.dialogueTab)
        self.showWindow.setObjectName(u"showWindow")
        self.showWindow.setReadOnly(True)

        self.verticalLayout.addWidget(self.showWindow)

        self.inputWindow = QTextEdit(self.dialogueTab)
        self.inputWindow.setObjectName(u"inputWindow")
        self.inputWindow.setMaximumSize(QSize(16777215, 150))

        self.verticalLayout.addWidget(self.inputWindow)

        self.sendButton = QPushButton(self.dialogueTab)
        self.sendButton.setObjectName(u"sendButton")

        self.verticalLayout.addWidget(self.sendButton)


        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.tabWidget.addTab(self.dialogueTab, "")
        self.settingTab = QWidget()
        self.settingTab.setObjectName(u"settingTab")
        self.gridLayout_3 = QGridLayout(self.settingTab)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.LLMSaveButton = QPushButton(self.settingTab)
        self.LLMSaveButton.setObjectName(u"LLMSaveButton")

        self.verticalLayout_3.addWidget(self.LLMSaveButton)

        self.LLMCleanButton = QPushButton(self.settingTab)
        self.LLMCleanButton.setObjectName(u"LLMCleanButton")

        self.verticalLayout_3.addWidget(self.LLMCleanButton)


        self.gridLayout_3.addLayout(self.verticalLayout_3, 1, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer, 1, 2, 1, 1)

        self.label_5 = QLabel(self.settingTab)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 1)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.settingTab)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.provider_Edit = QLineEdit(self.settingTab)
        self.provider_Edit.setObjectName(u"provider_Edit")

        self.verticalLayout_2.addWidget(self.provider_Edit)

        self.label_2 = QLabel(self.settingTab)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_2.addWidget(self.label_2)

        self.apiKeyEdit = QLineEdit(self.settingTab)
        self.apiKeyEdit.setObjectName(u"apiKeyEdit")

        self.verticalLayout_2.addWidget(self.apiKeyEdit)

        self.label_3 = QLabel(self.settingTab)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_2.addWidget(self.label_3)

        self.baseUrlEdit = QLineEdit(self.settingTab)
        self.baseUrlEdit.setObjectName(u"baseUrlEdit")

        self.verticalLayout_2.addWidget(self.baseUrlEdit)

        self.label_4 = QLabel(self.settingTab)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_2.addWidget(self.label_4)

        self.modelEdit = QLineEdit(self.settingTab)
        self.modelEdit.setObjectName(u"modelEdit")

        self.verticalLayout_2.addWidget(self.modelEdit)


        self.gridLayout_3.addLayout(self.verticalLayout_2, 1, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer, 2, 0, 1, 1)

        self.tabWidget.addTab(self.settingTab, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"AI Companion", None))
        self.statusLabel.setText("")
        self.sendButton.setText(QCoreApplication.translate("MainWindow", u"\u53d1\u9001", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.dialogueTab), QCoreApplication.translate("MainWindow", u"\u5bf9\u8bdd", None))
        self.LLMSaveButton.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58\u6a21\u578b\u914d\u7f6e", None))
        self.LLMCleanButton.setText(QCoreApplication.translate("MainWindow", u"\u6e05\u7a7a\u6a21\u578b\u914d\u7f6e", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"\u6a21\u578b\u8bbe\u7f6e\uff1a", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"LLM_PROVIDER", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"LLM_API_KEY", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"LLM_BASE_URL", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"LLM_MODEL", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settingTab), QCoreApplication.translate("MainWindow", u"\u914d\u7f6e", None))
    # retranslateUi

