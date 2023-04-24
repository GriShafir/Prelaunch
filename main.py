#!/usr/bin/env python3

# Created by YourKalamity and earedguitr
# https://github.com/YourKalamity/lazy-dsi-file-downloader


from tkinter import *
import tkinter.filedialog
import tkinter.font
import tkinter.ttk
import os
import platform
import sys
import requests
import json
from pathlib import Path
import shutil
import zipfile
import webbrowser
import threading
import py7zr
import webview

pageNumber = 0
memoryPitLink = "https://dsi.cfw.guide/assets/files/memory_pit/"
memoryPitLinks = [
    memoryPitLink + "256/pit.bin",
    memoryPitLink + "768_1024/pit.bin"
]


def downloadFile(link, destination):
    global fileName
    try:
        r = requests.get(link, allow_redirects=True)
        if link.find('/'):
            fileName = link.rsplit('/', 1)[1]
        if destination.endswith("/") is False:
            destination = destination + "/"
        downloadLocation = destination + fileName
        open(downloadLocation, 'wb').write(r.content)
        return downloadLocation
    except Exception:
        print("File not available, skipping...")
        return None


def getLatestGitHub(usernamerepo, assetNumber):
    if not isinstance(assetNumber, int):
        return False
    release = json.loads(
        requests.get(
            "https://api.github.com/repos/" + usernamerepo + "/releases/latest"
        ).content)
    url = release["assets"][assetNumber]["browser_download_url"]
    return url


def outputbox(message):
    outputBox.configure(state='normal')
    outputBox.insert('end', message)
    outputBox.see(tkinter.END)
    outputBox.configure(state='disabled')


def validateDirectory(directory):
    if directory == "":
        outputbox("That's not a valid directory \n")
        outputbox("Press the Back button to change the folder\n")
        return False
    try:
        directory = str(directory)
    except TypeError:
        outputbox("That's not a valid directory \n")
        outputbox("Press the Back button to change the folder\n")
        return False
    try:
        string = directory + "/test.file"
        with open(string, 'w') as file:
            file.close()
        os.remove(string)
    except FileNotFoundError:
        outputbox("That's not a valid directory or you do not have the\n")
        outputbox("permissions needed to write there\n")
        outputbox("Press the Back button to change the folder\n")
        return False
    except PermissionError:
        outputbox("You do not have write access to that folder\n")
        outputbox("Press the Back button to change the folder\n")
        return False
    else:
        return True


def unzipper(unzipped, destination):
    if not zipfile.is_zipfile(unzipped):
        return False
    try:
        with zipfile.ZipFile(unzipped, 'r') as zip_ref:
            zip_ref.extractall(destination)
            zip_ref.close()
        return True
    except Exception:
        return False


def un7zipper(zipfile, destination, files=None):
    if not py7zr.is_7zfile(zipfile):
        return False
    with py7zr.SevenZipFile(zipfile) as archive:
        if files is None:
            archive.extractall(path=destination)
        else:
            targets = files
            for extractable in archive.getnames():
                for file in files:
                    if extractable != file and extractable.startswith(file):
                        targets.append(extractable)
            archive.extract(path=destination, targets=files)


def download_MemoryPit(directory):
    memoryPitLocation = directory + "/private/ds/app/484E494A/"
    Path(memoryPitLocation).mkdir(parents=True, exist_ok=True)
    outputbox("Downloading Memory Pit\n")
    downloadLocation = downloadFile(memoryPitLinks[facebookIcon.get()], memoryPitLocation)
    if downloadLocation is None:
        outputbox("Memory Pit not found, skipping...\n")
        print("[debug] Memory Pit not found, skipping...")
        return False
    outputbox("Memory Pit downloaded\n")
    print("[debug] Memory Pit downloaded")
    return True


def download_DSJ_cheat_codes(directory):
    outputbox("Downloading DeadSkullzJr's Cheat database\n")
    downloadLocation = downloadFile(
        'https://bitbucket.org/DeadSkullzJr/nds-i-cheat-databases/raw/963fff3858de7539891ef7918d992b8b06972a48/Cheat%20Databases/usrcheat.dat',
        directory + "/_nds/TWiLightMenu/extras/")

    if downloadLocation is None:
        outputbox("DeadSkullzJr's Cheat database not found, skipping...\n")
        print("[debug] DeadSkullzJr's Cheat database not found, skipping...")
        return False

    Path(directory + "/_nds/TWiLightMenu/extras/").mkdir(parents=True, exist_ok=True)
    print("[debug] DeadSkullzJr's Cheat Database downloaded")
    outputbox("DeadSkullzJr's Cheat Database downloaded\n")


