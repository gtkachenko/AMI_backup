import boto3
from datetime import datetime
from termcolor import colored
import time
import aws_credentials

#Function for creating AMI's
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

#Get redunant images
def get_redundant_images(instance,name):

    tags = get_tags_dict(instance)
    ami_retention = int(tags['ami_backup'] if tags['ami_backup'] else 7)
    images = ec2.images.filter(
        Filters=[
            {
                'Name': 'name',
                'Values': [
                    str(name) + '*',
                ]
            },
        ]
    ).all()

    image_dates = {image.image_id: image.creation_date for image in images}
    sorted_images = sorted(image_dates.items(), key=lambda x: x[1], reverse=True)

    return sorted_images[ami_retention:]

#Delete redundant instance
def delete_redundant_images(images):
    for i in images:
        image = ec2.Image(i[0])
        print("Image with id {} deregistered".format(image.id))
        image.deregister()
        snaps = ec2.snapshots.filter(
            DryRun=False,
            Filters=[
                {
                    'Name': 'description',
                    'Values': [
                        '*{}*'.format(image.id),
                    ]
                },
            ]
        ).all()
        for snap in snaps:
            print("Snapshot with id {} deleted".format(snap.snapshot_id))
            snap.delete()


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

#Get instnaces tags
def get_tags_dict(instance):
    return {item['Key']: item['Value'] for item in instance.tags}

ec2 = boto3.resource('ec2',
                         aws_access_key_id=aws_credentials.access_key,
                         aws_secret_access_key=aws_credentials.secret_key,
                         region_name=aws_credentials.ec2_region
                         )

for i in get_instances():
        create_image(i,get_instances_name(i))
        print ('AWS need some times during AMI will be created time set by dafult two minutes')
        time.sleep(120)
        redundant_images = get_redundant_images(i,get_instances_name(i))
        delete_redundant_images(redundant_images)
        print('AWS need sime time during AMI will be deleted so we get list of all available AMI it takes one minutes by default')
        time.sleep(60)
        list_amis = get_list_images(i, get_instances_name(i))
        oldest_ami, new_ami = list_amis[-1],list_amis[0]
        print ('The oldest  AMI is: ' + colored(oldest_ami, 'red'))
        print ('The newest AMI is: ' + colored(new_ami, 'green'))

