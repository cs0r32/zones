import json
import boto3
import json
from bedrock_util import *
from s3_util import *
from prompts import *

from botocore.exceptions import ClientError
from textract_util import extract_text


rekognition = boto3.client('rekognition',region_name='us-east-1')
s3_client = boto3.client('s3', region_name='us-east-1')
sagemaker_client = boto3.client('sagemaker-runtime', region_name='us-east-1')
                        

def process_image(bucket_name, obj):

    extraction_res, labels = extract_with_rekognition(bucket_name, obj)
    label_str = ', '.join(labels)
    print('Rekognition detected labels: ' + label_str)

    response_json = {}
    if label_str.find('text') != -1 or label_str.find('chart') != -1 or label_str.find('diagram') != -1:

        if label_str.find('chart') != -1 or label_str.find('diagram') != -1:
            print('This image contains either a chart or a graph')
            query_config = {
                'imageType': 'graph',
                'action': 'summarize'
            }
        else:
            print('This image is not a graph or chart. Extracting text via textract')
            query_config = {
                'imageType': 'text',
                'action': 'summarize'
            }
            extraction_res = extract_text(bucket_name, obj, True)
            
        response_json = gen_alt_text_bedrock(extraction_res, query_config)
    else:
        print('This image does not contain any text. Using Blip2')
        response_json = gen_alt_text_sagemaker_blip('', bucket_name, obj)
    
    return response_json


def extract_with_rekognition(bucket_name, obj):
    label_text = ''
    response = rekognition.detect_labels(
        Image={'S3Object':{'Bucket':bucket_name,'Name':obj}},
        Features=['GENERAL_LABELS']
    )
    
    text_res = rekognition.detect_text(
        Image={'S3Object':{'Bucket':bucket_name,'Name':obj}}
    )

    for text in text_res['TextDetections']:
        if text['Type'] == 'LINE':
            label_text += text['DetectedText'] + ' '

    rekognition_labels = []
    for label in response['Labels']:
        print('Label: ' + label['Name'].lower() + ', ' + str(label['Confidence']))
        if label['Confidence'] > 70:
            rekognition_labels.append(label['Name'].lower())
    
    return label_text, rekognition_labels


def gen_alt_text_bedrock(context, query_config: json):

    claude_p =  ''
    if query_config['imageType'] == 'graph' and query_config['action'] == 'interpret':
        claude_p = claude_prompt_graphs_interpret(context)
    elif query_config['imageType'] == 'graph' and query_config['action'] == 'summarize':
        claude_p = claude_prompt_graph(context)
    else:
        claude_p = claude_prompt(json.dumps(context))
    
    claude_response = invoke_model(BedRockModel.ANTHROPIC_CLAUDE_V2.name, claude_p)
    # remove all new lines and response xml tags from claude_response
    claude_response = claude_response.replace('\n', '')
    claude_response = claude_response.replace('<response>', '')
    claude_response = claude_response.replace('</response>', '')
    
    print(claude_response)
    
    # TODO customize the prompt for the J2 model
    ai21_response = invoke_model(BedRockModel.AI21_J2_ULTRA.name, j2_prompt(context))
    print(ai21_response)
    #remove all new lines from ai21_response
    ai21_response = ai21_response.replace('\n', '')
    #remove double quotes from ai21_response
    ai21_response = ai21_response.replace('"', '')
    # split ai21_response by : and take the second part (the answer)
    if (ai21_response.find(':') != -1):
        ai21_response = ai21_response.split(':')[1]
    response: json = [{
        "name": "option1",
        "modelProvider": "ai21",
        "altText": ai21_response
    }, {
        "name": "option2",
        "modelProvider": "claude",
        "altText": claude_response
    }]
    return response

def gen_alt_text_sagemaker_blip(context, bucket_name, object):

    image_url= create_presigned_url(bucket_name, object)
    print(image_url)

    # Specify the SageMaker endpoint name
    endpoint_name = "huggingface-pytorch-inference-2023-09-16-20-51-29-776"

    # Provide the payload you want to use for prediction
    data = {
        "inputs": {
            "img_url": image_url
        }
    }
    payload = json.dumps(data)

    # Specify the content type and accept headers
    content_type = "application/json"
    accept = "application/json"

    # Invoke the endpoint
    response = sagemaker_client.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType=content_type,
        Accept=accept,
        Body=payload
    )
    response_text = response['Body'].read().decode()
    response_json = json.loads(response_text)
    generated_text = response_json['generated text']
    generated_text = generated_text.replace('\n', '')

    response: json = [{
        "name": "option1",
        "modelProvider": "blip2",
        "altText": generated_text
    }]
    return response



