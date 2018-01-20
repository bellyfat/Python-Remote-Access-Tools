import gtk
import os
w = gtk.gdk.get_default_root_window()
sz = w.get_size()
pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, sz[0], sz[1])
pb = pb.get_from_drawable(w, w.get_colormap(), 0, 0, 0, 0, sz[0], sz[1])

pb.save("1.png", "png")
with open("1.png") as f :
    print f.read()
os.remove("1.png")
