### B-Safe Checker V 1 2020-12-28
### Create by Brendon Rathbone[ambustion@gmail.com]
###

from tkinter import filedialog
from tkinter import *
from python_get_resolve import GetResolve
import os
from pathlib import Path
from itertools import groupby
import itertools
from operator import itemgetter
#from GetVideoStats import signal
import json
import configparser
import subprocess

config = configparser.ConfigParser()
config_loc = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Comp\bSafeConfig.ini"

config.read(config_loc)
#print(config['DEFAULT']['FFProbe_location'])

ff_path = str(config['DEFAULT']['FFProbe_location'])
initial_dir = str(config['DEFAULT']['FFProbe_location'])
#print(ff_path)
status_text = ""
fail_List = []
movie = ""
filepath = ""
filename = ""
report = ""
prcnt = 0
fps = 23.976
#movie = r"C:/Users/ambus/Desktop/signalStats/bsafeTests.mxf"

ui = fu.UIManager
disp = bmd.UIDispatcher(ui)

resolve = GetResolve()
project = resolve.GetProjectManager().GetCurrentProject()
mediapool = project.GetMediaPool()
bin = mediapool.GetCurrentFolder()
Clips = bin.GetClipList()
timeline = project.GetCurrentTimeline()
if not project:
    print("No project is loaded")
    sys.exit()

def view_with_overlay(start, end ,FPS):
    global fps
    global filename
    global filepath
    filepath_play, ff_file = os.path.split(ff_path)
    play_path = os.path.join(filepath_play + "\\ffplay.exe")
    #print(start, end, FPS)
    #print(play_path)
    dur = int(float(end)) - int(float(start))
    start = int(float(start) / float(fps))
    dur = int(float(dur) / float(fps))
    #ffplay example.mov -vf signalstats="out=brng:color=red"
    width, height = 720,480
    ##ffplay ~/matrixbench_mpeg2.mpg -vf "split[a][b];[a]waveform=e=3,split=3[c][d][e];[e]crop=in_w:20:0:235,lutyuv=v=180[low];[c]crop=in_w:16:0:0,lutyuv=y=val:v=180[high];[d]crop=in_w:220:0:16,lutyuv=v=110[mid] ; [b][high][mid][low]vstack=4"
    ###playCommand = f'{play_path} -ss {start} -t {dur} -x {width} -y {height} -autoexit -vf "signalstats=out=brng:color=yellow" "{filename}"'
    playCommand = f'{play_path} -ss {start} -t {dur} -x {width} -y {height} -autoexit -vf "signalstats=out=brng:color=yellow" "{filename}"'
    #print(filename)
    #print(str(playCommand))
    p1=subprocess.Popen(playCommand , cwd=filepath, shell=True)


def failList(movie_json):
    global fail_List
    for x in movie_json['frames']:
        #print("printing x in  movie_json")
        #print(x)
        for k,v in x['tags'].items():
            if k == 'BRNG':
                brng = float(v)*100
                #print(brng)
                if brng >= 1:
                    #print("brng is great than 1 at: " + str(brng))
                    fail_List.append([float(x['best_effort_timestamp']),float(x['best_effort_timestamp_time']),
                                      float(v), float(x['tags']['YMIN']), float(x['tags']['YMAX']),
                                      float(x['tags']['UMIN']), float(x['tags']['UMAX']),
                                      float(x['tags']['VMIN']), float(x['tags']['VMAX']),
                                      float(x['tags']['SATMIN']), float(x['tags']['SATMAX']),
                                      float(x['tags']['YDIF']), float(x['tags']['UDIF']),float(x['tags']['VDIF']),
                                      #float(x['tags']['TOUT']), float(x['tags']['VREP'])
                                      ])
    times = []
    for x in fail_List:
        #print(x)
        times.append(x[0])
    ranges = []
    for key, group in groupby(enumerate(times), lambda i:i[0]-i[1]):
        group = list(map(itemgetter(1),group))

        ranges.append((group[0], group[-1]))
    #print(ranges)
    marks = []
    for x in ranges:
        for y in fail_List:
            #print(y)
            if x[0] <= y[0]  >= x[1]:
                #print()
                marks.append([x[0],x[1],y[2],y[3],y[4],y[5],y[6],y[7],y[8],y[9],y[10],y[11],y[12],y[13]])
    #print(marks)
    markList2 = []
    for x in ranges:
        counter = 0
        for y in marks:
            if x[0] == y[0]:
                if counter == 0:
                    markList2.append(y)
                    counter = counter + 1

    #print(markList2)
    return markList2


    #print(fail_List)
    #for x in fail_List:





