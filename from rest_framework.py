from rest_framework.views import APIView
from rest_framework.response import Response
import os

class BucketView(APIView):
    def get(self, request):
        path = request.query_params.get('path')
        dirs = {'buckets' : []}
        for files in os.listdir(path):
            if not os.path.isfile(files):
                dirs['buckets'].append(files)
        
        return Response(dirs)
    
    
class BucketDetailView(APIView):
    def get(self, request):
        bucket_name = request.query_params.get('bucket_name')
        txt_files_dict = {'files' : []}
        for files in os.listdir(bucket_name):
            if os.path.isfile(files) and files.endswith('.txt'):
                txt_files_dict['files'].append(files) 
            
        return Response(txt_files_dict)
    

class TextFileView(APIView):
    def get(self, request):
        bucket_name = request.query_params.get('path')
        txt_files_dict = {'files' : []}
        for files in os.listdir(bucket_name):
            if os.path.isfile(files) and files.endswith('.txt'):
                txt_files_dict['files'].append(files) 
            
        return Response(txt_files_dict)
    
    
                
                
        