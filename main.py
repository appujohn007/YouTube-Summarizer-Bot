import os
import re
import speech_recognition as sr
from pydub import AudioSegment
from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL
from pyrogram import Client, filters
from groq import Groq
from config import Telegram, Ai
from database import db

import pyrogram.utils

pyrogram.utils.MIN_CHANNEL_ID = -1009999999999

Log = -1002211381375
Summary_Topic = 3
Error_Topic = 4

system_prompt ="""
Do NOT repeat unmodified content.
Do NOT mention anything like "Here is the summary:" or "Here is a summary of the video in 2-3 sentences:" etc.
User will only give you youtube video subtitles, For summarizing YouTube video subtitles:
- No word limit on summaries.
- Use Telegram markdowns for better formatting: **bold**, *italic*, `monospace`, ~~strike~~, <u>underline</u>, <pre language="c++">code</pre>.
- Try to cover every concept that are covered in the subtitles.

For song lyrics, poems, recipes, sheet music, or short creative content:
- Do NOT repeat the full content verbatim.
- This restriction applies even for transformations or translations.
- Provide short snippets, high-level summaries, analysis, or commentary.

Be helpful without directly copying content."""

# Initialize the Pyrogram client
client = Client('bot', api_id=Telegram.API_ID, api_hash=Telegram.API_HASH, bot_token=Telegram.BOT_TOKEN)

# Speech recognizer
recognizer = sr.Recognizer()

async def extract_youtube_transcript(youtube_url, client, message):
    try:
        video_id_match = re.search(r"(?<=v=)[^&]+|(?<=youtu.be/)[^?|\n]+", youtube_url)
        video_id = video_id_match.group(0) if video_id_match else None
        if video_id is None:
            return "no transcript"

        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try to find a transcript in the desired languages
        try:
            transcript = transcript_list.find_transcript(['en', 'ja', 'ko', 'de', 'fr', 'ru', 'it', 'es', 'pl', 'uk', 'nl', 'zh-TW', 'zh-CN', 'zh-Hant', 'zh-Hans'])
            transcript_text = ' '.join([item['text'] for item in transcript.fetch()])
            return transcript_text
        except:
            # If not found, try to get the first available transcript
            for trans in transcript_list:
                transcript_text = ' '.join([item['text'] for item in trans.fetch()])
                return transcript_text

    except Exception as e:
        error_message = f"Error: {e}\nUser: {message.chat.id}"
        await client.send_message(Log, error_message)
        print(f"Error: {e}")
        return "no transcript"

