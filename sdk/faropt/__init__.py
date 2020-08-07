import boto3
from botocore.exceptions import ClientError
import logging
import os
import zipfile
from datetime import datetime
from uuid import uuid4


class FarOpt(object):
    def __init__(self, framework = 'ortools', stackname = 'faropt'):
        
        # Check if backend stack is launched
        cf = boto3.client('cloudformation')
        try:
            response = cf.describe_stacks(StackName=stackname)
            if response['Stacks'][0]['StackStatus'] in ['CREATE_COMPLETE','UPDATE_COMPLETE']:
                print('FarOpt backend is ready!')
                self.ready = True
                self.stackname = stackname
                self.bucket = response['Stacks'][0]['Outputs'][0]['OutputValue']
        except Exception as e:
            self.ready = False
            print(e)
        
        self.allowed_frameworks = ['ortools']
        
        if framework not in self.allowed_frameworks:
            logging.warning("Only ortools is supported for now. You entered "+framework)
            #exit(0)
        else:
            self.framework = framework
    
    def configure (self,source_dir):
        print("Listing project files ...")
        file_name = "source.zip"
        zf = zipfile.ZipFile("source.zip", "w")
    
        for dirname, subdirs, files in os.walk(source_dir):
            #zf.write(dirname)
            for filename in files:
                print(filename)
                zf.write(os.path.join(dirname,filename),filename)
        zf.close()
        
        self.path_file_name = os.path.abspath(file_name)
        self.file_name = file_name
            
        self.configured = True
        print("Configured job!")
        
    def submit(self):
        if self.configured :
            print("Submitting job")
            s3_client = boto3.client('s3')
            try:
                eventid = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                response = s3_client.upload_file(self.path_file_name, self.bucket,eventid+'/'+self.file_name)
                print(response)
                print("Submitted job!")
            except ClientError as e:
                logging.error(e)
                return False
        else:
            logging.error('Please configure the job first!')
            
        self.submitted = True
        
    def logs(self):
        print("Tailing logs")