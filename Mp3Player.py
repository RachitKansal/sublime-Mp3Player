""" ==========================================================
File:        Mp3Player.py
Description: An easy to use mp3 player for Sublime Text 3.
License:     BSD, see LICENSE for more details.
Author:   	 Rachit Kansal
E-mail: 	 rachitkansalgithub@gmail.com
==========================================================="""

__version__ = '1.0.0'

import sublime, sublime_plugin
import threading
import platform
import time
import csv
import os
from .vlc import Instance

instance = Instance()
player = instance.media_player_new()
player.index = 0
player.path_list = []
player.titles_list = []
player.media_list_mod = []
threads = []
if platform.system() == 'Linux':
	dir_path = os.path.join(os.path.expanduser('~'), '.config/sublime-text-3/Packages/Mp3Player/Titles')
elif platform.system() == 'Windows':
	dir_path = os.path.expanduser('~') + '\AppData\Roaming\Sublime Text 3\Packages\Mp3Player\Titles'
else:
	sublime.status_message('Invalid Operating System')

def reload_lists():
	player.path_list = []
	player.titles_list = []
	player.media_list_mod = []
	RefreshList().refresh()

class RefreshList:
	def refresh(self):
		for file in os.listdir(dir_path):
			flag = 1
			if file.endswith('.mp3'):
				for title in player.titles_list:
					if file == title:
						flag = 0
						break
				if flag == 1:
					player.titles_list.append(file)
					dummy = dir_path + '/' + file
					player.path_list.append(dummy)
					player.media_list_mod.append(instance.media_new(dummy))
		readfile = open(dir_path + '/folder_path.csv', 'r')
		readfile_reader = csv.reader(readfile)
		for row in readfile_reader:
			for file in os.listdir(row[0]):
				flag = 1
				if file.endswith('.mp3'):
					for title in player.titles_list:
						if file == title:
							flag = 0
							break
					if flag == 1:
						player.titles_list.append(file)
						dummy = row[0] + '/' + file
						player.path_list.append(dummy)
						player.media_list_mod.append(instance.media_new(dummy))
		readfile.close()

class ReloadrefreshCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		reload_lists()

RefreshList().refresh()

class playerThread(threading.Thread):
	def __init__(self, threadID):
		threading.Thread.__init__(self)
		self.threadID = threadID
	def run(self):
		if(os.path.exists(player.path_list[player.index]) == False):
			reload_lists()
		player.set_media(player.media_list_mod[player.index])
		sublime.status_message(player.titles_list[player.index])
		player.play()

class Mp3PlayerCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if player.is_playing():
			player.stop()
			sublime.status_message('Player stopped')
		else:
			player_thread = playerThread(1)
			player.index = 0
			player_thread.start()

class PauseCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		player.pause()
		if player.is_playing():
			sublime.status_message('Paused')
		else:
			sublime.status_message(player.titles_list[player.index])

class PreviousCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if(player.index == 0):
			player.index = len(player.titles_list) - 1
		else:
			player.index = player.index - 1
		if(os.path.exists(player.path_list[player.index]) == False):
			if(player.index == len(player.titles_list) - 1):
				player.index = player.index - 1
			reload_lists()
		player.set_media(player.media_list_mod[player.index])
		sublime.status_message(player.titles_list[player.index])
		player.play()

class NextCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if(player.index == len(player.titles_list) - 1):
			player.index = 0
		else:
			player.index = player.index + 1
		if(os.path.exists(player.path_list[player.index]) == False):
			if(player.index == len(player.titles_list) - 1):
				player.index = 0
			reload_lists()
		player.set_media(player.media_list_mod[player.index])
		sublime.status_message(player.titles_list[player.index])
		player.play()

class SelectCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.window().show_quick_panel(player.titles_list, self.on_done)
	def on_done(self, user_input):
		if(user_input == -1):
			sublime.status_message('No option selected')
		else:
			player.index = user_input
			if(os.path.exists(player.path_list[player.index]) == False):
				sublime.status_message('The path to file does not exist')
				reload_lists()
			else:
				player.set_media(player.media_list_mod[player.index])
				sublime.status_message(player.titles_list[player.index])
				player.play()

class AddCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.window().show_input_panel("Enter the Directory(a: add, r: remove):", 'a:', self.on_done, None, None)
	def on_done(self, user_input):
		add_remove_flag = 1
		if(user_input.startswith('a:')):
			user_input = user_input[2:]
			add_remove_flag = 1
		elif(user_input.startswith('r:')):
			user_input = user_input[2:]
			add_remove_flag = 0
		else:
			user_input = user_input[2:]
			add_remove_flag = -1
		if(add_remove_flag == 1):
			if(os.path.exists(user_input)):
				if(user_input.endswith('.mp3')):
					sublime.status_message('Give path to directory')
				else:
					flag = 1
					readfile = open(dir_path + '/folder_path.csv', 'r')
					readfile_reader = csv.reader(readfile)
					for row in readfile_reader:
						if row[0] == user_input:
							sublime.status_message('Folder already added!!')
							flag = 0
					readfile.close()
					if flag == 1:
						writefile = open(dir_path + '/folder_path.csv', 'a')
						writefile_writer = csv.writer(writefile)
						writefile_writer.writerow([user_input])
						writefile.close()
						sublime.status_message('Folder Added')
					reload_lists()
			else:
				sublime.status_message('Path does not exist')
		elif(add_remove_flag == 0):
			readfile = open(dir_path + '/folder_path.csv', 'r')
			readfile_reader = csv.reader(readfile)
			file_list = []
			rem_flag = 0
			for row in readfile_reader:
				if row[0] == user_input:
					rem_flag = 1
				else:
					file_list.append(row[0])
			readfile.close()
			if rem_flag == 1:
				sublime.status_message('Removed')
			else:
				sublime.status_message('No such path was added')
			writefile = open(dir_path + '/folder_path.csv', 'w')
			writefile_writer = csv.writer(writefile)
			for line in file_list:
				writefile_writer.writerow([line])
			writefile.close()
			reload_lists()
		else:
			sublime.status_message('Please enter valid start symbol, a:(add) or r:(remove)')
