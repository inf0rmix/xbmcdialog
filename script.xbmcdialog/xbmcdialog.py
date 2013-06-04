# -*- coding: utf-8 -*-
import os
from sys import argv , stdout , exit
from base64 import b64decode

try:
  import xbmc , xbmcgui
except:
  print "Error: Cannot import xbmc/xbmcgui - This script must be started using RunScript() within xbmc."
  exit(0)


XDLG_TITLE = 'XBMC-Dialog'
XDLG_VERSION = '0.91'
XDLG_DEBUG=False
XDLG_PID = 0
XBMC_DIR = xbmc.translatePath('special://home')
XDLG_RESFILE = XBMC_DIR + '/temp/xbmcdialog.out'
XDLG_PGBFIFO = XBMC_DIR + '/temp/xbmcdialog.gauge.fifo'
XDLG_BASEDIR = os.path.dirname(os.path.realpath(__file__))

def file_write(myfile,mytxt):
  f = open(myfile, 'w')
  f.write(mytxt)
  f.close()

def fifo_write(myfifo,mytxt):
  f = open(myfifo, 'w')
  f.write(mytxt)
  f.flush()
  f.close()

def file_read(myfile):
  if os.path.exists(myfile):
    f = open(myfile, 'r')
    data = f.read()
    f.close()
    return data
  else:
    return ''

#Open system-command in a pipe and return data
def system_popen(mycmd):
  mypipe = os.popen(mycmd, 'r')
  myret = mypipe.read()
  try:
    stdout.flush()
  except:
    pass
  try:
    mypipe.close()
  except:
    pass
  return myret

def get_statdir(mydir=''):
  if mydir == '':
    mydir = '/home'
  if mydir.startswith('file://'):
    mydir=mydir[7:]
  if not mydir.endswith('/'):
    mydir = mydir + '/'
  return mydir

def decode_argv_b64(mystr):
  myargvstr = b64decode(mystr)
  mynewargv = []
  for mycarg in myargvstr.split('\00'):
    mynewargv.append(mycarg)
    mystr += myargv[mypos] + '\00'
  if mystr.endswith('\00'):
    mystr = mystr[:-1].encode('utf-8')
  return 

##
## TextViewer
##