def download_TWLMenu(directory, cwdtemp):
    # Download TWiLight Menu
    outputbox("Downloading TWiLight Menu++\n")
    TWLmenuLocation = downloadFile(getLatestGitHub('DS-Homebrew/TWiLightMenu', 1), cwdtemp)

    if TWLmenuLocation is None:
        outputbox("TWiLight Menu++ not found, skipping...\n")
        print("[debug] TWiLight Menu++ not found, skipping...")
        return False

    outputbox("TWiLight Menu++ downloaded\n")
    print("[debug] TWiLight Menu++ downloaded")

    # Extract TWiLight Menu

    twlfolders = ['_nds', 'roms', 'title']
    twlfiles = ['BOOT.NDS', 'snemul.cfg']
    if un7zipper(zipfile=TWLmenuLocation, destination=cwdtemp, files=twlfolders + twlfiles) is False:
        outputbox("Failed to extract TWiLight Menu++\n")
        print("[debug] Failed to extract TWiLight Menu++")
        return False

    outputbox("TWiLight Menu++ extracted\n")
    print("[debug] TWiLight Menu++ extracted to", cwdtemp)

    # Move TWiLight Menu
    for folder in twlfolders:
        shutil.copytree(cwdtemp + folder, directory + "/" + folder + "/", dirs_exist_ok=True)
    for file in twlfiles:
        dest_filepath = os.path.join(directory, file)
        shutil.move(cwdtemp + file, dest_filepath)

    shutil.rmtree(cwdtemp + "_nds/")
    Path(cwdtemp + "_nds/").mkdir(parents=True, exist_ok=True)

    print("[debug] TWiLight Menu++ placed in", directory)
    outputbox("TWiLight Menu++ placed on the SD card\n")

    # Download DeadSkullzJr's Cheat Database
    download_DSJ_cheat_codes(directory)
    return True


def download_dumpTool(directory):
    outputbox("Downloading dumpTool\n")
    if downloadFile(getLatestGitHub('zoogie/dumpTool', 0), directory) is None:
        outputbox("Failed to download dumpTool\n")
        print("[debug] Failed to download dumpTool")
        return False
    print("[debug] dumpTool downloaded")
    outputbox("dumpTool downloaded.\n")
    return True


def download_Unlaunch(directory, cwdtemp):
    outputbox("Downloading Unlaunch\n")
    url = "https://web.archive.org/web/20201112031436/https://problemkaputt.de/unlaunch.zip"
    unlaunchLocation = downloadFile(url, cwdtemp)
    if unlaunchLocation is None:
        outputbox("Failed to download Unlaunch. \nTry to download it manually from dsi.cfw.guide.\n")
        print("[debug] Failed to download Unlaunch")
        return False
    print("[debug] Unlaunch downloaded")
    outputbox("Unlaunch downloaded.\n")

    if not unzipper(unlaunchLocation, directory):
        print("Failed to extract Unlaunch")
        outputbox("Failed to extract Unlaunch\n")
        return False

    print("[debug] Unlaunch extracted")
    outputbox("Unlaunch extracted.\n")
    return True


def clean_up(cwdtemp):
    shutil.rmtree(cwdtemp)
    # Restore button access
    finalnextButton.config(state="normal")
    window.protocol("WM_DELETE_WINDOW", lambda: closeButtonPress(window))
    print("[debug] Done!")
    outputbox("Done!\n")
    outputbox("Press the Finish button to continue... \n")


