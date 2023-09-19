import os
from urllib import response
from .models import S3Object
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.core.files.storage import default_storage
from storages.backends.s3boto3 import S3Boto3Storage
import boto3
from django.templatetags.static import static

s3 = boto3.client('s3',
                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
bucket_name = settings.AWS_STORAGE_BUCKET_NAME

def get_image_url(key: str):
    location = s3.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
    url = "https://s3-%s.amazonaws.com/%s/%s" % (location, bucket_name, key)
    return url

def display_image(request):
    files =[]

    response = s3.list_objects(Bucket=bucket_name, Prefix='ultrasond_images/') 
    location = s3.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
    
    for content in response.get('Contents', []):
        object_key = content['Key']
        url = "https://s3-%s.amazonaws.com/%s/%s" % (location, bucket_name, content.get('Key'))
                
        object_metadata = s3.head_object(Bucket=bucket_name, Key=object_key)['Metadata']
        aux = {"key":object_key, "metadata": object_metadata, "url": url}
        files.append(aux)
        
    context = {
        'files': files
        }
           
    return render(request, 'display_image.html', context=context)

def update_metadata(request, url:str):    
    if request.method == 'POST':
        ga = request.POST.get('ga')
        hallazgo = request.POST.get('hallazgo')
        tipo_examen = request.POST.get('tipo_examen')
        sexo = request.POST.get('sexo')
        if request.POST.get('new_name_metadato') == None:
            otro_name = ""
        else:
            otro_name = request.POST.get('new_name_metadato')
        if request.POST.get('new_value_metadato') == None:
            otro_value = ""
        else:
            otro_value = request.POST.get('new_value_metadato')
        all_post_parameters = request.POST.keys()
        
        new_metadata = {'Content-Type': 'application/json', 'ga': ga, 'hallazgo': hallazgo,
                        'tipo_examen' : tipo_examen, 'sexo': sexo, otro_name : otro_value}
        
        other_parameters = [param for param in all_post_parameters if param not in ['ga', 'hallazgo', 'tipo_examen', 'sexo', 'new_name_metadato', 'new_value_metadato', 'csrfmiddlewaretoken']]
        for param_name in other_parameters:
            param_value = request.POST.get(param_name)
            new_metadata[param_name] = param_value

        s3.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key':'ultrasond_images/'+url }, MetadataDirective='REPLACE', Metadata=new_metadata, Key='ultrasond_images/'+url)

    tipo_examen_file = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key='metadata_info/tipo_examen.txt')
    hallazgo_file = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key='metadata_info/hallazgo.txt')
    ga_file = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key='metadata_info/ga.txt')
    sexo_file = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key='metadata_info/sexo.txt')
    
    tipo_examen_file_content = tipo_examen_file['Body'].iter_lines()
    hallazgo_file_content = hallazgo_file['Body'].iter_lines()
    ga_file_content = ga_file['Body'].iter_lines()
    sexo_file_content = sexo_file['Body'].iter_lines()
    
    
    aux_1 = []
    aux_2 = []
    aux_3 = []
    aux_4 = []
    for line in tipo_examen_file_content:
        aux_1.append(line.decode('utf-8'))
    
    for line in hallazgo_file_content:
        aux_2.append(line.decode('utf-8'))
        
    for line in ga_file_content:
        aux_3.append(line.decode('utf-8'))
    
    for line in sexo_file_content:
        aux_4.append(line.decode('utf-8'))
    
    object_metadata = s3.head_object(Bucket=bucket_name, Key='ultrasond_images/'+url)['Metadata']
    
    context = {
        'url': get_image_url('ultrasond_images/'+url),
        'tipo_examen' : aux_1,
        'hallazgo' : aux_2,
        'ga': aux_3,
        'sexo': aux_4,
        'tipo_examen_metadato': object_metadata.get('tipo_examen'),
        'hallazgo_metadato': object_metadata.get('hallazgo'),
        'ga_metadato': object_metadata.get('ga'),
        'sexo_metadato': object_metadata.get('sexo'),
        'filtered_metadata' : {key: value for key, value in object_metadata.items() if key != 'sexo' and key != 'ga' and key !='tipo_examen' and key != 'hallazgo' and key != 'content-type' and key != 'csrfmiddlewaretoken'}
    }
    
    return render(request, 'image_details.html', context=context)
