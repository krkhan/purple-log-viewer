#!/usr/bin/env python

import os

from gi.repository import Gtk, WebKit

class PurpleLogViewerApp(object):
  LOGSDIR = '~/.purple/logs'
  def __init__(self):
    self.db = {}

    self._scan_logsdir()
    self._load_ui()
    self._fill_models()
    self._connect_models()
    self._connect_signals()
    self._show()

  def _scan_logsdir(self):
    for root, dirs, files in os.walk(os.path.expanduser(self.LOGSDIR)):
      for filename in files:
        dirnames = root.split('/')
        protocol, account, buddy = dirnames[dirnames.index('logs') + 1:]

        if not self.db.has_key(buddy):
          self.db[buddy] = {}
        if not self.db[buddy].has_key(protocol):
          self.db[buddy][protocol] = []

        title, _ = os.path.splitext(filename)
        filepath = os.path.join(root, filename)
        entry = (title, filepath)
        self.db[buddy][protocol].append(entry)

  def _filter_visible(self, treestore, treeiter, data):
    entry = self.builder.get_object('entry_main')
    text = entry.get_text()

    if text == '':
      return True

    rootiter = treestore.get_iter(str(treestore.get_path(treeiter)).split(':')[0])

    if text in treestore.get_value(rootiter, 0):
      return True

    return False

  def _load_ui(self):
    self.builder = Gtk.Builder()
    self.builder.add_from_file('ui.xml')

    treeview = self.builder.get_object('treeview_main')
    treestore = self.builder.get_object('treestore_main')
    self._treefilter = treestore.filter_new()
    self._treefilter.set_visible_func(self._filter_visible, None)
    treeview.set_model(self._treefilter)

    scrolledwindow = self.builder.get_object('scrolledwindow_view')
    self._view = WebKit.WebView()
    scrolledwindow.add(self._view)

  def _treeview_row_activated(self, treeview, path, column):
    treestore = self.builder.get_object('treestore_main')
    treepath = self._treefilter.convert_path_to_child_path(path)
    treeiter = treestore.get_iter(treepath)
    filepath = treestore.get_value(treeiter, 1)
    self._view.open('file://' + filepath)

  def _fill_models(self):
    treestore = self.builder.get_object('treestore_main')
    for buddy, protocols in self.db.iteritems():
        buddyiter = treestore.append(None, (buddy, None))
        for protocol in protocols:
          protocoliter = treestore.append(buddyiter, (protocol, None))
          for filetitle, filepath in self.db[buddy][protocol]:
            treestore.append(protocoliter, (filetitle, filepath))
    treestore.set_sort_column_id(0, Gtk.SortType.ASCENDING)

  def _connect_models(self):
    treeview = self.builder.get_object('treeview_main')
    cell = Gtk.CellRendererText()
    col = Gtk.TreeViewColumn("Title", cell, text=0)
    treeview.append_column(col)

  def _connect_signals(self):
    window = self.builder.get_object('main_window')
    window.connect('destroy', lambda w: Gtk.main_quit())

    entry = self.builder.get_object('entry_main')
    entry.connect('changed', lambda w: self._treefilter.refilter())

    treeview = self.builder.get_object('treeview_main')
    treeview.connect('row-activated', self._treeview_row_activated)

  def _show(self):
    window = self.builder.get_object('main_window')
    window.show_all()

  def run(self):
    Gtk.main()

if __name__ == '__main__':
  app = PurpleLogViewerApp()
  app.run()