def start():
    # Clear outputBox
    outputBox.configure(state='normal')
    outputBox.delete('1.0', tkinter.END)
    outputBox.configure(state='disabled')

    directory = SDentry
    if directory.endswith("\\") or directory.endswith("/"):
        directory = directory[:-1]
    # Validate directory
    if validateDirectory(directory) is False:
        finalbackButton.configure(state='normal')
        return

    # Creates a temporary directory for the files to be downloaded to
    cwdtemp = os.getcwd() + "/prelaunch-tmp/"
    Path(cwdtemp).mkdir(parents=True, exist_ok=True)

    if downloadmemorypit.get() == 1:
        download_MemoryPit(directory)

    if downloadtwlmenu.get() == 1:
        download_TWLMenu(directory, cwdtemp)

    if downloaddumptool.get() == 1:
        download_dumpTool(directory)

    if unlaunch.get() == 1:
        download_Unlaunch(directory, cwdtemp)

    clean_up(cwdtemp)
    return True


def chooseDir(SDentry):
    sourceFolder = tkinter.filedialog.askdirectory(
        initialdir="/",
        title='Select the root directory of your SD card')
    SDentry.delete(0, tkinter.END)
    SDentry.insert(0, sourceFolder)


def extraHomebrew():
    webbrowser.open("http://db.universal-team.net/ds/")


def closeButtonPress(source):
    source.destroy()
    root.destroy()


# def nextWindow(windownumbertosummon):
#     globals()["summonWindow" + windownumbertosummon]


def donothing():
    return


def summonWindow0():
    window.title("Prelaunch")
    window.resizable(False, False)
    window.geometry("500x360")
    window.option_add("*Background", backgroundColour)
    window.configure(bg=backgroundColour)
    topFrame = tkinter.Frame(window)
    topFrame.pack(expand=True, fill=tkinter.BOTH, padx=5)
    topFrame.option_add("*Background", backgroundColour)
    bottomFrame = tkinter.Frame(window)
    bottomFrame.pack(side=tkinter.BOTTOM, fill=tkinter.X, padx=5)
    bottomFrame.option_add("*Background", backgroundColour)
    first = tkinter.Label(topFrame, text="Prelaunch",
                          font=firstTitleFont, fg=foregroundColour)
    line = tkinter.Label(topFrame, text="———————————————————————————————",
                         font=buttonFont, fg=foregroundColour, anchor="center", height=1)
    stepsBold = tkinter.Label(topFrame, text="Start", font=buttonFont, fg=foregroundColour)
    steps = tkinter.Label(topFrame, text=" > Memory Pit > Homebrew > Download > Finish",
                          font=paragraphFont, fg=foregroundColour)
    line.place(x=0, y=17)
    stepsBold.grid(column=0, row=0, sticky="w", padx=0)
    steps.grid(column=0, row=0, sticky="w", padx=38.5)
    first.grid(column=0, row=1, sticky="w", padx=5, pady=5)
    bulletpoints = [
        "Welcome! This program will help you to download any files necessary to run homebrew games on your DSi.",
        "This program is best used when following DSi CFW Guide.",
        "You can check the guide by going to https://dsi.cfw.guide/ website or by clicking the \"DSi CFW Guide\" button below.",
        "Have any questions or issues regarding DSi hacking process? Join the Discord server using the \"Discord server\" button below!",
        "To continue the setup, press the Next button."
    ]

    for count, x in enumerate(bulletpoints):
        bullet = tkinter.Label(topFrame, text=x, font=paragraphFont, fg=foregroundColour, justify="left",
                               wraplength=450)
        bullet.grid(column=0, row=count + 3, sticky="w", padx=3)

    websiteButton = Button(bottomFrame, text="DSi CFW Guide", fg="#121212", bg=buttonColour,
                           font=buttonFont, command=lambda: webbrowser.open("https://dsi.cfw.guide/", new=1))
    discordButton = Button(bottomFrame, text="Discord server", fg="#121212", bg=buttonColour,
                           font=buttonFont, command=lambda: webbrowser.open("https://discord.gg/yD3spjv", new=1))
    websiteButton.pack(side=tkinter.LEFT, padx="5", pady="5")
    discordButton.pack(side=tkinter.LEFT, padx="5", pady="5")
    nextButton = Button(bottomFrame, text="Next", width=button_width, fg="#121212", bg=nextButtonColour,
                        font=buttonFont, command=lambda: [topFrame.destroy(), bottomFrame.destroy(), summonWindow1()])
    nextButton.pack(side=tkinter.RIGHT, padx=5, pady=5)

    window.protocol("WM_DELETE_WINDOW", lambda: closeButtonPress(window))


