def send_message(sock, message):
    """
    Sends a message through the socket.
    <END> is used as the end-of-message marker.
    """

    sock.send((message + "\n<END>\n").encode())


def receive_message(sock):
    """
    Receives data until <END> is found.
    """

    data = ""

    while "<END>" not in data:

        chunk = sock.recv(1024).decode()

        if not chunk:
            break

        data += chunk

    return data.replace("<END>", "").strip()