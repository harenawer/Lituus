#!/usr/bin/python

import math

import matplotlib
matplotlib.use('GTK')

from matplotlib.figure import Figure
from matplotlib.axes import Subplot
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
from matplotlib.widgets import SpanSelector
import matplotlib.cm as cm

import pygtk
pygtk.require("2.0")
import gtk

import pyfits
import numpy

def cuts_minmax(array):
    return array.min(), array.max()

def linearwrapper(cuts):
    def wrap(x):
        return (x - cuts[0]) / (cuts[1] - cuts[0])
    return wrap

def logwrapper(cuts):
    def wrap(x):
        return numpy.log(1+ x - cuts[0]) / math.log(1 + cuts[1] - cuts[0])
    return wrap

def image_scale(array, cuts, how):
    
    y = numpy.piecewise(array, [array < cuts[0], array > cuts[1]],
                           [0, 1, how])

    return y.astype('float32')

def linear_scale(array, cuts):
    how = linearwrapper(cuts)
    return image_scale(array, cuts, how)

def log_scale(array, cuts):
    how = logwrapper(cuts)
    return image_scale(array, cuts, how)

class PlotArea(FigureCanvas):
  def __init__(self):
      # Adding the plot canvas
      self.figure = Figure(figsize=(8,6), dpi=72)
      #subplots_adjust(top=0.8,bottom=0.05,left=0.01,right=0.99)
      self.axis = self.figure.add_subplot(111) 
      # Hide axis
      self.axis.set_axis_off()
      array = numpy.ones((100, 100))
      array[0,0] = 0
      self.im = self.axis.imshow(array, cmap=cm.gray)
      self.im.set_array(array)
      super(PlotArea, self).__init__(self.figure)

class LituusApp(object):       
  def __init__(self):
      builder = gtk.Builder()
      builder.add_from_file("lituus.glade")
      self.window = builder.get_object("window")
      self.about_dialog = builder.get_object("aboutdialog")

      signals = { "on_window_destroy" : gtk.main_quit,
                  "on_quitmenuitem_activate" : gtk.main_quit,
                  "on_aboutmenuitem_activate" : lambda x : self.about_dialog.show(),
                  "on_aboutdialog_response" : lambda x,y : self.about_dialog.hide(),
                  "on_aboutdialog_destroy" : lambda  x : self.about_dialog.hide(),
                  "on_aboutdialog_delete_event" : self.delete_event,
                  "open_fits" : self.open_fits,
                }
      # Adding the plot canvas
      self.canvas = PlotArea()
      self.canvas.show()
      self.canvas.set_size_request(600, 400)
      self.vp = builder.get_object("viewport")
      self.vp.add(self.canvas)
      self.window.show()
      builder.connect_signals(signals)

  def delete_event(self, widget, event, data=None):
       print 'delete event', data
       return True
 
  def open_fits(self, widget, data=None):
	dialog = gtk.FileChooserDialog(title=None,
                 action=gtk.FILE_CHOOSER_ACTION_OPEN,
                 buttons=(gtk.STOCK_CANCEL,
                          gtk.RESPONSE_CANCEL,
                          gtk.STOCK_OPEN,
                          gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

	filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)

	filter = gtk.FileFilter()
   	filter.set_name("Fits images")
        filter.add_mime_type("image/fits")
        filter.add_mime_type("image/x-fits")
        filter.add_mime_type("application/fits")
        filter.add_pattern("*.fits")
        filter.add_pattern("*.fit")
        dialog.add_filter(filter)

	filename = ''

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
           filename = dialog.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
           pass
        dialog.destroy()

	if filename:
	    array = pyfits.getdata(filename)
            cuts = cuts_minmax(array)
            d = linear_scale(array.astype('float32'), cuts)
            self.canvas.im.set_array(d[200:300, 200:300])
	    self.canvas.draw()


if __name__ == "__main__":
  app = LituusApp()
  gtk.main()

