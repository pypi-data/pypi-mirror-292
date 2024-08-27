"""
GUI for batch pypost config
"""


from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from pydantic import BaseModel, Field

import argparse
import sys
import os
import glob
import shutil
import subprocess
import multiprocessing as mp
import time
import logging

from .config import *
from .vtk_meta import *
from . import colorscales
from . import batch_post
from . import resources

def ToQtColor(rgb: RGBIntValue):
	return QColor(rgb.red, rgb.green, rgb.blue)

def FromQtColor(rgb: QColor):
	return RGBIntValue(red=rgb.red(), green=rgb.green(), blue=rgb.blue())

def EnumToStrListModel(parent, en: Enum)->QStringListModel:
	return QStringListModel([ e.name for e in en ], parent)

def EnumToInt(enVal):
	enumMap = dict(zip(enVal.__class__, range(len(enVal.__class__))))
	return enumMap[enVal]

def IntToEnum(iVal, eClass):	
	enumMap = list(eClass)
	return enumMap[iVal]

class CheckableVariable(BaseModel):
	enabled: bool = True
	variable: DataVariable
	color_scale: str = "magma"

	def GetColCount(self):
		return 4

	def GetCol(self, col: int):
		if col == 0:
			return self.variable.name
		elif col == 1:
			return self.variable.component_index		
		elif col == 2:								
			return self.variable.minimum
		elif col == 3:		
			return self.variable.maximum
		raise ValueError("column index out of bounds")

	def SetCol(self, col: int, value: None):
		if col == 0:
			self.variable.name = value
		elif col == 1:
			self.component_index = value		
		elif col == 2:
			self.variable.minimum = value
		elif col == 3:			
			self.variable.maximum = value
		else:
			raise ValueError("column index out of bounds")
		return True
		
	def Headers(self):
		return ["Name", "Component", "Minimum", "Maximum"]


class VariablesModel(QAbstractTableModel):
	def __init__(self, parent, model: list[DataVariable] = None):
		super().__init__(parent)
		self.model: list[CheckableVariable] = []
		for v in model:
			self.model.append(CheckableVariable(enabled=True, variable=v))		

	def GetVariables(self):
		for v in self.model:
			if v.enabled:				
				yield v

	def rowCount(self, parent: QModelIndex):
		return len(self.model)
	
	def columnCount(self, parent):
		if len(self.model):
			return self.model[0].GetColCount()
		return 0
	
	def headerData(self, section, orientation, role=Qt.DisplayRole):
		if role != Qt.DisplayRole:
			return None
		if orientation == Qt.Horizontal:        	
			return self.model[0].Headers()[section]
		return None

	def flags(self, parent: QModelIndex):
		if parent.isValid():
			fl = super().flags(parent) | QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled
			if parent.column() == 0:
				return fl | QtCore.Qt.ItemIsUserCheckable
			elif parent.column() < 2:
				return fl
			else:
				return fl | QtCore.Qt.ItemIsEditable
		return None

	def data(self, index, role):
		if not index.isValid():
			return None

		row = index.row()
		col = index.column()

		if role == Qt.DisplayRole or role == Qt.EditRole:
			return self.model[row].GetCol(col)
		if col == 0 and role == QtCore.Qt.CheckStateRole:			
			if self.model[index.row()].enabled:				
				return int(QtCore.Qt.Checked)
			else:				
				return int(QtCore.Qt.Unchecked)		
		return None
	
	def setData(self, index, value, role):
		if not index.isValid():
			return False			
		
		row = index.row()
		col = index.column()

		if col == 0 and role == QtCore.Qt.CheckStateRole:
			self.model[row].enabled = value == int(QtCore.Qt.Checked)
			self.dataChanged.emit(index, index, [role])
			return True
		elif role == QtCore.Qt.EditRole:
			return self.model[row].SetCol(col, value)
		return False

	def setEnabled(self, indices: Iterable[QModelIndex], value):
		rowIndices = set([ r.row() for r in indices])
		#self.beginResetModel()
		for rowI in rowIndices:
			print ("Setting enabled", rowI, value)
			self.setData(self.createIndex(rowI, 0), value, Qt.CheckStateRole)
			#self.model[rowI].enabled = value
			#self.dataChanged.emit(self.createIndex(rowI, 0), [Qt.CheckStateRole, Qt.DisplayRole])
		#self.endResetModel()
		


