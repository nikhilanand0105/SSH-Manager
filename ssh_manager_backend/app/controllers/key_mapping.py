# from threading import Thread
# from typing import Dict
#
# import boto3
# from botocore.exceptions import ClientError
# from flask import Response
#
# from ssh_manager_backend.app.controllers import api
# from ssh_manager_backend.app.models import KeyMappingModel
#
#
# def get_ec2_ip_and_key(region_name: str, mapping: Dict[str, str]):
#     """
#     Gets the IP address and key name of ec2 in the given region and inserts it into the mapping.
#
#     :param region_name: Region name of the ec2
#     :param mapping: mapping of ip addresses and key names
#     :return:
#     """
#
#     client = boto3.client("ec2", region_name=region_name)
#     response = client.describe_instances()
#
#     reservations = response["Reservations"]
#     if len(reservations) > 0:
#         for reservation in reservations:
#             for instance in reservation["Instances"]:
#                 private_ip = instance.get("PrivateIpAddress")
#                 public_ip = instance.get("PublicIpAddress")
#                 key_name = instance.get("KeyName")
#
#                 if key_name is not None:
#                     if private_ip is not None:
#                         mapping[private_ip] = key_name
#                     if public_ip is not None:
#                         mapping[public_ip] = key_name
#
#
# def create_mapping(body: Dict[str, any]) -> Dict[str, str]:
#     """
#     Creates a mapping of EC2 ip addresses to keyName(the ssh key ec2 is using).
#
#     :return:
#     """
#
#     mapping: Dict[str, str] = {}
#     client = boto3.client("ec2", "us-east-1")
#
#     regions = [region["RegionName"] for region in client.describe_regions()["Regions"]]
#
#     workers = list()
#     for region in regions:
#         thread = Thread(target=get_ec2_ip_and_key, args=[region, mapping])
#         workers.append(thread)
#
#     for worker in workers:
#         worker.start()
#
#     for worker in workers:
#         worker.join()
#
#     return mapping
#
#
# def store_mapping(body: Dict[str, any]) -> Response:
#     """
#     Stores the creates mapping in dynamodb table(Table is taken from config file).
#
#     :param body:
#     :return: bool
#     """
#
#     data, key, iv = api.decrypt_request_data(body=body)
#
#     try:
#         mapping: Dict[str, str] = create_mapping()
#         key_mapping: KeyMappingModel = KeyMappingModel()
#         for ip in mapping:
#             key_mapping.create(ip_address=ip, key_name=mapping[ip])
#     except ClientError as err:
#         data = {"success": False}
#         return api.response_data(
#             data=data, message=str(err), status_code=500, key=key, iv=iv
#         )
#
#     data = {"success": True}
#     return api.response_data(data=data, message="", status_code=500, key=key, iv=iv)
#
#
# def get_mapping(body: Dict[str, any]) -> Response:
#     """
#     Searches the stored mapping for the given ip_address and returns the key_name associated with it. If the
#     ip_address is not present in the mapping.
#
#     :param body:
#     :return:
#     """
#
#     data, key, iv = api.decrypt_request_data(body=body)
#     try:
#         key_name = KeyMappingModel().get_mapping(data["ip_address"]).key_name
#         data = {"success": False, "ke_name": key_name}
#         return api.response_data(
#             data=data, message="Key mapping not found", status_code=404, key=key, iv=iv
#         )
#     except AttributeError:
#         data = {"success": False}
#         return api.response_data(
#             data=data, message="Key mapping not found", status_code=404, key=key, iv=iv
#         )