def treeView(tree_List):
    ui = fu.UIManager
    disp2 = bmd.UIDispatcher(ui)
    resolve=GetResolve()
    project=resolve.GetProjectManager().GetCurrentProject()
    #mediapool=project.GetMediaPool()
    #bin=mediapool.GetCurrentFolder()
    Clips=bin.GetClipList()
    timeline=project.GetCurrentTimeline()
    width , height = 500 , 700
    dlg = disp.AddWindow({"WindowTitle" : "Broadcast Safe Checker" , "ID" : "TreeWin" , "Geometry" : [600 , 100 , 700 , 500] , } ,
        [

            ui.VGroup({"Spacing" : .5 , },
                [
                    ui.Label({ "ID" : "test" , "Text" : "Broadcast Safe Checker" , "Weight" : .2 , "Alignment" : { "AlignHCenter" : True , "AlignTop" : True } }) ,
                    ui.Tree({"ID" : "Tree", "SortingEnabled" : True ,"Events" : {"ItemDoubleClicked" : True , "ItemClicked" : True }}),
                    ui.VGap(0 , .2) ,
                    ui.Button({"ID" : "MarksButton" , "Text" : "Add Marks To Timeline" , "Weight" : 0.5}),
                    ui.VGap(0 , .2) ,
                    ])
                ]
            )

    itm = dlg.GetItems()

    hdr = itm["Tree"].NewItem()
    hdr.Text[0] = 'Frames start'
    hdr.Text[1] = 'Frames End'
    hdr.Text[2] = 'BRNG'
    hdr.Text[3] = 'YMin'
    hdr.Text[4] = 'YMax'
    hdr.Text[5]='UMin'
    hdr.Text[6]='UMax'
    hdr.Text[7]='VMin'
    hdr.Text[8]='VMax'
    hdr.Text[9]='SatMin'
    hdr.Text[10]='SatMax'
    hdr.Text[11]='YDif'
    hdr.Text[12]='UDif'
    hdr.Text[13]='VDif'


    itm["Tree"].SetHeaderItem(hdr)

    itm["Tree"].ColumnCount = 14
    ###Resize the Columns
    itm['Tree'].ColumnWidth[0]=90
    itm['Tree'].ColumnWidth[1]=90
    itm['Tree'].ColumnWidth[2]=90
    itm['Tree'].ColumnWidth[3]=90
    itm['Tree'].ColumnWidth[4]=90
    itm['Tree'].ColumnWidth[5]=90
    itm['Tree'].ColumnWidth[6]=90
    itm['Tree'].ColumnWidth[7]=90
    itm['Tree'].ColumnWidth[8]=90
    itm['Tree'].ColumnWidth[9]=90
    itm['Tree'].ColumnWidth[10]=90
    itm['Tree'].ColumnWidth[11]=90
    itm['Tree'].ColumnWidth[12]=90
    itm['Tree'].ColumnWidth[13]=90

    for x in tree_List:
        itRow=itm['Tree'].NewItem()
        itRow.Text[0] = str(x[0])
        itRow.Text[1]= str(x[1])
        itRow.Text[2]= str(x[2])
        itRow.Text[3]= str(x[3])
        itRow.Text[4]= str(x[4])
        itRow.Text[5]=str(x[5])
        itRow.Text[6]=str(x[6])
        itRow.Text[7]=str(x[7])
        itRow.Text[8]=str(x[8])
        itRow.Text[9]=str(x[9])
        itRow.Text[10]=str(x[10])
        itRow.Text[11]=str(x[11])
        itRow.Text[12]=str(x[12])
        itRow.Text[13]=str(x[13])
        itm['Tree'].AddTopLevelItem(itRow)
    #print("test")
    ## The window was closed

    def _func(ev):
        global movie
        global filepath
        global filename
        #print("marker button pressed")
        for x in tree_List:
            dur = int(x[1] - x[0])
            brng = str(int(x[2]*100)) + "% of pixels not broadcast safe"
            ###AddMarker(frameId, color, name, note, duration
            #print(str(x[0]), "Red" , "brng" , brng , dur)
            timeline.AddMarker(int(x[0]), "Red" , "brng" , brng , dur)

    dlg.On.MarksButton.Clicked=_func

    def _func(ev):
        #print('[Double Clicked] ' + str(ev['item'].Text[0]))
        view_with_overlay(int(float(ev['item'].Text[0])),int(float(ev['item'].Text[1])),fps)

    dlg.On.Tree.ItemDoubleClicked=_func

    def _func(ev):
        disp.ExitLoop()

    dlg.On.TreeWin.Close=_func

    dlg.Show()
    disp.RunLoop()
    dlg.Hide()