def summonWindow1():
    topFrame = tkinter.Frame(window)
    topFrame.pack(expand=True, fill=tkinter.BOTH, padx=5)
    topFrame.option_add("*Background", backgroundColour)
    bottomFrame = tkinter.Frame(window)
    bottomFrame.pack(side=tkinter.BOTTOM, fill=tkinter.X, padx=5)
    bottomFrame.option_add("*Background", backgroundColour)
    first = tkinter.Label(topFrame, text="Memory Pit", font=titleFont, fg=foregroundColour)
    line = tkinter.Label(topFrame, text="———————————————————————————————",
                         font=buttonFont, fg=foregroundColour, anchor="center", height=1)
    steps = tkinter.Label(topFrame, text="Start >                        > Homebrew > Download > Finish",
                          font=paragraphFont, fg=foregroundColour)
    stepsBold = tkinter.Label(topFrame, text="Memory Pit", font=buttonFont, fg=foregroundColour)
    line.place(x=0, y=17)
    stepsBold.place(x=50, y=0)
    steps.grid(column=0, row=0, sticky="w", padx=0)
    first.grid(column=0, row=1, sticky="w", padx=5, pady=10)
    filler = tkinter.Label(topFrame, text=" ")
    filler.grid(column=0, row=3)
    downloadmemorypitCheck = tkinter.Checkbutton(topFrame, text="Download Memory Pit exploit?", font=buttonFont,
                                                 fg=foregroundColour, variable=downloadmemorypit)
    downloadmemorypitCheck.grid(column=0, row=2, sticky="w")
    instructionLabel = tkinter.Label(topFrame, text="Check your DSi Camera Version:", font=paragraphFont,
                                    fg=foregroundColour, wraplength=450)
    instructionLabel.grid(column=0, row=3, sticky="w", padx=5)
    instructions = [
        "1. Power on your DSi console.",
        "2. Open the Nintendo DSi Camera app.",
        "3. Open the album with the big button on the right.",
        "4. Check for a Facebook icon alongside the star, clubs and hearts icons."
    ]
    for count, instruction in enumerate(instructions):
        instructionLabel = tkinter.Label(topFrame, text=instruction, font=instructionFont, fg=foregroundColour,
                                        justify="left", wraplength=450)
        instructionLabel.grid(column=0, row=count + 4, sticky="w", padx=5)
    facebookIconCheck = tkinter.Checkbutton(topFrame, text="Is the Facebook Icon present?", fg=foregroundColour,
                                            font=buttonFont, variable=facebookIcon)
    facebookIconCheck.grid(column=0, row=9, sticky="w")

    # if platform.system() == "Darwin":
    #     macOS_hiddentext = tkinter.Label(topFrame,
    #                                      text="(Click the area above this text\n if you can't see the dropdown menu) ",
    #                                      fg=foregroundColour, font=bodyFont)
    #     macOS_hiddentext.grid(column=0, row=6, sticky="w")

    backButton = Button(bottomFrame, text="Back", font=buttonFont, fg="#121212", bg=backButtonColour,
                        command=lambda: [topFrame.destroy(), bottomFrame.destroy(), summonWindow0()],
                        width=button_width)
    backButton.pack(side=tkinter.LEFT)
    nextButton = Button(bottomFrame, text="Next", width=button_width, fg="#121212", bg=nextButtonColour,
                        font=buttonFont, command=lambda: [topFrame.destroy(), bottomFrame.destroy(), summonWindow2()])
    nextButton.pack(side=tkinter.RIGHT, padx=5, pady=5)
    window.protocol("WM_DELETE_WINDOW", lambda: closeButtonPress(window))


