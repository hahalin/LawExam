"""錄「電腦正在播放的聲音」（WASAPI loopback），存成 wav。
用法：py record_loopback.py 秒數 輸出.wav 狀態檔
"""
import sys, time, wave
import pyaudiowpatch as pyaudio

secs = float(sys.argv[1]); out = sys.argv[2]; status = sys.argv[3]

p = pyaudio.PyAudio()
wasapi = p.get_host_api_info_by_type(pyaudio.paWASAPI)
dev = p.get_device_info_by_index(wasapi["defaultOutputDevice"])
if not dev.get("isLoopbackDevice"):
    for lb in p.get_loopback_device_info_generator():
        if dev["name"] in lb["name"]:
            dev = lb
            break
ch = int(dev["maxInputChannels"]) or 2
rate = int(dev["defaultSampleRate"])
print("device:", dev["name"], ch, rate, flush=True)

wf = wave.open(out, "wb")
wf.setnchannels(ch)
wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
wf.setframerate(rate)

def cb(data, frames, info, flags):
    wf.writeframes(data)
    return (None, pyaudio.paContinue)

stream = p.open(format=pyaudio.paInt16, channels=ch, rate=rate, input=True,
                input_device_index=dev["index"], frames_per_buffer=2048,
                stream_callback=cb)
with open(status, "w", encoding="utf-8") as f:
    f.write("RECORDING %s\n" % time.strftime("%H:%M:%S"))
stream.start_stream()
time.sleep(secs)
stream.stop_stream(); stream.close(); wf.close(); p.terminate()
with open(status, "a", encoding="utf-8") as f:
    f.write("DONE %s\n" % time.strftime("%H:%M:%S"))
print("saved", out, flush=True)
