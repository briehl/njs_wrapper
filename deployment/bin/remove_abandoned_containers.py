#!/usr/bin/env python
# This script is used to find abandoned containers running on a condor worker.
# It requires a webhook URL environmental variable in order to send a notification to a slack channel
import os
import subprocess
import logging

logging.basicConfig(level=logging.DEBUG)

# Improvements: Use a library


delete = os.environ.get('DELETE_ABANDONED_CONTAINERS')
webhook_url = os.environ.get('SLACK_WEBHOOK_URL')

hostname = subprocess.check_output('hostname').strip()
logging.info("About to check for jobs on" + str(hostname))

cmd = "docker ps | grep dockerhub | cut -f1 -d' '"
running_containers = subprocess.check_output(cmd, shell=True)

container_ids = running_containers.split("\n")
container_ids = filter(None, container_ids)

cmd = 'ps -ax -o command | egrep "java -cp /mnt/awe/condor/.+/NJSWrapper-all.jar us.kbase.narrativejobservice.sdkjobs.SDKLocalMethodRunner" | grep -v grep | cut -f5 -d" "'
java_procs = str(subprocess.check_output(cmd, shell=True))
running_job_ids = java_procs.split("\n")

running_job_ids = filter(None, running_job_ids)

logging.info(running_job_ids)

for container_id in container_ids:

    cmd = "docker inspect --format '{{ index .Config.Labels \"job_id\"}}' " + container_id
    try:
        container_job_id = subprocess.check_output(cmd, shell=True).strip()
    except Exception as e:
        print(e)

    if container_job_id not in running_job_ids:
        message = "container:{} job:{} is dead ({})".format(container_id,
                                                            container_job_id,
                                                            hostname)
        #
        # payload = '{' + "'text' : {}".format(message) + '}'
        # call = ['curl', '-X', 'POST', '-H', 'Content-type: application/json', '--data', payload,
        #         webhook_url]
        # subprocess.check_output(call, shell=True)
        # #
        # # curl_cmd = 'curl -X POST -H "Content-type: application/json" --data "{\'text\': \' ' + message + '\'  }" ' + webhook_url



        if delete  == "true":
            cmd = 'docker stop {} && docker container rm -v {}'.format(container_id, container_id)
            logging.error(message)
            logging.error(cmd)
            subprocess.check_output(cmd, shell=True)

    if container_job_id in running_job_ids:
        logging.info("Success" + container_job_id)
