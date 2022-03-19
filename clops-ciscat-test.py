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

    except Exception as e:        
        print("Ciscat scan fail: ", e)
    #finally:
        #delete_instance(project, zone, instance_name)


def delete_instance(project, zone, name):
    instance_delete_command = "gcloud compute instances delete projects/"+project+"/zones/"+zone+"/instances/"+name+" --quiet --format json"
    instance_delete_output = subprocess.check_output(shlex.split(instance_delete_command))
    print(name+" is terminated")
        
def main():

    instance_name = create_instance("syy-clops-np-c4e6","us-central1-a","ciscat-client-v2", "clops-ciscat-client","projects/syy-networking-np-e538/regions/us-central1/subnetworks/snet-nonprod-us-central1-dynamic-01" )
    print("Waiting for the startup script to be execute")
    time.sleep(60)    
    intiatescan(instance_name,"ciscat-user","/root/Assessor-CLI/ciscat","CIS_Ubuntu_Linux_18.04_LTS_Benchmark_v2.1.0-xccdf.xml","syy-clops-np-c4e6", "us-central1-a", "ciscat-client-v2")

main()
