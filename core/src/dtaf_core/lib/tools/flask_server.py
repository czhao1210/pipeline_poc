#! /bin/usr/python
#revision 1.1 10-jan-2020
"""
created it
"""
#revision 1.2 10-feb-2020
"""
added timeout support for ac/dc/physical control so it fetches frm the cfg or parameter
and delays the relay channel according to the timeout specified.
"""
#revison 1.3 29-feb-2020
"""
added ifwi flash support
"""
#revison 1.4 12-march-2020
"""
made changes in flash folder creation and modified print statement
"""
#revison 1.5 13-march-2020
"""
string changed to str in write in find operation #bug
refined better logic
"""
#revios 1.6 23-march-2020
"""
camera
timing made optional
jumper for vcc cut initialized automatically for chip write identify read
timing adjusted for sp and d,e,ws segment
pythonsv connection done
"""
#revision 1.7 21-may-2020
"""
multi-threading
upload and dowload service for ifwi/bmc image
"""
#revision 1.7a 4-jun-2020
"""
hostname added
"""
import six
import re
import sys
import time
import os
import subprocess
import datetime
import mmap
import glob
if six.PY2:
    import ConfigParser
if six.PY3:
    import configparser as ConfigParser
    
try:
    from flask import Flask, request, abort, jsonify, send_from_directory
except:
    print("FLASK service not installed")
    try:
        if sys.platform == 'win32':
            a=subprocess.check_output("pip install flask --proxy https://proxy-chain.intel.com:911",shell=True)
            print("INstallation Done")
            from flask import Flask,jsonify,request
        else:
            subprocess.check_output("export http_proxy=http://proxy-chain.intel.com:911;export https_proxy=http://proxy-chain.intel.com:912;sudo pip install flask",shell=True)
    except:
        print("Flask Missing")
        
from subprocess import Popen,PIPE,STDOUT
try:
    import smbus
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
except:
    pass

try:
    from picamera import PiCamera
except:
    print("Camera Not Conneted")
    pass

try:
    import socket    
    hostname = socket.gethostname()    
    ipadd = socket.gethostbyname(hostname) 
except:
    ipadd = "rpi_ipaddress"
    print("socket Library Not Found")
    pass

try:
    from cycling_senderLinuswindows import execute
except:
    print("execute missing")
    pass

UPLOAD_DIRECTORY = "/home/pi/Public/firmware/chipwrite"
try:
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
except:
    print("This is a Windows Machine")
    pass

os_path="/opt/APP/xmlcli/"
config_file_path="/home/pi/Desktop/bios_knoob_change_xml_cli/Willsonpoint.cfg"
#global flashrom_path
flashrom_path="/home/pi/Public"
app = Flask(__name__)
try:
    ret=subprocess.check_output("uname -m",shell=True)
    ret=ret.strip()
    if(str(ret).find("arm")!=-1):
        write_folder=os.path.exists(str(flashrom_path)+"/firmware/chipwrite")
        if(write_folder == False):
            subprocess.check_output("sudo mkdir "+str(flashrom_path)+"/firmware/chipwrite;sudo chmod 777 "+str(flashrom_path)+"/firmware/chipwrite",shell=True)
        read_folder=os.path.exists(str(flashrom_path)+"/firmware/chipread")
        if(read_folder == False):
            subprocess.check_output("sudo mkdir "+str(flashrom_path)+"/firmware/chipread;sudo chmod 777 "+str(flashrom_path)+"/firmware/chipread",shell=True)                
except:
    pass

def aconfromacoff(timeouton=None):     
    print('\n PLEASE WAIT TURNING ON AC POWER')
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(31, GPIO.OUT)
    GPIO.setup(33, GPIO.OUT)
    GPIO.cleanup(31)
    GPIO.cleanup(33)
    if not timeouton:
        timeouton=5
    time.sleep(int(timeouton))
    if(acdetection() == True):
        print('AC ON Performed and Verified ')
    return True

def acofffromacon(timeoutoff=None):
    print('\n PLEASE WAIT TURNING OFF AC POWER')
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(31, GPIO.OUT)
    GPIO.setup(33, GPIO.OUT)
    GPIO.output(31, True)
    GPIO.output(33, True)
    if not timeoutoff:
        timeoutoff=4
    time.sleep(int(timeoutoff))
    if(acdetection() != True):
        print('AC OFF Performed and Verified ')
        return True

