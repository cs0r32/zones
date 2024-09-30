import streamlit as st
import time
from streamlit_image_select import image_select
import pandas as pd
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import os
from streamlit import runtime
from streamlit.web import cli as stcli
import sys
import requests
from html_parser import *
from s3_util import *
try:
    from processor import *
except:
    print("No credentials found. Running on local machine?")
import boto3
import json
from yattag import Doc

st.set_page_config(
    page_title="Image Alt Text Tool",
    page_icon="♿",
    layout="wide",
)

if 'initialised' not in st.session_state:
    st.session_state.initialised = False
if 'generate' not in st.session_state:
    st.session_state.generate = False
if 'generate_all' not in st.session_state:
    st.session_state.generate_all = False
if 'data' not in st.session_state:
    st.session_state.data = None
if 'images' not in st.session_state:
    st.session_state.images = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'html' not in st.session_state:
    st.session_state.html = None
if 'image_original' not in st.session_state:
    st.session_state.image_original = None


st.markdown("""# <center> Zones Demo</center>""", unsafe_allow_html=True)
m1, m2, m3 = st.columns([3, 4, 3])
#st.write(st.session_state)

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]] and st.session_state["login_button"]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        m2.text_input("Username", on_change=password_entered, key="username")
        m2.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        m2.button("Login", type="primary", use_container_width=True, key="login_button", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        m2.text_input("Username", on_change=password_entered, key="username")
        m2.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        m2.button("Login", type="primary", use_container_width=True, key="login_button", on_click=password_entered)
        #st.error("😕 User not known or password incorrect")
        st.error("Login to enter")
        return False
    else:
        # Password correct.
        return True

def upload_img_selected(file_path):
    #ACCESS_KEY = st.secrets["ACCESS_KEY"]
    #SECRET_KEY = st.secrets["SECRET_KEY"]
    s3 = boto3.resource(
        's3'
        #aws_access_key_id=ACCESS_KEY,
        #aws_secret_access_key=SECRET_KEY
    )
    #value = s3.meta.client.upload_file('/tmp/hello.txt', 'hackathonimagebucket2', 'hello.txt')
    s3.meta.client.upload_file(file_path, 'ne-hackathon-demosites-391551377552', file_path)
    client = boto3.client(
        's3'
        #aws_access_key_id=ACCESS_KEY,
        #aws_secret_access_key=SECRET_KEY
    )
    #st.write(client.list_objects(Bucket='hackathonimagebucket2'))
    #st.write(client.head_object(Bucket='hackathonimagebucket2', Key=file_path))

def upload_img_list(img_list):
    s3 = boto3.resource('s3')
    for file_path in img_list:
        s3.meta.client.upload_file(file_path, 'ne-hackathon-demosites-391551377552', file_path)

def main():
    #st.markdown("""# <center> :ledger: Image Alt Text Tool</center>""", unsafe_allow_html=True)
    # Section 1 - Input website data
    with st.form("form_1"):
        col1, col2, col3, col4 = st.columns([2, 4, 1, 2])
        website_link = col2.text_input(
                                        label="Enter website link",
                                        value="website link",
                                        label_visibility="collapsed"
                                    )

        submitted = col3.form_submit_button("Analyze", use_container_width=True)
        downloaded_images = []
        if submitted:
            with col2.status("Analyzing website..."):
                html = scrape_page(website_link)
                st.session_state.html = html
                images = get_images(html)
                st.session_state.image_original = images
                analysis_info = f"Found {len(images)} images without alt text."
                st.toast(analysis_info)
                st.toast("Downloading data...")
                for image in images:
                    image_src = image["src"]
                    downloaded_images.append(download_file(image_src, '/tmp'))
                st.session_state.images = downloaded_images

                st.toast('Success!', icon='🎉')
            col2.success(analysis_info)
            st.session_state.initialised = True

    def generate_alt_text(img_object):
        st.session_state.summary = process_image(bucket_name='ne-hackathon-demosites-391551377552', obj=img_object)
        st.session_state.generate = True
        st.session_state.generate_all = False

    def generate_alt_text_all():
        summary_list = []
        img_list = st.session_state.images 
        for img_object in img_list:
            summary = {}
            summary['image'] = img_object
            summary ['options'] = process_image(bucket_name='ne-hackathon-demosites-391551377552', obj=img_object)
            summary_list.append(summary)
        st.session_state.summary = summary_list
        st.session_state.generate = False
        st.session_state.generate_all = True

    def generate_img_tag(img_path, alt_text):
        doc, tag, text = Doc().tagtext()
        doc.stag('img', src=img_path, alt=alt_text)
        return doc.getvalue()

    def generate_html(html_tags_list):
        doc, tag, text = Doc().tagtext()

        doc.asis('<!DOCTYPE html>')
        with tag('html'):
            with tag('body'):
                for i in range(0, len(html_tags_list)):
                    text(f'{html_tags_list[i]}')
        return doc.getvalue()

    # Section 2 - Thumbnail of images without alt text
    c1, c2, c3 = st.columns([8, 1, 1])
    c1.subheader("Images missing alt text")
    if st.session_state.initialised:
        image_selected = image_select("Select any one", st.session_state.images)
        #st.write(image_selected)
        c3.button("Generate All", disabled=not(st.session_state["initialised"]), use_container_width=True, on_click=generate_alt_text_all, key="gen_all")
        c2.button("Generate", disabled=not(st.session_state["initialised"]), use_container_width=True, on_click=generate_alt_text, args=(image_selected,))
        # upload images to S3 on click
        try:
            upload_img_selected(image_selected)
            upload_img_list(st.session_state.images)
        except:
            st.info("No credentials found. Running on local machine?")
        
        st.subheader("Alt text options")
        o1, o2, o3 = st.columns([1, 8, 1])
        if st.session_state.generate:
            # show alt text options based on the image selected
            img_name = (image_selected.split("tmp/")[1].split(".")[0])
            #o1.markdown(f"#### Selected Image : `{img_name}`")
            options = []
            captions = []
            radio_text = "Alt text options for " + image_selected.split("tmp/")[1]
            for i in st.session_state.summary:
                options.append(i['name'])
                captions.append(i['altText'])
            selected_alt_text = o2.radio(
                    radio_text,
                    captions,
                    #captions = captions,
                    key = img_name
                )
            updated_html = None
            for image in st.session_state.image_original:
                if image['src'].find(img_name) != -1:
                    updated_html = update_alt_text(st.session_state.html, image['src'], selected_alt_text)
                    break
            #img_tag = generate_img_tag(img_name, selected_alt_text)
            #html_output = generate_html(list(img_tag))
            #o2.code(html_output, language='html')
            # extract & display all data
            o3.download_button(
                    label="Extract",
                    data=str(updated_html.prettify()),
                    file_name='hackathon.html',
                    mime='text/html',
                    use_container_width=True,
                )
        elif st.session_state.generate_all:
            #img_tags_list = []
            #img_list_no = 0
            updated_html = st.session_state.html
            for sum1 in st.session_state.summary:
                #st.info("Generating alt texts")
                # show alt text options based on the image selected
                img_name = (sum1['image'].split("tmp/")[1].split(".")[0])
                #o1.markdown(f"#### Selected Image : `{img_name}`")
                opts = []
                captions = []
                radio_text = "Alt text options for " + sum1['image'].split("tmp/")[1]
                for i in sum1['options']:
                    opts.append(i['name'])
                    captions.append(i['altText'])
                    
                selected_alt_text = o2.radio(
                    radio_text,
                    captions,
                    key = img_name
                    #captions = captions
                )

                for image in st.session_state.image_original:
                    if image['src'].find(img_name) != -1:
                        updated_html = update_alt_text(updated_html, image['src'], selected_alt_text)
                        break
                #img_list_no +=1

                #img_tag = generate_img_tag(img_name, selected_alt_text)
                #img_tags_list.append(img_tag)
                
            #html_output = generate_html(img_tags_list)
            #o2.code(html_output, language='html')
            # extract & display all data
            o3.download_button(
                    label="Extract",
                    data=str(updated_html.prettify()),
                    file_name='hackathon.html',
                    mime='text/html',
                    use_container_width=True,
                )
        else:
            st.info("Press Generate/Generate All to get thumbnail alt text")
    else:
        st.info("Enter any website & analyse to search for thumbnails")

if check_password():
    main()