def summonWindow2():
    topFrame = tkinter.Frame(window)
    topFrame.pack(expand=True, fill=tkinter.BOTH, padx=5)
    topFrame.option_add("*Background", backgroundColour)
    bottomFrame = tkinter.Frame(window)
    bottomFrame.pack(side=tkinter.BOTTOM, fill=tkinter.X, padx=5)
    bottomFrame.option_add("*Background", backgroundColour)
    line = tkinter.Label(topFrame, text="———————————————————————————————",
                         font=buttonFont, fg=foregroundColour, anchor="center", height=1)
    first = tkinter.Label(topFrame, text="Homebrew", font=titleFont, fg=foregroundColour)
    steps = tkinter.Label(topFrame, text="Start > Memory Pit >                       > Download > Finish",
                          font=paragraphFont, fg=foregroundColour)
    stepsBold = tkinter.Label(topFrame, text="Homebrew", font=buttonFont, fg=foregroundColour)
    line.place(x=0, y=17)
    stepsBold.place(x=152, y=0)
    steps.grid(column=0, row=0, sticky="w", padx=0)
    first.grid(column=0, row=1, sticky="w", pady=10)
    downloadtwlmenuCheck = tkinter.Checkbutton(topFrame, text="Download latest TWiLight Menu++ version?",
                                               fg=foregroundColour, variable=downloadtwlmenu, font=buttonFont)
    downloadtwlmenuCheck.grid(column=0, row=2, sticky="w")
    downloaddumptoolCheck = tkinter.Checkbutton(topFrame, text="Download latest dumpTool version?",
                                                variable=downloaddumptool, fg=foregroundColour, font=buttonFont)
    downloaddumptoolCheck.grid(column=0, row=3, sticky="w")
    unlaunchCheck = tkinter.Checkbutton(topFrame, text="Download latest Unlaunch version?", variable=unlaunch,
                                        fg=foregroundColour, font=buttonFont)
    unlaunchCheck.grid(column=0, row=4, sticky="w")
    univdbLabel = tkinter.Label(topFrame, text="Want to download additional homebrew? Visit Universal-DB by \nclicking the button below:",
                                font=paragraphFont, fg=foregroundColour, justify="left")
    univdbLabel.grid(column=0, row=8, sticky="w")
    buttonExtraHomebrew = tkinter.Button(topFrame, text="Universal-DB",
                                         command=lambda: [extraHomebrew()], fg=foregroundColour,
                                         font=buttonFont)
    buttonExtraHomebrew.grid(column=0, row=9, sticky="w", pady=5)
    backButton = Button(bottomFrame, text="Back", font=buttonFont, fg="#121212", bg=backButtonColour,
                        command=lambda: [topFrame.destroy(), bottomFrame.destroy(), summonWindow1()],
                        width=button_width)
    backButton.pack(side=tkinter.LEFT)
    nextButton = Button(bottomFrame, text="Next", width=button_width, fg="#121212", bg=nextButtonColour,
                        font=buttonFont, command=lambda: [topFrame.destroy(), bottomFrame.destroy(), summonWindow3()])
    nextButton.pack(side=tkinter.RIGHT, padx=5, pady=5)
    window.protocol("WM_DELETE_WINDOW", lambda: closeButtonPress(window))


def summonWindow3():
    topFrame = tkinter.Frame(window)
    topFrame.pack(expand=True, fill=tkinter.BOTH, padx=5)
    topFrame.option_add("*Background", backgroundColour)
    bottomFrame = tkinter.Frame(window)
    bottomFrame.pack(side=tkinter.BOTTOM, fill=tkinter.X, padx=5)
    bottomFrame.option_add("*Background", backgroundColour)
    line = tkinter.Label(topFrame, text="———————————————————————————————",
                         font=buttonFont, fg=foregroundColour, anchor="center", height=1)
    first = tkinter.Label(topFrame, text="Select SD Card", font=titleFont, fg=foregroundColour)
    steps = tkinter.Label(topFrame, text="Start > Memory Pit > Homebrew >                       > Finish",
                          font=paragraphFont, fg=foregroundColour)
    stepsBold = tkinter.Label(topFrame, text="Download", font=buttonFont, fg=foregroundColour)
    line.place(x=0, y=17)
    stepsBold.place(x=250, y=0)
    steps.grid(column=0, row=0, sticky="w", padx=0)
    first.grid(column=0, row=1, sticky="w", pady=10)
    noticeLabel = tkinter.Label(topFrame, text="Plug in your SD card and select the root directory. " +
                                               "\nNot sure what \"root\" is? Check this ",
                                fg=foregroundColour, font=buttonFont, justify="left")
    link = tkinter.Label(topFrame, text="image.", font=buttonFont, fg="#3366ff", cursor="hand2")
    link.bind("<Button-1>", lambda e: webbrowser.open_new(
        "https://media.discordapp.net/attachments/489307733074640926/756947922804932739/wherestheroot.png"))
    noticeLabel.grid(column=0, row=2, sticky="w")
    link.place(x=269, y=111)
    SDentry = tkinter.Entry(topFrame, fg="#121212", bg=buttonColour, font=buttonFont, width=35)
    SDentry.grid(column=0, row=3, sticky="w")
    chooseDirButton = Button(topFrame, text="Click to select folder", command=lambda: chooseDir(SDentry),
                             fg=foregroundColour, font=buttonFont, width=folder_width)
    chooseDirButton.grid(column=0, row=4, sticky="w", pady=5)
    backButton = Button(bottomFrame, text="Back", font=buttonFont, fg="#121212", bg=backButtonColour,
                        command=lambda: [topFrame.destroy(), bottomFrame.destroy(), summonWindow2()],
                        width=button_width)
    backButton.pack(side=tkinter.LEFT)
    nextButton = Button(bottomFrame, text="Start", width=button_width, fg="#121212", bg=nextButtonColour, font=buttonFont,
                        command=lambda: [globalify(SDentry.get()), topFrame.destroy(), bottomFrame.destroy(),
                                         summonWindow4()])
    nextButton.pack(side=tkinter.RIGHT, padx=5, pady=5)
    window.protocol("WM_DELETE_WINDOW", lambda: closeButtonPress(window))


