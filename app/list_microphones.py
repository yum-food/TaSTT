import pyaudio
import json
import sys

try:
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    microphones = []
    for i in range(0, numdevices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        if device_info.get('maxInputChannels') > 0:
            microphones.append({
                'index': i,
                'name': device_info.get('name'),
                'defaultSampleRate': device_info.get('defaultSampleRate')
            })

    print(json.dumps(microphones))
    p.terminate()
except Exception as e:
    print(json.dumps({'error': str(e)}), file=sys.stderr)
    sys.exit(1) 