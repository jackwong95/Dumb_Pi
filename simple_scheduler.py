import time
import os
import subprocess

program_dir = '.\scripts'
processes = []

while True:
    if processes != []:
        for proc in processes:
            proc.kill()
    
    for file in os.listdir(program_dir):
        if file.endswith(".py"):
            script_path = os.path.join(program_dir, file)       
            proc = subprocess.Popen("python " + script_path, stdout=subprocess.PIPE, shell=True)
            print 'starting : ', "python " + script_path
            processes.append(proc)
            print proc.communicate()[0]
    
    time.sleep(10)
    
    
    print 'New cycle'
    