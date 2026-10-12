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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QSizePolicy, QSpacerItem, QTabWidget, QTextEdit,
    QVBoxLayout, QWidget)

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
        self.companionTab = QWidget()
        self.companionTab.setObjectName(u"companionTab")
        self.gridLayout_4 = QGridLayout(self.companionTab)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_6 = QLabel(self.companionTab)
        self.label_6.setObjectName(u"label_6")

        self.verticalLayout_4.addWidget(self.label_6)

        self.recentMessagesEdit = QLineEdit(self.companionTab)
        self.recentMessagesEdit.setObjectName(u"recentMessagesEdit")

        self.verticalLayout_4.addWidget(self.recentMessagesEdit)

        self.label_7 = QLabel(self.companionTab)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout_4.addWidget(self.label_7)

        self.historyPageSizeEdit = QLineEdit(self.companionTab)
        self.historyPageSizeEdit.setObjectName(u"historyPageSizeEdit")

        self.verticalLayout_4.addWidget(self.historyPageSizeEdit)

        self.label_8 = QLabel(self.companionTab)
        self.label_8.setObjectName(u"label_8")

        self.verticalLayout_4.addWidget(self.label_8)

        self.summaryBatchSizeEdit = QLineEdit(self.companionTab)
        self.summaryBatchSizeEdit.setObjectName(u"summaryBatchSizeEdit")

        self.verticalLayout_4.addWidget(self.summaryBatchSizeEdit)

        self.label_9 = QLabel(self.companionTab)
        self.label_9.setObjectName(u"label_9")

        self.verticalLayout_4.addWidget(self.label_9)

        self.summaryCountEdit = QLineEdit(self.companionTab)
        self.summaryCountEdit.setObjectName(u"summaryCountEdit")

        self.verticalLayout_4.addWidget(self.summaryCountEdit)

        self.label_10 = QLabel(self.companionTab)
        self.label_10.setObjectName(u"label_10")

        self.verticalLayout_4.addWidget(self.label_10)

        self.summaryMaxCharsEdit = QLineEdit(self.companionTab)
        self.summaryMaxCharsEdit.setObjectName(u"summaryMaxCharsEdit")

        self.verticalLayout_4.addWidget(self.summaryMaxCharsEdit)


        self.horizontalLayout.addLayout(self.verticalLayout_4)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_11 = QLabel(self.companionTab)
        self.label_11.setObjectName(u"label_11")

        self.verticalLayout_5.addWidget(self.label_11)

        self.contestMaxCharsEdit = QLineEdit(self.companionTab)
        self.contestMaxCharsEdit.setObjectName(u"contestMaxCharsEdit")

        self.verticalLayout_5.addWidget(self.contestMaxCharsEdit)

        self.label_12 = QLabel(self.companionTab)
        self.label_12.setObjectName(u"label_12")

        self.verticalLayout_5.addWidget(self.label_12)

        self.followupsEnabledBox = QComboBox(self.companionTab)
        self.followupsEnabledBox.setObjectName(u"followupsEnabledBox")

        self.verticalLayout_5.addWidget(self.followupsEnabledBox)

        self.label_13 = QLabel(self.companionTab)
        self.label_13.setObjectName(u"label_13")

        self.verticalLayout_5.addWidget(self.label_13)

        self.followupDedlayDaysEdit = QLineEdit(self.companionTab)
        self.followupDedlayDaysEdit.setObjectName(u"followupDedlayDaysEdit")

        self.verticalLayout_5.addWidget(self.followupDedlayDaysEdit)

        self.label_14 = QLabel(self.companionTab)
        self.label_14.setObjectName(u"label_14")

        self.verticalLayout_5.addWidget(self.label_14)

        self.followupCooldownDaysEdit = QLineEdit(self.companionTab)
        self.followupCooldownDaysEdit.setObjectName(u"followupCooldownDaysEdit")

        self.verticalLayout_5.addWidget(self.followupCooldownDaysEdit)

        self.label_15 = QLabel(self.companionTab)
        self.label_15.setObjectName(u"label_15")

        self.verticalLayout_5.addWidget(self.label_15)

        self.followExpiryDaysEdit = QLineEdit(self.companionTab)
        self.followExpiryDaysEdit.setObjectName(u"followExpiryDaysEdit")

        self.verticalLayout_5.addWidget(self.followExpiryDaysEdit)


        self.horizontalLayout.addLayout(self.verticalLayout_5)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_16 = QLabel(self.companionTab)
        self.label_16.setObjectName(u"label_16")

        self.verticalLayout_6.addWidget(self.label_16)

        self.followupIdleSecondsEdit = QLineEdit(self.companionTab)
        self.followupIdleSecondsEdit.setObjectName(u"followupIdleSecondsEdit")

        self.verticalLayout_6.addWidget(self.followupIdleSecondsEdit)

        self.label_17 = QLabel(self.companionTab)
        self.label_17.setObjectName(u"label_17")

        self.verticalLayout_6.addWidget(self.label_17)

        self.quietStartHourEdit = QLineEdit(self.companionTab)
        self.quietStartHourEdit.setObjectName(u"quietStartHourEdit")

        self.verticalLayout_6.addWidget(self.quietStartHourEdit)

        self.label_18 = QLabel(self.companionTab)
        self.label_18.setObjectName(u"label_18")

        self.verticalLayout_6.addWidget(self.label_18)

        self.quietEndHourEdit = QLineEdit(self.companionTab)
        self.quietEndHourEdit.setObjectName(u"quietEndHourEdit")

        self.verticalLayout_6.addWidget(self.quietEndHourEdit)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_2)


        self.horizontalLayout.addLayout(self.verticalLayout_6)


        self.gridLayout_4.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.saveCompanionButton = QPushButton(self.companionTab)
        self.saveCompanionButton.setObjectName(u"saveCompanionButton")

        self.horizontalLayout_2.addWidget(self.saveCompanionButton)

        self.recoveryCompanionButton = QPushButton(self.companionTab)
        self.recoveryCompanionButton.setObjectName(u"recoveryCompanionButton")

        self.horizontalLayout_2.addWidget(self.recoveryCompanionButton)


        self.gridLayout_4.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer_3, 2, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_2, 0, 1, 1, 1)

        self.tabWidget.addTab(self.companionTab, "")
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

        self.llmStatusLabel = QLabel(self.settingTab)
        self.llmStatusLabel.setObjectName(u"llmStatusLabel")
        self.llmStatusLabel.setWordWrap(True)

        self.gridLayout_3.addWidget(self.llmStatusLabel, 3, 0, 1, 3)

        self.tabWidget.addTab(self.settingTab, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"AI Companion", None))
        self.statusLabel.setText("")
        self.sendButton.setText(QCoreApplication.translate("MainWindow", u"\u53d1\u9001", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.dialogueTab), QCoreApplication.translate("MainWindow", u"\u5bf9\u8bdd", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u6d88\u606f\u6761\u76ee\u6570\uff1a", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"\u52a0\u8f7d\u5386\u53f2\u6761\u76ee\u6570\uff1a", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"\u6458\u8981\u5904\u7406\u65e7\u6761\u76ee\u6570\uff1a", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"\u6458\u8981\u6570\u91cf\uff1a", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"\u6458\u8981\u6700\u5927\u5b57\u7b26\u6570\uff1a", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"\u5355\u6b21\u5bf9\u8bdd\u4e0a\u9650\u5b57\u7b26\uff1a", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"\u662f\u5426\u5141\u8bb8\u4e3b\u52a8\u5173\u5fc3\uff1a", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"\u8ddf\u8fdb\u7b49\u5f85\u5929\u6570\uff08\u5929\uff09\uff1a", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"\u540c\u4e00\u8bdd\u9898\u8ddf\u8fdb\u95f4\u9694\uff08\u5929\uff09\uff1a", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"\u4e8b\u9879\u6709\u6548\u671f\uff08\u5929\uff09\uff1a", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"\u7a7a\u95f2\u89e6\u53d1\u65f6\u957f\uff08\u79d2\uff09\uff1a", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"\u9759\u9ed8\u5f00\u59cb\uff08\u5317\u4eac\u65f6\u95f4\u6574\u70b9\uff09\uff1a", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"\u9759\u9ed8\u7ed3\u675f\uff08\u5317\u4eac\u65f6\u95f4\u6574\u70b9\uff09\uff1a", None))
        self.saveCompanionButton.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58\u914d\u7f6e", None))
        self.recoveryCompanionButton.setText(QCoreApplication.translate("MainWindow", u"\u6062\u590d\u9ed8\u8ba4", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.companionTab), QCoreApplication.translate("MainWindow", u"\u4ea4\u4e92\u8bbe\u7f6e", None))
        self.LLMSaveButton.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58\u6a21\u578b\u914d\u7f6e", None))
        self.LLMCleanButton.setText(QCoreApplication.translate("MainWindow", u"\u6e05\u7a7a\u6a21\u578b\u914d\u7f6e", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"\u6a21\u578b\u8bbe\u7f6e\uff1a", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"LLM_PROVIDER", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"LLM_API_KEY", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"LLM_BASE_URL", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"LLM_MODEL", None))
        self.llmStatusLabel.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settingTab), QCoreApplication.translate("MainWindow", u"\u6a21\u578b\u8bbe\u7f6e", None))
    # retranslateUi

