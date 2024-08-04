import streamlit as st
import requests
import json
import time
import random
import string

def generate_unique_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))

def create_music(prompt, style, title, custom_mode, instrumental):
    url = 'https://brev.erweima.ai/api/v1/suno/create'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'authority': 'brev.erweima.ai',
        'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
        'origin': 'https://brev.ai',
        'referer': 'https://brev.ai/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'uniqueId': generate_unique_id()
    }
    data = {
        "prompt": prompt,
        "style": style,
        "title": title,
        "customMode": custom_mode,
        "instrumental": instrumental
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def load_pending_record(record_id):
    url = 'https://brev.erweima.ai/api/v1/suno/loadPendingRecordList'
    headers = {
        'authority': 'brev.erweima.ai',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/json',
        'origin': 'https://brev.ai',
        'referer': 'https://brev.ai/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'uniqueid': generate_unique_id(),
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
    }
    data = {"pendingRecordIdList": [record_id]}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def extend_music(record_id, audio_index):
    url = 'https://brev.erweima.ai/api/v1/suno/extend'
    headers = {
        'authority': 'brev.erweima.ai',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/json',
        'origin': 'https://brev.ai',
        'referer': 'https://brev.ai/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'uniqueid': generate_unique_id(),
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
    }
    data = {"customFlag": False, "recordId": record_id, "audioIndex": audio_index}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def main():
    st.title("Chirp - AI Music Generator")

    prompt = st.text_input("Enter a prompt for your music:")
    style = st.text_input("Enter a style (optional):")
    title = st.text_input("Enter a title (optional):")
    custom_mode = st.checkbox("Custom Mode")
    instrumental = st.checkbox("Instrumental")

    if st.button("Generate Music"):
        with st.spinner("Generating music..."):
            result = create_music(prompt, style, title, custom_mode, instrumental)
            if result['code'] == 200:
                record_id = result['data']['recordId']
                st.success(f"Music generation started. Record ID: {record_id}")

                # Poll for the music to be ready
                complete = False
                while not complete:
                    time.sleep(5)  # Wait for 5 seconds before checking again
                    pending_result = load_pending_record(record_id)
                    if pending_result['code'] == 200 and pending_result['data']:
                        data = pending_result['data'][0]
                        if data['state'] == 'success' and data['sunoData']['sunoData']:
                            complete = True
                            audio_data = data['sunoData']['sunoData'][0]
                            st.audio(audio_data['audioUrl'], format='audio/mp3')
                            st.image(audio_data['imageUrl'], caption="Generated Music Image")
                            st.success(f"Music generated successfully. Title: {audio_data['title']}")

                            # Option to extend the music
                            if st.button("Extend Music"):
                                with st.spinner("Extending music..."):
                                    extend_result = extend_music(record_id, 0)
                                    if extend_result['code'] == 200:
                                        extended_record_id = extend_result['data']['recordId']
                                        st.success(f"Music extension started. New Record ID: {extended_record_id}")

                                        # Poll for the extended music to be ready
                                        extend_complete = False
                                        while not extend_complete:
                                            time.sleep(5)
                                            extended_pending_result = load_pending_record(extended_record_id)
                                            if extended_pending_result['code'] == 200 and extended_pending_result['data']:
                                                extended_data = extended_pending_result['data'][0]
                                                if extended_data['state'] == 'success' and extended_data['sunoData']['sunoData']:
                                                    extend_complete = True
                                                    extended_audio_data = extended_data['sunoData']['sunoData'][0]
                                                    st.audio(extended_audio_data['audioUrl'], format='audio/mp3')
                                                    st.image(extended_audio_data['imageUrl'], caption="Extended Music Image")
                                                    st.success(f"Music extended successfully. New duration: {extended_audio_data['duration']} seconds")
                    else:
                        st.warning("Music is still being generated. Please wait...")
            else:
                st.error("Failed to start music generation. Please try again.")

if __name__ == "__main__":
    main()
