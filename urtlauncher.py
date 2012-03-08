#!/usr/bin/python
#A simple Urban Terror (or other ioquake-based) game launcher
#This program is licensed by GNU General Public License version 2.

import pygtk
pygtk.require('2.0')
import gtk
import os
import sqlite3

class UrtLauncher:
    def excheck(self): #check for existence of database file and read config from it
        if os.path.isfile('launcher.sqlite'):
            self.conn = sqlite3.connect('launcher.sqlite')
            self.c = self.conn.cursor()
            self.c.execute("select * from config")
            for self.raw in self.c:
                self.path = self.raw[0]
                self.name = self.raw[1]
            self.fentry.set_text(self.path)
            self.nentry.set_text(self.name)
        else:
            self.conn = sqlite3.connect('launcher.sqlite')
            self.c = self.conn.cursor()
            self.c.execute("create table config (path text, name text, showfull bool, showempty bool)")
            self.path = ''
            self.name = ''
            self.c.execute("insert into config values ('', '')")
            self.c.execute("create table servers (name text, addr text, port text, pass text, rcon text)")

    def filechooser(self, widget): #run a executable chooser dialog
        self.dialog = gtk.FileChooserDialog("Choose your Urban Terror Executable", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        self.dialog.set_default_response(gtk.RESPONSE_OK)
        self.filter = gtk.FileFilter()
        self.filter.set_name("Executables")
        self.filter.add_pattern("*.exe")
        self.filter.add_pattern("*.i386")
        self.filter.add_pattern("*.x86_64")
        self.dialog.add_filter(self.filter)
        self.response = self.dialog.run()
        if self.response == gtk.RESPONSE_OK:
            self.fentry.set_text(self.dialog.get_filename())
            self.dialog.destroy()
        elif self.response == gtk.RESPONSE_CANCEL:
            self.dialog.destroy()

    def quit(self, widget, data=None):
        #save name and path in database
        self.query = "update config set path = '%s', name = '%s'" % (self.fentry.get_text(), self.nentry.get_text())
        self.c.execute(self.query)
        self.conn.commit()
        self.c.close()
        gtk.main_quit()

    def favload(self, *widget):
        self.liststore.clear()
        self.c.execute("select * from servers")
        for self.raw in self.c:
            self.liststore.append([self.raw[0], self.raw[1], self.raw[2], self.raw[3], self.raw[4]])

    def connect(self, widget): #connect to a server
        self.treeselection = self.treeview.get_selection() #get selection from the favorites list
        (self.model, self.iter) = self.treeselection.get_selected()
        if self.iter != None:
            self.servname = self.model.get_value(self.iter, 0)
            self.servaddress = self.model.get_value(self.iter, 1)
            self.servport = self.model.get_value(self.iter, 2)
            self.servpass = self.model.get_value(self.iter, 3)
            self.servrcon = self.model.get_value(self.iter, 4)
        self.filename = self.fentry.get_text()
        self.pname = self.nentry.get_text()
        self.runstring = "%s +connect %s:%s +password %s +rconpassword %s +name %s &" % (self.filename, self.servaddress, self.servport, self.servpass, self.servrcon, self.pname)
        os.system(self.runstring)
        self.quit(None)
        
    def rundialog(self, widget, edit=False):
        self.dialog = gtk.Dialog("Add/Edit server")
        self.dialog.set_resizable(False)
        self.dialog.set_border_width(5)
        self.dialog.connect("delete_event", lambda la, lb: self.dialog.destroy())
        self.dialog.table = gtk.Table()
        self.dialog.vbox.pack_start(self.dialog.table, False, False, 0)
        self.dialog.cnt = 0
        self.dialog.entry = [gtk.Entry(), gtk.Entry(), gtk.Entry(), gtk.Entry(), gtk.Entry()]
        for self.dialog.iter in ["Server name: ", "Server address: ", "Server port: ", "Server pass: ", "Rcon pass: "]:
            self.dialog.label = gtk.Label("%s" % self.dialog.iter)
            self.dialog.table.attach(self.dialog.label, 0, 1, self.dialog.cnt, self.dialog.cnt + 1)
            self.dialog.table.attach(self.dialog.entry[self.dialog.cnt], 1, 2, self.dialog.cnt, self.dialog.cnt + 1)
            if edit == True: #show selected item if we clicked Edit
                self.treeselection = self.treeview.get_selection() #get selection from the favorites list
                (self.model, self.iter) = self.treeselection.get_selected()
                if self.iter == None: return #do not show the dialog if we didn't choose an item and clicked Edit
                else:
                    self.dialog.entrytext = self.model.get_value(self.iter, self.dialog.cnt)
                    if self.dialog.entrytext != None: self.dialog.entry[self.dialog.cnt].set_text(self.dialog.entrytext)
            self.dialog.cnt = self.dialog.cnt + 1
        if edit == True: name = self.dialog.entry[0].get_text()
        else: name = False
        self.dialog.bbox = gtk.HButtonBox()
        self.dialog.vbox.pack_start(self.dialog.bbox, False, False, 0)
        self.dialog.button = gtk.Button("OK")
        self.dialog.button.connect("clicked", self.manage_item, name, edit)
        self.dialog.bbox.pack_start(self.dialog.button, False, False, 0)
        self.dialog.button = gtk.Button("Cancel")
        self.dialog.bbox.pack_start(self.dialog.button, False, False, 0)
        self.dialog.button.connect("clicked", lambda la: self.dialog.destroy())
        self.dialog.show_all()
        self.dialog.run()

    def manage_item(self, widget, name, edit=False): #add or edit items in the database
        self.nname = self.dialog.entry[0].get_text()
        self.naddr = self.dialog.entry[1].get_text()
        self.nport = self.dialog.entry[2].get_text()
        self.npass = self.dialog.entry[3].get_text()
        self.nrcon = self.dialog.entry[4].get_text()
        if edit == True: self.query = "update servers set name = '%s', addr = '%s', port = '%s', pass = '%s', rcon = '%s' where name = '%s'" % (self.nname, self.naddr, self.nport, self.npass, self.nrcon, name)
        else: self.query = "insert into servers values ('%s', '%s', '%s', '%s', '%s')" % (self.nname, self.naddr, self.nport, self.npass, self.nrcon)
        self.c.execute(self.query)
        self.favload()
        self.dialog.destroy()

    def deldialog(self, widget):
        self.ddialog = gtk.Dialog("Delete?")
        self.ddialog.set_resizable(False)
        self.ddialog.connect("delete_event", lambda la, lw: self.ddialog.destroy())
        self.treeselection = self.treeview.get_selection() #get selection from the favorites list
        (self.model, self.iter) = self.treeselection.get_selected()
        if self.iter != None:
            self.name = self.model.get_value(self.iter, 0)
            self.ddialog.label = gtk.Label("Are you sure you want to delete server %s?" % self.name)
            self.ddialog.vbox.pack_start(self.ddialog.label, False, False, 0)
            self.ddialog.bbox = gtk.HButtonBox()
            self.ddialog.vbox.pack_start(self.ddialog.bbox, False, False, 0)
            self.ddialog.button = gtk.Button("Yes")
            self.ddialog.button.connect("clicked", self.delete_item, self.name)
            self.ddialog.bbox.pack_start(self.ddialog.button, False, False, 0)
            self.ddialog.button = gtk.Button("No")
            self.ddialog.button.connect("clicked", lambda la: self.ddialog.destroy())
            self.ddialog.bbox.pack_start(self.ddialog.button, False, False, 0)
            self.ddialog.show_all()
            self.ddialog.run()

    def broptdialog(self, widget):
        self.brdialog = gtk.Dialog("Browser Options")
        self.brdialog.set_border_width(5)
        self.brdialog.connect("delete_event", lambda la, lb: self.brdialog.destroy())
        self.brdialog.set_resizable(False)
        self.brdialog.fcheck = gtk.CheckButton("Show full servers")
        self.brdialog.echeck = gtk.CheckButton("Show empty servers")
        self.c.execute("select showfull, showempty from config")
        for res in self.c:
            self.brdialog.fcheck.set_active(bool(res[0]))
            self.brdialog.echeck.set_active(bool(res[1]))
        self.brdialog.fcheck.connect("toggled", lambda la: self.c.execute(("update config set showfull = %s") % int(self.brdialog.fcheck.get_active())))
        self.brdialog.vbox.add(self.brdialog.fcheck)
        self.brdialog.echeck.connect("toggled", lambda la: self.c.execute(("update config set showempty = %s") % int(self.brdialog.echeck.get_active())))
        self.brdialog.vbox.add(self.brdialog.echeck)
        self.brdialog.button = gtk.Button("Close")
        self.brdialog.button.connect("clicked", lambda la: self.brdialog.destroy())
        self.brdialog.vbox.add(self.brdialog.button)
        self.brdialog.show_all()
        self.brdialog.run()

    def browser(self, widget, data=None):
        self.statusbar.push(0, "Fetching server list...")
        self.c.execute("select showfull, showempty from config")
        for res in self.c:
            self.fullflag = bool(res[0])
            self.emptyflag = bool(res[1])
        

    def delete_item(self, widget, name):
        self.query = "delete from servers where name = '%s'" % name
        self.c.execute(self.query)
        self.favload()
        self.ddialog.destroy()

    def simplylaunch(self, widget):
        self.filename = self.fentry.get_text()
        self.runstring = "%s &" % self.filename
        os.system(self.runstring)
        self.quit(None)

    def __init__(self):
        self.window = gtk.Window()
        self.window.set_resizable(False)
        self.window.show()
        self.window.set_border_width(5)
        self.window.connect("delete_event", self.quit)
        self.window.set_title("pyUrTLauncher")
        self.vbox = gtk.VBox()
        self.window.add(self.vbox)
        self.vbox.show()
        self.table = gtk.Table(3, 2, False)
        self.vbox.pack_start(self.table, False, False, 0)
        self.table.show()
        self.label = gtk.Label("Path to Urban Terror executable: ")
        self.table.attach(self.label, 0, 1, 0, 1)
        self.label.show()
        self.fentry = gtk.Entry()
        self.fentry.set_max_length(50)
        self.table.attach(self.fentry, 1, 2, 0, 1)
        self.fentry.show()
        self.button = gtk.Button("Browse...")
        self.button.connect("clicked", self.filechooser)
        self.table.attach(self.button, 2, 3, 0, 1)
        self.button.show()
        self.label = gtk.Label("Your name: ")
        self.table.attach(self.label, 0, 1, 1, 2)
        self.label.show()
        self.nentry = gtk.Entry()
        self.nentry.set_max_length(50)
        self.table.attach(self.nentry, 1, 2, 1, 2)
        self.nentry.show()
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.vbox.pack_start(self.notebook, False, False, 0)
        self.notebook.show()
        self.fixed = gtk.Fixed()
        self.label = gtk.Label("Favorites")
        self.notebook.append_page(self.fixed, self.label)
        self.fixed.show()
        self.excheck()
        #create a list with servers
        self.scaleadj = gtk.Adjustment(0, 0, 100, 100, 100, 200)
        self.scrolled = gtk.ScrolledWindow()
        self.scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.scrolled.set_size_request(400, 200)
        self.fixed.put(self.scrolled, 0, 0)
        self.scrolled.show()
        self.liststore = gtk.ListStore(str, str, str, str, str)
        self.treeview = gtk.TreeView(self.liststore)
        self.x = 0
        #add a number of columns in list
        for self.iter in ["Name", "Address", "Port", "Password", "Rcon"]:
            self.column = gtk.TreeViewColumn("%s" % self.iter)
            self.treeview.append_column(self.column)
            self.cell = gtk.CellRendererText()
            self.column.pack_start(self.cell, True)
            self.column.add_attribute(self.cell, 'text', self.x)
            self.treeview.set_search_column(self.x)
            self.column.set_sort_column_id(self.x)
            self.x = self.x + 1
        self.scrolled.add_with_viewport(self.treeview)
        self.treeview.show()
        self.buttonbox = gtk.VButtonBox()
        self.fixed.put(self.buttonbox, 420, 0)
        self.buttonbox.show()
        self.button = gtk.Button("Add...")
        self.button.connect("clicked", self.rundialog)
        self.buttonbox.add(self.button)
        self.button.show()
        self.button = gtk.Button("Edit...")
        self.button.connect("clicked", self.rundialog, True)
        self.buttonbox.add(self.button)
        self.button.show()
        self.button = gtk.Button("Delete")
        self.button.connect("clicked", self.deldialog)
        self.buttonbox.add(self.button)
        self.button.show()
        self.buttonbox = gtk.HButtonBox()
        self.vbox.pack_start(self.buttonbox, False, False, 1)
        self.buttonbox.show()
        self.button = gtk.Button("Connect!")
        self.button.connect("clicked", self.connect)
        self.buttonbox.add(self.button)
        self.button.show()
        self.button = gtk.Button("Launch w/o connection")
        self.button.connect("clicked", self.simplylaunch)
        self.buttonbox.add(self.button)
        self.button.show()
        self.button = gtk.Button("Quit")
        self.button.connect("clicked", self.quit)
        self.buttonbox.add(self.button)
        self.button.show()
        self.favload()
        self.ablabel = gtk.Label("Made by Boten (http://boten.blindage.org)")
        self.vbox.pack_start(self.ablabel, False, False, 0)
        self.ablabel.show()
        self.statusbar = gtk.Statusbar()
        self.vbox.pack_start(self.statusbar, False, False, 0)
        self.statusbar.show()
        self.statusbar.push(0, "Welcome!")
        self.label = gtk.Label("Browser")
        self.fixed = gtk.Fixed()
        self.notebook.append_page(self.fixed, self.label)
        self.label.show()
        self.fixed.show()
        if os.system("which quakestat > /dev/null") == 0:
            #self.bscaleadj = gtk.Adjustment(0, 0, 100, 100, 100, 200)
            self.bscrolled = gtk.ScrolledWindow()
            self.bscrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
            self.bscrolled.set_size_request(400, 200)
            self.fixed.put(self.bscrolled, 0, 0)
            self.bscrolled.show()
            self.bliststore = gtk.ListStore(str, str, str, str, str)
            self.btreeview = gtk.TreeView(self.bliststore)
            self.x = 0
            #add a number of columns in list
            for self.iter in ["Name", "Map", "Players", "Ping", "Type"]:
                self.bcolumn = gtk.TreeViewColumn("%s" % self.iter)
                self.btreeview.append_column(self.bcolumn)
                self.bcell = gtk.CellRendererText()
                self.bcolumn.pack_start(self.bcell, True)
                self.bcolumn.add_attribute(self.bcell, 'text', self.x)
                self.btreeview.set_search_column(self.x)
                self.bcolumn.set_sort_column_id(self.x)
                self.x = self.x + 1
            self.bscrolled.add_with_viewport(self.btreeview)
            self.btreeview.show()
            self.buttonbox = gtk.VButtonBox()
            self.fixed.put(self.buttonbox, 400, 0)
            self.buttonbox.show()
            self.refreshbutton = gtk.Button("Refresh")
            self.buttonbox.pack_start(self.refreshbutton, False, False, 0)
            self.refreshbutton.show()
            self.stopbutton = gtk.Button("Stop")
            self.buttonbox.pack_start(self.stopbutton, False, False, 0)
            self.stopbutton.set_sensitive(False)
            self.stopbutton.show()
            self.button = gtk.Button("Info...")
            self.buttonbox.pack_start(self.button, False, False, 0)
            self.button.show()
            self.button = gtk.Button("Add to Favs...")
            self.buttonbox.pack_start(self.button, False, False, 0)
            self.button.show()
            self.button = gtk.Button("Options...")
            self.buttonbox.pack_start(self.button, False, False, 0)
            self.button.connect("clicked", self.broptdialog)
            self.button.show()
        else:
            self.label = gtk.Label("quakestat binary was not found in your system.\nPlease install package q3stat in your distribution.")
            self.fixed.put(self.label, 100, 50)
            self.label.show()
unit = UrtLauncher()
if __name__ == '__main__':
    gtk.main()
