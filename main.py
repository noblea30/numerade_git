print("hello world")


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

#constants.
force_take_videos_per_page = 0  #just change this variable if i want to debug.  won't actually buy, just open page  0=normal,   X=force this many to be bought.
max_fast_take_videos = 20
interval = 25 #25#60*2  # time between page refresh
added_limit = 40  # number of increased videos from last check
verbose = True  #change to true when you want to print a lot of details
min_questions = 200   #if more than 300, just go through them.  don't wait.

#model for prediction.
loaded_model = joblib.load('model.pkl')
loaded_vectorizer = joblib.load('vectorizer.pkl')
model_threshold = .35#.258
do_ai = True  #also set to ignore time as well
if force_take_videos_per_page >0:
    interval = -60 * 2  # time between page refresh
    added_limit = -10  # number of increased videos from last check

error_number = 2  # how many times I don't get a valid answer before calling me.
current_error = 0  #just set to 0 to start
avoid = []
direct_want = []
debug_time = time.time()


import openai
import string

openai.api_key = "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"

def sanitize_text(text):
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Convert to lowercase
    text = text.lower()

    # Remove multiple whitespaces and leading/trailing whitespaces
    text = ' '.join(text.split())

    # Return the sanitized text
    return text

# Create a global variable to store the model


    global model_id

    take_data_path = '../strng_model_predictor/take.txt'
    skip_data_path = '../strng_model_predictor/skip.txt'

    # Read the "take" training data from the file
    with open(take_data_path, 'r', encoding='utf-8') as file:
        take_data = file.read()

    # Read the "skip" training data from the file
    with open(skip_data_path, 'r', encoding='utf-8') as file:
        skip_data = file.read()
    # Split the "take" data into individual examples
    take_examples = take_data.split('\n')

    # Split the "skip" data into individual examples
    skip_examples = skip_data.split('\n')
    training_data = []
    for example in take_examples:
        e = sanitize_text(example)
        training_data.append(f"{e} == take")
    for example in skip_examples:
        e = sanitize_text(example)
        training_data.append(f"{e} == skip")
    # Fine-tune the GPT-3 model with the training data
    response = openai.Completion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": training_data}
        ],
        max_tokens=5,
        n=1,
        stop=None,
        temperature=0.8,
        log_level="info"
    )

    model_id = response['id']


# print("starting")
# create_model()
#
# print("done")
# exit(0)


#twilio details.
account_sid = "ACa853e4da90638c9d1babcd106b8a7039"
auth_token = "1ac15527bbbcee261e8d9ae4a312d48a"
client = Client(account_sid, auth_token)



def want_from_ai(str):
    global took_ai
    new_strings_vectorized = loaded_vectorizer.transform([str])
    probabilities = loaded_model.predict_proba(new_strings_vectorized)
    #print(probabilities)
    # if probabilities[0][0] <model_threshold:
    #     print("take", probabilities[0])
    # else:
    #     print("skip", probabilities[0])
    print(probabilities[0][0])
    if probabilities[0][0] < model_threshold:
        took_ai.append(str)
    return probabilities[0][0] < model_threshold
# Set environment variables for your credentials
# Read more at http://twil.io/secure
 #twilio.com:  ogametesting123@gmail.com, apple + aabbccdd

#not used yes.  This is for sending coded message of number of videos
def call_text_me(num):
    mess = ""
    if num == "full":
        mess = "Hello from Twilio"
    else:
        level = num//5   #0=H, 5=He, 10=l, 15= Hello, 20 = "Hello from"
        if level ==0:
            mess = "H"
        if level ==1:
            mess = "He"
        if level ==2:
            mess = "Hel"
        if level ==3:
            mess = "Hello"
        if level ==4:
            mess = "Hello from"



    text_thread = threading.Thread(target=text_me, args=(mess,))
    text_thread.start()
    text_thread.join()
#checks if I have recieved a message.  returns what the message was.
def check_messages():
    messages = client.messages.list()
    for message in messages:
        incoming_message = message.body
        #print("I got a message", message.body)
        if "Twilio" in incoming_message:
            continue
        print(incoming_message)

        clear_messages()
        if "Wait" in incoming_message:
            return "wait"
        return "check"
    clear_messages()
def send_num_videos(driver):
    num = driver.find_element(By.CLASS_NAME, "bg-tangerine2-500").text
    assigned = num.split("(")[1].split(")")[0]
    call_text_me(int(assigned))
    pass
def clear_messages():
    messages = client.messages.list()
    for message in messages:
        #print("delete:", ".",message.body,".")
        try:
            message.delete()
        except:
            time.sleep(10)
            message.delete()

#check if I have received a message.  Be careful of duplicates.
def check_for_message():
    messages = client.messages.list()
    for message in messages:
        incoming_message = message.body
        print("I got a message", message.body)
        time.sleep(20)
        message.delete()
        print("it worked?")
        continue
        response = "Yay, I got it !!!"
        response_message = MessagingResponse()
        response_message.message(response)
        client.messages.create(
            body=response_message.to_xml(),
            from_="+18885944068",
            to="+17192522375"
        )
        print("waitng")
        time.sleep(20*1000)
        print("done waiting")
        message.delete()
# print("checking now")
# while 1:
#     check_for_message()

def text_me(mess):

    message = client.messages.create(
      body=mess,
      from_="+18885944068",
      to="+17192522375"
    )

def input_with_timeout(timeout, prompt = ""):  #returns True if input recieved.  False otherwise.  Doesn't capture input
    print(prompt, end='', flush=True)
    result = []
    input_thread = threading.Thread(target=lambda: result.append(input()))
    input_thread.start()
    input_thread.join(timeout)
    if input_thread.is_alive():

        return False
    return True




def get_e(l1,l2=[], retries = 5,wait_after = True):
    if l2==[]:
        try:
            element = driver.find_element(l1[0],l1[1])  #By.ID probably
            if element == None:
                print("error, ID not found", l1)
            else:
                return element
        except Exception as exc:
            #print(traceback.format_exc())
            #print(exc)
            pass
    else:
        elements = driver.find_elements(l1[0],l1[1])  #By.CLASS_NAME likely
        if len(elements)==0:
            print("error, no elements available",l1,l2)
        else:
            for e in elements:
                if l2[0] == "text":
                    val = e.text
                else:
                    val = e.get_attribute(l2[0])
                if val == l2[1]:
                    return e
    if not wait_after:
        print("warning, attribute not found.  ignoring",l1,l2)
        return False
    print("warning, attribute not found. trying again ", retries, l1, l2)
    if not wait_after:
        return False
    if retries:
        time.sleep(1)
        return get_e(l1,l2,retries-1)
    print("error, attribute not found",l1,l2)
    print("waiting for response")

    while (1):
        time.sleep(10000)
    return False

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


