#!/usr/bin/env python3

import time
import multiprocessing
import sigint_handler
from database import SHUTDOWN, VOICE_COMMAND, db_initialize
from multiprocessing.managers import DictProxy
import asyncio
import sounddevice
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

# Captures spoken sound and converts speech to text commands
# This requires AWS transcribe:StartStreamTranscription permissions
def speech_recognizer(db: DictProxy):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(basic_transcribe(db))
    loop.close()

    print("Shutting down the Speech Recognizer")

class MyEventHandler(TranscriptResultStreamHandler):
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):

        valid_set_commands = ["take off",
                              "land",
                              "move left",
                              "move right",
                              "move forward",
                              "move backward",
                              "turn right",
                              "turn left"]

        valid_open_commands = ["target"]

        results = transcript_event.transcript.results
        if len(results):
            command = results[0].alternatives[0].transcript
            for substring in valid_set_commands:
                if substring in command.lower():
                    if substring == self.last_command:
                        return
                    self.last_command = substring
                    self.db[VOICE_COMMAND] = substring
            for substring in valid_open_commands:
                if substring in command.lower():
                    if substring == self.last_command:
                        return
                    res = command.lower().split(substring, 1)
                    attribute = res[1].replace(".","")
                    self.db[VOICE_COMMAND] = substring + attribute
        else:
            self.last_command = None

async def mic_stream(db):
    loop = asyncio.get_event_loop()
    input_queue = asyncio.Queue()

    def callback(indata, frame_count, time_info, status):
        loop.call_soon_threadsafe(input_queue.put_nowait, (bytes(indata), status))

    stream = sounddevice.RawInputStream(
        channels=1,
        samplerate=16000,
        callback=callback,
        blocksize=1024 * 2,
        dtype="int16",
    )

    with stream:
        while True:
            if db.get(SHUTDOWN, False):
                return
            indata, status = await input_queue.get()
            yield indata, status


async def write_chunks(stream, db):
    async for chunk, status in mic_stream(db):
        await stream.input_stream.send_audio_event(audio_chunk=chunk)
    await stream.input_stream.end_stream()


async def basic_transcribe(db):
    client = TranscribeStreamingClient(region="us-east-2")

    # Start transcription to generate our async stream
    stream = await client.start_stream_transcription(
        language_code="en-US",
        media_sample_rate_hz=16000,
        media_encoding="pcm",
    )

    # Instantiate our handler and start processing events
    handler = MyEventHandler(stream.output_stream)
    handler.db = db
    handler.last_command = None
    await asyncio.gather(write_chunks(stream, db), handler.handle_events())

# ---------------------------------------------------------------------
# The following is only an example of how to call the speech_recognizer
# and how to get the text command from the db
# You can start this with:
#     python speech_recognizer.py
# And Ctrl+C to shut it down

if __name__ == '__main__':
    with multiprocessing.Manager() as manager:
        db = manager.dict()
        db_initialize(db)

        p = multiprocessing.Process(target=speech_recognizer, args=(db, ))

        p.start()

        while not sigint_handler.shutdown_signal:
            voice_command = db[VOICE_COMMAND]
            if voice_command:
                print(f'Got voice command: {voice_command}')
                db[VOICE_COMMAND] = None
            else:
                print('No voice command')
            time.sleep(1)

        print('Main process shutting down ...')

        # Signal all subprocesses to shutdown
        db[SHUTDOWN] = True

        # Wait for them to finish
        p.join()

        print('Shutdown complete')
