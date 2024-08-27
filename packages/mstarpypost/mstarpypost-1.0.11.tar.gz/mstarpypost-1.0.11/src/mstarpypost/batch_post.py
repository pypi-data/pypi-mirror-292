"""
- Read configuration of post processed output
- Run all plot generation
"""

import argparse
import itertools
import xml.etree.ElementTree as ET
import logging
import vtk
import sys
import os
import glob
import io
from PIL import Image, ImageFont, ImageDraw
import polars as pl
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import subprocess
import json
from pprint import pprint

from . import mstarvtk, vtk_meta
from .config import *
from .vtk_meta import DataTypeEnum, DataTimeEnum, DataVariable

def get_file_path(outdir, fn):	
	if not os.path.isabs(fn) and not os.path.isfile(fn):
		return os.path.join(outdir, fn)
	return fn

def get_pipeline_times(outdir, pl):
	if os.path.splitext(os.path.basename(pl.file))[1].lower() == ".pvd":	
		fn = get_file_path(outdir, pl.file)
		readerPvd = mstarvtk.PvdReader(fn)
		return readerPvd.get_times()
	return []

def get_plot_times(outdir, plotConf):
	all_pipelines = itertools.chain(plotConf.block_pipelines, plotConf.moving_pipelines, plotConf.particle_pipelines, plotConf.volume_pipelines)
	all_times = []
	for pl in all_pipelines:
		all_times.append((pl.file, get_pipeline_times(outdir, pl) ))
	return all_times


def create_example_config():
	conf = BatchPostConfig()

	c1 = VTKPlotConfig(name="Slice Y Plot", 
						variables=[VTKVariable(name="Velocity Magnitude (m/s)", min=0, max=1, discrete=True)],
						block_pipelines=[BlockDataPipeline(file="SliceY_0.167.pvd", color_by=ColorByEnum.variable)],
						standard_views=[ViewStandard(name="Top", eye_side=DirEnum.yp, up=DirEnum.zp)],
						video_options=VideoOption(enabled=True))	

	conf.plots = [ c1 ] 
	return conf


def create_example_volume_config():
	conf = BatchPostConfig()

	c1 = VTKPlotConfig(name="Volume", 
						variables=[VTKVariable(name="Velocity Magnitude (m/s)", min=0, max=1)],
						volume_pipelines=[VolumePipeline(file="Volume.pvd")],
						standard_views=[ViewStandard(name="Top", eye_side=DirEnum.yp, up=DirEnum.zp)],
						video_options=VideoOption(enabled=True))	
						
	conf.plots = [ c1 ] 
	return conf

def create_example_stat_plots_config():

	c1 = VTKPlotConfig(name="Slice Y Plot", 
						variables=[VTKVariable(name="Velocity Magnitude (m/s)", min=0, max=1, discrete=True)],
						block_pipelines=[BlockDataPipeline(file="SliceY_0.167.pvd", color_by=ColorByEnum.variable)],
						standard_views=[ViewStandard(name="Top", eye_side=DirEnum.yp, up=DirEnum.zp)],
						video_options=VideoOption(enabled=True))

	conf = BatchPostConfig(
		auto_stat_plots=True,
		auto_pdf_report=True,
		default_stat_plot_style=StatPlotStyle(
				legend_location=LegendLocEnum.upper_right,
				size=(1000, 300),
				style=["ggplot"]),
		stat_plots=[
		StatPlot(name="Impeller Forces", 
			x_title="Time [s]",
			y_title="Force [N]",
			chart_title="Moving Body Forces",
			series=[
				StatPlotDataSeries(filename="MovingBody_Moving Body.txt", y="Force X [N]"),
				StatPlotDataSeries(filename="MovingBody_Moving Body.txt", y="Force Y [N]"),
				StatPlotDataSeries(filename="MovingBody_Moving Body.txt", y="Force Z [N]")
				]),],
		plots=[VTKPlotConfig(name="Slice Y Plot", time=TimesEnum.last,
						variables=[VTKVariable(name="Velocity Magnitude (m/s)", min=0, max=1, discrete=True)],
						block_pipelines=[BlockDataPipeline(file="SliceY_0.167.pvd", color_by=ColorByEnum.variable)],
						standard_views=[ViewStandard(name="Top", eye_side=DirEnum.yp, up=DirEnum.zp)],
						video_options=VideoOption(enabled=True))]
		)

	return conf