#import debugging

direction  = 1
mouse_location =  pyautogui.position()
def keep_awake():
    #return
    global direction
    global mouse_location
    curr = pyautogui.position()
    if mouse_location != curr:  #I must have moved it.  dont' do anything
        mouse_location = curr
        return
    #prev = curr
    for i in range(0,50):
        pyautogui.moveTo((curr[0],curr[1]+direction*i*5))
        curr = pyautogui.position()
        time.sleep(.1)
        if pyautogui.position() != curr:
            return
    direction *= -1
    for i in range(0,3):
        pyautogui.press('shift')
    mouse_location = curr

def vprint(*args):
    if verbose:
        print(args)

#get data from file on videos I want to have

def get_direct_want_list():
    global direct_want
    direct_want = []
    with open("direct_want.txt") as f:
        lines = f.readlines()
    for l in lines:
        l=l.strip()
        dict = {}
        sp = l.split(":")
        dict["want"] = sp[0].split(",,")
        dict["not"] = sp[1].split(",,")
        direct_want.append(dict)
    #print("directWant :", direct_want)

def get_want_list():
    get_avoid_list()
    get_direct_want_list()
    want = []
    with open("do_these.txt") as f:
        lines = f.readlines()
    for l in lines:
        l=l.strip()
        dict = {}
        sp = l.split(":")
        dict["want"] = sp[0].split(",,")
        dict["not"] = sp[1].split(",,")
        want.append(dict)
    #print(want)
    #also need to do items that should be skipped?
    return want   #list of videos details.  Each contains dictionary of list of want and not strings.

def get_avoid_list():
    global avoid
    avoid = []
    with open("avoid.txt") as f:
        lines = f.readlines()
    for l in lines:
        l = l.strip()
        avoid.append(l.lower())
#get the number of questions that are avaialable for calculus
student_questions = "https://www.numerade.com/educator/dashboard?chapterId=4&questionStudentDisplay=true&questionType=ask&chapterIds=4&question-type=ask&chapter-ids=4" #calculus
#student_questions = "https://www.numerade.com/educator/dashboard?question-type=ask&chapter-ids=1" #algebra

def check_num_questions(driver):
    try:
        e = driver.find_element(By.XPATH, "/html/body/div[2]/nav/div/div/ul/li[3]")  #student questions:  incase it wasn't logged in already
        e.click()
    except:
        pass
    navigate_wait(driver, student_questions,"tag-style-tangerine" )

    time.sleep(2)
    #e = driver.find_elements(By.CLASS_NAME, "question-subject-li") #calculus button
    #print("nums", len(e))
    try:
        num = driver.find_element(By.CLASS_NAME, "tag-style-tangerine").text
        num = num.split()[0]
        if num == "0":
            print("got 0, that can't be right.  trying again.")
            time.sleep(2)
            num = driver.find_element(By.CLASS_NAME, "tag-style-tangerine").text
            num = num.split()[0]
            if num =="0":
                print("no, really, can't be right.  reload.")
                return check_num_questions(driver)
        #print(num)
        return int(num)
    except:
        print("could not find num")
        return check_num_questions(driver)  #should I throw error?
    return -1

def check_num_questions_old(driver):
    try:
        e = driver.find_element(By.XPATH, "/html/body/div[2]/nav/div/div/ul/li[3]")  #student questions:  incase it wasn't logged in already
        e.click()
    except:
        pass
    e = driver.find_elements(By.CLASS_NAME, "question-subject-li") #calculus button
    #print("nums", len(e))
    try:
        e[4].click()  #calculus button
        #e[0].click()  #all subjects.  try it out.  Didn't take anything after calculus was ran
    except:
        print("what???caculus button wasn't there.")
        restart_and_login(driver)
        return check_num_questions(driver)
    time.sleep(10)
    try:
        num = driver.find_element(By.CLASS_NAME, "tag-style-tangerine").text
        num = num.split()[0]
        if num ==0:
            print("got 0, that can't be right.  trying again.")
            return check_num_questions(driver)
        #print(num)
        return int(num)
    except:
        print("could not find num")
        return check_num_questions(driver)  #should I throw error?
    return -1

def explicit_login(driver):
    return
    #click_e("class", "LgbsSe-bN97Pc")
    print("waiting again now.")
    time.sleep(25)
    print("checking now")
    e = driver.find_elements(By.CLASS_NAME, "LgbsSe-bN97Pc")
    if e:
        e.click()
    else:
        print("login not found.")
    while 1:
        pass
#open both google voice and numerade.

def navigate_wait(driver,url = student_questions, cl_name = "tag-style-tangerine"):
    #student_questions
    driver.get(url)
    try:
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, cl_name)))  # calculus button
    except:
        print("oops, can't load url: ", url, cl_name)  #probably logged out.
        restart_and_login(driver)

def open_browser(url, cl_name):
    options = uc.ChromeOptions()
    # profile = "C:/Users/noble/AppData/Local/Google/Chrome/User Data/Default"
    # executable_path = "C:/Users/noble/Downloads/chromedriver_win32/chromedrive.exe"
    profile = "C:/Users/Public/Public Documents/Chrome_details/Default"
    executable_path = "C:/Users/Public/Public Documents/Chrome_details/chromedriver_7.exe"
    # if it stops working, need to open browser under any profile and click on "About Chrome" in settings.  This will start the update.  WHen done , just click "relaunch" and it should work now.
    print("H1")
    options.user_data_dir = profile
    options2 = uc.ChromeOptions()
    options2.user_data_dir = profile
    driver = uc.Chrome(use_subprocess=True, options=options, executable_path=executable_path, headless = False)
    #driver2 = uc.Chrome(use_subprocess=True, options=options2, executable_path=executable_path, headless= False)
    # driver.get("https://voice.google.com/u/0/messages")
    # WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.NAME, 'identifier'))).send_keys(f'{email}\n')
    # WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.NAME, 'password'))).send_keys(f'{password}\n')
    # time.sleep(5)
    # url = "https://www.numerade.com/ask/educators/"
    print("H2")
    script = '''window.open("''' + url + '''");'''
    driver.execute_script(script)
    print("H3")
    # time.sleep(15) #can reduce to 1?
    driver.switch_to.window(driver.window_handles[1])
    print("waiting")
    # WebDriverWait(driver, 40).until(EC.visibility_of_element_located((By.ID,"carouselEducatorHome"))
    time.sleep(2)
    #explicit_login(driver)
    try:
        WebDriverWait(driver, 40).until(EC.visibility_of_element_located((By.CLASS_NAME, cl_name)))  # calculus button
    except:
        print("gave up waiting for :", cl_name, " Trying again.")
        restart_and_login(driver)
        return driver
    # open question subjects tab
    # e = driver.find_elements(By.CLASS_NAME, "plan__button")
    # e[1].click()
    print("found it ")
    return driver

