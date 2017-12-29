import boto3
from datetime import datetime
from termcolor import colored

##Function for creating AMI's
def create_image(instance,name):
    image = instance.create_image(
        Name=str(name) +'_{0}_{1}'.format(instance.id, datetime.now().strftime('%Y-%m-%d_%H-%M')),
        Description='string',
        NoReboot=True,
    )
    print("Image with id {} created".format(image.image_id))

    tag = image.create_tags(
        Tags=[
            {
                'Key': 'Instance_id',
                'Value': instance.id
            },
        ]
    )

    return image.image_id


def get_list_images(instance):
    images = ec2.images.filter(
        Filters=[
            {
                'Name': 'name',
                'Values': [
                    'ami_backup_{}*'.format(instance.id),
                ]
            },
        ]
    ).all()
    image_dates = {image.image_id: image.creation_date for image in images}

    return images
#Get instance name
def get_instances_name(instance):
    names = []
    for tag in instance.tags:
        if tag['Key'] == 'Name':
            names.append(tag['Value'])
    return names

#Function for getting instances that should be backuped
def get_instances():
    instances = ec2.instances.filter(
        Filters=[
            {
                'Name': 'tag:Backup',
                'Values': ['yes']

            }
        ]
    ).all()

    return instances


access_key = '*'
secret_key = '*'
ec2_region = '*'

ec2 = boto3.resource('ec2',
                         aws_access_key_id=access_key,
                         aws_secret_access_key=secret_key,
                         region_name=ec2_region
                         )

for i in get_instances():
        create_image(i,get_instances_name(i))
        for item in get_list_images(i):
            print (colored(item, 'green'))