class DialogTextViewer( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        self.filename = kwargs.get( "filename" )
        self.viewmode = kwargs.get( "viewmode" )
        self.text = ''
        xbmc.sleep( 100 )

    def onInit( self ):
        try:
            self.getControl( 1 ).setLabel( self.filename )
            self.load_data()
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        pass

    def onAction( self, action ):
        if action in [ 9, 10]:
            self.close()
        else:
	  action_id = str(action.getId())
	  if action_id == '7':
	    self.load_data()
	  elif action_id == '117':
	    self.load_data()

    def load_data( self ):
        if self.viewmode == 'tail':
	  self.text = system_popen("tail -30 '"+self.filename+"'")
        elif self.viewmode == 'cmd':
	  self.text = system_popen(self.filename)
	else:
	  self.text = file_read(self.filename)
        self.getControl( 5 ).setText( self.text )

def view_text( filename="", viewmode="" ):
    try:
      w = DialogTextViewer( "XBMCDialogTextViewer.xml", XDLG_BASEDIR,  filename=filename, viewmode=viewmode )
    except:
      w = DialogTextViewer( "DialogTextViewer.xml", os.getcwd(), filename=filename, viewmode=viewmode )
    w.doModal()
    del w

def dlg_textbox(myfile):
  #mydata = file_read(myfile)
  view_text(myfile)
  return ''

def dlg_tailbox(myfile):
  view_text(myfile,'tail')
  return ''

##
## XBMCConsole
##

class DialogConsole( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        self.window = xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        self.heading = "XBMC-Console"
        self.command = kwargs.get( "command" )
        xbmc.sleep( 100 )

    def updateView( self ):
	self.text = system_popen(self.command + ' | tail -5000 | tac ')
	self.getControl( 5 ).setText( self.text )

    def onInit( self ):
        try:
            self.getControl( 1 ).setLabel( self.heading )
        except:
            pass
	self.updateView()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        pass

    def contextMenu( self ):
        dialog = xbmcgui.Dialog()
        myelist = [ 'Enter Command','Command History','Save output','Exit Console' ]
        myindex = dialog.select('testest',myelist)

    def onAction( self, action ):
        if action in [ 9, 10 ]:
            self.close()
        else:
	  action_id = str(action.getId())
	  if action_id == '7':
	    self.updateView()
	  elif action_id == '117':
	    self.contextMenu()
	  #os.system("logger actcon: '"+str(action.getId())+"'")

def view_console(command="" ):
    #xmldir = '/home/inf0rmix/xbmc-addons/dev/plugin.program.xi'
    try:
      w = DialogConsole( "XBMCDialogTextViewer.xml", XDLG_BASEDIR, command=command )
    except:
      w = DialogConsole( "DialogTextViewer.xml", os.getcwd(), command=command )
    w.doModal()
    del w

def dlg_consolebox(mycmd):
  view_console(mycmd)
  return ''


##
## Progress-Dialog functions
##

from select import select

def dlg_gauge(myhead,myval=""):
  if myval.isdigit():
    mypos = int(myval)
  else:
    return 'Usage dialog --gauge [Text] [Percentage]'
  if not os.path.exists(XDLG_PGBFIFO):
    os.system('logger starting gauge at '+str(mypos))
    dlg_gauge_start(myhead,mypos)
  elif str(mypos).isdigit():
    fifo_write(XDLG_PGBFIFO,str(mypos)+' '+myhead+'\n')
  return ''

def dlg_gauge_update(myindata,mydialog):
  for myline in myindata.split('\n'):
    mysplit=myline.split(' ',1)
    if len(mysplit) == 2:
      mypos , mytext = mysplit[0] , mysplit[1]
      if mypos.isdigit():
	if mypos.isdigit():
	  if int(mypos) <= 99:
	    mydialog.update(int(mypos),mytext)
	    return True
	  else:
	    mydialog.close()
	    os.system('rm '+XDLG_PGBFIFO)
	    return False
  return False

def dlg_gauge_start(myhead,mypos):
  dialog = xbmcgui.DialogProgress()
  dialog.create(myhead)
  if str(mypos).isdigit():
    dialog.update(int(mypos))
  else:
    dialog.update(0)
  #xbmc.sleep(1)
  shell_exit()
  os.system('mkfifo '+XDLG_PGBFIFO)
  mycnt , is_running = 0 , True
  while is_running:
    mycnt += 1
    #os.system('logger run:'+str(mycnt))
    try:
      myfifo = os.open(XDLG_PGBFIFO, os.O_RDONLY) # | os.O_NONBLOCK)
      is_running = True
    except:
      is_running = False
    if is_running:
      select([myfifo], [], [])
      mystring = os.read(myfifo, 256)
      dlg_gauge_update(mystring,dialog)
    xbmc.sleep(100)
    #os.system('logger run:'+str(mycnt))
    #is_running=os.path.exists(XDLG_PGBFIFO)
  return ''

def dlg_gauge_stop():
  os.system('rm '+XDLG_PGBFIFO)

##
## Dialog functions
##

def dlg_menu(myhead,myargs=[]):
  mytaglist, myelist = [] , []
  #Generate menu-maps
  mylen = len(myargs)
  myistag = True
  for mypos in range(0,mylen):
    if myistag:
      myistag = False
      mytaglist.append(myargs[mypos])
    else:
      myistag = True
      myelist.append(myargs[mypos])
  #build dialog
  dialog = xbmcgui.Dialog()
  myindex = dialog.select(myhead,myelist)
  myret = myelist[myindex]
  return myret

def dlg_calendar(myhead='',myval=''):
  #Force heading
  if myhead == '':
    myhead = XDLG_TITLE
  #Generate list
  dialog = xbmcgui.Dialog()
  myret = str(dialog.numeric(1, myhead,myval)).strip(' ')
  return myret

def dlg_time(myhead='',myval=''):
  #Force heading
  if myhead == '':
    myhead = XDLG_TITLE
  #Generate list
  dialog = xbmcgui.Dialog()
  myret = str(dialog.numeric(2, myhead,myval)).strip(' ')
  if myret.count(':') == 1:
    myret = myret + ':00'
  return myret

def dlg_number(myhead='',myval=''):
  #Force heading
  if myhead == '':
    myhead = XDLG_TITLE
  #Generate list
  dialog = xbmcgui.Dialog()
  myret = str(dialog.numeric(0, myhead,myval)).strip(' ')
  return myret

def dlg_ip(myhead='',myval=''):
  #Force heading
  if myhead == '':
    myhead = XDLG_TITLE
  #Generate list
  dialog = xbmcgui.Dialog()
  myret = str(dialog.numeric(3, myhead,myval)).strip(' ')
  return myret

def dlg_list(myhead='',myargs=[]):
  #Generate list
  dialog = xbmcgui.Dialog()
  myindex = dialog.select(myhead,myargs)
  myret = myargs[myindex]
  return myret

def dlg_password(myhead='',myival=''):
  #Get heading-argument [myargs[0]
  if myhead == '':
    myhead = 'Enter password'
  #get keyboard
  keyboard = xbmc.Keyboard(myival,myhead)
  keyboard.setHiddenInput(True)
  keyboard.doModal()
  if (keyboard.isConfirmed()):
    return keyboard.getText()
  else:
    return ''

def dlg_inputbox(myhead='',myival=''):
  #Force heading
  if myhead == '':
    myhead = XDLG_TITLE
  #get keyboard
  keyboard = xbmc.Keyboard(myival,myhead)
  keyboard.setHiddenInput(False)
  keyboard.doModal()
  if (keyboard.isConfirmed()):
    return keyboard.getText()
  else:
    return ''

def dlg_yesno(mymsg):
  dialog = xbmcgui.Dialog()
  myret = str(dialog.yesno(XDLG_TITLE,mymsg))
  return myret

def dlg_ok(mymsg):
  dialog = xbmcgui.Dialog()
  myret = str(dialog.ok(XDLG_TITLE,mymsg))
  return myret

def dlg_con(myhead,mycmd=''):
  if mycmd == '':
    mycmd = myhead
    myhead = XDLG_TITLE
  #View
  mycmd = mycmd+' | tail -5000'
  view_text(mycmd,'pipe')
  return ''

def dlg_browse(myhead,mydir='/',mydlgmode=1):
  #Force heading
  if myhead == '':
    myhead = XDLG_TITLE
  #Build dialog
  dialog = xbmcgui.Dialog()
  myret = str(dialog.browse(mydlgmode,myhead, 'files', '', False, False,get_statdir(mydir)))
  return myret

def dlg_image(myhead,myval=''):
  #Force heading
  if myhead == '':
    myhead = XDLG_TITLE
  #Get startpath-argument myargs[0]
  if not myval.endswith('/'):
    myval = myval+'/'
  #Build dialog
  dialog = xbmcgui.Dialog()
  myret = str(dialog.browse(2,myhead, 'files', '', False, False,get_statdir(myval)))
  return myret

def dlg_notify(mytext,mytime='5',myicon=''):
  xbmc.executebuiltin('notification('+XDLG_TITLE+','+myarg+')')
  return 'sent'

def xbmc_getvar(myvar):
  myret = xbmc.translatePath(myvar)
  myval = myret
  return myval

#Play argument as media
def xcmd_playmedia(myvar):
  myloc = myvar.replace("'","\\'")
  xbmc.executebuiltin('PlayMedia('+myloc+')')
  return 'playing '+myvar

#Show slideshow for argument
def xcmd_slideshow(myvar):
  myloc = myvar.replace("'","\\'")
  xbmc.executebuiltin('SlideShow('+myloc+')')
  return 'playing slideshow '+myvar

#Send full command to xmbc-builtin
def xcmd_exec(myvar):
  xbmc.executebuiltin(myvar)
  return 'executing command '+myvar

#Send action to xbmc-builtin
def xcmd_action(myvar):
  xbmc.executebuiltin('Action('+myvar+')')
  return 'running action '+myvar

#Activate XBMC-Window
def xcmd_activate(myvar):
  xbmc.executebuiltin('ActivateWindow('+myvar+')')
  return 'activating window '+myvar

#Run script in xbmc
def xcmd_script(myvar,myval):
  xbmc.executebuiltin('RunScript('+myvar+','+myval+')')
  return 'running script '+myvar+' args -- ' + myval

#Send log-entry to xbmc-log
def xcmd_logger(myvar,mylevel=5):
  if not str(mylevel).isdigit():
    mylevel = 5
  else:
    mylevel = int(mylevel)
  xbmc.log(myvar,mylevel)
  return ''

#Translatepath shell-compatible and extended to check input and output
def xcmd_translatepath(myvar):
  #Check if protocol is set
  if myvar.find('://') == -1:
    myvar = 'special://'+myvar
  #Check if we find ///
  if myvar.find('///') > -1:
    myvar = myvar.replace('///','//')
  #Get path
  myret = xbmc.translatePath(myvar)
  #Strip last /
  myval = myret.rstrip('/')
  return myval

def is_alias(myact,myname):
  if myact == 'dsel':
    if myname in [ '--getexistingdirectory', '--dselect']:
      return True
  elif myact == 'fsel':
    if myname in [ '--getopenfilename', '--fselect']:
      return True
  elif myact == 'ibox':
    if myname in [ '--passivepopup', '--infobox']:
      return True
  return False

def do_action(myargs=[]):
  myret , myarglen = '' , len(myargs)
  myact , myarg , myval = '--help', '', ''
  #Get Action and argument
  if myarglen >= 1:
    myact = myargs[0]
    myargs.pop(0)
    if myarglen >= 2:
      myarg = myargs[0]
      myargs.pop(0)
      if myarglen >= 3:
        myval = myargs[0]
  #Do action
  if myact == '--yesno':	myret = dlg_yesno(myarg)
  elif is_alias('dsel',myact):	myret = dlg_browse(myarg,myval,0)
  elif is_alias('fsel',myact):	myret = dlg_browse(myarg,myval,1)
  elif is_alias('ibox',myact):	myret = dlg_notify(myarg,myval)
  elif myact == '--combobox':	myret = dlg_list(myarg,myargs)
  elif myact == '--menu':	myret = dlg_menu(myarg,myargs)
  elif myact == '--calendar':	myret = dlg_calendar(myarg,myval)
  elif myact == '--timebox':	myret = dlg_time(myarg,myval)
  elif myact == '--msgbox':	myret = dlg_ok(myarg)
  elif myact == '--prgbox':	myret = dlg_con(myarg,myval)
  elif myact == '--ip':		myret = dlg_ip(myarg,myval)
  elif myact == '--number':	myret = dlg_number(myarg,myval)
  elif myact == '--image':	myret = dlg_image(myarg,myval)
  
  elif myact == '--con':	myret = dlg_consolebox(myarg)
  elif myact == '--textbox':	myret = dlg_textbox(myarg)
  elif myact == '--tailbox':	myret = dlg_tailbox(myarg)
  elif myact == '--inputbox':	myret = dlg_inputbox(myarg,myval)
  elif myact == '--gauge':	myret = dlg_gauge(myarg,myval)
  elif myact == '--passwordbox':myret = dlg_password(myarg,myval)
  
  elif myact == '--xplay':	myret = xcmd_playmedia(myarg)
  elif myact == '--xslideshow':	myret = xcmd_slideshow(myarg)
  elif myact == '--xexec':	myret = xcmd_exec(myarg)
  elif myact == '--xscript':	myret = xcmd_script(myarg,myval)
  elif myact == '--xaction':	myret = xcmd_action(myarg)
  elif myact == '--xactivate':	myret = xcmd_activate(myarg)
  elif myact == '--xpath':	myret = xcmd_translatepath(myarg)
  elif myact == '--xlog':	myret = xcmd_logger(myarg,myval)
  
  else:
    myret = Help()
  return myret

##
## Main
##

def shell_exit():
  if XDLG_PID > 0:
    os.system('kill -10 '+str(XDLG_PID))

def shell_except(myexecpt):
  mymsg = '\nError:\n\n'
  mymsg += str(type(myexecpt)) + '\n'
  mymsg += str(inst) + '\n'
  file_write(XDLG_RESFILE,mymsg)
  shell_exit()

def Help():
  myt = '\nxbmcdialog '+str(XDLG_VERSION)+'\n'
  myt += '\nXBMCGui-only functions\n\n'
  myt += '  --ip [Message] [default]\n'
  myt += '  --number [Message] [default]\n'
  myt += '  --image [Message] [Start-dir]\n'
  myt += '\nXBMC-only functions\n\n'
  myt += '  --xscript [Script-Path] [Arguments]\n'
  myt += '  --xpath [Translate-Path]\n'
  myt += '  --xlog [Log-String] [Log-level]\n'
  myt += '  --xexec [XBMC-Command]\n'
  myt += '  --xaction [XBMC-Action]\n'
  myt += '  --xactivate [XBMC-Window]\n'
  myt += '\nGeneric dialog functions\n\n'
  myt += '  --yesno [Message]\n'
  myt += '  --calendar [Message]\n'
  myt += '  --msgbox [Text]\n'
  myt += '  --textbox [File]\n'
  myt += '  --password [Text]\n'
  myt += '  --inputbox [Text] [Default]\n'
  myt += '  --menu [Headline] [tag1] [item1] ...\n'
  myt += '\nCDialog functions\n\n'
  myt += '  --prgbox [Command]\n'
  myt += '  --tailbox [File]\n'
  myt += '  --timebox [Message]\n'
  myt += '  --infobox [Message]\n'
  myt += '  --fselect [Start-Dir]\n'
  myt += '  --dselect [Start-Dir]\n'
  myt += '\nKDialog functions\n\n'
  myt += '  --getopenfilename [Start-Dir]\n'
  myt += '  --getexistingdirectory [Start-Dir]\n'
  myt += '  --passivepopup [Message] [Seconds]\n'
  myt += '  --combobox [Headline] [item1] [item2] ...\n'
  #myt += '-- []\n'
  return myt
  
def MainArgs():
  myret , mycnt , mypid = [] , 0 , ''
  if len(argv) > 1:
    myargval = argv[1]
    if myargval.count(':') == 1:
      mypid,myargval = myargval.split(':')
    myargstr = b64decode(myargval)
    if not myargstr:
      myret.append('--help')
      return myret
    for mycarg in myargstr.split('\00'):
      myret.append(mycarg)
      mycnt += 1
    if mycnt > 1:
      if myret[0] == '--title':
	global XDLG_TITLE
	XDLG_TITLE = myret[1]
	myret.pop(0)
	myret.pop(0)
  return mypid,myret
  
def Main():
  mypid , myargs = MainArgs()
  if mypid.isdigit():
    global XDLG_PID
    XDLG_PID = int(mypid)
  if myargs[0] == '--help':
    file_write(XDLG_RESFILE,Help())
  else:
    myres = do_action(myargs)
    file_write(XDLG_RESFILE,myres)
  shell_exit()

if ( __name__ == "__main__" ):
  #Main()
  if not XDLG_DEBUG:
    Main()
  else:
    try:
      Main()
    except Exception as inst:
      shell_except(inst)
