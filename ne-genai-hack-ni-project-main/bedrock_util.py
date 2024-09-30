import boto3
import json
from enum import Enum

class BedRockModel(Enum):
    ANTHROPIC_CLAUDE = 'anthropic.claude-v1'
    ANTHROPIC_CLAUDE_V2 = 'anthropic.claude-v2'
    ANTHROPIC_CLAUDE_INSTANT = 'anthropic.claude-instant-v1'
    AMAZON_TITAN_LARGE = 'amazon.titan-tg1-large'
    AI21_J2_ULTRA = 'ai21.j2-ultra'
    AI21_J2_MID = 'ai21.j2-mid'

session = boto3.Session(profile_name='bedrock-user')
bedrock = session.client('bedrock' , 'us-east-1', endpoint_url='https://bedrock.us-east-1.amazonaws.com')


def invoke_model(model_type, prompt):
    model_id = get_model_id(model_type)
    input = get_input_config(model_id, prompt)
    response = bedrock.invoke_model(modelId=input['modelId'], contentType=input['contentType'], accept=input['accept'], body=json.dumps(input['body']))
    response_body = json.loads(response.get('body').read())
    response = get_response_text(model_id, response_body)
    return response

def get_model_id(model_type):
    for model in BedRockModel:
        if model.name == model_type:
            return model.value

def get_input_config(model_id, prompt):
    if model_id.startswith('anthropic'):
        return {
            "modelId": model_id,
            "contentType": "application/json",
            "accept": "*/*",
            "body": {
                "prompt": prompt,
                "max_tokens_to_sample": 150,
                "temperature": 0.5,
                "top_k": 250,
                "top_p": 0.5,
                "stop_sequences": []
            }
        }
    elif model_id.startswith('ai21'):
        return {
            "modelId": model_id,
            "contentType": "application/json",
            "accept": "*/*",
            "body": {
                "prompt": prompt,
                "maxTokens": 150,
                "temperature": 0.5,
                "topP": 0.5,
                "stopSequences": [],
                "countPenalty":{"scale":0},
                "presencePenalty":{"scale":0},
                "frequencyPenalty":{"scale":0}
            }  
        }
    elif model_id.startswith('amazon'):
        return {
        "modelId": model_id,
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 50,
            "stopSequences": [],
            "temperature":0,
            "topP":0.9
            }
        } 
    }
    else:
        raise Exception('unsupported model type')

        
def get_response_text(model_id, response_body):
    if model_id.startswith('anthropic'):
        return response_body.get('completion')
    elif model_id.startswith('ai21'):
        return response_body.get('completions')[0].get('data').get('text')
    elif model_id.startswith('amazon'):
        return response_body.get('results')[0].get('outputText')
    else:
        raise Exception('unsupported model type')