###initialize main window
dlg = disp.AddWindow({"WindowTitle" : "Broadcast Safe Checker" , "ID" : "MyWin" , "Geometry" : [100 , 100 , 500 , 500] , } ,
    [
        ui.VGroup({"Spacing" : .5 , } ,
               [# Add your GUI elements here:
                ui.Label({"ID" : "Title" , "Text" : "Broadcast Safe Checker", "Weight" : .2, "Alignment" : { "AlignHCenter" : True, "AlignTop" : True } }),
                #ui.TextEdit({"ID" : "ClipList" , "Text" : "ClipList" , "PlaceholderText" : "ClipList" , "Weight" : 0.5 ,"Height" : "200" , "ReadOnly" : True}) ,
                    ui.HGroup({"Spacing" : .5 , } ,
                        [
                        ui.LineEdit({"ID" : "MovieLoc","Text" : "Movie Path", "ReadOnly":True}),
                        ui.Button({"ID" : "MovieButton" , "Text" : "Select Movie File" , "Weight" : 0.5}) ,
                            ]) ,

                        ui.VGroup({"Spacing" : 1 , } ,
                                  [

                            ui.HGap(0 , .2) ,

                                ui.HGroup({"Spacing" : .5 , } ,
                                    [
                                    ui.CheckBox({"ID" : "ReportCheck","Text" : "Save Report"}),
                                    ui.LineEdit({"ID" : "ReportLoc","Text" : "Report Path", "ReadOnly":True}),
                                    ui. Button({"ID" : "ReportButton" , "Text" : "Custom Location" , "Weight" : 0.5})
                                        ]) ,

                                    ui.VGroup({"Spacing" : 1 , } ,
                                              [

                                                ui.CheckBox({"ID" : "BSafe", "Text" : "Broadcast Safe Checks", "Checked": True}) ,
                                                ui.CheckBox({"ID" : "tOut","Text" : "Temporal Outliers"}) ,
                                                ui.CheckBox({"ID" : "vRep","Text" : "Vertical Repitions"}) ,
                                                ui.CheckBox({"ID" : "Audio","Text" : "Audio", "Enabled" : False}) ,
                                                    ui.HGroup({"Spacing" : .5 , } ,
                                                        [
                                                            ui.CheckBox ( { "ID" : "Blanking" , "Text" : "Blanking", "Enabled" : False } ) ,
                                                            ui.ComboBox ({ "ID" : 'BlankingCombo' , "Text" : 'Combo Menu', "Enabled" : False } ) ,
                                                        ]) ,

                                                            ui.VGroup({"Spacing" : 1 , } ,
                                                                      [

                                                                        ui.CheckBox({"ID" : "compare","Text" : "Compare to known good render", "Enabled" : False}) ,
                                                                        ui.VGap(0 , .5) ,
                                                                        ui.Button({"Weight" : "0.25" , "ID" : 'RUN' , "Text" : 'RUN'}) ,
                                                                        ui.Label({"ID" : "Status" , "Text" : prcnt, "Alignment" : { "AlignHCenter" : True, "AlignTop" : True }})])
                                            ])
                                        ])
                                ])
        ])


#itm['Status'].Text = str(prcnt)
itm = dlg.GetItems()

## Add the items to the ComboBox menus
itm["BlankingCombo"].AddItem('2.39')
itm["BlankingCombo"].AddItem('2.40')
itm["BlankingCombo"].AddItem('1.78')
itm["BlankingCombo"].AddItem('2:1')