#this doesn't currently work.  text instead.
def call_me(driver):
    if force_take_videos_per_page>0:
        return
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(2)
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "il1"))).send_keys("7192522375\n")
    while(1):
        pass


def text_me_orig(driver):
    if force_take_videos_per_page>0:
        print("debuging, ignow text.")
        return
    print("texting now")
    #return  #removed for debug
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(2)
    #WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "mat-icon notranslate navItemIcon mat-icon-no-color"))).click()
    #e = driver.find_elements(By.CLASS_NAME, "navItemIcon") #open messages
    #e[6].click()
    try:
        e = driver.find_elements(By.CLASS_NAME, "gvMessagingView-actionButtonIcon") #new message
        e[0].click()
    except:
        print("can't click new message")
    #e = driver.find_elements(By.CLASS_NAME, "gvMessagingView-actionButtonIcon")  # new message
    try:
        e = driver.find_element(By.ID, "input_0").send_keys("7192522375\n") #phonenumber
        e = driver.find_element(By.ID, "input_1").send_keys("yeppers\n")  # phonenumber
        driver.switch_to.window(driver.window_handles[1])
    except:
        print("can't send message")
        driver.switch_to.window(driver.window_handles[1])
attempts_to_fix = 1
def fix_video_errors(driver):
   global attempts_to_fix
   attempts_to_fix+=1
   print("trying again, attempt: ",attempts_to_fix )
   driver.get("https://www.numerade.com/educator/dashboard/assigned")
   time.sleep(2)
   #driver.get("https://www.numerade.com/educator/dashboard/student_questions")
   driver.get(student_questions)
   videos = check_num_questions(driver)
   taken = add_questions(driver,get_full=True)
   if taken <5:
        return fix_video_errors(driver)
   return taken
def watch_for_questions(driver,previous_videos):
    t = time.time()
    global current_error, total_videos_trickled, debug_num
    #max_questions = 5  #how many questions will I check at the top before concluding that I don't want to check any more.
    total_trickle_taken = 0
    total_mass_taken = 0
    add_questions(driver,get_full = False, take_videos=True)
    total_videos_trickled =0
    while(1):
        keep_awake()
        message = check_messages()
        if message == "wait":
            print("waiting due to request.")
            time.sleep(15 * 60)  # wait 15 minutes.
            continue

        if message == "check":
            send_num_videos(driver)
        if time.time()<t + interval:  #testing this to see if it doesn't hang computer as bad.
            time.sleep(t+interval - time.time())
        if (time.time()>t+interval) or (previous_videos ==-1):  #has it been long enough yet?

            videos = check_num_questions(driver)

            if videos == -1:
                current_error += 0  #set to 0 becuase actual videos is 55
                if current_error > error_number:
                    #text_me(driver)
                    print("this shouldn't happen!!!!!! 432342")
                    break   #hopefully this doesn't happen at all.
                continue
            current_error = 0
            t = time.time()
            if previous_videos == -1:
                previous_videos = videos
                continue
            #should normally get to here when I'm checking.
            #print(type(videos), type(previous_videos), type(added_limit))

            if videos > previous_videos + added_limit:
                print("calling text now: " + str(videos))
                #text_thread = threading.Thread(target=text_me, args=("Hello from Twilio",))
                #text_thread.start()
                call_text_me("full")
                taken = add_questions(driver, get_full=True)  #run it three times.  I can stop manually if needed
                write_list_to_file("ai.txt", took_ai)  #this will be overridden if I let it finish.
                write_list_to_file("old.txt", took_old)
                taken += add_questions(driver, get_full=True)
                taken += add_questions(driver, get_full=True)
                if taken < 0:   #this should be 5 for a full run, changing to trickle only now.
                    print("didn't take enough.  go again I guess?")
                    scroll_up(driver)
                    check_num_questions(driver)
                    taken += fix_video_errors(driver) #add_questions(driver, get_full=True)
                #text_thread.join()
                previous_videos = videos - taken
                total_mass_taken += taken
                print("How many of each.  old, ai   :   ", len(took_old), len(took_ai))
                write_list_to_file("ai.txt", took_ai)
                write_list_to_file("old.txt", took_old)
                while 1:
                    pass  #for now, just wait for it to go....will change it later.
            elif videos > previous_videos:  #do full trickle.
                print("saw an added video.  adding questions.")
                taken = add_questions(driver)
                previous_videos = videos - taken
            else:
                pass
                print("none new.  ", videos, previous_videos )
                previous_videos = videos
                #print("")
                # try:
                #     taken = add_questions(driver,get_full=False) #check top videos against list of checked videos.  If new, take them.  return hom many I added in this run
                #     previous_videos = videos - taken
                #     total_trickle_taken+=taken
                # except Exception:
                #     traceback.print_exc()  #I'm assuming for now that the browser was closed.  Re-open it.


                #print("total_trickle", total_trickle_taken)
            print(time.strftime("%H:%M:%S", time.localtime()), videos, "len", len(videos_checked), "taken", total_trickle_taken, "trickled",total_videos_trickled, "mass", total_mass_taken, "debug:", debug_num)
            #print(videos_checked)
    print("here1")
#get a list of all elements that represent videos
def scroll_up(driver):
    driver.execute_script("window.scrollTo(0, 0);")