def RgbToFloat(rgb):
	return max(0.0, min(1.0, rgb / 255.0))

def RgbValToFloat(rgb):
	return (RgbToFloat(rgb.red), RgbToFloat(rgb.green), RgbToFloat(rgb.blue))

def CreateOpacityFunction(opacity: OpacityFunction, variable: VTKVariable):

	if opacity.type == OpacityFuncType.autoselect:
		if variable.min < 0 and variable.max > 0:			
			opfunc = vtk.vtkPiecewiseFunction()		
			opfunc.AddPoint(variable.min, 		1.0)
			opfunc.AddPoint(0.1*variable.min, 	0.0)
			opfunc.AddPoint(0, 					0.0)
			opfunc.AddPoint(0.1*variable.max, 	0.0)	
			opfunc.AddPoint(variable.max, 		1.0)	
			return opfunc

		else:
			opfunc = vtk.vtkPiecewiseFunction()		
			opfunc.AddPoint(0.0, 				0.0)
			opfunc.AddPoint(0.1 * variable.max, 0.0)
			opfunc.AddPoint(variable.max, 		1.0)
			return opfunc	
	else:

		if opacity.type == OpacityFuncType.ramp:
			data = [(opacity.start, 0.0), 
					(opacity.end, 1.0) ]
		elif opacity.type == OpacityFuncType.constant:		
			data = [ (0.0, opacity.constant_value), (1.0, opacity.constant_value) ]
		elif opacity.type == OpacityFuncType.smooth:
			xs = np.linspace(0, 1, 128)
			e0 = opacity.start
			e1 = opacity.end
			ys = [ smootherStep(e0, e1, xi) for xi in xs  ]
			data = zip(xs, ys)
		else:
			raise ValueError ("Opacity type not supported: " + str(opacity.type))
		
		opfunc = vtk.vtkPiecewiseFunction()	
		vrange = variable.max - variable.min
		for x,y in data:
			xval = variable.min + x * vrange
			opfunc.AddPoint(xval, y)

		return opfunc


