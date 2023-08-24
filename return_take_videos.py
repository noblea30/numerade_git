#this relies on main.py functions.  If they change there, better change here too.

import time
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import PySimpleGUI as sg
import traceback
import urllib.request

#variables section
import threading



import os
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import joblib


def retake_videos(driver, videos):
    path = "/html/body/div[3]/main/div/main/div[2]/div/div/div/div[2]/div/div/div[{}]/div/div/div/div/div"  #/div[2]/div[2]/div/span/p
    attempts = 20
    time.sleep(5*60)
    while len(videos) > 0 and attempts > 0:
        index = 2
        navigate_wait(driver,student_questions, "tag-style-tangerine")
        print("attempts remaining:", attempts)
        while 1:
            try:
                video = driver.find_element(By.XPATH, path.format(index))
            except:
                if open_more_videos(driver) == False:
                    break
                else:
                    time.sleep(1)
                    continue
            if want_this_video(driver, videos, video.text):
                #take it. remove from videos list.
                assign_button = driver.find_element(By.XPATH, path.format(index) + "/div[3]/button[1]")
                e = driver.find_element(By.XPATH, path.format(index) + "/div[3]/button[1]")
                e.click()
                time.sleep(.1)
                print("got it back")
                videos.remove(video)


            index +=1
        scroll_up(driver)
        attempts -=1
def scroll_up(driver):
    driver.execute_script("window.scrollTo(0, 0);")        
def want_this_video(driver, videos, text):
    t2 = text.replace("\n", "")
    for v in videos:
        if v in t2:
            return

    return False
def open_more_videos(driver):

    for i in range(10):
        try:
            e = driver.find_element(By.CLASS_NAME, "btn-style-secondary")
            e.click()
            time.sleep(.1)
            #print("it worked I guess....")
            return True
        except:
            time.sleep(.1)
    return False
        
 
def return_take():
    #open browser
    driver = open_browser("https://www.numerade.com/educator/dashboard/assigned","tag-style-standard")
    #get list of all videos
    videos = get_all_checkedout(driver)#also returns them
    #return videos
    
    #re-assign them
    retake_videos(driver,videos)
def get_all_checkedout(driver):
    #path = "/html/body/div[3]/main/div/main/div[2]/div                div[{}]/div/div/div/div/div"  #/div[2]/div[2]/div/span/p
    print("running in 1 seconds")
    time.sleep(1)
    print("going now")
    path = "/html/body/div[3]/main/div/main/div[2]/div[2]/div/div/div/div[{}]/div/div/div/div/"
    index = 1
    videos = []
    while 1:
        print(index)
        try:
            video = driver.find_element(By.XPATH, path.format(index) + "div[2]/div[2]/div/pre/span")
        except:
            break
        t = video.text
        #print(t)
        #index = t.index("ago")
        videos.append(t.replace("\n", ""))

        try:
            unassign = driver.find_element(By.XPATH, path.format(index) + "/div[3]/button")
        except:
            print("what, it isn't there?", index, path.format(index) + "/div[3]/button")
        for i in range(4):
            try:
                unassign.click()  #remove for debug
                break
            except:
                
                time.sleep(.1)
        scroll_up(driver)
        #index +=1 #only if I don't take it away

    return videos

def open_browser(url, cl_name):


    options = uc.ChromeOptions()
    profile = "C:/Users/Public/Public Documents/Chrome_details/Default"
    executable_path = "C:/Users/Public/Public Documents/Chrome_details/chromedriver_7.exe"

    options.user_data_dir = profile
    options2 = uc.ChromeOptions()
    options2.user_data_dir = profile
    driver = uc.Chrome(use_subprocess=True, options=options, executable_path=executable_path, headless = False)
    script = '''window.open("''' + url + '''");'''
    driver.execute_script(script)
    driver.switch_to.window(driver.window_handles[1])
    print("waiting")
    time.sleep(1)
    #explicit_login(driver)
    try:
        WebDriverWait(driver, 1000).until(EC.visibility_of_element_located((By.CLASS_NAME, cl_name)))  # calculus button
    except:
        print("gave up waiting for :", cl_name, " Trying again.")
        restart_and_login(driver)
        return driver
    # open question subjects tab
    # e = driver.find_elements(By.CLASS_NAME, "plan__button")
    # e[1].click()
    print("found it ")
    return driver
    
def navigate_wait(driver,url, cl_name = "tag-style-tangerine"):
    #student_questions
    driver.get(url)
    try:
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, cl_name)))  # calculus button
    except:
        print("oops, can't load url: ", url, cl_name)  #probably logged out.
        #restart_and_login(driver)    





student_questions = "https://www.numerade.com/educator/dashboard?chapterId=4&questionStudentDisplay=true&questionType=ask&chapterIds=4&question-type=ask&chapter-ids=4" #calculus

print("hello")

return_take()