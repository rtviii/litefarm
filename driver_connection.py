import paramiko
import psycopg


def create_ssh_tunnel(ssh_host, ssh_port, ssh_user, ssh_key_path, remote_host, remote_port):
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_key = paramiko.RSAKey.from_private_key_file(ssh_key_path)

    ssh_client.connect(ssh_host, port=ssh_port, username=ssh_user, pkey=ssh_key)
    transport = ssh_client.get_transport()

    print("Connected to app.litefarm.org")
    print("transport:", transport)
    exit(1)
    ssh_tunnel = ssh_client.get_transport().open_tunnel( remote_host, remote_port )
    return ssh_tunnel

def connect_to_postgres(ssh_tunnel, db_user, db_password, db_name):
    conn = psycopg.connect(
        database = db_name,
        user     = db_user,
        password = db_password,
        host     = 'localhost',
        port     = ssh_tunnel.local_bind_port
    )
    return conn


if __name__ == "__main__":

    SSH_HOST     = 'app.litefarm.org'
    SSH_PORT     = 22
    SSH_USER     = 'litefarm'
    SSH_KEY_PATH = '/home/rtviii/.ssh/litefarm_rsa'

    REMOTE_HOST = 'app.litefarm.org'
    REMOTE_PORT = 5433
    DB_USER     = 'readonly'
    DB_PASSWORD = '*P%9yVPxDb6&68$vW3'
    DB_NAME     = 'pg-litefarm'

    ssh_tunnel = create_ssh_tunnel( SSH_HOST, SSH_PORT, SSH_USER, SSH_KEY_PATH, REMOTE_HOST, REMOTE_PORT )
    exit(1)
    conn       = connect_to_postgres(ssh_tunnel, DB_USER, DB_PASSWORD, DB_NAME)


    # Now you can use `conn` to execute SQL queries or interact with the database
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM your_table;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    cursor.close()
    conn.close()