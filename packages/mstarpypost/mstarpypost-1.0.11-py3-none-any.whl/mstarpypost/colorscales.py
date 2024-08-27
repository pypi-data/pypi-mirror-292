
#import vtk
import numpy as np
from matplotlib import cm
import matplotlib as mpl

def RgbToFloat(rgb):
	return max(0.0, min(1.0, rgb / 255.0))

class ColorScale:
	def __init__(self, name="", category="", rgbdata=None):
		self.name = name
		self.category = category
		self.data = rgbdata
	
	def GetColor(self, x):
		return np.array([np.interp(x, self.data[:,0], self.data[:,1]),
						np.interp(x, self.data[:,0], self.data[:,2]),
						np.interp(x, self.data[:,0], self.data[:,3])])
	
	def GetColorUInt(self, x):
		rgb = self.GetColor(x) * 255
		return tuple(map(int, rgb))

allMplColors = [
	('Perceptually Uniform Sequential', ['viridis', 'plasma', 'inferno', 'magma', 'cividis']),
	('Sequential',
                     ['Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                      'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                      'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']),
	('Sequential (2)',
                     ['binary', 'gist_yarg', 'gist_gray', 'gray', 'bone',
                      'pink', 'spring', 'summer', 'autumn', 'winter', 'cool',
                      'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper']),
	('Diverging',
                     ['PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu',
                      'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']),
	('Miscellaneous',
                     ['gnuplot', 'gnuplot2', 'CMRmap',
                      'cubehelix', 'brg', 'gist_rainbow', 'rainbow', 'jet',
                      'turbo' ]),
]

def GetAllColorScales(minlimit=0, maxlimit=1, ncolors=256):

	for category, colorScaleNames in allMplColors:
		for colorScaleName in colorScaleNames:
			
			#ctf = vtk.vtkColorTransferFunction()								
			norm = mpl.colors.Normalize(minlimit, maxlimit)		
			c = cm.get_cmap(colorScaleName, ncolors)
			rgbdata = np.zeros((ncolors,4))
			rgbdata[:,0] = np.linspace(minlimit, maxlimit, ncolors)
			for i in range(ncolors):
				r,g,b,a = c(norm(rgbdata[i,0]))
				rgbdata[i,1] = r
				rgbdata[i,2] = g
				rgbdata[i,3] = b

			yield ColorScale(name=colorScaleName, category=category, rgbdata=rgbdata)

			