class CommonPlotConfig(QAbstractTableModel):
	def __init__(self, parent, model: VTKPlotConfig = None):
		super().__init__(parent)
		self.model = model
		if self.model is None:
			self.model = VTKPlotConfig(name="prototype")
			self.alwaysShowParticles = True
			self.particleSolidColor = QColor(128, 128, 128)

	def GetModelCopy(self):
		return self.model.copy()

	def rowCount(self, parent: QModelIndex):
		return 1	

	def columnCount(self, parent: QModelIndex):
		return 6

	def flags(self, parent: QModelIndex):
		return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled

	def getBackColor(self):
		return ToQtColor(self.model.background_color)
	
	def setBackColor(self, val: QColor):
		self.setData(self.createIndex(0, 2), val, QtCore.Qt.DisplayRole | QtCore.Qt.EditRole )

	def data(self, index, role):
		if ( role == QtCore.Qt.DisplayRole ) or ( role == QtCore.Qt.EditRole ):
			r = index.column()
			if r == 0:
				return self.model.size_x
			elif r == 1:
				return self.model.size_y
			elif r == 2:
				return ToQtColor(self.model.background_color)
			elif r == 3:
				return EnumToInt(self.model.time)
			elif r == 4:
				return self.alwaysShowParticles
			elif r == 5:
				return self.particleSolidColor
		
		return None

	def setData(self, index, value, role):
		if ( role == QtCore.Qt.DisplayRole ) or ( role == QtCore.Qt.EditRole ):
			r = index.column()
			if r == 0:
				self.model.size_x = value
				return True
			elif r == 1:
				self.model.size_y = value
				return True
			elif r == 2:
				self.model.background_color = FromQtColor(value)
				return True
			elif r == 3:
				self.model.time = IntToEnum(value, TimesEnum)
				return True
			elif r == 4:
				self.alwaysShowParticles = value
				return True
			elif r == 5:
				self.particleSolidColor = value
				return True

		return False

class CheckableViewStd(ViewStandard):
	checked: bool = True			

class StandardViewsModel(QAbstractListModel):
	def __init__(self, parent):
		super().__init__(parent)
		self.viewOptions = [
			CheckableViewStd(name="X+", eye_side=DirEnum.xp, up=DirEnum.yp),
			CheckableViewStd(name="Y+", eye_side=DirEnum.yp, up=DirEnum.xp),
			CheckableViewStd(name="Z+", eye_side=DirEnum.zp, up=DirEnum.yp),
			CheckableViewStd(name="X-", eye_side=DirEnum.xn, up=DirEnum.yp),
			CheckableViewStd(name="Y-", eye_side=DirEnum.yn, up=DirEnum.xp),
			CheckableViewStd(name="Z-", eye_side=DirEnum.zn, up=DirEnum.yp),
		]

	def GetEnabledViews(self):
		for v in self.viewOptions:
			if v.checked:
				yield ViewStandard(name=v.name, eye_side=v.eye_side, up=v.up)

	def rowCount(self, parent: QModelIndex):
		return len(self.viewOptions)

	def flags(self, parent: QModelIndex):
		if parent.isValid():	
			fl = super().flags(parent)
			return fl | QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable
		return None

	def data(self, index, role):
		if not index.isValid():
			return None

		row = index.row()
		col = index.column()

		if role == QtCore.Qt.DisplayRole:					
			return self.viewOptions[index.row()].name
		if role == QtCore.Qt.CheckStateRole:			
			if self.viewOptions[index.row()].checked:				
				return int(QtCore.Qt.Checked)
			else:				
				return int(QtCore.Qt.Unchecked)		
		return None
	
	def setData(self, index, value, role):
		if not index.isValid():
			return False			
		if role == QtCore.Qt.CheckStateRole:
			r = index.row()
			self.viewOptions[r].checked = value == int(QtCore.Qt.Checked)
			self.dataChanged.emit(index, index, [role])
			return True
		return False

		