def shutdown(timeoutoff=None):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(15, GPIO.OUT)
    GPIO.output(15, True)
    if not timeoutoff:
        timeoutoff=6
    time.sleep(int(timeoutoff))
    GPIO.cleanup(15)
    if(dcdetection() != True):
        print('Shutdown Performed and Verified ')
        return True

def wake_up(timeouton=None):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(15, GPIO.OUT)
    GPIO.output(15, True)
    if not timeouton:
        timeouton=2
    time.sleep(int(timeouton))
    GPIO.cleanup(15)
    if(dcdetection() == True):
        print('Waking Up The Platform DONE and Verified')
        return True

def acdetection():
    GPIO.setmode(GPIO.BOARD)
    GPIO.cleanup(37)
    time.sleep(1)
    GPIO.setup(37, GPIO.IN)
    if GPIO.input(37):
       return True

def dcdetection():
    GPIO.setmode(GPIO.BOARD)
    GPIO.cleanup(16)
    time.sleep(0.5)
    GPIO.setup(16, GPIO.IN)
    if GPIO.input(16):
       return True

def s3detection():
    GPIO.setmode(GPIO.BOARD)
    GPIO.cleanup(13)
    GPIO.setup(13, GPIO.IN)
    if GPIO.input(13):
       return True

def s4detection():
    GPIO.setmode(GPIO.BOARD)
    GPIO.cleanup(18)
    GPIO.setup(18, GPIO.IN)
    if GPIO.input(18):
       return True
    
def reboot():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(15, GPIO.OUT)
    GPIO.output(15, True)
    time.sleep(1)
    GPIO.cleanup(15)
    print('Hard Rebooting The Platform')
    return True

def clearcmos():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.OUT)
    GPIO.output(11, True)
    time.sleep(3)
    GPIO.cleanup(11)
    print("Clear CMOS Platform DONE")
    return True

def usb_switch_to_host():
    try:
        GPIO.setmode(GPIO.BOARD)
        print('\n PLEASE WAIT SWITCHING THE USB TO PI')
        time.sleep(2)
        GPIO.setup(22, GPIO.OUT)
        GPIO.setup(29, GPIO.OUT)
        GPIO.setup(36, GPIO.OUT)
        GPIO.output(22, True)
        GPIO.output(29, True)
        GPIO.output(36, True)
        time.sleep(3)
        return True
    except:
        print("NO SWITCHING DIDN'T TAKE PLACE")

def usb_disconnect():
    try:
        GPIO.setmode(GPIO.BOARD)
        print('\n PLEASE WAIT SWITCHING THE USB TO PI')
        time.sleep(2)
        GPIO.setup(22, GPIO.OUT)
        GPIO.setup(29, GPIO.OUT)
        GPIO.setup(36, GPIO.OUT)
        GPIO.output(22, True)
        GPIO.output(29, False)
        GPIO.output(36, True)
        time.sleep(3)
        return True
    except:
        print("Disconnect USB DIDN'T Happen")
        
def usb_switch_to_sut():
    try:
        subprocess.Popen("udisksctl unmount -b /dev/sda1",shell=True)
        time.sleep(5)    
        print('\n PLEASE WAIT SWITCHING THE USB TO SUT')
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(22, GPIO.OUT)
        GPIO.setup(29, GPIO.OUT)
        GPIO.setup(36, GPIO.OUT)
        GPIO.cleanup(22)
        GPIO.cleanup(29)
        GPIO.cleanup(36)
        time.sleep(3)
        return True
    except:
        print("NO SWITCHING DIDN'T TAKE PLACE")

def camera_detection():
    try: 
        pi_camera_detection=subprocess.check_output("vcgencmd get_camera",shell=True)
        if(pi_camera_detection.find("detected=1")!=-1):
            print("=========> Raspberry Pi Camera Detected <==========")
            return True
        else:
            platform=sys.platform
            if(platform.find("windows")!=-1):
                print("====> Camera Module Not Supported In Windows <====")
                #return windows_environment
            elif(platform.find("linux2")!=-1):
                print("====> Camera Module Not Connected Properly Check <====")                          
            else:
                print("====> This Is Not Raspian Environment <====")
                #return Not_Raspian_os
    except:
        return False
        raise

def camera_initialize():
    try:
        camera = PiCamera()
    except:
        return("Camera Module Not Installed")
    camera.resolution=(720,720)
    camera.start_preview(fullscreen=False, window = (10, 90, 160, 1800))

