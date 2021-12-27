from GUI_newest import GUI
from PyQt5 import QtWidgets
import sys

if __name__ == "__main__" :
    app = QtWidgets.QApplication(sys.argv) #will allow the whole script to be run as an application that can be quit by the user.
    main_window = QtWidgets.QMainWindow() #create the frame which the GUI will run in
    main_GUI = GUI(main_window) #run the GUI
    main_window.show() #loop the GUI
    sys.exit(app.exec_()) #exit when the command is given to exit