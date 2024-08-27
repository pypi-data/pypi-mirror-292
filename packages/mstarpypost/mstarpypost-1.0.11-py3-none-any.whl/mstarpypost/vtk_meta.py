import os
import re
from typing import Optional
from pydantic import BaseModel
from enum import Enum
import logging
import collections
import io
import xml.etree.ElementTree as ET
from collections.abc import Iterable

from . import mstarvtk

class DataTimeEnum(str, Enum):
	init = "init"
	slice = "slice"
	volume = "volume"

class DataTypeEnum(str, Enum):
	walls = "walls"
	bc = "bc"
	slice = "slice"
	volume = "volume"
	particles = "particles"
	body = "body"
	unknown = "unknown"

class VtkDataTypeEnum(str, Enum):
	point = "point"
	cell = "cell"

class DataVariable(BaseModel):
	name: str
	type: VtkDataTypeEnum
	number_components: int = 1
	component_index: int = 0
	minimum: Optional[float]
	maximum: Optional[float]

class DataSource(BaseModel):

	filename: str
	name: str
	time_group: DataTimeEnum
	data_type: DataTypeEnum
	variables: list[DataVariable] = []


def GetFieldDataRanges(fd=None):
	r = []
	for i in range(fd.GetNumberOfArrays()):
		a = fd.GetArray(i)
		ncomp = a.GetNumberOfComponents()
		for ci in range(ncomp):
			amin,amax = a.GetRange(ci)
			r.append( (a.GetName(), ncomp, ci, amin, amax ) )
	return r

def GetVariables(fd):

	cellData = fd.GetCellData()
	for i in range(cellData.GetNumberOfArrays()):
		a = cellData.GetArray(i)
		ncomp = a.GetNumberOfComponents()		
		name = a.GetName()
		for compi in range(ncomp):
			yield DataVariable(name=name, type=VtkDataTypeEnum.cell, number_components=ncomp, component_index=compi)

	pointData =  fd.GetPointData()
	for i in range(pointData.GetNumberOfArrays()):
		a = pointData.GetArray(i)
		ncomp = a.GetNumberOfComponents()		
		name = a.GetName()
		for compi in range(ncomp):
			yield DataVariable(name=name, type=VtkDataTypeEnum.point, number_components=ncomp, component_index=compi)


def GetVariableRanges(dset):
	for name,ncomp,compi,compmin,compmax in GetFieldDataRanges(dset.GetCellData()):	
		yield DataVariable(name=name, type=VtkDataTypeEnum.cell, number_components=ncomp, component_index=compi, minimum=compmin, maximum=compmax)
	for name,ncomp,compi,compmin,compmax in GetFieldDataRanges(dset.GetPointData()):	
		yield DataVariable(name=name, type=VtkDataTypeEnum.point, number_components=ncomp, component_index=compi, minimum=compmin, maximum=compmax)

def VarToKey(v: DataVariable, ignoreType=True):	
	key = [v.name, v.number_components, v.component_index]
	if not ignoreType:
		key.append(v.type)
	return tuple(key)

def VarListToKeySet(variables: Iterable[DataVariable], ignoreType=True):
	return frozenset( [ VarToKey(v, ignoreType=True) for v in variables ] )

def VarListToDict(variables: Iterable[DataVariable], ignoreType=True):
	return dict(zip([ VarToKey(v, ignoreType=True) for v in variables ], variables))

def ReduceUniqueVariables(varAgg: Iterable[DataVariable], ignoreVarType=False) -> list[DataVariable]:
	vars = {}
	for v in varAgg:
		key = VarToKey(v, ignoreType=ignoreVarType)
		vars[key] = v
	return [v for k,v in vars.items()]

def ReduceMinMaxVariables(varAgg: Iterable[DataVariable], ignoreVarType=False) -> list[DataVariable]:
	"""
	Reduce an aggregated list of data variables by taking min/max on variable range
	"""
	vars = {}
	for v in varAgg:
		key = VarToKey(v, ignoreType=ignoreVarType)
		if key in vars:
			vars[key].minimum = min(vars[key].minimum, v.minimum)
			vars[key].maximum = max(vars[key].maximum, v.maximum)
		else:
			vars[key] = v
	return [v for k,v in vars.items()]	