def _func(ev):
    disp.ExitLoop()
dlg.On.MyWin.Close = _func

def _func(ev):
    print( "[ReportCheck] " + str(itm['ReportCheck'].Checked))
dlg.On.ReportCheck.Clicked = _func

def _func(ev):
    print( "[BSafe] " + str(itm['BSafe'].Checked))
dlg.On.BSafe.Clicked = _func

def _func(ev):
    print( "[tOut] " + str(itm['tOut'].Checked))
dlg.On.tOut.Clicked = _func

def _func(ev):
    print( "[vRep] " + str(itm['vRep'].Checked))
dlg.On.vRep.Clicked = _func

def _func(ev):
    print( "[Audio] " + str(itm['Audio'].Checked))
dlg.On.Audio.Clicked = _func

def _func(ev):
    print( "[Blanking] " + str(itm['Blanking'].Checked))
dlg.On.Blanking.Clicked = _func

def _func(ev):
    print( "[addMarks] " + str(itm['addMarks'].Checked))
dlg.On.addMarks.Clicked = _func

def _func(ev):
    print( "[compare] " + str(itm['compare'].Checked))


dlg.On.compare.Clicked = _func

def _func(ev):
    global movie
    global filepath
    global filename
    #print( "[MovieButton] " + str(itm['MovieButton'].Checked))
    root = Tk ()
    root.withdraw ()
    movie = filedialog.askopenfilename(initialdir=initial_dir , title="Select file" ,
                                         filetypes=(("video files" , "*.mov, *.mxf") , ("all files" , "*.*")) )
    filepath , filename = os.path.split(movie)
    itm['MovieLoc'].Text = str(movie)

dlg.On.MovieButton.Clicked = _func

def _func(ev):
    global report
    #print( "[ReportButton] " + str(itm['ReportButton'].Checked))
    root = Tk ()
    root.withdraw ()
    report = filedialog.askdirectory( initialdir="/" , title="Save Report file")
    itm [ 'ReportLoc' ].Text = str(report)
    #Tk().withdraw
dlg.On.ReportButton.Clicked = _func

def _func(ev):
    #from GetVideoStats import signal
    #print( "[RUN]" + str(itm['RUN'].Checked))
    progress_update
    #print("running process")
    #if os.path(movie).isfile() == False:
    #    print("Movie file does not exist")
    if itm["ReportCheck"].Checked == False:
        report = os.path.realpath(os.path.join(filepath , filename + '_report.txt'))
        #print(report)
    #print(filename , ff_path , filepath , report)
    bsaf = ffprobe_string()
    signal_json = signal(filename , ff_path , filepath , report, bsaf)
    itm['Status'].Text= "Finished"

    tree_List = failList(signal_json)

    treeView(tree_List)
dlg.On.RUN.Clicked = _func

def progress_update(ev):
    itm['Status'].Text = str(prcnt)

###Create the ffprobe String(in progress)
def ffprobe_string():
    bsafeList = []
    if itm["ReportCheck"].Checked == False:
        print()
    if itm["BSafe"].Checked == True:
        bsafeList.append("brng")
    if itm["tOut"].Checked == True:
        bsafeList.append("tout")
    if itm["vRep"].Checked == True:
        bsafeList.append("vrep")
    if itm["Audio"].Checked == False:
        print()
    if itm["Blanking"].Checked == False:
        print()
    if itm["compare"].Checked == False:
        print()
    if itm["ReportCheck"].Checked == False:
        print()
    #print(bsafeList)
    bsafeList2="+".join(bsafeList)

    #print(bsafeList2)
    return(bsafeList2)

