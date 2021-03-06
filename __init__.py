from aqt import mw
from PyQt5.QtWidgets import QAction, QMenu
from aqt.qt import *
from aqt.utils import showInfo, showWarning, tooltip

from os.path import dirname, join, realpath
import webbrowser
import requests
from bs4 import BeautifulSoup
import datetime

from .Leaderboard import start_main
from .Setup import start_setup
from .Stats import Stats

def Main():
	check_info()
	config = mw.addonManager.getConfig(__name__)
	setup = config['new_user']
	if setup == "True":
		invoke_setup()
	else:
		mw.leaderboard = start_main()
		mw.leaderboard.show()
		mw.leaderboard.raise_()
		mw.leaderboard.activateWindow()

def invoke_setup():
	mw.lb_setup = start_setup()
	mw.lb_setup.show()
	mw.lb_setup.raise_()
	mw.lb_setup.activateWindow()

def config_setup():
	s = start_setup()
	if s.exec():
		pass

def github():
	webbrowser.open('https://github.com/ThoreBor/Anki_Leaderboard/issues')

def check_info():
	try:
		url = 'https://ankileaderboardinfo.netlify.app'
		headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36 OPR/62.0.3331.116'}
		page = requests.get(url, headers=headers)
		soup = BeautifulSoup(page.content, 'html.parser')
		if soup.find(id='show_message').get_text() == "True":
			info = soup.find(id='Message').get_text()
			showInfo(info, title="Leaderboard")
		else:
			pass
	except:
		showWarning("Make sure you're connected to the internet.")

#Make sure own username is in friendlist

def add_username_to_friendlist():
	config = mw.addonManager.getConfig(__name__)
	if config['username'] != "" and config['username'] not in config['friends']:
		friends = config["friends"]
		friends.append(config['username'])
		config = {"new_user": config['new_user'], "username": config['username'], "friends": friends, "newday": config["newday"], 
		"subject": config['subject'], "country": config['country'], "scroll": config['scroll'], "refresh": config["refresh"]}
		mw.addonManager.writeConfig(__name__, config)

def background_sync():
	config = mw.addonManager.getConfig(__name__)
	url = 'https://ankileaderboard.pythonanywhere.com/sync/'
	config5 = config['subject'].replace(" ", "")
	config6 = config['country'].replace(" ", "")
	streak, cards, time, cards_past_30_days, retention = Stats()
	data = {'Username': config['username'], "Streak": streak, "Cards": cards , "Time": time , "Sync_Date": datetime.datetime.now(), 
	"Month": cards_past_30_days, "Subject": config5, "Country": config6, "Retention": retention}
	try:
		x = requests.post(url, data = data)
	except:
		showWarning("Make sure you're connected to the internet.")

	if x.text == "Done!":
		tooltip("Synced data successfully.")
	else:
		showWarning(str(x.text))

def add_menu(Name, Button, exe, *sc):
	action = QAction(Button, mw)
	action.triggered.connect(exe)
	if not hasattr(mw, 'menu'):
		mw.menu = {}
	if Name not in mw.menu:
		add = QMenu(Name, mw)
		mw.menu[Name] = add
		mw.form.menubar.insertMenu(mw.form.menuTools.menuAction(), add)
	mw.menu[Name].addAction(action)
	for i in sc:
		action.setShortcut(QKeySequence(i))

add_menu('&Leaderboard',"&Leaderboard", Main, 'Shift+L')
add_menu('&Leaderboard',"&Sync", background_sync, "Shift+S")
add_menu('&Leaderboard',"&Config", invoke_setup)
add_menu('&Leaderboard',"&Make a feature request or report a bug", github)

mw.addonManager.setConfigAction(__name__, config_setup)

add_username_to_friendlist()