def scroll_down(driver):
    driver.execute_script("window.scrollTo(150, 150);")
def scroll_bottom_of_page(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height <= last_height:
            break
        print("added a bit more videos")
        last_height = new_height
def scroll_bottom_of_page_a(driver):
    #scroll down to the bottom of current page
    #load extra items there
    #continue until all items loaded.
    num = check_num_questions(driver)
    elements = driver.find_elements(By.CLASS_NAME, "bungalow-card-body-wrapper")
    print("we now have ", num, len(elements))
    if len(elements) >= num-1:
        print("scrolled all the way down")
        return elements
    for i in range(20):
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(1)
        elements = driver.find_elements(By.CLASS_NAME, "bungalow-card-body-wrapper")
        print("we now have ", num, len(elements))
        if len(elements) >= num:
            return elements

checked_text  = []
lock = threading.Lock()
list_lock = threading.Lock()
def process_element(driver, path):
    e = driver.find_element(By.XPATH, path)
    t = e.text
    with lock:
        if t in checked_text:
            return 0
        checked_text.append(t)
    return 1

def debug_time(e,by, val, times):
    t1 = time.time()
    for i in range(times):
        e2 = e.find_element(by, val)
        t = e2.text
    t2 = time.time()
    return t2-t1
def debug_threading_text(driver,e):
    return e.text

def debug_time_sets():
    lst  =[]
    s = set()
    for i in range(1000):
        st = "aabbccddeeddfs"*50 + str(i)
        #print(st)
        lst.append(st)
        s.add(st)

    print("starting now.")
    t1 = time.time()
    for t in s:
        if(t in lst):
            pass#print("yep")
    t2 = time.time()
    print("list:", t2-t1)
    for t in lst:
        if(t in s):
            pass
    t3 = time.time()
    print("set:", t3-t2)
# debug_time_sets()
# exit(0)



def debug_find_videos(driver):

    path = "/html/body/div[3]/main/div/div/div[2]/div[2]/div/div/div[{}]/div/div/div/div/div" #/div[2]/div[2]/div/span/p"
    cl = "section-frame"
    t1 = time.time()
    for i in range(2,52):
        e= driver.find_element(By.XPATH, path.format(i))
        t = e.text
    t2 = time.time()
    print("basic:", t2-t1)

    e = driver.find_element(By.XPATH, path.format(2))
    e_text = threading.Thread(target=debug_threading_text, args = (driver,e))
    e_text.start()
    for i in range(3,52):
        e = driver.find_element(By.XPATH, path.format(i))
        e_text.join()
        e_text = threading.Thread(target=debug_threading_text, args=(driver, e))
        e_text.start()
    print("threading:", time.time()-t2)
    t1 = time.time()
    # create a list of threads
    threads = []
    for i in range(2, 52):
        t = threading.Thread(target=process_element, args=(driver, path.format(i)))
        t.start()
        threads.append(t)

    # wait for all threads to complete
    for t in threads:
        t.join()
    t2 = time.time()
    print("full threading:", t2-t1)
    # text_thread = threading.Thread(target=text_me, args = ("message 4",))
    # text_thread.start()
    # text_thread.join()

num_threads = 0
def process_element_thread(driver, video, lock, list_lock, full_get, index, path, want, take_videos):
    global num_videos_taken, num_threads
    #print("checking element in thread")
    if want_this_video(video, want, full_get, take_videos, list_lock):
        try:
            assign_button = driver.find_element(By.XPATH, path.format(index) + "/div[3]/button[1]")
        except:
            print("H3:", "consider checking path variable against button xpath.  It has changed in the past", index)
            print("program waiting for input")
            while 1:
                pass
        with lock:
            for i in range(1): #removed loop since now I use the click method
                try:
                    e = driver.find_element(By.XPATH, path.format(index) + "/div[3]/button[1]")
                    click(driver,e)
                    time.sleep(.1)
                    print("successfully took video")
                    break
                except Exception:
                    # traceback.print_exc()
                    print("didn't work to click")  # is there a difference between if there is an image or not?
                    time.sleep(.3)  # .1 works, but it is clicking a lot?
        num_videos_taken += 1
    num_threads-=1

num_videos_taken =0

def click(driver, e):
    try:
        e.click()
    except:
        time.sleep(1)
        driver.execute_script("window.scrollBy(0,10);")
        try:
            e.click()
        except:
            time.sleep(1)
            driver.execute_script("window.scrollBy(0,-20);")
            try:
                e.click()
            except:
                print("didn't work at all...")
                #return click(driver,e)
                return
    print("yay, it worked!!")

def click_old(driver, e):
    # path = "/html/body/div[3]/main/div/div/div[2]/div/div/div/div[2]/div/div/div[10]/div/div/div/div/div"  #/div[2]/div[2]/div/span/p
    # time.sleep(20)
    # e = driver.find_element(By.XPATH, path)
    try:
        e.click()
    except:
        time.sleep(1)
        updated_y = e.location_once_scrolled_into_view['y']
        print(updated_y)
        if updated_y >0:
            while 1:
                try:
                    print("A")
                    time.sleep(10)
                    driver.execute_script("window.scrollTo(0,929)")

                    print("B")
                    time.sleep(10)
                    e.click()
                    print("top worked")
                    return
                except:
                    print("top not working")
                    pass
        else:
            while 1:
                    try:

                        driver.execute_script("window.scrollTo(0,-50)")
                        e.click()
                        print("below worked")
                        return
                    except:
                        print("below not working")
                        pass
    while 1:
        pass
    while updated_y< 0:
        #driver.execute_script("arguments[0].scrollIntoView(true);", element)
        driver.execute_script("window.scrollTo(0,-1000)")
        updated_y = e.location_once_scrolled_into_view['y']
        time.sleep(1)
        print(updated_y)
   #updated_y = e.location_once_scrolled_into_view['y']
    while updated_y != 1:
        print(updated_y)
        updated_y = e.location_once_scrolled_into_view['y']
    #e.click()
    try:
        e.click()
        print("yep, got it.")
    except:
        print("nope, didn't work")
        while 1:
            pass
    while 1:
        pass
    while 1:
        # print(e.location['y'])
        #         # print(driver.execute_script("return window."))
        #viewport_height = driver.execute_script("return window.innerHeight;")
        #updated_y = driver.execute_script(f"return arguments[0].getBoundingClientRect().top + window.pageYOffset - {viewport_height};", e)
        updated_y = e.location_once_scrolled_into_view['y']
        print(updated_y)
        #driver.execute_script("arguments[0].scrollIntoView(true);", e)
        time.sleep(2)

    y = e.location['y']




    wait = WebDriverWait(driver, 10)
    driver.execute_script("arguments[0].scrollIntoView(true);", e)
    wait.until(EC.visibility_of(e))
    e.click()

def get_videos_on_page_fast(driver, want,total_videos,full_get = True, take_videos =True): #max checks is the maximum videos to check.  If set 0 zero, check them all (non zero means trickle videos)
    global num_threads
    if full_get ==True or full_get == False:  #always run it.
        time.sleep(4)
        # e = driver.find_elements(By.CLASS_NAME, "question-subject-li")  # calculus button
        # e[4].click()
        # time.sleep(1)
        navigate_wait(driver,student_questions, "tag-style-tangerine")
        #open_more_videos(driver)
        time.sleep(2)
        #scroll_bottom_of_page(driver)
    global num_videos_taken
    #path = "/html/body/div[2]/main/div/div/div[2]/div[2]/div/div/div[{}]/div/div/div/div"
    #path = "/html/body/div[2]/main/div/div/div[2]/div[2]/div/div/div[{}]/div/div/div/div/div"
    #path =  "/html/body/div[3]/main/div/div/div[2]/div[2]/div/div/div[{}]/div/div/div/div/div" #/div[2]/div[2]/div/span/p"
    path = "/html/body/div[3]/main/div/div/div[2]/div/div/div/div[2]/div/div/div[{}]/div/div/div/div/div"  #/div[2]/div[2]/div/span/p
    path = "/html/body/div[3]/main/div/main/div[2]/div/div/div/div[2]/div/div/div[{}]/div/div/div/div/div"  #/div[2]/div[2]/div/span/p

    scroll_up(driver)
    #video = driver.find_element(By.XPATH,path.format(2))  #first video is index 2
    index = 2 #first video
    num_videos_taken =0
    threads = []
    if full_get == True:
        print("checking them now")
    t1 = time.time()
    while 1:
        try:
            video = driver.find_element(By.XPATH, path.format(index))
        except Exception:
            if index < 4:
                traceback.print_exc()  #this should happen when index is too big.
                print("")
                print("")
                print("didn't work!!!!!!! what happened!!! waiting", index)
                time.sleep(2)
                # while 1:
                #     pass
                continue
            #print("index too big?", index)
            if open_more_videos(driver, lock) == False:
                #time.sleep(10)
                break
            else:
                time.sleep(1)
                continue
        #print("in while loop now.")
        # while num_threads > 4:
        #     print("waiting for threads....", num_threads)
        #     pass
        process_element_thread(driver, video, lock,list_lock, full_get,index,path,want,take_videos)
        #     t = threading.Thread(target=process_element_thread, args=(driver, video, lock,list_lock, full_get,index,path,want,take_videos))
        #     t.start()
        #     threads.append(t)
        #     print(index)
        #     num_threads +=1
        index+=1
        #
        # for t in threads:
        #     t.join()

    scroll_up(driver)
    print("all done", num_videos_taken)
    return num_videos_taken



def get_videos_on_page_fast_old(driver, want,total_videos,full_get = True, take_videos =True): #max checks is the maximum videos to check.  If set 0 zero, check them all (non zero means trickle videos)
    if full_get ==True or full_get == False:  #always run it.
        time.sleep(4)
        # e = driver.find_elements(By.CLASS_NAME, "question-subject-li")  # calculus button
        # e[4].click()
        # time.sleep(1)
        navigate_wait(driver,student_questions, "tag-style-tangerine")
        scroll_bottom_of_page(driver)
    global num_videos_taken
    #path = "/html/body/div[2]/main/div/div/div[2]/div[2]/div/div/div[{}]/div/div/div/div"
    #path = "/html/body/div[2]/main/div/div/div[2]/div[2]/div/div/div[{}]/div/div/div/div/div"
    #path =  "/html/body/div[3]/main/div/div/div[2]/div[2]/div/div/div[{}]/div/div/div/div/div" #/div[2]/div[2]/div/span/p"
    path = "/html/body/div[3]/main/div/div/div[2]/div/div/div/div[2]/div/div/div[{}]/div/div/div/div/div"  #/div[2]/div[2]/div/span/p

    scroll_up(driver)
    #video = driver.find_element(By.XPATH,path.format(2))  #first video is index 2
    index = 2 #first video
    num_videos_taken =0
    threads = []
    if full_get == True:
        print("checking them now")
    t1 = time.time()
    while 1:
        try:
            video = driver.find_element(By.XPATH, path.format(index))
        except Exception:
            if index < 4:
                traceback.print_exc()  #this should happen when index is too big.
                print("")
                print("")
                print("didn't work!!!!!!! what happened!!! waiting now....")
                while 1:
                    pass
            #print("index too big?", index)
            break
        #print("in while loop now.")
        t = threading.Thread(target=process_element_thread, args=(driver, video, lock,list_lock, full_get,index,path,want,take_videos))
        t.start()
        threads.append(t)

        index+=1

    for t in threads:
        t.join()
    #print("fast took:",time.time()-t1)
    scroll_up(driver)
    print("all done", num_videos_taken)
    return num_videos_taken


def restart_and_login(driver):

    #driver.get("https://www.numerade.com/login/")
    #time.sleep(10)
    try:
        wait = WebDriverWait(driver, 10)
        button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='login__button btn-base'][contains(text(), 'Log In With Email')]")))
        button.click()
    except:
        return  #it wasn't logged out.  something else, we will just wait.



    return navigate_wait(driver)

    time.sleep(5)
    print("now logged it")
    #url = "https://www.numerade.com/educator/dashboard/student_questions"
    url = student_questions


    cl_name = "question-subject-li"

    print("going to URL now for questions")
    driver.get(url)
    print("should be going to questions now.")
    #time.sleep(10)


    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, cl_name)))
    time.sleep(5)


