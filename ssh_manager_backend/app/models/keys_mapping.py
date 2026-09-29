# from typing import List, Union
#
# from sqlalchemy.exc import SQLAlchemyError
#
# from ssh_manager_backend.db import Key, KeyMapping
# from ssh_manager_backend.db.database import db_session
#
#
# class KeyMappingModel:
#     def __init__(self):
#         self.session = db_session()
#
#     def exists(self, ip_address: str) -> bool:
#         """
#         Checks whether a mapping exists or not.
#
#         :param ip_address:
#         :return: Boolean value indicating whether mapping is present or not.
#         """
#
#         return (
#             self.session.query(KeyMapping)
#             .filter(KeyMapping.ip_address == ip_address)
#             .first()
#             is not None
#         )
#
#     def create(self, ip_address: str, key_name: str) -> bool:
#         """
#         Creates a key mapping in db.
#
#         :param ip_address:
#         :param key_name:
#         :return: Boolean value indicating success/failure.
#         """
#
#         try:
#             key_mapping = KeyMapping(key_name=key_name, ip_address=ip_address)
#             self.session.add(key_mapping)
#             self.session.commit()
#         except SQLAlchemyError:
#             self.session.rollback()
#             return False
#
#         return True
#
#     def get_mapping(self, ip_address: str) -> Union[None, KeyMapping]:
#         """
#         Gets the mapping with specified IP.
#
#         :param ip_address:
#         :return: KeyMapping object
#         """
#
#         return (
#             self.session.query(KeyMapping)
#             .filter(KeyMapping.ip_address == ip_address)
#             .first()
#         )
#
#     def get_all_mappings(self) -> List[KeyMapping]:
#         """
#         Gets all mappings from db.
#
#         :return: list of mappings
#         """
#
#         return self.session.query(KeyMapping).all()
