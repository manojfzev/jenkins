import argparse
import google.auth
import google.auth.exceptions
import os
import time
import random
import subprocess
import json
import shlex
import string
import googleapiclient.discovery
import re
import requests
import sys

def get_random_string():
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(8))
    # print("Random string of length", length, "is:", result_str)
    print("Random string of length is:", result_str)
    return result_str


def create_instance(project, zone, name, imagename,subnet):

    print("Parameters are ", project, zone, name, imagename,subnet)
    instance_create_command = "gcloud beta compute instances create "+ name +" --project "+ project +" --subnet "+ subnet +" --zone " + zone + " --source-machine-image "+ imagename +" --no-address  --format json"
    instance_output = subprocess.check_output(shlex.split(instance_create_command), shell = True)
    instance_output_json = json.loads(instance_output)

    for instance in instance_output_json:
       return instance['networkInterfaces'][0]['networkIP']

# [END create_instance]

def intiatescan(ciscatscaninstnaceip,ciscatscanbenchmark,project, zone, instance_name):

    path = "C:/Assessor-CLI/config/sessions.properties"  # set the path to ciscat folder on the scanner computer
    completed = subprocess.run(["powershell", "-Command", "Set-ExecutionPolicy Unrestricted \n\
    (Get-Content -Path '"+path+"') | \n\
    Foreach-Object { if ($_ -match 'session.1.host=') {\n\
    $_.Substring(0,'session.1.host='.Length) + '"+ciscatscaninstnaceip+"'}else{ $_ }\n\
    } | Set-Content  -Path '"+path+"'"\
    ], capture_output=True)


    commands = [
        "cd C:/Assessor-CLI && del /f output1",
        "cd C:/Assessor-CLI && Assessor-CLI.bat -b benchmarks/"+ciscatscanbenchmark+" > output1",
        "cd C:/Assessor-CLI && findstr /i \"Total:\" output1"
    ]

    try:
        #finaloutput='1:12'
        finaloutput=''
        #print("Running in the existing HOST")
        for command in commands:
            output1=subprocess.run(command, shell=True, stdout=subprocess.PIPE)
            finaloutput=output1.stdout.decode("utf-8")
    

        print(finaloutput)
        finaloutput = finaloutput.split(":")[1]
        finalscore = finaloutput.strip().split('%',1)[0]
        if not finalscore:
            print ("scan results are empty")
        else:
            print ("Scan results precentage: "+finalscore)          
            return finalscore

    except Exception as e:
        print("Ciscat scan fail: ", e)

    finally:
        delete_instance(project, zone, instance_name)    


def delete_instance(project, zone, name):
    instance_delete_command = "gcloud compute instances delete projects/"+project+"/zones/"+zone+"/instances/"+name+" --quiet --format json"
    instance_delete_output = subprocess.check_output(shlex.split(instance_delete_command), shell=True)
    print(name+" is terminated")

def get_os(osversion):
    if osversion in ['Windows_2016']:
        print("the os windows server 2016")
        ciscatscanbenchmark='CIS_Microsoft_Windows_Server_2016_STIG_Benchmark_v1.1.0-xccdf.xml'
    elif osversion in ['Windows_2019']:
        print("the os windows server 2019")
        ciscatscanbenchmark='CIS_Microsoft_Windows_Server_2019_Benchmark_v1.2.1-xccdf.xml'    
    elif osversion in ['Windows_2012']:
        print("the os windows server 2012")
        ciscatscanbenchmark='CIS_Microsoft_Windows_Server_2012_(non-R2)_Benchmark_v2.3.0-xccdf.xml'
    elif osversion in ['Windows_2012R2']:
        print("the os windows server 2012 R2")
        ciscatscanbenchmark='CIS_Microsoft_Windows_Server_2012_R2_Benchmark_v2.5.0-xccdf.xml'    
    elif osversion in ['Windows_2008']:
        print("the os windows server 2008")
        ciscatscanbenchmark='CIS_Microsoft_Windows_Server_2008_Benchmark_v3.1.0-xccdf.xml'
    elif osversion in ['Windows_2008R2']:
        print("the os windows server 2008 R2")
        ciscatscanbenchmark='CIS_Microsoft_Windows_Server_2008_R2_Benchmark_v3.2.0-xccdf.xml'  
    else:
        print("please check the instance OSVersion tags is in approved format[Ubuntu_xx.xx , AmazonLinux2, CentOS_x]")
        sys.exit()
    return ciscatscanbenchmark

# def post_data(ciscatscore):  
#     payload = {"Total": ciscatscore}
#     r = requests.post("https://6qmfyjdek3.execute-api.us-east-1.amazonaws.com/test/test",params=payload)
#     print(r.status_code)


def main(project, image_name, zone, osversion,  instance_name):
    print("Running os version is ", osversion)
    ciscatscanbenchmark = get_os(osversion)
    print("Benchmark is ",  ciscatscanbenchmark)  
    projectresp=project.rpartition('-')[0]
    projecttype=projectresp.rpartition('-')[2]
    print("selected project is ==> "+ project)
    subnet=""

    if projecttype == "np":
        print("running on np prod project")
        subnet= "projects/second-project-339908/regions/us-central1/subnetworks/subnet-a"
    else:
        print("running on prod project")
        subnet="projects/second-project-339908/regions/us-central1/subnetworks/subnet-a"
    instance_ip = create_instance(project,zone,instance_name, image_name, subnet)
    print("Waiting for the startup script to be execute")
    time.sleep(60)
    print("instance ip is", instance_ip )
    ciscatscore = intiatescan(instance_ip, ciscatscanbenchmark, project, zone, instance_name)
    print(ciscatscore)
    #post_data(ciscatscore)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--project_id', help='Your Google Cloud project ID.')
    parser.add_argument(
        '--image_name', help='Your Google Cloud machine image name.')
    parser.add_argument(
        '--zone',
        default='us-central1-a',
        help='Compute Engine zone to deploy to.')
    parser.add_argument(
        '--osversion',        
        help='OS Version of the machine image.') 

    args = parser.parse_args()
    iname=get_random_string()
    instance_name="ciscatinstance-"+iname    

    main(args.project_id, args.image_name, args.zone, args.osversion, instance_name)
