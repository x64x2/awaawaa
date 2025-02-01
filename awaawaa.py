import sys
import os
import signal
import configparser
import hashlib
import socket
import errno
import select
import threading
import traceback


# "05" Version of the SOCKS protocol
VER = b"\x05"

# "00" Reserved null-byte
RSV = b"\x00"

S_VER  = b"\x01"

# "00" Succeed of authentication
S_PASS = b"\x00"

# "01" Failure of authentication
S_FAIL = b"\x01"


## METHOD constants

# "00" NO AUTHENTICATION REQUIRED
M_NOAUTH     = b"\x00"

# "01" GSSAPI
M_GSSAPI     = b"\x01"

# "02" USERNAME/PASSWORD
M_USERPASS   = b"\x02"

# "FF" NO ACCEPTABLE METHODS (as a response)
M_UNACCEPTED = b"\xff"


# "01" CONNECT
C_CONNECT = b"\x01"

# "02" BIND
C_BIND    = b"\x02"

# "03" UDP ASSOCIATE
C_UDP     = b"\x03"


## ATYP constants

# "01" IP V4 address
A_IPV4 = b"\x01"

# "03" DOMAINNAME
A_NAME = b"\x03"

# "04" IP V6 address
A_IPV6 = b"\x04"


## REP constants

# "00" succeeded
R_SUCCEED = b"\x00"

# "01" general SOCKS server failure
R_FAILURE = b"\x01"

# "02" conenction not allowed by ruleset
R_DENIED  = b"\x02"

# "03" Network unreachable
R_UNNET   = b"\x03"

# "04" Host unreachable
R_UNHOST  = b"\x04"

# "05" Connection refused
R_REFUSED = b"\x05"

# "06" TTL expired
R_EXPIRED = b"\x06"

# "07" Command not supported
R_INVCMD  = b"\x07"

# "08" Address type not supported
R_INVADR  = b"\x08"


thread_id = 0


## Configuration variables (assigned at by load_config)

enable_log         = None
server_port        = None

buffer_size        = None
socket_timeout     = None
max_connections    = None
force_ipv4         = None

auth_mandated      = None
auth_username      = None
auth_password_hash = None

class ServerFailure       (Exception): pass
class AbortedConnection   (Exception): pass
class FailedAuthentication(Exception): pass
class FailedRequest       (Exception): pass
class FallbackToIPv4      (Exception): pass
class QuitProxyLoop       (Exception): pass


def receive_sigterm(sig, frame):

    raise KeyboardInterrupt


def load_config(sig = None, frame = None):

    log("Reloading configuration")

    # List all configuration variables
    global thread_id, buffer_size, socket_timeout, max_connections, \
            enable_log, server_port, auth_mandated, auth_username, \
            auth_password_hash, force_ipv4

    conf = configparser.ConfigParser()
    conf.read(("/etc/awaawaa.ini", os.path.expanduser("~/.awaawaa.ini")))
        # order is important

    enable_log = conf.getboolean("server", "enable_log", fallback = False)
    server_port = conf.getint("server", "inbound_port", fallback = 1080)

    buffer_size = conf.getint("socket", "buffer_size", fallback = 256) * 1024
        # buffer_size in kilobytes
    socket_timeout = conf.getint("socket", "timeout", fallback = 60)
    max_connections = conf.getint("socket", "max_connections", fallback = 128)
    force_ipv4 = conf.getboolean("socket", "force_ipv4", fallback = False)

    auth_mandated = conf.getboolean("auth", "mandated", fallback = False)
    auth_username = conf.get("auth", "username", fallback = "user")
    auth_password_hash = conf.get("auth", "password_hash", fallback =
            "d74ff0ee8da3b9806b18c877dbf29bbde50b5bd8e4dad7a3a725000feb82e8f1")
            # sha256 hash for "pass"


def log(message, report_traceback = False):

    if enable_log:
        
        if threading.current_thread() == threading.main_thread():
            thread = "MAIN"
        else:
            thread = "%04d" % thread_id

        print("[{}] {}".format(thread, message), file = sys.stderr)

    if report_traceback:
        traceback.print_exc()