def globalify(value):
    global SDentry
    SDentry = value


def summonWindow4():
    global outputBox, finalbackButton
    startThread = threading.Thread(target=start, daemon=True)
    topFrame = tkinter.Frame(window)
    topFrame.pack(expand=True, fill=tkinter.BOTH, padx=5)
    topFrame.option_add("*Background", backgroundColour)
    bottomFrame = tkinter.Frame(window)
    bottomFrame.pack(side=tkinter.BOTTOM, fill=tkinter.X, padx=5)
    bottomFrame.option_add("*Background", backgroundColour)
    line = tkinter.Label(topFrame, text="———————————————————————————————",
                         font=buttonFont, fg=foregroundColour, anchor="center", height=1)
    first = tkinter.Label(topFrame, text="Download", font=titleFont, fg=foregroundColour)
    steps = tkinter.Label(topFrame, text="Start > Memory Pit > Homebrew >                       > Finish",
                          font=paragraphFont, fg=foregroundColour)
    stepsBold = tkinter.Label(topFrame, text="Download", font=buttonFont, fg=foregroundColour)
    line.place(x=0, y=17)
    stepsBold.place(x=250, y=0)
    steps.grid(column=0, row=0, sticky="w", padx=0)
    first.grid(column=0, row=1, sticky="w", pady=10)
    outputBox = tkinter.Text(topFrame, state='disabled', width=60, height=13, bg="black", fg="white")
    outputBox.grid(column=0, row=2, sticky="w")
    startThread.start()
    finalbackButton = Button(bottomFrame, state="disabled", text="Back", font=buttonFont, fg="#121212",
                             bg=backButtonColour,
                             command=lambda: [topFrame.destroy(), bottomFrame.destroy(), summonWindow3()],
                             width=button_width)
    finalbackButton.pack(side=tkinter.LEFT)
    global finalnextButton
    finalnextButton = Button(bottomFrame, state="disabled", text="Finish", width=button_width, fg="#121212",
                             bg=nextButtonColour, font=buttonFont,
                             command=lambda: [topFrame.destroy(), bottomFrame.destroy(), summonWindow5()])
    finalnextButton.pack(side=tkinter.RIGHT, padx=5, pady=5)
    window.protocol("WM_DELETE_WINDOW", lambda: donothing)


