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

def get_random_string():
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(8))
    # print("Random string of length", length, "is:", result_str)
    print("Random string of length is:", result_str)
    return result_str


def create_instance(project, zone, name, imagename,subnet):
    
    # oscreateresponse= os.system("gcloud beta compute instances create "+ name +" --project "+ project +" --subnet projects/syy-networking-np-e538/regions/us-central1/subnetworks/snet-nonprod-us-central1-dynamic-01 --zone us-central1-a --source-machine-image ciscat-host-setupcompleted --no-address"  )
    #print (oscreateresponse)
    instance_create_command = "gcloud beta compute instances create "+ name +" --project "+ project +" --subnet "+ subnet +" --zone " + zone + " --source-machine-image "+ imagename +" --no-address --metadata-from-file=startup-script=startup.sh --format json"
    instance_output = subprocess.check_output(shlex.split(instance_create_command))
    instance_output_json = json.loads(instance_output)

    for instance in instance_output_json:
       return instance['networkInterfaces'][0]['networkIP']

# [END create_instance]

def intiatescan(ciscatscaninstnaceip,ciscatscaninstanceuser, ciscatinstancekey, ciscatscanbenchmark,project, zone, instance_name):

    commands = [
        "sed -i '/session.2.host=/c\session.2.host='"+ciscatscaninstnaceip+" /root/Assessor-CLI/config/sessions.properties",
        "sed -i '/session.2.user=/c\session.2.user='"+ciscatscaninstanceuser+" /root/Assessor-CLI/config/sessions.properties",
        "sed -i '/session.2.identity=/c\session.2.identity='"+ciscatinstancekey+" /root/Assessor-CLI/config/sessions.properties",
        "cd /root/Assessor-CLI && ./Assessor-CLI.sh -b /root/Assessor-CLI/benchmarks/"+ciscatscanbenchmark+" > output",
        "grep Total: /root/Assessor-CLI/output"
    ]
    try:
        finaloutput=''
        for command in commands:
            output = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
            finaloutput=output.stdout.decode("utf-8")
        finalscore=re.split(': |%',finaloutput)[1]
        print("Final score is: ", finalscore)
        if not finalscore:
            print("scan result are empty")
        else:
            print("Scan results precentage: ", finalscore + "%")
            return finalscore

    except Exception as e:        
        print("Ciscat scan fail: ", e)
 #  finally:
 #      delete_instance(project, zone, instance_name)


def delete_instance(project, zone, name):
    instance_delete_command = "gcloud compute instances delete projects/"+project+"/zones/"+zone+"/instances/"+name+" --quiet --format json"
    instance_delete_output = subprocess.check_output(shlex.split(instance_delete_command))
    print(name+" is terminated")

def get_os(osversion):
    if osversion in ['Ubuntu_18', 'ubuntu_18', 'Ubuntu_18.04', 'ubuntu_18.04']:
        print("the os is ubuntu 18")       
        ciscatscanbenchmark='CIS_Ubuntu_Linux_18.04_LTS_Benchmark_v2.1.0-xccdf.xml'
    elif osversion in ['Ubuntu_20', 'ubuntu_20', 'Ubuntu_20.04', 'ubuntu_20.04']:
        print("the os is ubuntu 20")        
        ciscatscanbenchmark='CIS_Ubuntu_Linux_20.04_LTS_Benchmark_v1.1.0-xccdf.xml'
    elif osversion in ['Ubuntu_16', 'ubuntu_16', 'Ubuntu_16.04', 'ubuntu_16.04']:
        print("the os is ubuntu 16")        
        ciscatscanbenchmark='CIS_Ubuntu_Linux_16.04_LTS_Benchmark_v2.0.0-xccdf.xml'    
    elif osversion in ['RedhatEnterprise', 'redhatenterprise', 'RedhatEnterprise_7', 'redhatenterprise_7']:
        print("the os is RedhatEnterprise 7")       
        ciscatscanbenchmark='CIS_Red_Hat_Enterprise_Linux_7_Benchmark_v3.1.1-xccdf.xml'
    elif osversion in ['RedhatEnterprise_6', 'redhatenterprise_6']:
        print("the os is RedhatEnterprise_6")        
        ciscatscanbenchmark='CIS_Red_Hat_Enterprise_Linux_6_Benchmark_v3.0.0-xccdf.xml'
    elif osversion in ['CentOS_7', 'centos_7', 'CentOS', 'centos','CentOS7', 'centos7']:
        print("the os is CentOS_7")        
        ciscatscanbenchmark='CIS_CentOS_Linux_7_Benchmark_v3.1.2-xccdf.xml'
    elif osversion in ['CentOS_6', 'centos_6', 'CentOS6', 'centos6']:
        print("the os is CentOS_6")        
        ciscatscanbenchmark='CIS_CentOS_Linux_6_Benchmark_v3.0.0-xccdf.xml'
    elif osversion in ['SUSE', 'suse', 'SUSE_12', 'suse_12']:
        print("the os is suse 12")        
        ciscatscanbenchmark='CIS_SUSE_Linux_Enterprise_12_Benchmark_v3.0.0-xccdf.xml'
    elif osversion in ['SUSE_15', 'suse_15']:
        print("the os is suse 15")       
        ciscatscanbenchmark='CIS_SUSE_Linux_Enterprise_15_Benchmark_v1.1.0-xccdf.xml'    
    elif osversion in ['Debian', 'Debian9',]:
        print("the os is Debian")        
        ciscatscanbenchmark='CIS_Debian_Linux_9_Benchmark_v1.0.1-xccdf.xml'
    else:
        print("please check the instance OSVersion tags is in approved format[Ubuntu_xx.xx , AmazonLinux2, CentOS_x]")
        sys.exit()
    return ciscatscanbenchmark

def post_data(ciscatscore):  
    payload = {"Total": ciscatscore}
    r = requests.post("https://6qmfyjdek3.execute-api.us-east-1.amazonaws.com/test/test",params=payload)
    print(r.status_code)


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
        subnet= "projects/syy-networking-np-e538/regions/us-central1/subnetworks/snet-nonprod-us-central1-dynamic-01"
    else:
        print("running on prod project")
        subnet="projects/syy-networking-8461/regions/us-central1/subnetworks/snet-prod-us-central1-dynamic-01"
    instance_ip = create_instance(project,zone,instance_name, image_name, subnet)
    print("Waiting for the startup script to be execute")
    time.sleep(60)    
    ciscatscore = intiatescan(instance_ip,"ciscat-user","/root/Assessor-CLI/ciscat", ciscatscanbenchmark, project, zone, instance_name)
    post_data(ciscatscore)

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