def undergo_client_connection(client):

    dest = None

    try:

        try:
            log("Receiving identification packet from client")
            ident_packet = client.recv(buffer_size)

        except socket.error:
            log("Cannot receive the packet.  Will abort", True)
            raise AbortedConnection("No identification packet")

        finally:
                try:
                    log("Sending the auth reply to client")
                    client.sendall(S_VER + auth_status)
                    
                except socket.error:
                    log("Cannot send the reply.  Will abort", True)
                    raise AbortedConnection("Cannot confirm authentication")

        if auth_status != S_PASS:
                raise AbortedConnection("Failed to authenticate")

                try:
                    dest.connect((dest_host, dest_port))

                except OSError as e:
                    if e.errno == errno.ENETUNREACH:
                        raise FallbackToIPv4  # Try IPv4 if possible
                    elif e.errno == errno.EHOSTUNREACH:
                        log("Cannot connect to destination", True)
                        raise FailedRequest("Host unreachable", R_UNHOST)
                    elif e.errno == errno.CONNREFUSED:
                        log("Cannot connect to destination", True)
                        raise FailedRequest("Connection refused", R_REFUSED)
                    elif e.errno == errno.ETIME:
                        log("Cannot connect to destination", True)
                        raise FailedRequest("TTL expired", R_EXPIRED)
                    else:
                        log("Cannot connect to destination", True)
                        raise FailedRequest("General failure", R_FAILURE)
 
                except FallbackToIPv4:

                  if atyp == A_IPV6:
                    raise FailedRequest("Address type not supported", R_INVADR)

                log("Using IPv4 now")

                dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dest.settimeout(socket_timeout)
                
                try:
                    dest.connect((dest_host, dest_port))

                except OSError as e:
                    if e.errno == errno.ENETUNREACH:
                        raise FailedRequest("Network unreachable", R_UNNET)
                    elif e.errno == errno.EHOSTUNREACH:
                        log("Cannot connect to destination", True)
                        raise FailedRequest("Host unreachable", R_UNHOST)
                    elif e.errno == errno.CONNREFUSED:
                        log("Cannot connect to destination", True)
                        raise FailedRequest("Connection refused", R_REFUSED)
                    elif e.errno == errno.ETIME:
                        log("Cannot connect to destination", True)
                        raise FailedRequest("TTL expired", R_EXPIRED)
                    else:
                        log("Cannot connect to destination", True)
                        raise FailedRequest("General failure", R_FAILURE)

                    rep = R_SUCCEED

                rep_atyp = A_IPV4 if dest.family == socket.AF_INET else A_IPV6

    finally:
        
        if dest:
            log("Closing the destination connection")
            dest.close()

        log("Closing the client connection")
        client.close()

    log("The thread is terminated")


def main():

    global thread_id
    
    err_code = 1  # default exit status
    
    # Redirecting SIGTERM into SIGINT
    signal.signal(signal.SIGTERM, receive_sigterm)

    # Reload configuration by a SIGHUP
    signal.signal(signal.SIGHUP, load_config)

    # Load configuration at start
    load_config()


    log("awaawaa v1.0 - Log enabled")
    log("Starting the SOCKSv5 proxy server")

    if socket.has_ipv6:
        log("Creating an IPv6 server socket")
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        if socket.has_dualstack_ipv6():
            log("Enabling IPv4 for the socket")
            server.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        else:
            log("Platform does not support dualstack.  Server is IPv6-only")
    else:

        log("Platform does not support IPv6.  Server is IPv4-only")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if __name__ == "__main__":
    
    pid_path = "/run{}awaawaa.pid".format("/" if os.getuid() == 0 else
            "/user/{}/".format(os.getuid()))

    # Writing PID to the pid file
    if os.path.exists(pid_path):
        print("Another awaawaa process is probably running.  Exiting")
        exit(1)

    with open(pid_path, "w") as f:
        f.write(str(os.getpid()))
    
    try:
        main()
    except:
        # Deleting the pid file
        os.remove(pid_path)
        raise