def summonWindow5():
    topFrame = tkinter.Frame(window)
    topFrame.pack(expand=True, fill=tkinter.BOTH, padx=5)
    topFrame.option_add("*Background", backgroundColour)
    bottomFrame = tkinter.Frame(window)
    bottomFrame.pack(side=tkinter.BOTTOM, fill=tkinter.X, padx=5)
    bottomFrame.option_add("*Background", backgroundColour)
    line = tkinter.Label(topFrame, text="———————————————————————————————",
                         font=buttonFont, fg=foregroundColour, anchor="center", height=1)
    first = tkinter.Label(topFrame, text="Completed", font=titleFont, fg=foregroundColour)
    steps = tkinter.Label(topFrame, text="Start > Memory Pit > Homebrew > Download > ",
                          font=paragraphFont, fg=foregroundColour)
    stepsBold = tkinter.Label(topFrame, text="Finish", font=buttonFont, fg=foregroundColour)
    line.place(x=0, y=17)
    stepsBold.place(x=339, y=0)
    steps.grid(column=0, row=0, sticky="w", padx=0)
    first.grid(column=0, row=1, sticky="w", pady=10)
    label = tkinter.Label(topFrame, text="Your SD card is now ready to run and use homebrew on your Nintendo DSi.",
                          font=bodyFont, fg=foregroundColour, wraplength=450, justify="left")
    label.grid(column=0, row=2, sticky="w")
    linktoguide = tkinter.Button(topFrame, text="Return to dsi.cfw.guide", command=lambda: webbrowser.open_new(
        "https://dsi.cfw.guide/launching-the-exploit.html#section-iii-launching-the-exploit="), fg=foregroundColour,
                                 font=buttonFont, width=guidebuttonwidth)
    linktoguide.grid(column=0, row=3, sticky="w")
    label = tkinter.Label(topFrame, text="Press the Close button to Exit.", font=bodyFont, fg=foregroundColour)
    label.grid(column=0, row=6, sticky="w")
    finish = Button(bottomFrame, text="Close", width=button_width, fg="#121212", bg=nextButtonColour,
                    font=buttonFont,
                    command=lambda: [topFrame.destroy(), bottomFrame.destroy(), closeButtonPress(window)])
    finish.pack(side=tkinter.RIGHT, padx=5, pady=5)
    window.protocol("WM_DELETE_WINDOW", lambda: closeButtonPress(window))


if __name__ == "__main__":
    if sys.version_info.major < 3:
        print("This program will ONLY work on Python 3 and above.")
        sys.exit()
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

    root = tkinter.Tk()
    window = tkinter.Toplevel(root)
    root.withdraw()

    #except:
    #    print("This program requires internet to run. Run this program after connecting to a WiFi network or a hotspot.")

    # TKinter Vars
    downloadmemorypit = tkinter.IntVar(value=1)
    facebookIcon = tkinter.IntVar(value=1)
    downloadtwlmenu = tkinter.IntVar(value=1)
    downloaddumptool = tkinter.IntVar(value=1)
    unlaunch = tkinter.IntVar(value=1)

    # Fonts
    firstTitleFont = tkinter.font.Font(
        family="Segoe UI",
        size=30,
        weight="bold"
    )
    titleFont = tkinter.font.Font(
        family="Segoe UI",
        size=20,
        weight="bold"
    )
    subtitleFont = tkinter.font.Font(
        family="Segoe UI",
        size=11,
        slant="italic"
    )
    bodyFont = tkinter.font.Font(
        family="Segoe UI",
        underline=False,
        size=11
    )
    buttonFont = tkinter.font.Font(
        family="Segoe UI",
        underline=False,
        size=12,
        weight="bold"
    )
    bigListFont = tkinter.font.Font(
        family="Segoe UI",
        underline=False,
        size=9
    )
    paragraphFont = tkinter.font.Font(
        family="Segoe UI",
        size=12
    )
    instructionFont = tkinter.font.Font(
        family="Segoe UI",
        size=10
    )

    if platform.system() == "Darwin":
        from tkmacosx import Button

        backgroundColour = "#f0f0f0"
        foregroundColour = "black"
        buttonColour = "#f0f0f0"
        backButtonColour = "#f0f0f0"
        nextButtonColour = "#f0f0f0"
        button_width = 80
        guidebuttonwidth = 200
        folder_width = 350
    else:
        from tkinter import Button

        backgroundColour = "#121212"
        foregroundColour = "#ffffff"
        buttonColour = "#dbdbdb"
        backButtonColour = "#f0f0f0"
        nextButtonColour = "#f0f0f0"
        button_width = 8
        guidebuttonwidth = 20
        folder_width = 35

    summonWindow0()
    root.mainloop()
