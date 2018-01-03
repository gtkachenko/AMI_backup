import boto3
from datetime import datetime
from termcolor import colored
import time
import aws_credentials

##Function for creating AMI's
def create_image(instance, name):
    image = instance.create_image(
        Name=str(name) +'_{0}_{1}'.format(instance.id, datetime.now().strftime('%Y-%m-%d_%H-%M')),
        Description='string',
        NoReboot=True,
    )
    print("Image with id {} creating".format(image.image_id))

    tag = image.create_tags(
        Tags=[
            {
                'Key': 'Instance_id',
                'Value': instance.id
            },
        ]
    )

    return image.image_id


#Get list of available AMI's after
def get_list_images(instance, name):
    images = ec2.images.filter(
        Filters=[
            {
                'Name': 'name',
                'Values': [
                   str(name) + "*",
                 ]
            },
        ]
    ).all()
    image_dates = {image.image_id: image.creation_date for image in images}
    sorted_images = sorted(image_dates.items(), key=lambda x: x[1], reverse=True)
    return sorted_images

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



ec2 = boto3.resource('ec2',
                         aws_access_key_id=aws_credentials.access_key,
                         aws_secret_access_key=aws_credentials.secret_key,
                         region_name=aws_credentials.ec2_region
                         )

for i in get_instances():
        create_image(i,get_instances_name(i))
        print ('AWS need some times during AMI will be created so we get list of AMI after 2 minutes')
        time.sleep(120)
        list_amis = get_list_images(i, get_instances_name(i))
        oldest_ami, new_ami = list_amis[-1],list_amis[0]
        print ('The oldest  AMI is: ' + colored(oldest_ami, 'red'))
        print ('The newest AMI is: ' + colored(new_ami, 'green'))

