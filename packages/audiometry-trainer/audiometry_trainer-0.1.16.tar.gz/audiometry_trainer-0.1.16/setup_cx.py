from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [],
                 'excludes': ['tkinter',
                              'PyQt5',
                              'PyQt5.QtCore',
                              'PyQt5.QtGui',
                              'PyQt5.QtWidgets',
                              'PyQt5.QtQml',
                              'PyQt5.QtBluetooth',
                              'PyQt5.QtQuickWidgets',
                              'PyQt5.QtSensors',
                              'PyQt5.QtSerialPort',
                              'PyQt6.QtSql',
                              'PyQt6.QtQml',
                              'PyQt6.QtBluetooth',
                              'PyQt6.QtQuickWidgets',
                              'PyQt6.QtSensors',
                              'PyQt6.QtSerialPort',
                              'PyQt6.QtSql',
                              'PyQt6.QtQuick',
                              'PyQt6.QtQuick3D',
                              'PyQt6.QtQuickWidgets',
                              'PyQt6.QtDesigner',
                              'PyQt6.QtPdf',
                              'PyQt6.QtPdfWidgets',
                              'PyQt6.QtSensors',
                              'PyQt6.QtTest',
                              'PyQt6.QtTextToSpeech',
                              ]}


import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('audiometry_trainer\\__main__.py',
               base=base,
               target_name = 'audiometry_trainer',
               icon='icons/audiometry_trainer_icon.ico'
               )
]

setup(name='audiometry_trainer',
    version="0.1.16",
      description = '',
      options = {'build_exe': build_options},
      executables = executables)