def CreateAllBatchConfig(case_dir="", 
						do_slice=False, 
						do_volume=False, 
						do_particle=False, 
						do_body=False, 
						exclude_rare=True, 
						range_last_only=True, 
						always_show_particles=False,
						last_only=False) -> BatchPostConfig:						
	"""
	
	:param case_dir: case directory path
	:param do_slice: process slices
	:param do_particle: process particles
	:param do_body: process moving body field data
	:param exclude_rare: exclude rarely used fields and files
	:param range_last_only: determine color scale ranges from last time step only, otherwise, use all times
	"""

	conf = BatchPostConfig()

	timeop =  TimesEnum.all
	if last_only:
		timeop = TimesEnum.last
			
	conf.auto_pdf_report = False
	conf.auto_stat_plots = False
	conf.default_stat_plot_style = StatPlotStyle(
				legend_location=LegendLocEnum.upper_right,
				size=(1000, 300),
				style=["ggplot"])

	input_dir = os.path.join(case_dir, "out/Output")

	excludedFiles = []
	excludedFields = []
	if exclude_rare:
		excludedFiles = [
			"BoundaryConditions.pvd"
		]

		excludedFields = [
			"vtkGhostType",
			#"Volume Fraction (-)", # todo -- turn this on/off if free surface model is detected
			"ID",
			"OriginID",
			"Nearest Neighbor Distance (m)"
		]

	srcs: list[vtk_meta.DataSource] = []
	for fn in glob.glob(os.path.join(input_dir, "*.pvd")):

		if os.path.basename(fn) in excludedFiles:
			continue

		if (metad := vtk_meta.GetPvdDataSource(fn, range_last_only)) is not None:
			srcs.append(metad)

	common_views = [ 
		ViewStandard(name="YP", eye_side=DirEnum.yp, up=DirEnum.zp), 
		ViewStandard(name="XP", eye_side=DirEnum.xp, up=DirEnum.yp),
		ViewStandard(name="ZP", eye_side=DirEnum.zp, up=DirEnum.yp)
	]

	defaultMovingBodySolidColor = RGBIntValue(red=128, green=128, blue=128)
	defaultParticleSolidColor = RGBIntValue(red=128, green=0, blue=128)	

	if do_slice:

		proto = VTKPlotConfig(name="Slice Plot")
		proto.video_options.enabled = timeop == TimesEnum.all
		proto.time = timeop

		vars = []
		for src in srcs:
			if src.time_group == DataTimeEnum.slice:
				if src.data_type == DataTypeEnum.walls:
					proto.stl_pipelines.append(StaticStlPipeline(file=src.filename))
				elif src.data_type == DataTypeEnum.slice:
					vars.extend(src.variables)
					proto.block_pipelines.append(BlockDataPipeline(file=src.filename, color_by=ColorByEnum.variable))
				elif src.data_type == DataTypeEnum.body:
					proto.moving_pipelines.append(MovingBodyPipeline(file=src.filename, color_by=ColorByEnum.solid_color, solid_color=defaultMovingBodySolidColor))
				elif always_show_particles and src.data_type == DataTypeEnum.particles:
					proto.particle_pipelines.append(ParticlesPipeline(file=src.filename, color_by=ColorByEnum.solid_color, solid_color=defaultParticleSolidColor))
		
		vars = vtk_meta.ReduceMinMaxVariables(vars)

		for v in vars:
			if v.name in excludedFields:
				continue

			proto.variables.append(VTKVariable(name=v.name, 
												min=v.minimum, 
												max=v.maximum, 
												component=v.component_index, 
												discrete=True, 
												number_components=v.number_components))

		proto.standard_views = common_views

		conf.plots.append(proto)

	if do_volume:

		proto = VTKPlotConfig(name="Volume Plot")
		proto.video_options.enabled = timeop == TimesEnum.all
		proto.time = timeop

		vars = []
		for src in srcs:
			if src.time_group == DataTimeEnum.volume:
				if src.data_type == DataTypeEnum.walls:
					proto.stl_pipelines.append(StaticStlPipeline(file=src.filename))
				elif src.data_type == DataTypeEnum.body:
					proto.moving_pipelines.append(MovingBodyPipeline(file=src.filename, color_by=ColorByEnum.solid_color, solid_color=defaultMovingBodySolidColor))
				elif always_show_particles and src.data_type == DataTypeEnum.particles:
					proto.particle_pipelines.append(ParticlesPipeline(file=src.filename, color_by=ColorByEnum.solid_color, solid_color=defaultParticleSolidColor))
				elif src.data_type == DataTypeEnum.volume:
					vars = src.variables
					proto.volume_pipelines.append(VolumePipeline(file=src.filename))

		vars = vtk_meta.ReduceMinMaxVariables(vars)

		for v in vars:
			if v.name in excludedFields:
				continue
	
			if v.name in [ "Velocity (m/s)" ]:
				continue

			proto.variables.append(VTKVariable(name=v.name, 
												min=v.minimum, 
												max=v.maximum, 
												component=v.component_index, 
												discrete=False, 
												number_components=v.number_components))

		proto.standard_views = common_views

		conf.plots.append(proto)

	if do_body:

		proto = VTKPlotConfig(name="Body Plot")
		proto.video_options.enabled = timeop == TimesEnum.all
		proto.time = timeop

		vars = []
		for src in srcs:
			if src.time_group == DataTimeEnum.slice:
				if src.data_type == DataTypeEnum.walls:
					proto.stl_pipelines.append(StaticStlPipeline(file=src.filename))			
				elif src.data_type == DataTypeEnum.body:
					vars.extend(src.variables)
					proto.moving_pipelines.append(MovingBodyPipeline(file=src.filename, color_by=ColorByEnum.variable))
				elif always_show_particles and src.data_type == DataTypeEnum.particles:
					proto.particle_pipelines.append(ParticlesPipeline(file=src.filename, color_by=ColorByEnum.solid_color, solid_color=defaultParticleSolidColor))

		for v in vars:			
			proto.variables.append(VTKVariable(name=v.name, min=v.minimum, max=v.maximum, component=v.component_index, discrete=True))

		proto.standard_views = common_views

		conf.plots.append(proto)

	if do_particle:			
		proto = VTKPlotConfig(name="Particle Plot")
		proto.video_options.enabled = timeop == TimesEnum.all
		proto.time = timeop

		vars = []
		for src in srcs:
			if src.time_group == DataTimeEnum.slice:
				if src.data_type == DataTypeEnum.walls:
					proto.stl_pipelines.append(StaticStlPipeline(file=src.filename))			
				elif src.data_type == DataTypeEnum.body:				
					proto.moving_pipelines.append(MovingBodyPipeline(file=src.filename, color_by=ColorByEnum.solid_color, solid_color=defaultMovingBodySolidColor))
				elif src.data_type == DataTypeEnum.particles:
					vars.extend(src.variables)
					proto.particle_pipelines.append(ParticlesPipeline(file=src.filename, color_by=ColorByEnum.variable))

		for v in vars:			
			proto.variables.append(VTKVariable(name=v.name, min=v.minimum, max=v.maximum, component=v.component_index, discrete=True))

		proto.standard_views = common_views

		conf.plots.append(proto)

	return conf