def signal(filename, ff_path, filepath, report, bsaf):
    global dlg
    global itm
    global prcnt
    global fps
    #global filepath
    itm = dlg.GetItems()
    ff_path = ff_path
    #ff_path = os.path.abspath(ff_path)
    ##ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4
    durCommand = f'{ff_path} -i "{filename}" -show_format | grep duration'
    FPSCommand = f'{ff_path} -i "{filename}" -show_format | grep fps'
    #p0 = subprocess.Popen(durCommand, cwd=filepath, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #output = p0.stdout.read()
    #dur = output
    p0 = subprocess.run([ff_path, "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd= filepath, encoding='utf-8')
    #p3 = subprocess.run(FPSCommand, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd= filepath, shell=True)
    dur = float(p0.stdout)
    print("duration is " + str(dur))
    p3=subprocess.run(
        [ff_path , "-v" , "error","-select_streams", "v:0", "-show_entries" , "stream=r_frame_rate", "-of" , "default=noprint_wrappers=1:nokey=1" ,
         filename] , stdout=subprocess.PIPE , stderr=subprocess.STDOUT , cwd=filepath , encoding='utf-8', shell=True)
    #p3 = subprocess.run( FPSCommand , stdout=subprocess.PIPE , stderr=subprocess.STDOUT , cwd=filepath, encoding='utf-8')
    fps = p3.stdout
    print(fps)
    fps = eval(fps)
    print(str(fps) + " is the fps")
    #bsaf = bsafe()
    #statsCommand = f'{ff_path} -f lavfi movie="{filename}","signalstats=stat=tout+vrep+brng" -show_frames'
    statsCommand = f'{ff_path} -f lavfi movie="{filename}","signalstats=stat={bsaf}" -show_entries "frame=best_effort_timestamp_time,best_effort_timestamp" -show_entries "frame_tags=lavfi.signalstats.YMIN,lavfi.signalstats.YLOW,lavfi.signalstats.YAVG,lavfi.signalstats.YHIGH,lavfi.signalstats.YMAX,lavfi.signalstats.UMIN,lavfi.signalstats.ULOW,lavfi.signalstats.UAVG,lavfi.signalstats.UHIGH,lavfi.signalstats.UMAX,lavfi.signalstats.VMIN,lavfi.signalstats.VLOW,lavfi.signalstats.VAVG,lavfi.signalstats.VHIGH,lavfi.signalstats.VMAX,lavfi.signalstats.SATMIN,lavfi.signalstats.SATLOW,lavfi.signalstats.SATAVG,lavfi.signalstats.SATHIGH,lavfi.signalstats.SATMAX,lavfi.signalstats.HUEMED,lavfi.signalstats.HUEAVG,lavfi.signalstats.YDIF,lavfi.signalstats.UDIF,lavfi.signalstats.VDIF,lavfi.signalstats.YBITDEPTH,lavfi.signalstats.UBITDEPTH,lavfi.signalstats.VBITDEPTH,lavfi.signalstats.BRNG,lavfi.signalstats.BRNG,lavfi.signalstats.TOUT,lavfi.signalstats.VREP" -select_streams v -print_format json"'
    #print(statsCommand)
    p1 = subprocess.Popen(statsCommand, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,encoding='utf-8',universal_newlines=True, cwd=filepath, shell=True)
    percent_check = 0
    print("processing...0%")
    pc_check = 0

    with open(report , "w") as text_file :
        for line in p1.stdout:
            text_file.write(line)
            line2 = line
            #print(line2)
            if line2.startswith('            "best_effort_timestamp_time":'):
                #print(line2)
                line2 = line2.split(':')[1]
                line2 = line2.replace('"','')
                line2 = line2.replace(',' , '')
                line2 = line2.strip()
                #line2 = float(line2[0])
                #print(line2,dur)
                percent_complete = round((float(line2) / float(dur))*100,1)
                #print(str(percent_complete) + "% complete")
                if pc_check != percent_complete:
                    #print(str(percent_complete) + "% complete")
                    prcnt = str(percent_complete) + "% complete"
                    itm['Status'].Text=str(prcnt)
                    pc_check = percent_complete


            percent_check = percent_check +1

    #p1 = subprocess.Popen(statsCommand, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, cwd=filepath)
    output = p1.stdout.read()
    p1.wait()

    with open(report) as f1 :
        lines = f1.readlines()
        lines = "\n".join (lines)
        lines = lines.split("ffprobe")[0]
        lines = lines.strip("ffprobe")
        lines = lines.replace("lavfi.signalstats.","")
        lines = lines.strip()

    with open(report , 'w') as f2 :
        f2.writelines(lines)


        #data = json.load(f2)

    with open(report) as json_file :
        data = json.load(json_file)

    signalstats = data


    return signalstats
    # print(output)

#def prcnt_complete(self):



dlg.Show()
disp.RunLoop()
dlg.Hide()