async def get_groq_response(user_prompt, system_prompt, client, message):
    try:
        client = Groq(api_key=Ai.GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        error_message = f"#Error\n\nError getting Groq response: {e}\n\nUser: {message.chat.id}"
        await client.send_message(Log, error_message)
        print(f"Error getting Groq response: {e}")
        return "Error getting AI response."

@client.on_message(filters.command('start'))
async def start(client, message):
    await message.reply("""
**ʜᴇʟʟᴏ 😗**

**𝙸 𝚊𝚖 𝚊 𝚜𝚒𝚖𝚙𝚕𝚎 𝚝𝚎𝚕𝚎𝚐𝚛𝚊𝚖 𝙱𝚘𝚝 𝚖𝚊𝚍𝚎 𝚝𝚘 𝚜𝚞𝚖𝚖𝚊𝚛𝚒𝚣𝚎 𝚊 𝚈𝚘𝚞𝚝𝚞𝚋𝚎 𝚅𝚒𝚍𝚎𝚘......**

**𝗛𝗼𝘄 𝘁𝗼 𝗨𝘀𝗲 𝗠𝗲**

**sᴇɴᴅ ᴍᴇ ᴀɴʏ ʏᴏᴜᴛᴜʙᴇ ʟɪɴᴋs. ᴀɴᴅ ɪ ᴡɪʟʟ.sᴜᴍᴍᴀʀɪᴢᴇ ɪᴛs ᴄᴏɴᴛᴇɴᴛ ᴀɴᴅ ᴇxᴘʟᴀɪɴ ɪᴛ ᴛᴏ ʏᴏᴜ. ᴠᴇʀʏ sɪᴍᴘʟᴇ ʙᴏᴛ.
ʏᴏᴜ ᴄᴀɴ sᴀᴠᴇ ʏᴏᴜʀ ᴛɪᴍᴇ ᴡᴀᴛᴄʜɪɴɢ ᴜɴᴡᴀɴᴛᴇᴅ ᴠɪᴅᴇᴏs, ʙᴜᴛ ǫᴜɪᴄᴋʟʏ ɢᴇᴛs ɪᴛs ɪɴғᴏ
ɪ ᴄᴀɴ ʙᴇ ᴀ ʟᴏᴛ ᴏғ ᴀ ʜᴇʟᴘ ɪɴ ʏᴏᴜʀ sᴛᴜᴅɪᴇs**


**𝖒𝖆𝖉𝖊 𝖜𝖎𝖙𝖍 😘 𝖇𝖟 [.ｉｏ ｄｅｖｓ](https://t.me/botio_devs)**
""", disable_web_page_preview=True)
    if not await db.is_inserted("users", message.chat.id):
        await db.insert("users", message.chat.id)

@client.on_message(filters.command('users') & filters.user(6883997969))
async def users(client, message):
    try:
        users = len(await db.fetch_all("users"))
        await message.reply(f'Total Users: {users}')
    except Exception as e:
        error_message = f"#Error\n\nError: {e}\nUser: {message.chat.id}"
        await client.send_message(Log, error_message)
        print(e)

@client.on_message(filters.private & filters.regex(r'https?://\S+'))
async def handle_message(client, message):
    url = message.text
    print(f"Received URL: {url}")

    # Check if the message is a YouTube link
    if 'youtube.com' in url or 'youtu.be' in url:
        x = await message.reply('Attempting to download captions from the YouTube video...')
        print("Attempting to download captions from YouTube...")

        try:
            # Try to get the transcript first
            transcript_text = await extract_youtube_transcript(url, client, message)
            if transcript_text != "no transcript":
                print("Transcript fetched successfully.")
                await x.edit('Captions found and downloaded. Summarizing the text...')

                summary = await get_groq_response(transcript_text, system_prompt, client, message)
                await x.edit(f'{summary}')

                # Send summary to the log group
                summary_message = f"#Success\n\n Summary:\n{summary}\nUser: {message.chat.id}"
                await client.send_message(Log, summary_message)
            else:
                # No transcript available, fallback to audio transcription
                return await x.edit('No captions found. Unable To Transcribe The YouTube video. Sorry...')
               # print("No captions found. Downloading audio from YouTube...")

                try:
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                        'outtmpl': 'downloaded_audio.%(ext)s'
                    }

                    with YoutubeDL(ydl_opts) as ydl:
                        info_dict = ydl.extract_info(url, download=True)
                        output_file = ydl.prepare_filename(info_dict)
                        output_file = output_file.replace(".webm", ".mp3")  # Adjust extension if needed

                    print(f"Downloaded audio to {output_file}")
                    await x.edit('Converting audio to text...')
                    print("Converting audio to text...")

                    # Convert audio to WAV format
                    try:
                        audio = AudioSegment.from_file(output_file)
                        wav_file = "audio.wav"
                        audio.export(wav_file, format="wav")
                        print(f"Converted audio to {wav_file}")

                        # Convert audio to text
                        with sr.AudioFile(wav_file) as source:
                            recognizer.adjust_for_ambient_noise(source)
                            audio_data = recognizer.record(source)
                            try:
                                text = recognizer.recognize_google(audio_data)
                                print(f"Transcribed text: {text}")

                                # Summarize the transcribed text
                                await x.edit('Summarizing the text...')
                                summary = await get_groq_response(text, system_prompt, client, message)
                                print(f"Summary: {summary}")
                                await x.edit(f'{summary}')

                                # Send summary to the log group
                                summary_message = f"#Success\n\nSummary:\n{summary}\nUser: {message.chat.id}"
                                await client.send_message(Log, summary_message)
                            except sr.RequestError:
                                error_message = "API unavailable."
                                await client.send_message(Log, f"#Error\n\nError: {error_message}\nUser: {message.chat.id}")
                                print(error_message)
                                await x.edit(error_message)
                            except sr.UnknownValueError:
                                error_message = "Unable to recognize speech."
                                await client.send_message(Log, f"#Error\n\nError: {error_message}\nUser: {message.chat.id}")
                                print(error_message)
                                await x.edit(error_message)
                    except Exception as e:
                        error_message = f"Error during transcription: {str(e)}"
                        await client.send_message(Log, f"#Error\n\nError: {error_message}\nUser: {message.chat.id}")
                        print(error_message)
                        await x.edit(error_message)
                    finally:
                        # Clean up files
                        if os.path.exists(output_file):
                            os.remove(output_file)
                            print(f"Deleted file: {output_file}")
                        if os.path.exists(wav_file):
                            os.remove(wav_file)
                            print(f"Deleted file: {wav_file}")
                except Exception as e:
                    error_message = f"Error: {str(e)}"
                    await client.send_message(Log, f"#Error\n\nError: {error_message}\nUser: {message.chat.id}")
                    print(error_message)
                    await x.edit(error_message)
        except Exception as e:
            error_message = f"Error: {str(e)}"
            await client.send_message(Log, f"#Error\n\nError: {error_message}\nUser: {message.chat.id}")
            print(error_message)
            await x.edit(error_message)
    else:
        print("Invalid YouTube link.")
        await message.reply('Please send a valid YouTube link.')

@client.on_message(filters.command('bcast') & filters.user(Telegram.AUTH_USER_ID))
async def bcast(client, message):
    if not message.reply_to_message:
        return await message.reply(
            "Please use `/bcast` as reply to the message you want to broadcast."
        )
    msg = message.reply_to_message
    xx = await message.reply("In progress...")
    users = await db.fetch_all('users')
    done = error = 0
    for user_id in users:
        try:
            await client.send_message(
                int(user_id),
                msg.text.format(user=(await client.get_users(int(user_id))).first_name),
                file=msg.media,
                buttons=msg.buttons,
                disable_web_page_preview=True,
            )
            done += 1
        except Exception as brd_er:
            error_message = f"Broadcast error:\nChat: {int(user_id)}\nError: {brd_er}"
            await client.send_message(Log, error_message)
            print(error_message)
            error += 1
    await xx.edit(f"Broadcast completed.\nSuccess: {done}\nFailed: {error}")

if __name__ == '__main__':
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        loop.run_until_complete(client.start())
        loop.run_until_complete(idle())
    except Exception as e:
        error_message = f"Error running the bot: {e}"
        loop.run_until_complete(client.send_message(Log, error_message))
        print(error_message)
    finally:
        loop.run_until_complete(client.stop())
        loop.close()
