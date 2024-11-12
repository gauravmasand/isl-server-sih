import socket
import threading
import base64
import os

# # Function to handle receiving image data (Server side)
# def receive_image(sock):
#     with open("received_image_utf8.txt", "a") as file:  # Open file in append mode to save all lines
#         image_count = 0  # Initialize counter for number of images received
#         buffer = ""  # Buffer to accumulate image data
#         while True:
#             try:
#                 message = sock.recv(1024).decode()
#                 if message:
#                     # # Append received message to buffer
#                     # buffer += message
#                     # # Check for end of an image by delimiter or signal and count it
#                     # if message.endswith("==") or len(message) < 1024:
#                     #     image_count += 1
#                     #     file.write(buffer + "\n")  # Write the full image data to file and add a new line
#                     #     buffer = ""  # Reset buffer for the next image
#                     #     print(f"Number of images received: {image_count}")

#                     # Convert the received base64 encoded string back to binary image data
#                     image_data = base64.b64decode(message)
#                     image_filename = f"images/received_image_{image_count}.jpg"
#                     # Save the image to the 'images' directory
#                     with open(image_filename, "wb") as img_file:
#                         img_file.write(image_data)

#                     # Write the full image data to file and add a new line
#                     file.write(message + "\n")
#                     image_count += 1
#                     print(f"Number of images received: {image_count}")

#                 else:
#                     break
#             except Exception as e:
#                 # If any exception occurs, close the connection
#                 print(f"Connection closed. Error: {e}")
#                 sock.close()
#                 break



# Function to handle receiving image data (Server side)
def receive_image(sock):
    if not os.path.exists("images"):  # Create directory for saving images if it does not exist
        os.makedirs("images")
    
    image_count = 0  # Initialize counter for number of images received
    buffer = ""  # Buffer to accumulate image data
    while True:
        try:
            # Receive data in larger chunks to capture entire images
            message = sock.recv(4096).decode()
            if message:
                buffer += message
                # Use a delimiter to determine end of an image
                while "<END_OF_IMAGE>" in buffer:
                    img_str, buffer = buffer.split("<END_OF_IMAGE>", 1)
                    try:
                        # Convert the received base64 encoded string back to binary image data
                        image_data = base64.b64decode(img_str)
                        image_filename = f"images/received_image_{image_count}.jpg"
                        # Save the image to the 'images' directory
                        with open(image_filename, "wb") as img_file:
                            img_file.write(image_data)
                        print(f"Image saved: {image_filename}")
                        image_count += 1
                        print(f"Number of images received: {image_count}")
                    except base64.binascii.Error:
                        # If decoding fails, continue accumulating
                        print("Decoding error. Continuing to next image.")
                        continue
            else:
                break
        except Exception as e:
            # If any exception occurs, close the connection
            print(f"Connection closed. Error: {e}")
            sock.close()
            break


# Function to handle sending text messages (Server side)
def send_messages(sock):
    while True:
        message = input("Server (You): ")
        sock.send(message.encode())

# Function to act as a server
def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", port))
    server_socket.listen(1)
    print(f"Server listening on port {port}...")
    conn, addr = server_socket.accept()
    print(f"Got connection from {addr}")
    return conn

# Main function to start the server
if __name__ == "__main__":
    port = 12345
    connection = start_server(port)
    # Start threads for receiving images from client and sending text messages
    receive_thread = threading.Thread(target=receive_image, args=(connection,))
    send_thread = threading.Thread(target=send_messages, args=(connection,))
    receive_thread.start()
    send_thread.start()
    receive_thread.join()
    send_thread.join()
