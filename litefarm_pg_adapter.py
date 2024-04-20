import os
import psycopg
from sshtunnel import SSHTunnelForwarder
import paramiko
import io
import logging
import pandas as pd
import sys
from sqlalchemy import text
import psycopg2
from psycopg import Connection
import dotenv


# persist "Started" session in class
# class yields a postgress session on query

dotenv.load_dotenv("/home/rtviii/dev/litefarm/db.env")

LITEFARM_DB_HOST     = os.environ["LITEFARM_DB_HOST"]
LITEFARM_DB_USER     = os.environ["LITEFARM_DB_USER"]
LITEFARM_DB_PASSWORD = os.environ["LITEFARM_DB_PASSWORD"]
LITEFARM_DB_NAME     = os.environ["LITEFARM_DB_NAME"]
LITEFARM_DB_SSH_KEY  = os.environ["LITEFARM_DB_SSH_KEY"]
LITEFARM_DB_SSH_USER = os.environ["LITEFARM_DB_SSH_USER"]

print(LITEFARM_DB_HOST)
print(LITEFARM_DB_SSH_KEY)
print(LITEFARM_DB_SSH_USER)


class LitefarmPostgresAdapter(): 

    tunnel_to_remote    : SSHTunnelForwarder| None = None
    postgres_connection : Connection|None          = None


    def __init__(self) -> None:
        self._establish_tunnel()
        self._establish_postgres_connection()

    def _establish_tunnel(self):
        print("Initially the tunnel to remote is ", self.tunnel_to_remote)
        if self.tunnel_to_remote is not None:
            self.tunnel_to_remote.restart()
            return
        key                   = paramiko.RSAKey.from_private_key_file(LITEFARM_DB_SSH_KEY)
        self.tunnel_to_remote = SSHTunnelForwarder(
            (LITEFARM_DB_HOST, 22),
            ssh_username        = LITEFARM_DB_SSH_USER,
            ssh_pkey            = key,
            remote_bind_address = ("localhost", 5433),
            local_bind_address  = ("localhost", 5433))

        self.tunnel_to_remote.start()
        print("Established SSH tunnel to {}.".format(LITEFARM_DB_HOST))

    def _establish_postgres_connection(self):
        conn = psycopg.connect(conninfo="dbname={} user={} password={} host={} port={}".format( 
            LITEFARM_DB_NAME,
              LITEFARM_DB_USER,
              LITEFARM_DB_PASSWORD,
              'localhost',
              '5433' ))
        self.postgres_connection = conn
        print("Established connection to Postgres database.")

    def query(self, query):
        try:
            assert(self.tunnel_to_remote is not None and self.tunnel_to_remote.is_active)
        except AssertionError as e:  
            print(e)
            self._establish_tunnel()

        try: 
            assert(self.postgres_connection is not None and self.postgres_connection.broken is not True)
        except AssertionError as e:
            print(e)
            self._establish_postgres_connection()

        pd.read_sql(text(query), LPA.postgres_connection)
        
def main():
    LPA = LitefarmPostgresAdapter()


    # while True:
    #     user_input = input("Enter 'q' to quit, 'e' to execute action E, or 'f' to execute action F: ")

    #     if user_input == 'q':
    #         # print("Exiting the program...")
    #         print(pd.read_sql("SELECT * FROM farm", LPA.postgres_connection))
    #     elif user_input == 'e':
    #         print("Performing action E...")
    #         # Perform action E here
    #         print(pd.read_sql("SELECT * FROM crop_variety", LPA.postgres_connection))
    #     elif user_input == 'f':
    #         print("Performing action F...")
    #         # Perform action F here
    #     else:
    #         print("Invalid input. Please enter 'q', 'e', or 'f'.")


# main()

# class SSHTunnel():
#     tunnel_to_remote: SSHTunnelForwarder

#     def __init__(self) -> None:
#         key          = paramiko.RSAKey.from_private_key_file(LITEFARM_DB_SSH_KEY)
#         self.tunnel_to_remote = SSHTunnelForwarder(
#             (LITEFARM_DB_HOST, 22),
#             ssh_username=LITEFARM_DB_SSH_USER,
#             ssh_pkey=key,
#             remote_bind_address=("localhost", 5433),
#             local_bind_address=("localhost", 5433)
#             )

#         self.tunnel_to_remote.start()
#         print("Tunnel is active? ", self.tunnel_to_remote.is_active)

# SSHTunnel()