def GetDataObjectVariableRanges(dobj) -> list[DataVariable]:
	
	items = []
	if dobj.IsA("vtkCompositeDataSet"):

		# reduce variable min/max over all blocks
		it = dobj.NewIterator()
		it.InitTraversal()
		allvars = []
		while not it.IsDoneWithTraversal():
			allvars.extend(GetVariableRanges(it.GetCurrentDataObject()))
			it.GoToNextItem()
		
		items = ReduceMinMaxVariables(allvars)
		
	else:
		for v in GetVariableRanges(dobj):		 
			items.append(v)
			
	return items

def GetVtkFileVariables(pvd="", time=0.0):
	"""
	Parses the raw VTK header into DataVariable objects
	* does not expand vector variables, eg. you will only get a single vector variable instead of 3 separate ones with component=0 1 2
	"""

	reader = mstarvtk.PvdReader(pvd)
	for fn in reader.get_filenames(time):

		header = io.StringIO()
		with open(fn, 'rb') as f:
			while not header.getvalue().endswith("""<AppendedData""") and len(newchar := f.read(1).decode("utf-8")):
				header.write(newchar)
		header.write("/></VTKFile>")
		header.seek(0)
		
		root = ET.parse(header).getroot()		
		for pointData in root.findall(".//PointData"):
			for dataArr in pointData.findall("./DataArray"):
				yield DataVariable(name=dataArr.get("Name"), type=VtkDataTypeEnum.point, number_components=int(dataArr.get("NumberOfComponents", 1)))				
		
		for pointData in root.findall(".//CellData"):
			for dataArr in pointData.findall("./DataArray"):
				yield DataVariable(name=dataArr.get("Name"), type=VtkDataTypeEnum.point, number_components=int(dataArr.get("NumberOfComponents", 1)))


def GetPvdDataSource(fn="", last_only=True, computeMinMax=True) -> DataSource:
	"""
	"""

	fullpath = fn
	filename = os.path.basename(fn)
	obj_name = ""
	timegroup = DataTimeEnum.init
	type = DataTypeEnum.bc	
	color_by_variable = False
	solid_color_default = "lightgrey"

	solverTypeToEnum = {
		"particles": DataTypeEnum.particles,
		"movingbody": DataTypeEnum.body,
		"x": DataTypeEnum.slice,
		"y": DataTypeEnum.slice,
		"z": DataTypeEnum.slice,
	}

	if filename == "Walls.stl":
		timegroup = DataTimeEnum.init
		type = DataTypeEnum.walls
		obj_name = "Walls"
	elif filename == "BoundaryConditions.pvd":
		timegroup = DataTimeEnum.init
		type = DataTypeEnum.bc
		obj_name = "Boundary Conditions"
	elif filename == "Volume.pvd":
		timegroup = DataTimeEnum.volume
		type = DataTypeEnum.volume
		color_by_variable = True
		obj_name = "Volume"
	else:
		
		if (m := re.match(r"^(Slice|Volume)([^_]+)_(.*)\.pvd$", filename)) is not None:
									
			try:
				timegrpstr = m.group(1).lower()
				typestr = m.group(2).lower()

				timegroup = DataTimeEnum[timegrpstr]
				type = solverTypeToEnum[typestr]
				obj_name = m.group(3)

			except KeyError:
				logging.warn("Could not determine meta data: %s", fn)
				return None
		
		else:
			logging.warn("Unknown output filename: %s" % fn)
			return None

	pvdr = mstarvtk.PvdReader(fn)
	times = pvdr.get_times()
	if len(times):
		if last_only:
			times = [ times[-1] ]
	else:
		return None
	
	vars = []

	if computeMinMax:
		for t in times:
			dataobj = pvdr.get_data(t)
			vars.extend( GetDataObjectVariableRanges(dataobj) )

		vars = ReduceMinMaxVariables(vars)
	else:
		for t in times:
			vars.extend(GetVtkFileVariables(fn, t))			

		vars = ReduceUniqueVariables(vars)

	return DataSource(filename=fullpath, name=obj_name, time_group=timegroup, data_type=type, variables=vars)
	
