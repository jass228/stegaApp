"""
Author: Joseph ASSOUMA
Date: 30/04/2022
Description: The goal of the app, is to practice streamlit for deploying ML models.
             The app is for decode and encode messages into an image.
"""

import streamlit as st
import cv2
from PIL import Image
import numpy as np
import time
from io import BytesIO

def messageToBinary(message):
    """
    Convert any type of message to binary form
    :param message: Message encode
    """

    if type(message) == str:
      return ''.join([format(ord(i), "08b") for i in message])
    elif type(message) == bytes or type(message) == np.ndarray:
      return [format(i, "08b") for i in message]
    elif type(message) == int or type(message) == np.uint8:
      return format(message, "08b")
    else:
      raise TypeError("Input type not supported")

def hideMessage(image, secret_message):
    """
    function to hide secret message into the image 
    :param image: Image for hiding message
    :secret_message: Message that we want to hide
    :return: Image with the secret message into
    """

    #Maximum bytes to encode
    nBytes = image.shape[0] * image.shape[1] * 3 // 8
    
    #Check if the number of bytes to encode is less than the maximum bytes in the image
    if len(secret_message) > nBytes:
        raise ValueError("Error encountered insufficient bytes, need bigger image or less data !!")
    
    secret_message += "#####"
    dataIndex = 0

    binarySecretMessage = messageToBinary(secret_message)

    dataLen = len(binarySecretMessage)

    for values in image:
        for pixel in values:
            r,g,b = messageToBinary(pixel)
            if dataIndex < dataLen:
                pixel[0] = int(r[:-1] + binarySecretMessage[dataIndex],2)
                dataIndex += 1
            if dataIndex < dataLen:
              pixel[1] = int(g[:-1] + binarySecretMessage[dataIndex],2)
              dataIndex += 1
            if dataIndex < dataLen:
              pixel[2] = int(b[:-1] + binarySecretMessage[dataIndex],2)
              dataIndex += 1
            if dataIndex >= dataLen:
              break
    return image

def showMessage(image):
    """
    function to decode the hidden message from the image encode
    :param image: Image encode
    :return: the hidden message
    """

    binaryData = ""
    for values in image:
        for pixel in values:
            r,g,b = messageToBinary(pixel)
            binaryData += r[-1]
            binaryData += g[-1]
            binaryData += b[-1]

    allBytes = [binaryData[i: i+8] for i in range(0,len(binaryData),8)]

    decodedData = ""
  
    for byte in allBytes:
        decodedData += chr(int(byte, 2))
        if decodedData[-5:] == "#####":
            break
    return decodedData[:-5]

def encodeMessage(img):
    """
    function to encode message into an image
    :params img: Image that we want to hide message into
    """

    st.subheader("Encode Message in Image")

    st.write("The shape of the image is ",img.shape)
    resized_img = cv2.resize(img, (500,500))
    st.image(resized_img, caption='Original Image')
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    data = st.text_area("Enter the message to encode: ")

    if len(data) != 0:
        st.write(data)
        filename = st.text_input("Enter the name of the encoded images (with the extension .png): ")
        if len(filename) != 0 :
            encode_img = hideMessage(img, data)
            if encode_img is not None:
                my_bar = st.progress(0)

                for percent_complete in range(100):
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
                st.write('Image encoded with your message successfully :tada: :tada:')

            encode_img = cv2.cvtColor(encode_img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(encode_img)

            buf = BytesIO()
            pil_img.save(buf, format="PNG")
            byte_im = buf.getvalue()

            btn = st.download_button(
                label="Download encoded image",
                data=byte_im,
                file_name=filename,
                mime="image/png",)
            btn

def decodeMessage(img):
    """
    Function to decode message
    :params img: Image that we want to decode the message
    :returns: Message decode
    """
    st.subheader("Decode Message in Image")

    resized_img = cv2.resize(img, (500,500))
    st.image(resized_img, caption='Image to decode')
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    st.write('wait...')
    message = showMessage(img)
    return message

def main_loop():
    st.title('Encode - Decode App')
    st.subheader("This app allows you to encode and decode message into image")
    st.text("create by @jass228")

    page_name = ['Encode Message', 'Decode Message']

    choicePage = st.sidebar.radio('Choice',page_name)

    choice = ""
    if choicePage == page_name[0]:
        choice = 'encode'
    else:
        choice = 'decode'

    imgText = "Upload your image that you want to " + choice
    img_file = st.file_uploader(imgText,type=['jpg', 'png', 'jpeg'])
    if not img_file:
        return None
    
    original_image = Image.open(img_file)
    original_image = np.array(original_image)

    if choicePage == page_name[0]:
        encodeMessage(original_image)
            
    else:
        message = decodeMessage(original_image)
        my_bar = st.progress(0)
        for percent_complete in range(100):
            time.sleep(0.1)
            my_bar.progress(percent_complete + 1)
        st.subheader("Decode message of the image is : ")
        st.write(message)
        st.write('')
        st.write('Congratulation you have decoded the message from image :tada: :tada:')

        

if __name__ == '__main__':
    main_loop()