def run():

	mpl.use("agg")
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers(dest="action")

	# JSON based definition of post processing
	fileParser = subparsers.add_parser("file")
	fileParser.add_argument("filename", default="post.json", help="use an input file to declare batch post processing output")
	
	# CLI
	autoParser = subparsers.add_parser("auto")
	autoParser.add_argument("-d", "--directory", default=".", help="case directory")	
	autoParser.add_argument("--all", action='store_true', help="process all data sources (slice,volume,particle,body)")
	autoParser.add_argument("--last-time", action='store_true', help="only process last time available in data, otherwise processes all time steps")
	autoParser.add_argument("--slice", action='store_true', help="process all slices")
	autoParser.add_argument("--volume", action='store_true', help="process the volume")
	autoParser.add_argument("--particle", action='store_true', help="process all particles")
	autoParser.add_argument("--body", action='store_true', help="process all bodies")
	autoParser.add_argument("--always-show-particles", action='store_true', help="show particles on all plots")
	autoParser.add_argument("--debug", action='store_true', help="iterate all variables in all input files, by default, less commonly used fields exluded from processing")

	# Testing
	testParser = subparsers.add_parser("test")
	testParser.add_argument("--test", action='store_true', help="reserved for internal testing")

	clargs = parser.parse_args()
	case_dir = os.getcwd()	

	if clargs.action == "test":
		conf = create_example_stat_plots_config()

		with open("post.json", 'w') as f:
			json.dump(conf.dict(), f, indent=4, sort_keys=True)	

		print(conf.dict())
		run_post(case_dir, conf)
	
	elif clargs.action == "auto":
		case_dir = os.path.abspath(clargs.directory)

		if clargs.all:
			clargs.slice = True
			clargs.volume = True
			clargs.particle = True
			clargs.body = True

		conf = CreateAllBatchConfig(clargs.directory, 
									do_slice=clargs.slice, 
									do_volume=clargs.volume, 
									do_particle=clargs.particle, 
									do_body=clargs.body, 
									always_show_particles=clargs.always_show_particles,
									last_only=clargs.last_time)
		
		run_post(case_dir, conf)

	elif clargs.action == "file":
		case_dir = os.path.dirname(os.path.abspath(clargs.filename))
		conf = BatchPostConfig.parse_file(clargs.filename)
		run_post(case_dir, conf)

	else:

		parser.print_usage()
		sys.exit(1)
		

