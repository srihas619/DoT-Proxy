import socket
import ssl
import logging
import yaml


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )


def handle_dns(socket_address, dns_servers):
    """
    Binds a socket and listens for TCP connections. Sends response to client.
    :param socket_address: Address to bind the socket
    :param dns_servers: DoT servers for HA
    :return:
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (socket_address, 53)
    logging.info('starting server listening on %s port %s' % server_address)
    sock.bind(server_address)
    sock.listen(1)

    while True:
        logging.info('waiting for a connection')
        connection, client_address = sock.accept()

        try:
            logging.info('connection from %s', client_address)

            while True:
                data = connection.recv(512)
                logging.info('received "%s"' % data)

                if data:
                    logging.info('received data from the client')

                    response_data = encrypt_send(data, dns_servers)

                    if response_data:
                        connection.sendall(response_data)

                else:
                    logging.info('no more data from %s', client_address)
                    break

        except Exception as e:
            logging.error(e)

        finally:
            connection.close()


def encrypt_send(payload, dns_servers):
    """
    Encrypt payload and send to Nameserver. Return response from Nameserver.
    :param payload: Data containing DNS query
    :param dns_servers: DoT servers for HA
    :return: response from DoT server
    """

    for dns_server in dns_servers:

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations('/etc/ssl/cert.pem')

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as client_sock:
            with context.wrap_socket(client_sock, server_hostname=dns_server) as ssock:

                try:
                    ssock.settimeout(0.2)
                    ssock.connect((dns_server, 853))
                    ssock.send(payload)
                    logging.info('payload sent via encrypted socket')
                    response_ns = ssock.recv(1024)
                    logging.info('received response from Nameserver %s' % response_ns)
                    break

                except Exception as e:
                    logging.error('encountered exception %s', str(e))
                    continue

    else:
        logging.error('cannot connect to any server')
        return False

    return response_ns


if __name__ == '__main__':

    with open('./config.yml', 'r') as f:

        conf_parsed = yaml.load(f.read(), Loader=yaml.SafeLoader)

    handle_dns(socket_address=conf_parsed['SOCKET_ADDRESS'], dns_servers=conf_parsed['DNS_SERVERS'])