def camera_Deinitialize():
    try:
        camera = PiCamera()
    except:
        return("Camera Module Not Installed")
    #camera.wait_recording()
    #camera.stop_recording()
    camera.start_preview(fullscreen=False, window = (10, 90, 160, 1800))
    time.sleep(1)
    camera.stop_preview()
    
def platform_postcode():
        bus = smbus.SMBus(1)
        try:
             for device in range(128):
                 try:
                     bus.read_byte(device)
                     post=hex(device)
                 except Exception:
                     pass
             try:
                 pst_code=subprocess.check_output("sudo i2cget -y 1 "+str(post)+"",shell=True)
                 pst_code=(pst_code[2:4])
                 return pst_code
             except:
                 return "N/A"
        except Exception:
             print("Couldn't Read Post Code SmBus Failure")
             raise

def program_jumper(state,gpio_pin_number,timeout=""):
        """
        program_jumper controls the gpio pins of raspberry pi
        :param state=set or unset this makes the gpio pin high or low to cmmunicate with the relay
        gpio_pin_number which pins that needs to be programmed 
        :return: True
        :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        state=state.lower()
        gpio_pin_number=int(gpio_pin_number)
        if timeout:
             timeout=int(timeout)
        else:
             timeout=3
        if(state =="set"):
             try:
                 GPIO.setmode(GPIO.BOARD)
                 #print("aaaaaaaaaaaa",gpio_pin_number)
                 GPIO.setup(gpio_pin_number, GPIO.OUT)
                 GPIO.output(gpio_pin_number, True)
                 time.sleep(timeout)
                 return True
             except Exception:
                 print("Set State to the Jumper Failed tO Happen")
                 raise
        elif(state=="unset"):
             try:
                 GPIO.setmode(GPIO.BOARD)
                 GPIO.setup(gpio_pin_number, GPIO.OUT)
                 GPIO.cleanup(gpio_pin_number)
                 time.sleep(timeout)
                 return True
             except Exception:
                 print("UnSet State of the Jumper Failed to Happen")
                 raise
        else:
            print("Undefined Set State",state)
            
def read_bios_knobs(*inp):
        '''This function is used to read the bios knobs and their current values.
        Input is the knob names,
        Output contains the current knob values
        '''
        cp=ConfigParser.SafeConfigParser()
        cp.read(config_file_path)
        op=cp.sections()
        flag=1
        li=[]
        for i in inp:
            li.append(i)
            section=','.join(li)
        ret=execute("python "+str(os_path)+"xmlcli_get_verify_knobs.py \"read_current_knob\""+" "+"\""+str(section)+"\"",20)
        ret=''.join(str(ret))
        try:         
            out=re.findall(r"knob (.*)\n",ret,re.I|re.M)
            if out!=[]:
                print ('Resultant output is {0}'.format(out))
            else:
                print ('No output present')
                return (False,out)
        except (AttributeError,Exception) as e:
            print (e)
            return (False,out)
        if(ret.find("passed")!=-1):
            print("Success")                     
            return out
        else:
            print("Failure")
            return (False,out)


def get_knob_options(*inp):
        '''
        This function is used to read the bios knobs and all their values.
        Input is the knob names,
        Output contains the all the knob values
        '''
        cp=ConfigParser.SafeConfigParser()
        cp.read(config_file_path)
        op=cp.sections()
        flag=1
        li=[]
        for i in inp:
            li.append(i)
            section=','.join(li)
        ret=execute("python "+str(os_path)+"xmlcli_get_verify_knobs.py get_option"+" "+"\""+str(section)+"\"",20)
        ret=''.join(str(ret))
        #print(ret)
        #ret="available values for the knob"
        try:
            out=re.findall(r"available values for the knob (.*)\n",ret,re.I|re.M)
            if out!=[]:
                print ('Resultant output is {0}'.format(out))
            else:
                print ('Knob options not available')
                return (False,"Knob options not available")
        except (AttributeError,Exception) as e:
            print (e)
            return (False,"Knob options not available")
        if(ret.find("Current")!=-1):
            print("Success")
            return (True,out[0])
        else:
            print("Failure")
            return (False,"Knob options not available")

def set_bios_knobs(section,key):
        '''
        This function is used to set the bios knobs to the required value.
        Input is the knob name and the value to which the knob has to set.
        Output is the knob changed to the given input value
        '''
        ret=execute(r"python "+str(os_path)+"xmlcli_get_verify_knobs.py ProgKnobs_xml"+" "+"\""+str(section)+"\""+" "+"\""+str(key)+"\"",60)
        ret=str(ret)
        ret=''.join(ret)
        if(ret.find("True")!=-1):
            print("Success In Setting Up The Knob")
            return (True,"Success In Setting Up Given Knob "+str(section)+"--->"+str(key))
        else:
            return (False,"Failed In Setting Up The Knob "+str(section)+"--->"+str(key))


def get_bios_bootorder():
        '''
        This function is used to get the bios boot order.
        Output contains the current bios boot order.
        '''
        try:  
            ret=execute("python "+str(os_path)+"xmlcli_save_read_prog_knobs.py Get_boot_order_xml",20)
            out=re.search(r'\[(.*)\]',ret,re.I)
            if out!=[]:
                print("Resultant output Boot order list is: {0}".format(out.group(1)))
                return (True,out.group(1))
            else:
                print("Failure")
                return (False,"Failure")
        except Exception as e:
            print("Failure")
            return (False,e)

def set_bios_bootorder(Drive_name):
        '''
        This function is used to set the bios boot order.
        Input Target is the OS name i.e., linux or windows from the config file and Index is the position at which the OS device name is present in config file.
        Output is boot order changes to required boot device.
        '''
        try:
            ret=execute("python "+str(os_path)+"xmlcli_save_read_prog_knobs.py Change_boot_order_xml \""+str(Drive_name)+"\"",120)
            ret=''.join(str(ret))
            if (ret.find(r"Bios boot order got changed & passed")!=-1):
                print("Success",'Bios boot order got changed to {0}'.format(Drive_name))
                return (True,"Success In Changing Boot Order to "+str(Drive_name))
            else:
                print("failure")
                return (False,"Bios boot order not changed "+str(Drive_name))
        except Exception as e:
            print("Failure")
            return (False,e)


def load_default_bios():
    ret=execute("python "+str(os_path)+"/xmlcli_save_read_prog_knobs.py Default_xml",30)
    if("The Knob values were set to default & passed" in ret) == True:
        return (True,"Loading Default settings Successfull issue Reboot")
    else:
        return (False,"Loading Default settings Failed")

def flash_chip_identity(flash_speed=None):
        if flash_speed:
            print("flash_chip speed was passed",flash_speed)
            flash_speed=int(flash_speed)
        else:
            flash_speed=2000
        try:
            #print("cd "+str(flashrom_path)+"/flashbios;sudo ./flashrom -p linux_spi:dev=/dev/spidev0.0,spispeed={0}").format(flash_speed)
            s=subprocess.Popen("cd "+str(flashrom_path)+"/flashbios;sudo ./flashrom -p linux_spi:dev=/dev/spidev0.0,spispeed="+str(flash_speed)+"",stdin=PIPE,stdout=PIPE,stderr=STDOUT,preexec_fn=os.setsid,close_fds=True,shell=True)
            s=s.stdout.read()
            s=str(s)
            #path are all predefined fixed path,pi dependency will take care of this
            a=[]  
            a=s
            u=a.find("flash chip")
            #print(a[u:213])
            r=a.find("Found")
            h=a.find("kB, SPI")
            print(" THIS IS THE CHIP FOUND ===========> "+str(a[u:213])+" <=============")
            print(" MANUFACTURING COMPANY ===========> "+str(a[r+5:u])+" <=============")
            i=(int(a[h-6:h]) / 1024)
            print(" CHIP SIZE            ===========> "+str(a[h-6:h])+"KB <===== "+str(i)+"MB ========\n")
            return(a[u:213],str(a[r+5:u]),str(a[h-6:h]))
        except: 
            print("--------------- CHECK CONNECTION PROPERLY ----------------")
            k=os.path.exists(str(flashrom_path)+"/flashbios")#path are all predefined fixed path,pi dependency will take care of this
            if(k==True):
                print("---------- FOLDER EXISTS ----------\n")
                print("================> TURN OFF THE SUT AND TRY <==================")
                print(" TRY RUNNING BIOS FLASH DEPENDENCIES AGAIN AND REBOOT PI ONCE")
                return False
            raise
            
def flash_chip_read(flash_speed=None):
        '''
        To get the image stored in the bios chip or the bmc chip read and storing the chip data can be done.
        location after reading it will store it in this location "+str(root)+"/chipread with the current date and time beiging the file name
        '''
        if flash_speed:
            print("flash speed was passed by the user")
        else:
            flash_speed=2000
        flash_speed=int(flash_speed)
        start = time.time()
        now=datetime.datetime.now()
        a=now.strftime("%Y-%m-%d-%H:%M")
        h=os.path.exists(str(flashrom_path)+"/flashbios") # this is a fixed path
        if(h==True):
            k=os.path.exists(str(flashrom_path)+"/firmware/chipread")
            if(k==True):
                print("==================> BIOS CHIP READING BEGINGS IT WILL TAKE TIME <=================")
                n=subprocess.Popen("cd "+str(flashrom_path)+"/flashbios;sudo ./flashrom -p linux_spi:dev=/dev/spidev0.0,spispeed="+str(flash_speed)+" -r "+str(a)+".bin",stdin=PIPE,stdout=PIPE,stderr=STDOUT,preexec_fn=os.setsid,close_fds=True,shell=True)
                n=n.stdout.read()
                n=str(n)               
                #n="Reading flash... done."
                #a="apple"
                if(n.find(r"Reading flash... done.")!=-1):
                    print("==================> READING OF CHIP DONE <=================")
                    subprocess.check_output("sudo mv "+str(flashrom_path)+"/flashbios/"+str(a)+".bin "+str(flashrom_path)+"/firmware/chipread/",shell=True)
                    out=subprocess.Popen("sudo chmod 777 "+str(flashrom_path)+"/firmware/chipread/"+str(a)+".bin",stdin=PIPE,stdout=PIPE,stderr=STDOUT,preexec_fn=os.setsid,close_fds=True,shell=True)
                    out=out.stdout.read()
                    print("==================> READING THE CHIP AND STORING THAT IS DONE <=================")
                    print("===============> THIS IS THE FILE NAME "+str(a)+".BIN LOCATED IN THIS DIRECTORY "+str(flashrom_path)+"/firmware/chipread <==============")
                    l=(time.time()-start)
                    i=(int(l) / 60)
                    sec=(60-time.time()-start)
                    sec=round(sec,0)
                    sec=abs(sec)
                    sec=int(str(sec)[:2])
                    print("\n ------"+str(i)+" MINUTES ------ "+str(sec)+" ------SECONDS")
                    time_taken=(str(i)+" Min "+str(sec)+" Sec")
                    read_file_name=a+".bin"
                    return True,read_file_name,time_taken
                else:
                    print(" ==================> READING THE CHIP FAILED <=================")
                    return False
        else:
            print(" ==========================> FLASHBIOS FOLDER IS NOT PRESENT "+str(flashrom_path)+"<====================")

def flash_chip_write(flash_image_name=None,flash_speed=None):
        if flash_speed:
            print("flash speed was passed by user")
        else:
            flash_speed=2000
        flash_speed=int(flash_speed)
        start = time.time()
        now=datetime.datetime.now()
        a=now.strftime("%Y-%m-%d-%H:%M")
        h=os.path.exists(str(flashrom_path)+"/flashbios")
        #logic change required
        if flash_image_name:
            print("flashing image name was passed by user for writing")
            file_name=subprocess.check_output("ls "+str(flashrom_path)+"/firmware/chipwrite/",shell=True)
            if(str(file_name).find(flash_image_name)!=-1):
                flash_image_name=str(flashrom_path)+"/firmware/chipwrite/"+str(flash_image_name)
                print(flash_image_name)
            else:
                print("No FIle Present")
                return "Flashing File_Not_Found in Location","Given Img Name -->"+str(flash_image_name)+"<--","Found Img -->"+str(file_name)+"<--"
                raise
        else:
            print("it will flash only the lateset copied image to chipwrite folder only")
            try:
                if(flashrom_path+"/firmware/chipwrite/*.bin" !=-1):   
                    k=glob.glob(str(flashrom_path)+"/firmware/chipwrite/*.bin")  
                    flash_image_name=max(k,key=os.path.getctime)
                    print("\n THIS IS THE FIRMWARE BIN FILE : "+flash_image_name)
            except:
                print("No FIle Present")
                reason="No FIle Was Passed and No File Present For Flashing"
                return False,reason
                raise
        start = time.time()
        try:
            print("==================> BIOS CHIP FLASHING BEGINGS IT WILL TAKE TIME <=================")
            n=subprocess.Popen("cd "+str(flashrom_path)+"/flashbios;sudo ./flashrom -p linux_spi:dev=/dev/spidev0.0,spispeed="+str(flash_speed)+" -n -f -w"+str(flash_image_name),stdin=PIPE,stdout=PIPE,stderr=STDOUT,preexec_fn=os.setsid,close_fds=True,shell=True)
            n=n.stdout.read()
            n=str(n)
            #n="Erase/write done"
            if(n.find("Erase/write done")!=-1):
                print("Writing To Chip Was Done")
                l=(time.time()-start)
                i=(int(l) / 60)
                i=round(i,0)
                sec=(60-time.time()-start)
                sec=round(sec,0)
                sec=abs(sec)
                sec=int(str(sec)[:2])
                print("\n ------"+str(i)+" MINUTES ------ "+str(sec)+" ------SECONDS")
                time_taken=(str(i)+" Min "+str(sec)+" Sec")
                ifwi_file_name=flash_image_name
                return True,ifwi_file_name,time_taken
            else:
                print("Flashing Failed To Happen")
                #print("\n------"+str(i)+" MINUTES ------%.6s seconds------"%(time.time()-start))
                return False
        except:
            raise
            return False
        
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------      
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/')
def homepage():
    ret=subprocess.check_output("hostname",shell=True)
    ret=ret.strip()
    return "FLASH Rpi-ControlBox {} 1.7 version may-20-2020".format(ret)

@app.route('/',methods=['GET','POST'])
def index():
    if(required.method == 'POST'):
        some_json = request.get_json()
        return jsonify({'you sent':some_json}),201
    else:
        return jsonify({"Power on"})
        
@app.route('/multi/<int:num1>',methods=['GET'])
def get_multiply10(num1):
    return jsonify({'result':num1*10})

@app.route('/progjmpr/<string:state>/<int:num1>/<int:num2>',methods=['GET'])
def prog_jumper(state,num1,num2=""):
    print("qqqqqqqqqqqqqqqqqqqq",state,num1,num2)
    if(program_jumper(state,gpio_pin_number=num1,timeout=num2)==True):
        return "Jumper "+state+" Done"

@app.route('/execute/<string:cmd_input>',methods=['GET'])
def get_subprocess_module(cmd_input):
    out=subprocess.check_output(cmd_input,shell=True)
    return str(out)

@app.route('/clearcmos',methods=['GET'])
def platform_clearcmos():
    if(clearcmos()==True):
        return "ClearCmos Command Issued"
    else:
        return "N/A"

@app.route('/dcdetect',methods=['GET'])
def platform_dcpower():
    if dcdetection()==True:
        return "DC power detected"
    else:
        return "N/A"
    
@app.route('/s3detect',methods=['GET'])
def platform_s3_get_power():
    if s3detection()==True:
        return "S3 power detected"
    else:
        return "N/A"

@app.route('/postcode',methods=['GET'])
def platform_pstcode():
    ret=platform_postcode()
    if(ret=="N/A"):
        return "N/A"
    else:
        return ret

@app.route('/s4detect',methods=['GET'])
def platform_s4_get_power():
    if s4detection()==True:
        return "S4 power detected"
    else:
        return "N/A"

@app.route('/acdetect',methods=['GET'])
def platform_acpower():
    if(acdetection()==True):
        return "AC power detected"
    else:
        return "N/A"

@app.route('/usb2host',methods=['GET'])
def usb2host():
    if(usb_switch_to_host()==True):
        return "USB Switch to Host Done"
    else:
        return "Failed to Switch the Usb To Host"


@app.route('/usbdiscnt',methods=['GET'])
def usbdisconnect():
    if(usb_disconnect()==True):
        return "USB Disconnect Done"
    else:
        return "Failed to Disconnect USB"
    
@app.route('/usb2sut',methods=['GET'])
def usb2sut():
    if(usb_switch_to_sut()==True):
        return "USB Switch to SUT Done"
    else:
        return "Failed to Switch the Usb To SUT"
    
@app.route('/reboot',methods=['GET'])
def platform_reboot():
    if(reboot()==True):
            return "Reboot Command Issued"
            
@app.route('/acpower/num/',defaults={'timeout':None},methods=['GET'])
@app.route('/acpower/<int:num>',methods=['GET'])
@app.route('/acpower/<int:num>/<int:timeout>',methods=['GET'])
def acpower(num,timeout=None):
    if num == 0:
        if(acofffromacon(timeoutoff=timeout)==True):
            return "Power Turned OFF and Verified"
        else:
            return "AC Power OFF Failed"
    elif num == 1:
        if(aconfromacoff(timeouton=timeout)==True):
            return "Power Turned ON and Verified"
        else:
            return "AC Power ON Failed"
    else:
        return "Invalid Input:-\n 0 is Turn Power OFF \n 1 is Turn Power On"

@app.route('/options',methods=['GET'])
def informer1():
    return "img_upload ---- uploading .ima/.bin From your Device To Rpi \n\t**usage  curl -T full_location_path of image_name.bin|.ima -X POST http://"+str(ipadd)+"/img_upload/  \n\t \nread_chip  ----- Reads the Current image Flashed and Stores it under \"/home/pi/public/frimware/chipread\" folder \nwrite_chip/ ----- Flashes the latest image under \"/home/pi/public/frimware/chipwrite\" folder \nidentify_chip  ----- Detection of the chip and connection verfication \ndcpower/0 ------- To DC Turn Off Platform \ndcpower/1 ------- To DC Turn On Platform \nacpower/0 ------- To AC Power Turn Off Platform \nacpower/1 ------- To AC Power Turn On Platform \ncamera/0 ------- If a pi camera is connected it will initialize camera Off \ncamera/1 ------- If a pi camera is connected it will Turn On Camera \nexecute/xxx \nclearcmos \nreboot \npostcode \nusb2host ----- USB Device TO HOST Machine \nusb2sut ----- USB Device TO HOST Machine \nusbdiscnt ----- USB DISCONNECT FROM BOTH SUT AND HOST \ndcdetect \nacdetect \ns3detect \ns4detect \nprogjmpr  ----- set/unset pin_number timeout"# \nsetbootorder ---- setbootorder\\bootorder name add $ incase of any space use getbootorder to know the name \ngetbootorder \ndefaultbios \ncurrentknobval ---- currentknobval\knob_name if any space add $ WHEA Support ==> WHEA$Support \ngetoptions ---- getoptions\knob_name if any space add $ ==> Driver$Strength \nsetoptions ---- setoptions\knob_name if any space add $\option_name if any space add $ eg==>setoptions\WHEA$Support\Enable

@app.route('/help',methods=['GET'])
def informer():
    return "img_upload ---- uploading .ima/.bin From your Device To Rpi \n\t**usage  curl -T full_location_path of image_name.bin|.ima -X POST http://"+str(ipadd)+"/img_upload/  \n\t \nread_chip  ----- Reads the Current image Flashed and Stores it under \"/home/pi/public/frimware/chipread\" folder \nwrite_chip/ ----- Flashes the latest image under \"/home/pi/public/frimware/chipwrite\" folder \nidentify_chip  ----- Detection of the chip and connection verfication \ndcpower/0 ------- To DC Turn Off Platform \ndcpower/1 ------- To DC Turn On Platform \nacpower/0 ------- To AC Power Turn Off Platform \nacpower/1 ------- To AC Power Turn On Platform \ncamera/0 ------- If a pi camera is connected it will initialize camera Off \ncamera/1 ------- If a pi camera is connected it will Turn On Camera \nexecute/xxx \nclearcmos \nreboot \npostcode \nusb2host ----- USB Device TO HOST Machine \nusb2sut ----- USB Device TO HOST Machine \nusbdiscnt ----- USB DISCONNECT FROM BOTH SUT AND HOST \ndcdetect \nacdetect \ns3detect \ns4detect \nprogjmpr  ----- set/unset pin_number timeout"# \nsetbootorder ---- setbootorder\\bootorder name add $ incase of any space use getbootorder to know the name \ngetbootorder \ndef

@app.route('/dcpower/num/',defaults={'timeout':None},methods=['GET'])
@app.route('/dcpower/<int:num>',methods=['GET'])
@app.route('/dcpower/<int:num>/<int:timeout>',methods=['GET'])
def dcpower(num,timeout=None):
    if num == 0:
        if(shutdown(timeoutoff=timeout)==True):
            return "DC Power Turned OFF and Verified"
        else:
            return "Failed To DC Power Turned OFF"  
    elif num == 1:
        if(wake_up(timeouton=timeout)==True):
            return "Dc Power Turned ON and Verfied"
        else:
            return "Failed To DC Power Turned ON" 
    else:
        return "Invalid Input:-\n 0 is Turn Power OFF \n 1 is Turn Power On"

@app.route('/currentknobval/<string:knob>',methods=['GET'])
def read_current_knob(knob):
    knob=knob.replace("$"," ")
    ret=read_bios_knobs(knob)
    return str(ret)

@app.route('/camera/<int:action>',methods=['GET'])
def camera_module(action):
    if(camera_detection()==True):
        if(action == 1):
            if(camera_initialize()==True):
                return str("True, Camera Turned ON")
            else:
                return str("False, Failed To Turned ON Camera")
        elif(action == 0):
            if(camera_Deinitialize()==True):
                return str("True, Camera Turned OFF")
            else:
                return str("False, Camera Turned OFF Failed")
        else:
            return str("Invalid Input")
    else:
        return str("False, Pi Camera Not Connected")
        
@app.route('/getoptions/<string:knob>',methods=['GET'])
def knob_options(knob):
    knob=knob.replace("$"," ")
    ret=get_knob_options(knob)
    return str(ret)

@app.route('/setoptions/<string:knob>/<string:option>',methods=['GET'])
def set_bios_knob_options(knob,option):
    knob=knob.replace("$"," ")
    option=option.replace("$"," ")
    ret=set_bios_knobs(section=knob,key=option)
    return str(ret)

@app.route('/getbootorder',methods=['GET'])
def get_boot_options():
    ret=get_bios_bootorder()
    return str(ret)

@app.route('/setbootorder/<string:order>',methods=['GET'])
def set_boot_options(order):
    order=order.replace("$"," ")
    print("sdafadsfasdf",order)
    ret=set_bios_bootorder(Drive_name=order)
    time.sleep(4)
    return str(ret)

@app.route('/defaultbios',methods=['GET'])
def set_default_bios():
    ret=load_default_bios()
    return str(ret)

@app.route("/img_upload/<filename>", methods=["POST"])
def upload_img_file(filename):
    try:
        if "/" in filename:
            abort(400, "no subdirectories directories allowed")
        with open(os.path.join(UPLOAD_DIRECTORY, filename), "wb") as fp:
            fp.write(request.data)
        return str("uploading Image "+str(filename)+"... Completed")
    except:
        return str("Uploading Image Failed")

@app.route('/identify_chip',defaults={'speed':None},methods=['GET'])
@app.route('/identify_chip/<int:speed>',methods=['GET'])
def chip_identity(speed=None):
    if(program_jumper(state="set",gpio_pin_number='32',timeout='1')==True):
        ret=flash_chip_identity(flash_speed=speed)
        if ret != False:
            ret=("True",)+ret
        else:
            ret=('False',)+("Chip Not Detected",)
        if(program_jumper(state="unset",gpio_pin_number='32',timeout='1')==True):
            return str(ret)

@app.route('/read_chip',defaults={'speed':None},methods=['GET'])
@app.route('/read_chip/<int:speed>',methods=['GET'])
def chip_read(speed=None):
    if(program_jumper(state="set",gpio_pin_number='32',timeout='1')==True):
        ret=flash_chip_read(flash_speed=speed)
        if(program_jumper(state="unset",gpio_pin_number='32',timeout='1')==True):
            return str(ret)

@app.route('/write_chip/',defaults={'speed':None},methods=['GET'])
@app.route('/write_chip/<int:speed>',methods=['GET'])
@app.route('/write_chip/<string:img>',methods=['GET'])
@app.route('/write_chip/',defaults={'img':None},methods=['GET'])
@app.route('/write_chip/<int:speed>/<string:img>',methods=['GET'])
def chip_write(img=None,speed=None):
    if img:
        img=img.replace("$"," ")
    if(program_jumper(state="set",gpio_pin_number='32',timeout='1')==True):
        ret=flash_chip_write(flash_image_name=img,flash_speed=speed)
        print("eeeeeeeeeeeeeeee",ret)
        if(str(ret).find("Flashing File_Not_Found in Location")!=-1):
            ret=('False',ret)
        elif(ret[0] == True):
            ret=ret
        elif(str(ret).find("No FIle Was Passed and No File Present For Flashing")!=-1):
            ret=ret
        else:
            ret=("Flase",)+("Falshing_Image_Failed",)
        if(program_jumper(state="unset",gpio_pin_number='32',timeout='1')==True):
            return str(ret)

if __name__ == "__main__":
    app.run(host="0.0.0.0",threaded=True,port=80,debug=True)