def update_time(message):
    global debug_time
    print("Time:",time.time()-debug_time,":",message)
    debug_time = time.time()
def all_there(str, the_good):
    #vprint("the_good", the_good)
    for g in the_good:
        if g.lower() not in str:
            #vprint("failed because not found: ",g)
            return False
        # else:
        #     vprint("passed check on : ", g)
    return True

def none_there(t, the_bad):
    #vprint("the_bad", the_bad)
    for g in the_bad:
        if g in t:
            vprint("failed because found :",g)
            return False
        # else:
        #     vprint("passed check on :",g)
    return True

def debug_chosen(t,the_good,the_bad):
    print("debugging why")
    print(t,the_good,the_bad)

    for g in the_bad:
        print(g in t, "for " + g,"in " , t)
        if g in t:
            print("actual: ", g in t)
    print("done debugging")
# def vcheck(*args):
#     print("args is", args)
#     print("first arg is", args[0])
#     there = "\\x" in args[0]
#     print("is it there?", there)

def invalid_character(t):
    invalid_c = [226,136, 146]
    for c in t:
        if ord(c) in invalid_c:
            return True

def save_question_details(e, full_get, take_videos,reason = ""):
    return
    if full_get ==True or take_videos==False :
        return
    #parent = e.find_element(By.XPATH, "..")
    #print("saving something now...what?")
    href_element = e.find_element(By.XPATH, ".//*[@href]")
    t = e.text.replace("\n"," ")
    #print("save some text: " + t)
    with open("passed_on/text.txt", "a") as f:
        try:
            f.write(reason + "\n\n" + t + "\n\n\n\n\n\n\n")
        except:
            print("couldn't write text:\n" + t)

    href = href_element.get_attribute("href")
    #print("href=", href)

    if "png" in href:
        #print("saving an image")
        t = int(time.time())
        urllib.request.urlretrieve(href, "passed_on/image_"  + reason+ "_" +  str(t) + ".jpg")