def run_post(case_dir=".", conf: BatchPostConfig = None):

	ffmpeg_exe = "ffmpeg"

	ffmpegSearchPaths = [
		os.path.join(os.path.dirname(__file__), "../../ffmpeg.exe")
	]

	for pth in ffmpegSearchPaths:
		if os.path.isfile(pth):
			ffmpeg_exe = pth
			break

	
	input_dir = os.path.join(case_dir, "out")
	output_dir = os.path.join(input_dir, "Processed")

	os.makedirs(output_dir, exist_ok=True)

	logging.getLogger().setLevel(logging.INFO)
	
	results = ResultsProcessed()

	bounds = None
	try:
		inputxml = ET.parse(os.path.join(case_dir, "input.xml")).getroot()
		lx = float(inputxml.find("./system/domainX").text)
		ly = float(inputxml.find("./system/domainY").text)
		lz = float(inputxml.find("./system/domainZ").text)
		minDomain = tuple(map(float, inputxml.find("./system/domainOrigin").text.split()))
		bounds = (minDomain[0], minDomain[0] + lx, minDomain[1], minDomain[1] + ly, minDomain[2], minDomain[2] + lz) 
		logging.info("Found domain bounds: %s", str(bounds))
	
	except:
		logging.warn("Failed to parse input xml")
		raise

	# dump input post config to output dir
	with open(os.path.join(output_dir, "post.json"), 'w') as f:
		json.dump(conf.dict(), f, indent=4, sort_keys=True)	

	if (default_style := conf.default_stat_plot_style) is None:
		default_style = StatPlotStyle()

	if conf.stat_plots is not None:
		stat_data = { }
		px = 1/plt.rcParams['figure.dpi']  # pixel in inches

		for statPlot in conf.stat_plots:
			for s in statPlot.series:
				fn = s.filename
				if fn not in stat_data:
					final_fn = ""
					if os.path.isabs(fn):
						final_fn = fn
					elif os.path.isfile(final_fn := fn):
						pass
					elif os.path.isfile(final_fn := os.path.join(input_dir, "Stats/", fn)):
						pass							

					if os.path.isfile(final_fn):
						logging.info("Loading file: %s", fn)
						stat_data[fn] = pl.read_csv(final_fn, sep='\t')
					else:
						logging.error("Could not find file: %s", fn)
						raise ValueError()	

		for statPlot in conf.stat_plots:

			statPlotStyle = default_style.override(statPlot.style)

			mpl.style.use(statPlotStyle.style)

			fig, ax = plt.subplots(figsize=(statPlotStyle.size[0]*px,statPlotStyle.size[1]*px))

			xnames = set()
			ynames = set()
			for series in statPlot.series:
				dataframe = stat_data[series.filename]
				if (xcolname := series.x) is None:
					if series.x_column is None:
						raise ValueError("Must specify column name or index")
					else:
						xcolname = dataframe.columns[series.x_column]

				if (ycolname := series.y) is None:
					if series.y_column is None:
						raise ValueError("Must specify column name or index")
					else:
						ycolname = dataframe.columns[series.y_column]

				kwargs = dict()
				if series.line_color is not None:
					kwargs["color"] = series.line_color.ToFloatValue()
				if series.line_width is not None:
					kwargs["linewidth"] = series.line_width
				if series.line_style is not None:
					kwargs["linestyle"] = series.line_style

				xnames.add(xcolname)
				ynames.add(ycolname)
				#print(dataframe.head())
				ax.plot(dataframe.select(xcolname).to_numpy(), dataframe.select(ycolname).to_numpy(), **kwargs, label=ycolname)

			if statPlotStyle.legend_location is not None:
				fig.legend(loc=statPlotStyle.legend_location.value)
			
			if (xtitle := statPlot.x_title) is None:
				if len(xnames) == 1:
					xtitle = list(xnames)[0]
				else:
					logging.warn("Could not determine unique xtitle")

			if (ytitle := statPlot.y_title) is None:
				if len(ynames) == 1:
					ytitle = list(ynames)[0]
				else:
					logging.warn("Could not determine unique ytitle")

			if xtitle is not None:
				ax.set_xlabel(xtitle)

			if ytitle is not None:
				ax.set_ylabel(ytitle)

			if statPlot.chart_title is not None:
				ax.set_title(statPlot.chart_title)

			
			fig.tight_layout()

			img_out_dir = os.path.join(output_dir, "CustomStatPlots")
			outfn = os.path.join(img_out_dir, statPlot.name + ".png")
			os.makedirs(img_out_dir, exist_ok=True)
			fig.savefig(outfn)		

			results.custom_stat_plots.append(ResultStatImage(name=statPlot.name, config=statPlot.copy(), image_filename=outfn))

			plt.close(fig)
			del ax
			del fig

		del stat_data

	if conf.auto_stat_plots:
		stats_dir = os.path.join(input_dir, "Stats/")
		statPlotStyle = default_style
		for fn in glob.glob(os.path.join(stats_dir, "*.txt")):
			df = pl.read_csv(fn, sep='\t')
			xcolname = df.columns[0]
			for i in range(1, len(df.columns)):

				if statPlotStyle.style is not None and len(statPlotStyle.style) > 0:
					mpl.style.use(statPlotStyle.style)

				ycolname = df.columns[i]

				kwag = {}
				if statPlotStyle.size is not None:
					kwag["figsize"] = (statPlotStyle.size[0]*px,statPlotStyle.size[1]*px)

				fig, ax = plt.subplots(**kwag)
				ax.plot(df.select(xcolname).to_numpy(), df.select(ycolname).to_numpy(), label=ycolname)												
				ax.set_xlabel(xcolname)			
				ax.set_title(ycolname)
				
				fig.tight_layout()

				img_out_dir = os.path.join(output_dir, "AutoStatPlots", os.path.splitext(os.path.basename(fn))[0])
				img_fn = mstarvtk.NiceVariableName( ycolname + ".png" )
				outfn = os.path.join(img_out_dir, img_fn)
				os.makedirs(img_out_dir, exist_ok=True)
				fig.savefig(outfn)

				results.auto_stat_plots.append(ResultAutoStatImage(stat_filename=fn, name=ycolname, image_filename=outfn))

				plt.close(fig)

				del ax
				del fig

	if conf.plots is not None:

		colors = vtk.vtkNamedColors()
		outdir = os.path.join(input_dir, "Output")

		camera = vtk.vtkCamera()
		camera.SetPosition(1, 1, 1)
		camera.SetFocalPoint(0, 0, 0)
		
		# Create a single render window for all renderings
		# X window resources are not let go in timely manner, so can result in
		# "Maximum number of clients reached" error occuring in some contexts
		renderWindow = vtk.vtkRenderWindow()
		renderWindow.SetOffScreenRendering(1)		
		renderWindow.SetMultiSamples(4) # what do?

		renderWindowInteractor = vtk.vtkRenderWindowInteractor()
		renderWindowInteractor.SetRenderWindow(renderWindow)
		
		axes = vtk.vtkAxesActor()
		widget = vtk.vtkOrientationMarkerWidget()
		rgba = [0] * 4
		colors.GetColor('Carrot', rgba)
		widget.SetOutlineColor(rgba[0], rgba[1], rgba[2])
		widget.SetOrientationMarker(axes)
		widget.SetInteractor(renderWindowInteractor)
		widget.SetViewport(0.0, 0.0, 0.1, 0.1)
		widget.SetEnabled(1)	
		
		for p in conf.plots:	
			
			title = p.name		
			img_size = (p.size_x, p.size_y)			
			views = dict()		

			renderWindow.SetSize( int(img_size[0]/2), int(img_size[1]/2) ) # why /2 ? 					

			for view in p.custom_views:
				cam = vtk.vtkCamera()
				cam.SetParallelProjection(view.parallel_projection)	
				#cam.SetParallelScale(height)		
				cam.SetViewUp(view.up)
				cam.SetPosition(view.eye_position)
				cam.SetFocalPoint(view.look_at)
				views[view.name] = cam

			for view in p.standard_views:
				m = dict(x=0, y=1, z=2)
				eyeindex = view.eye_side.direction()
				eyeflip = view.eye_side.sign()
				up = view.up.direction()
				cam = mstarvtk.create_camera_tight(eyeindex, eyeflip, up, bounds)
				views[view.name] = cam

			for variable in p.variables:
				
				colorTranFunc = mstarvtk.CreateColorTransferFunction(variable.min, variable.max, variable.color_scale, 256, variable.discrete, variable.discrete_n)

				# if variable.number_components > 1 and variable.component >= 0:					
				# 	colorTranFunc.SetVectorModeToComponent()
				# 	colorTranFunc.SetVectorComponent(variable.component)
				# else:
				# 	colorTranFunc.SetVectorModeToComponent()
				# 	colorTranFunc.SetVectorComponent(0)

				pilFontSize = 18
				scalar_bar_img_2 = mstarvtk.draw_color_bar(colorTranFunc, opacityFunc=None, size=(76, img_size[1]), min=variable.min, max=variable.max, fontsize=pilFontSize)

				# Render the frames directly into a video file
				img_index = 0
				
				data_times_pairs = get_plot_times(outdir, p)
				data_times = []
				for pvdname,times in data_times_pairs:
					data_times = times
					break

				plot_times = []

				if p.time == TimesEnum.all:
					plot_times = data_times
				elif  p.time == TimesEnum.last:	
					plot_times = [ data_times[-1] ]		
				else:
					raise ValueError("Time selection option not supported: " + p.time_option)

				# dictionary of tuples
				# key: view name
				# value: (filename pattern)
				videos = dict()

				video_rate = 1.0

				if len(plot_times) >= 2:
					video_rate = 1.0 / (plot_times[1] - plot_times[0])
				
				video_rate *= p.video_options.speed

				for t in plot_times:

					logging.info("Processing: %s - %s - t=%g" % (p.name, variable.name, t) )

					renderer = vtk.vtkRenderer()
					renderer.SetBackground(RgbValToFloat(p.background_color))
					renderer.SetActiveCamera(camera)
					renderWindow.AddRenderer(renderer)
					
					for pipe in p.block_pipelines:
						readerFn = get_file_path(outdir, pipe.file)
						o = mstarvtk.BlockDataPipeline(readerFn, t, False, colorTranFunc)
						o.mapper.SelectColorArray(variable.name)			
						renderer.AddActor(o.actor)
					
					for pipe in p.moving_pipelines:
						readerFn = get_file_path(outdir, pipe.file)
						o = mstarvtk.MovingBodyPipeline(readerFn, t)
						if pipe.color_by == ColorByEnum.solid_color and pipe.solid_color is not None:
							o.SetSolidColor(pipe.solid_color.ToFloatValue())
						elif pipe.color_by == ColorByEnum.variable:
							o.SetVariableColor(variableName=variable.name, ctf=colorTranFunc)
						renderer.AddActor(o.actor)
					
					for pipe in p.stl_pipelines:			
						readerFn = get_file_path(outdir, pipe.file)
						o = mstarvtk.StaticStlPipeline(readerFn)
						renderer.AddActor(o.actor)

					
					for pipe in p.particle_pipelines:			
						readerFn = get_file_path(outdir, pipe.file)						

						src = vtk_meta.GetPvdDataSource(readerFn, True, False)
						isSuperQuadric = False
						for var in  src.variables:
							if var.name == "Superquadric Shape":
								isSuperQuadric = True
								break
						
						if isSuperQuadric:
							shapesFn = os.path.join(os.path.dirname(readerFn), "ParticleShapes_{0}.txt".format(src.name))

							o = mstarvtk.ParticlesSuperQuadricPipeline(readerFn, shapesFn, t)

							if pipe.color_by == ColorByEnum.solid_color and pipe.solid_color is not None:
								o.SetSolidColor(pipe.solid_color.ToFloatValue())
							elif pipe.color_by == ColorByEnum.variable:
								o.SetVariableColor(variableName=variable.name, ctf=colorTranFunc)
							
							o.AddActors(renderer)
						
						else:

							o = mstarvtk.ParticlesPointGaussianPipeline(readerFn, t)
							if pipe.color_by == ColorByEnum.solid_color and pipe.solid_color is not None:
								o.SetSolidColor(pipe.solid_color.ToFloatValue())
							elif pipe.color_by == ColorByEnum.variable:
								o.SetVariableColor(variableName=variable.name, ctf=colorTranFunc)
							renderer.AddActor(o.actor)

					for pipe in p.volume_pipelines:			
						readerFn = get_file_path(outdir, pipe.file)
						opacityFunc = CreateOpacityFunction(pipe.opacity_function, variable)
						o = mstarvtk.VolumeRenderingPipeline(readerFn, t, colorTranFunc, opacityFunc)
						o.mapper.SetScalarModeToUsePointFieldData()
						o.mapper.SelectScalarArray(variable.name)

						if variable.number_components > 1 and variable.component >= 0:					
							o.mapper.SetVectorMode(1)
							o.mapper.SetVectorComponent(variable.component)													

						renderer.AddActor(o.actor)											
						
					

					if p.image_output:

						for viewname,viewcam in views.items():

							renderer.SetActiveCamera(viewcam)
							renderWindow.Render()					

							windowto_image_filter = vtk.vtkWindowToImageFilter()
							windowto_image_filter.SetInput(renderWindow)
							windowto_image_filter.SetScale(2)

							writer = vtk.vtkPNGWriter()
							writer.SetInputConnection(windowto_image_filter.GetOutputPort())
							writer.WriteToMemoryOn()
							writer.Write()

							buf = io.BytesIO()
							buf.write(writer.GetResult())
							buf.seek(0)

							# Read data into PIL image buffer
							vtk_img = Image.open(buf)
							
							w = vtk_img.size[0]
							h = vtk_img.size[1]
							
							total_w = w + scalar_bar_img_2.size[0]
							total_h = h + 20

							# Stack VTK image with scalar bar and annotation in a new image		
							com_img = Image.new("RGBA", size=(total_w, total_h), color=(255,255,255))
							com_img.paste(vtk_img, (0,0) )
							com_img.alpha_composite(scalar_bar_img_2.copy(), dest=(w,0))

							for mark in p.watermarks:
								
								imgfn = mark.image
								if os.path.isfile(imgfn):
									
									watermarkImg = Image.open(imgfn).convert("RGBA")
									marksize = watermarkImg.size							

									desty = 0
									destx = 0
									if mark.location[0] == "t":
										desty = 0
									elif mark.location[0] == "m":
										desty = total_h * 0.5 - 0.5 * marksize[1]
									elif mark.location[0] == "b":
										desty = total_h - marksize[1]

									if mark.location[1] == "l":
										destx = 0
									elif mark.location[1] == "m":
										destx = total_w * 0.5 - 0.5 * marksize[0]
									elif mark.location[1] == "r":
										destx = total_w - marksize[0]
									
									blanklayer = Image.new('RGBA', com_img.size, (0, 0, 0, 0))
									marklayer = blanklayer.copy()
									marklayer.paste(watermarkImg, (int(destx), int(desty)))
									watermark2 = Image.blend(blanklayer, marklayer, mark.alpha)							
									com_img.alpha_composite(watermark2)

									
							font = mstarvtk.GetFontFamily(size=pilFontSize)
							dr = ImageDraw.Draw(com_img)					
							
							dr.text( (0,h), title , anchor='la', font=font, fill="black" )
							dr.text( (total_w/2,h), variable.name , anchor='ma', font=font, fill="black" )
							dr.text( (total_w,h), "t = {0}".format(t) , anchor='ra', font=font , fill="black")
							
							var_name,varunits = mstarvtk.SplitVtkVarName(variable.name)
							varCompDisp = variable.get_component_name()
							fn_prefix = p.name + "_" + var_name
							if len(varCompDisp) > 0:
								fn_prefix += "_" + varCompDisp
							fn_prefix += "_" + viewname

							video_img_fn_fmt = fn_prefix + "_%0" + str(len(str(len(plot_times)))) + "d.png"
							video_img_fn_fmt = video_img_fn_fmt.format(name=var_name, view_name=viewname)

							imageFramesOutDir = os.path.join(output_dir, fn_prefix)

							fn = video_img_fn_fmt % img_index
							fn = os.path.join(imageFramesOutDir, fn)		

							videos[viewname] = ( video_img_fn_fmt, fn_prefix, imageFramesOutDir )

							os.makedirs(imageFramesOutDir, exist_ok=True)

							logging.debug("Saving view: %s", fn)
							com_img.save(fn)

							results.vtk_images.append(ResultVtkImage(time=t, image_filename=fn, config=p, view=viewname))

						img_index += 1
					
					renderWindow.RemoveRenderer(renderer)
					del renderer
					
				if p.video_options.enabled:

					for viewname,videoTup in videos.items():

						img_pattern, fn_prefix, out_dir = videoTup
						outmp4 = os.path.join(output_dir, fn_prefix + ".mp4")
						cmd = [ffmpeg_exe, 
										"-r", str(video_rate), 
										"-i", img_pattern, 
										"-vcodec", "libx264", 
										"-crf", str(p.video_options.quality),
										"-pix_fmt", "yuv420p", 
										"-y",
										outmp4]

						logging.debug("Running command: %s", " ".join(cmd))
						subprocess.run(cmd, cwd=out_dir)


	if conf.auto_pdf_report:
		from mstarpypost.reports import create_auto_report
		reportConf = AutoReportConfig(title="M-Star CFD Report", results=results)

		modelxmlfn = os.path.join(case_dir, "report.xml")
		if os.path.isfile(modelxmlfn):
			reportConf.model_tree_filename = modelxmlfn
					
		create_auto_report(reportConf, outputfn=os.path.join(output_dir, "Report.pdf"))


	with open(os.path.join(output_dir, "results.json"), 'w') as f:
		json.dump(results.dict(), f, indent=4, sort_keys=True)

if __name__ == "__main__":

	run()