"""
Model
- Common prototype config (columns show below)
	- always show particles
	- Standard views list
	- Watermark
	- Video options
	- background color
	- size x, size y
	- time option

- Variables list
	- Velocity, color scale, range, opacity curve, enabled, slice, volume 
	- ...	

- Plot list
	- Slice X Plot: enabled
	- Slice Y Plot: enabled
	- Slice Particle plot: enabled
	- Volume rendering Plot: enabled
	- Volume Particle plot: enabled

"""

class ColorScaleDb:

	def __init__(self):
		self.colors = list(colorscales.GetAllColorScales(ncolors=12))
		self.names = [ x.name for x in self.colors ]
		self.name2index = dict(zip(self.names, range(len(self.names))))
	
	def GetColor(self, r: int):
		return self.colors[r]

colorDb = ColorScaleDb()

class ColorScalePaintDelegate(QStyledItemDelegate):
	def __init__(self, parent):
		super().__init__(parent)
		self.items = colorDb.names
		self.name2index = colorDb.name2index		

	def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):		
		colorname = index.model().data(index, Qt.DisplayRole)
		color = colorDb.GetColor(self.name2index[colorname])
		#color = colorDb.GetColor(index.row())
		r: QRectF = option.rect
		x0 = r.left()
		x = x0
		l = r.right() - r.left()
		y0 = r.bottom()
		y1 = r.top()
		while x <= r.right():
			xval = (x-x0) / l
			rgb = color.GetColorUInt(xval)			
			painter.setPen(QColor(rgb[0], rgb[1], rgb[2]))
			painter.drawLine(x, y0, x, y1)
			
			x += 1
		painter.drawText(r, 0, color.name)		
		

	def sizeHint(self, option, index):
		return QSize(50, 20)


class ColorScaleComboDelegate(QStyledItemDelegate):
	"""
	A delegate that places a fully functioning QComboBox in every
	cell of the column to which it's applied
	"""
	def __init__(self, parent):
		super().__init__(parent)			
		self.items = colorDb.names
		self.name2index = dict(zip(self.items, range(len(self.items))))
		self.itemsModel = QStringListModel(self.items, self)

		self.painterDelegate = ColorScalePaintDelegate(self)
		
	def createEditor(self, parent, option, index):
		combo = QComboBox(parent)
		combo.setModel(self.itemsModel)
		combo.setItemDelegate(ColorScalePaintDelegate(self))
		return combo
		
	def setEditorData(self, editor, index):		
		curValue = index.model().data(index, QtCore.Qt.EditRole)
		editor.setCurrentIndex(self.name2index[curValue])
		
	def setModelData(self, editor, model, index):
		model.setData(index, editor.currentText(), QtCore.Qt.EditRole)
	
	def updateEditorGeometry(self, editor, option, index):
		editor.setGeometry(option.rect)

	def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
		self.painterDelegate.paint(painter, option, index)


def makeIconColor(w=16, h=16, qcolor=None):
	pm = QtGui.QPixmap(w, h)
	pm.fill(qcolor)
	return QtGui.QIcon(pm)

def setBtnIconColor(btn: QPushButton, qcolor=None):	
	pm = QtGui.QPixmap(btn.iconSize())
	pm.fill(qcolor)
	btn.setIcon(QtGui.QIcon(pm))

def DoBatchPostRun(caseDir, conf):	
	batch_post.run_post(caseDir, conf)