def reassign_videos(driver):
    #for all videos currently assigned, un, than re-assign them to restart timer.
    driver.get("https://www.numerade.com/educator/dashboard/assigned")
    time.sleep(10)
    #/ html / body / div[3] / main / div / div[2] / div[1] / div / div / div[1] / div / div / div / div / div[2] / div[
    #    2] / div / p / span

    #/ html / body / div[3] / main / div / div[2] / div[1] / div / div / div[2] / div / div / div / div / div[2] / div[
    #    2] / div / p / span

    #/ html / body / div[3] / main / div / div[2] / div[1] / div / div / div[3] / div / div / div / div / div[2] / div[
    #    2] / div / p / span

    #save text of videos
    xpath = "/html/body/div[3]/main/div/div[2]/div[1]/div/div/div[{}]/div/div/div/div/div[2]/div[2]/div/p"
    keep = []
    for i in range(1,100):
        try:
            path = xpath.format(i)
            e = driver.find_element(By.XPATH,path)
            t = e.text
            keep.append(t)
        except:
            break

    print(len(keep), "videos are assigned.")

    #unassign videos
    xpath =  "/html/body/div[3]/main/div/div[2]/div[1]/div/div/div[1]/div/div/div/div/div[3]/button"
    while 1:
        try:
            e = driver.find_element(By.XPATH, xpath)
            print(e)
            try:
                e.click()
            except:
                #scroll_down(driver)
                time.sleep(1)
                #e.click()
            time.sleep(1)
        except:
            break
    i = 0
    taken = 0
    xpath = "/html/body/div[3]/main/div/div/div[2]/div[2]/div/div/div[{}]/div/div/div/div/div/div[2]/div[2]/div/p"

    button =  "/html/body/div[3]/main/div/div/div[2]/div[2]/div/div/div[{}]/div/div/div/div/div/div[3]/button"
    #driver.get("https://www.numerade.com/educator/dashboard/student_questions")
    driver.get(student_questions)
    time.sleep(15)
    while 1:
        try:
            i+=1
            e = driver.find_element(By.XPATH, xpath.format(i))
            if e.text in keep:
                b = driver.find_element(By.XPATH, button.format(i))
                i=0
                taken+=1
        except:
            break

    print("done")
    while 1:
        pass




videos_checked = set()
total_videos_trickled = 0
new_videos = set()

debug_num = 0  #keep track of num trickled.  never delete though.

debug_ignore = []

def want_from_keywords(want,t):
    global took_old
    if invalid_character(t):
        #print("failed to invalid character")
        #save_question_details(e,full_get, take_videos,"invalid")
        return False

    for i in range(len(direct_want)):

        w = direct_want[i]
        the_good = w['want']
        the_bad = w['not']
        try:
            if(all_there(t,the_good) and none_there(t,the_bad)):
                #print("video chosen based on direct", direct_want[i])
                took_old.append(t)
                #debug_chosen(t,the_good,the_bad)
                return True
        except:
            print("error stale element?")
            return False
    for a in avoid:
        if a in t:
            #print("Failed because we don't want ", a)
            #save_question_details(e,full_get, take_videos,"avoid")
            return False
        # else:
        #     vprint("Passed check on ", a)
    for i in range(len(want)):
        w = want[i]
        the_good = w['want']
        the_bad = w['not']
        try:
            if(all_there(t,the_good) and none_there(t,the_bad)):
                #print("video chosen based on ", want[i])
                #debug_chosen(t,the_good,the_bad)
                took_old.append(t)
                return True
        except:
            print("error stale element?",e)
    #print("video not chosen:", t)
    #save_question_details(e,full_get, take_videos,)
    return False

took_old = []
took_ai = []


def write_list_to_file(filename, data_list):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            for item in data_list:
                try:
                    file.write(str(item) + '\n')
                except Exception as e:
                    print(f"Skipping entry: {item} due to encoding error.")
        print(f"Data written to '{filename}' successfully.")
    except Exception as e:
        print(f"Error writing to '{filename}': {e}")


