import boto3
from botocore.exceptions import ClientError
import requests

s3_client = boto3.client('s3', region_name='us-east-1')

def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

# function to upload an image file to s3
def upload_file(file_name, bucket):

    object_name = file_name.split('/')[-1]

    # Upload the file
    s3_client.upload_file(file_name, bucket, object_name)

# function to download an image file from url to local
def download_file(url, folder_path=''):
    # NOTE the stream=True parameter below
    # extract filename from url and save it as file_name
    file_name = url.split('/')[-1]
    download_path = folder_path + '/' + file_name
    r = requests.get(url, stream=True)
    with open(download_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                # f.flush() commented by recommendation from J.F.Sebastian
    return download_path

# function to test download_file
def test_download_file():
    url = 'https://www.gstatic.com/webp/gallery/1.jpg'
    file_name = download_file(url,'/tmp')
    print(file_name)
    assert (file_name == '1.jpg')

if __name__ == '__main__':

    test_download_file()