class MyMainWindow(QtWidgets.QMainWindow):
	StopSignal = Signal()

	def __init__(self, clargs):
		super().__init__()		
		self.resize(QSize(1000, 1000))
		self.readSettings()
		self.setWindowTitle("M-Star Batch Post")

		tools = self.addToolBar("maintoolbar")
		tools.setObjectName("maintoolbar")
		tools.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
		actionRun = tools.addAction("Run")
		actionRun.setIcon(QIcon(":/icons/play_blue.png"))
		actionRun.triggered.connect(self.buttonRunClicked)

		self.caseDir = clargs.input_dir

		self.sources: list[DataSource] = []
		for fn in glob.glob(os.path.join(clargs.input_dir, "out/Output/*.pvd")):
			if (metad := GetPvdDataSource(fn, True, True)) is not None:
				self.sources.append(metad)				

		self.commonConfig = CommonPlotConfig(self)
		self.stdViewOptions = StandardViewsModel(self)
		self.variables: list[DataVariable] = []
		for s in self.sources:
			self.variables.extend(s.variables)
		self.variables = ReduceMinMaxVariables(self.variables, True)
		self.variablesModel = VariablesModel(self, self.variables)
		self.proxyModel = QSortFilterProxyModel()
		self.proxyModel.setSourceModel(self.variablesModel )
		
		logger = logging.getLogger()		
		#logging.getLogger().setLevel(logging.DEBUG)

		# 'application' code
		logger.debug('debug message')
		logger.info('info message')
		logger.warning('warn message')
		logger.error('error message')
		logger.critical('critical message')

		mainPage = QtWidgets.QWidget()						
		
		generalPage = QtWidgets.QWidget()
		tabs = QTabWidget()
		widthEdit = QLineEdit()
		heightEdit = QLineEdit()
		backColorBtn = QPushButton("")		
		timesCombo = QComboBox()
		viewsList = QListView()
		variableTable = QTableView()
		commonAlwaysShowParticles = QCheckBox()
		commonSolidParticleColorBtn = QPushButton("")		
		
		self.variablesModel.dataChanged.connect(self.updateEnabledOnDataChanged)
		variableTable.setModel(self.proxyModel)
		variableTable.resizeColumnsToContents()
		variableTable.setSortingEnabled(True)		
		variableTable.sortByColumn(0, Qt.AscendingOrder)
		variableTable.setColumnWidth(2, 200)
		#variableTable.setItemDelegateForColumn(2, ColorScaleComboDelegate(variableTable))
		self.bulkChange = False
		self.variableTable = variableTable
		#variableTable.selectionModel().sele
		#variableTable.setItemDelegateForColumn(3, QStyledItemDelegate())
		#variableTable.setItemDelegateForColumn(4, QStyledItemDelegate())

		viewsList.setModel(self.stdViewOptions)
		timesCombo.setModel(EnumToStrListModel(timesCombo, TimesEnum))
		setBtnIconColor(backColorBtn, self.commonConfig.getBackColor())
		setBtnIconColor(commonSolidParticleColorBtn, self.commonConfig.particleSolidColor)

		layout = QFormLayout(generalPage)
		layout.addRow("Image width", widthEdit)
		layout.addRow("Image height", heightEdit)
		layout.addRow("Background color", backColorBtn)
		layout.addRow("Times to process", timesCombo)		
		layout.addRow("Always show particles", commonAlwaysShowParticles)
		layout.addRow("Solid particle color", commonSolidParticleColorBtn)
		layout.addRow("Views", viewsList)
		#layout.addWidget(self.mode)	
		generalPage.setLayout(layout)	

		mapper = QDataWidgetMapper(generalPage)		
		mapper.setSubmitPolicy(QDataWidgetMapper.AutoSubmit)
		mapper.setModel(self.commonConfig)
		mapper.addMapping(widthEdit, 0)
		mapper.addMapping(heightEdit, 1)
		mapper.addMapping(timesCombo, 3, QByteArray("currentIndex"))
		mapper.addMapping(commonAlwaysShowParticles, 4)
		mapper.toFirst()		

		tabs.addTab(generalPage, "General")
		tabs.addTab(variableTable, "Variables")

		mainLayout = QtWidgets.QVBoxLayout()		
		mainLayout.addWidget(tabs)		
		
		mainPage.setLayout(mainLayout)
		
		self.setCentralWidget(mainPage)				

		self.backColorBtn = backColorBtn
		self.backColorBtn.clicked.connect(self.buttonPickBackgroundColor)

		self.particleColorBtn = commonSolidParticleColorBtn
		self.particleColorBtn.clicked.connect(self.buttonPickParticleSolidColor)

	def closeEvent(self, event):
		self.saveSettings()

	def readSettings(self):
		settings = QSettings("MStar", "BatchPostGui")
		if (v := settings.value("mainwindow/geometry")) is not None:
			self.restoreGeometry(v)
		if (v := settings.value("mainwindow/windowState")) is not None:
			self.restoreState(v)

	def saveSettings(self):
		settings = QSettings("MStar", "BatchPostGui")
		settings.setValue("mainwindow/geometry", self.saveGeometry())
		settings.setValue("mainwindow/windowState", self.saveState())		

	def updateEnabledOnDataChanged(self, topleft: QModelIndex, bottomright: QModelIndex, roles):
		if self.bulkChange:
			return
		
		self.bulkChange = True
		if topleft.column() == 0 and topleft == bottomright:
			value = topleft.data(Qt.CheckStateRole)			
			indices = map(self.proxyModel.mapToSource, [ index for index in self.variableTable.selectionModel().selection().indexes() ] )
			self.variablesModel.setEnabled(indices, value )
		self.bulkChange = False
		#self.variableTable.

	def GetPlotsConfig(self):

		### Collect prototype object to be used for all generated plots
		proto = self.commonConfig.GetModelCopy()

		for v in self.stdViewOptions.GetEnabledViews():
			proto.standard_views.append(v)		

		variables = list(self.variablesModel.GetVariables())
		pickedVariables = VarListToKeySet([ v.variable for v in variables])
		pickedVariablesDict = {}
		for v in variables:
			k = VarToKey( v.variable, True)
			pickedVariablesDict[k] = v		

		### Start construction of post config
		conf = BatchPostConfig()
		conf.auto_pdf_report = False
		conf.auto_stat_plots = False
		conf.default_stat_plot_style = StatPlotStyle(
					legend_location=LegendLocEnum.upper_right,
					size=(1000, 300),
					style=["ggplot"])

		input_dir = os.path.join(self.caseDir, "out/Output")

		srcs = self.sources		

		defaultMovingBodySolidColor = RGBIntValue(red=128, green=128, blue=128)
		defaultParticleSolidColor = FromQtColor(self.commonConfig.particleSolidColor)
		alwaysShowParticles = self.commonConfig.alwaysShowParticles

		## Slice Plots
		slicePlot = proto.copy()
		slicePlot.name = "SlicePlot"
		vars = pickedVariables.copy()
		for src in srcs:
			if src.time_group == DataTimeEnum.slice:
				if src.data_type == DataTypeEnum.walls:
					slicePlot.stl_pipelines.append(StaticStlPipeline(file=src.filename))
				elif src.data_type == DataTypeEnum.slice:
					vars = vars.intersection(VarListToKeySet(src.variables))
					slicePlot.block_pipelines.append(BlockDataPipeline(file=src.filename, color_by=ColorByEnum.variable))
				elif src.data_type == DataTypeEnum.body:
					slicePlot.moving_pipelines.append(MovingBodyPipeline(file=src.filename, color_by=ColorByEnum.solid_color, solid_color=defaultMovingBodySolidColor))
				elif alwaysShowParticles and src.data_type == DataTypeEnum.particles:
					slicePlot.particle_pipelines.append(ParticlesPipeline(file=src.filename, color_by=ColorByEnum.solid_color, solid_color=defaultParticleSolidColor))				

		for v in vars:
			dvar = pickedVariablesDict[v].variable			
			colorscale = pickedVariablesDict[v].color_scale
			
			slicePlot.variables.append(VTKVariable(name=dvar.name, 
												min=dvar.minimum, 
												max=dvar.maximum, 
												number_components=dvar.number_components,
												component=dvar.component_index, 
												discrete=True, 
												discrete_n=12,
												color_scale=colorscale
												))

		conf.plots.append(slicePlot)
		return conf


	@QtCore.Slot()
	def buttonPickBackgroundColor(self):
		col = QColorDialog.getColor(self.commonConfig.getBackColor(), self)
		if col.isValid():
			self.commonConfig.setBackColor(col)
			setBtnIconColor(self.backColorBtn, self.commonConfig.getBackColor())

	@QtCore.Slot()
	def buttonPickParticleSolidColor(self):
		col = QColorDialog.getColor(self.commonConfig.particleSolidColor, self)
		if col.isValid():
			self.commonConfig.particleSolidColor = col
			setBtnIconColor(self.particleColorBtn, self.commonConfig.particleSolidColor)

	@QtCore.Slot()
	def buttonRunClicked(self):
		conf = self.GetPlotsConfig()
		print(conf)
		mp.Process(target=DoBatchPostRun, args=(self.caseDir, conf)).start()

	# def runLongTask(self, cmd="", wd=""):
	# 	# Step 2: Create a QThread object
	# 	self.thread = QThread()
	# 	# Step 3: Create a worker object
	# 	self.worker = CmdRunnerWorker(cmd, wd)
	# 	# Step 4: Move worker to the thread
	# 	self.worker.moveToThread(self.thread)
	# 	# Step 5: Connect signals and slots
	# 	self.thread.started.connect(self.worker.run)
	# 	self.worker.finished.connect(self.thread.quit)
	# 	self.worker.finished.connect(self.worker.deleteLater)
	# 	self.StopSignal.connect(self.worker.StopRequested)
	# 	self.thread.finished.connect(self.thread.deleteLater)
	# 	#self.worker.progress.connect(self.reportProgress)
	# 	# Step 6: Start the thread
	# 	self.thread.start()		
		

	# @QtCore.Slot()
	# def buttonRunClicked(self):

	# 	caseDir = os.path.splitext(self.modelfn)[0] + "_RUN"

	# 	if os.path.isdir(caseDir):

	# 		ret = QMessageBox.warning(self, "Directory exists", "Run directory exists. Delete Now?", buttons= (QMessageBox.Ok | QMessageBox.Cancel))

	# 		if ret == QMessageBox.Ok:
	# 			shutil.rmtree(caseDir)
	# 		else:
	# 			return

	# 	os.makedirs(caseDir)
	# 	print ("Exporting case:", caseDir)
	# 	self.model.Export(caseDir)

	# 	print ("Running case")

	# 	cmd = [
	# 		"mpiexec",
	# 		"-n",
	# 		"1",
	# 		solver_exe,
	# 		"-i", "input.xml",
	# 		"-o", "out",
	# 		"--gpu-ids=0",
	# 		"--force",
	# 		"--queue"
	# 	]

	# 	self.runLongTask(cmd, caseDir)

	# @QtCore.Slot()
	# def buttonStopClicked(self):
	# 	if self.worker is not None:
	# 		self.worker.stopRequested = True

def rungui():
	app = QtWidgets.QApplication([])

	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input-dir", help="Input case directory", default=".")
	clargs = parser.parse_args()

	widget = MyMainWindow(clargs)    	
	widget.show()

	app.exec()

if __name__ == "__main__":
	mp.freeze_support()
	rungui()