def want_this_video(e,want, full_get = False,take_videos=0, list_lock = None):
    global videos_checked, total_videos_trickled, new_videos, debug_num
    max_text_length = 164
    #print("want this video?")
    try:
        t = e.text.lower().replace("\n", " ")
        index = t.index("ago")
        if (not "minute" in t[:index]):
            #print("too old: ", t[:15])
            return False  #don't do old ones
            pass  #for if last line gets commented out.

        if (not "calculus $5.00" in t) and (not "algebra $2.50" in t) and (not "precalculus $2.50" in t):

            if not (t[:15] in debug_ignore):  #just for debug.
                debug_ignore.append(t[:15])
                #print("ignoring this one: ", t[:15])
            return False
        t = t[index:]




    except:
        #print("error, it is stale?", e)
        return False
    #print("called want_this_video,", e.text.lower().replace("\n", " "))

    #debug_num +=1
    if list_lock ==None:
        if t[0:max_text_length] in videos_checked:
            new_videos.add(t[0:max_text_length])
            return False
        if t[0:max_text_length] in new_videos:
            return False
    else:
        with list_lock:
            if t[0:max_text_length] in videos_checked:
                new_videos.add(t[0:max_text_length])
                return False
            if t[0:max_text_length] in new_videos:
                return False



    #print("post",t,videos_checked)
    if full_get == False:
        total_videos_trickled +=1
        print("checking new video:  ", t, "                                           :")
    if list_lock ==None:
        videos_checked.add(t[0:max_text_length])
        new_videos.add(t[0:max_text_length])
    else:
        with list_lock:
            videos_checked.add(t[0:max_text_length])
            new_videos.add(t[0:max_text_length])
    #if len(videos_checked)>2000:
    #    videos_checked = videos_checked[10:-1] #just cut off 10 videos for now.  This will happen often, really only need it to be 1 I think.  either way....
    if take_videos == False:
        print("haha, not taking videos at all...")
        return False
    take_it = False
    if want_from_ai(t):
        take_it = True
    elif want_from_keywords(want,t):
        #take_it = True
        pass  #turing off old method.
    if take_it:
        return True
    # if want_from_keywords(want,t) or want_from_ai(t):
    #         debug_num+=1
    #         #print("ai took it", t)
    #         return True

    # if want_from_keywords(want,t):
    #         return True

    return False




def want_this_video_orig(e,want, full_get = False,take_videos=0, list_lock = None):
    global videos_checked, total_videos_trickled, new_videos, debug_num
    max_text_length = 164
    #print("want this video?")
    try:
        t = e.text.lower().replace("\n", " ")
        index = t.index("ago")
        if (not "minute" in t[:index]):
            #print("too old: ", t[:15])
            return False
        if not "calculus $5.00" in t or "algebra $2.50" in t or "precalculus #2.50" in t:
            #print("ignoring this one: ", t[:15])
            return False
        t = t[index:]


    except:
        #print("error, it is stale?", e)
        return False
    #print("called want_this_video,", e.text.lower().replace("\n", " "))

    #debug_num +=1
    if list_lock ==None:
        if t[0:max_text_length] in videos_checked:
            new_videos.add(t[0:max_text_length])
            return False
        if t[0:max_text_length] in new_videos:
            return False
    else:
        with list_lock:
            if t[0:max_text_length] in videos_checked:
                new_videos.add(t[0:max_text_length])
                return False
            if t[0:max_text_length] in new_videos:
                return False



    #print("post",t,videos_checked)
    if full_get == False:
        total_videos_trickled +=1
        print("checking new video:  ", t, "                                           :")
    if list_lock ==None:
        videos_checked.add(t[0:max_text_length])
        new_videos.add(t[0:max_text_length])
    else:
        with list_lock:
            videos_checked.add(t[0:max_text_length])
            new_videos.add(t[0:max_text_length])
    #if len(videos_checked)>2000:
    #    videos_checked = videos_checked[10:-1] #just cut off 10 videos for now.  This will happen often, really only need it to be 1 I think.  either way....
    if take_videos == False:
        return
    if invalid_character(t):
        print("failed to invalid character")
        save_question_details(e,full_get, take_videos,"invalid")
        return False

    for i in range(len(direct_want)):
        w = direct_want[i]
        the_good = w['want']
        the_bad = w['not']
        try:
            if(all_there(t,the_good) and none_there(t,the_bad)):
                print("video chosen based on direct", direct_want[i])
                #debug_chosen(t,the_good,the_bad)
                return True
        except:
            print("error stale element?",e)
    for a in avoid:
        if a in t:
            vprint("Failed because we don't want ", a)
            save_question_details(e,full_get, take_videos,"avoid")
            return False
        # else:
        #     vprint("Passed check on ", a)
    for i in range(len(want)):
        w = want[i]
        the_good = w['want']
        the_bad = w['not']
        try:
            if(all_there(t,the_good) and none_there(t,the_bad)):
                print("video chosen based on ", want[i])
                #debug_chosen(t,the_good,the_bad)
                return True
        except:
            print("error stale element?",e)
    #print(t)
    save_question_details(e,full_get, take_videos,)
    return False

def take_videos(driver,chosen_videos):
    #open them all
    if len(chosen_videos) ==0:
        return

    #clicklnk = Keys.chord(Keys.CONTROL, Keys.ENTER)
    hrefs = []
    for e in chosen_videos:
        try:
            children = e.find_elements(By.XPATH, "*")
            child = children[0]
            grandchildren = child.find_elements(By.XPATH, "*")
            grandchild = grandchildren[0]
            hrefs.append(grandchild.get_attribute("href"))
            # href = e.get_attribute("href")
        except:
            print("oops, couldn't find sref ", e)
        #e.send_keys(Keys.CONTROL, Keys.ENTER)
    for href in hrefs:
        try:
            script = '''window.open("''' + href + '''");'''
            driver.execute_script(script)
        except:
            print("oops, couldn't open sref")
    #print("done now opening tabs")
    time.sleep(1)  #only for debug
    #assign them and close tabs
    for i in range(2,len(driver.window_handles)):
        driver.switch_to.window(driver.window_handles[2])  #always 2 because I will close the tab after.
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "add-answer-button")))
        e = driver.find_elements(By.CLASS_NAME, "add-answer-button")
        print(len(e))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        if force_take_videos_per_page<=100:  #changed to 100 for debug.  SHould be 0.
            try:
                #e[0].click()  #removed for debug reasons.
                href = e[0].get_attribute("href")
                href = "www.google.com"
                script = '''window.open("''' + href + '''");'''
                driver.execute_script(script)
            except Exception as exp:
                print(exp)
                while 1:
                    pass
            time.sleep(1)   #added for debug.  Issue is that I dont' take all the videos the code says it does.  may make permanent
            driver.close() #removed for debug reasons.
    driver.switch_to.window(driver.window_handles[1]) #go back to main numerade tab.
    time.sleep(1)
    #print("done gathering this page")
def click_next_page(driver):
    e = driver.find_elements(By.CLASS_NAME, "bottom-pagination")
    children = e[0].find_elements(By.XPATH,"*")
    t = children[-1].text
    if t == "":  #not the last page
        print("next page")
        try:
            children[-1].click()
        except Exception:
            traceback.print_exc()
            return click_next_page(driver)
        e1 = driver.find_elements(By.CLASS_NAME, "ask-chapterization-question-r")[1]
        while 1:  # wait for the element to be gone.
            try:
                a = e1.text
            except:
                break
        #time.sleep(.5)  # not sure here?
        #time.sleep(1)  #This was here instead of .1
        return False
    print("last page")
    return True  #it was the last page.

def print_longest_time(ta):
    diff = 0
    t1 = 0
    val = ""
    for t in ta.keys():
        if t1 == 0:
            t1 = t
        else:
            d = t-t1
            print(t1,t,d,diff, val, ta[t])
            if d> diff:
                diff = d
                val = ta[t]
                print("best set")
            t1 = t

    print("longest is :", val, diff)

class time_diff_stuct:
    ta  = {}
    times = []
    names = []
    times.append(time.time())
    names.append("start")
    def add(self,val):
        self.times.append(time.time())
        self.names.append(val)
    def print_longest_time(self):
        diff = 0
        val = ""
        for i in range(1,len(self.times)):
            d = self.times[i] - self.times[i-1]
            print(self.times[i], self.times[i - 1], d,diff, val,self.names[i])
            if d>diff:
                diff = d
                val = self.names[i]
        print("longest time is : ", val, diff)



def add_questions(driver,get_full = True, take_videos = True):
    #print("H2")
    global new_videos, videos_checked
    total_videos = 0
    new_videos  =set()
    for i in range(1):
            want = get_want_list()
            t1 = time.time()
            #scroll to the bottom to load all questions a few tim
            #print("before I start:  ", videos_checked)
            num = get_videos_on_page_fast(driver,want,total_videos,get_full, take_videos)  #need to do full get as well.
            # if take_videos == True:
            #     print("took: ", time.time()-t1)
            #     while 1:
            #         pass
            videos_checked = new_videos
            return num
            print("this page chose : ", num)
            t2 = time.time()
            print("it took", t2-t1, "for ", total_videos, "videos")
    num = check_num_questions(driver)
    print("all passes done: ", total_videos, "debug:", debug_num)
    return total_videos

def debug_all_questions():
    #print("h1")
    driver = open_browser("https://www.numerade.com/educators/questions/", "assigned-question__question-text")
    #print("h2")
    #driver.get("https://www.numerade.com/educators/questions/")
    layout = [[sg.Button("Ignore")]]
    #print("h3")
    window = sg.Window('hi',layout=layout)
    #print("here I am")
    time.sleep(1)
    while 1:

        elements = driver.find_elements(By.CLASS_NAME, "assigned-question__question-text")
        #buttons = driver.find_elements(By.CLASS_NAME, "assigned-question__question-btn-answer")
        if len(elements) ==0:
            print("error, trying again")
            time.sleep(1)
        else:
            print("checking videos now")
            break

    want = get_want_list()
    for e in elements:
        result = want_this_video(e,want)
        if result:
            continue
        else:
            print("need to add this video:\n\n")
            print(e.text)
            add_it = True
            while(want_this_video(e,want) ==False):
                try:
                    want1 = get_want_list()
                    want = want1
                except:
                    print("error, bad want list")
                    continue
                event, values = window.read(timeout=100)
                #print("clicked")
                if event =="Ignore":
                    add_it = False
                    print("ignore hit")
                    break
                #what if I don't wan to add it?
                pass
            print("it's Done now with that video")
            if add_it:
                print("video added.")
            else:
                print("video NOT added")
    print("done checking all videos")
    while 1:
        pass
def debug_single_question():
    global verbose
    verbose = True
    while(1):
        try:
            #time.sleep(15)  # give a minute to pull up the question.
            #print("checking current question")
            want = get_want_list()
            #parent = get_e([By.CLASS_NAME,"ask-question-r"],[],0,False)
            #child = parent.find_elements(By.XPATH,"*")[0]
            #text = child.text
            element = driver.find_element(By.XPATH,"//*[@id='container']/div[2]/p")
            #print(element.text)
            result = want_this_video(element,want)
            if result:
                time.sleep(10)
            #print("want it? " , result)
        except Exception as exc:
            #print(exc)
            time.sleep(10)


def get_num_assigned(driver):
    e = driver.find_element(By.CLASS_NAME,"bg-tangerine2-500")
    try:
        num = int(e.text.split("(")[1].split(")")[0])
        print("taken:", num)
    except:
        print("can't get num taken:", e.text)
        while 1:
            pass
    return num
def open_more_videos(driver, lock):
    if get_num_assigned(driver) >= 99:
        print("all done, 99 checked out!!!!")
        return False
    with lock:
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


def debug_code(driver):
    #open the browser, wait for input then call whatever function is desired
    # want = get_want_list()
    # str = input("waiting for input")
    #
    # get_videos_on_page_new(driver, want, total_videos)



    time.sleep(10)
    while open_more_videos(driver):
        pass
    #open_more_videos(driver)
    while 1:
        pass


    print("going")
    scroll_down(driver)
    try:
        e = driver.find_element(By.CLASS_NAME, "btn-default-all")
        print("got it")

        e.click()
        print("done now")

    except:
        print("couldn't find it???")
        try:
            e = driver.find_element(By.CLASS_NAME, "btn-style-secondary")
            print("got it")
            e.click()
        except:
            print("well didn't work")
    while 1:
        pass
print("going now")

#driver = open_browser("https://www.numerade.com/educator/dashboard/student_questions","question-subject-li")
driver = open_browser(student_questions,"tag-style-tangerine")
#click(driver,None)

#ebug_code(driver)
clear_messages()
print('here now')
#debug_code()
#text_me(driver)
#debug_single_question()
#restart_and_login(driver)
#add_questions(driver,take_videos=False)
num = check_num_questions(driver)
get_num_assigned(driver)
print(num)
watch_for_questions(driver, num)  #text and gather questions when they become available.


while 1:
    print("oops, shouldn't happen!!!! 43234")
    time.sleep(100000)