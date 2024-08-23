import json
import sys
import time

for level in ['debug','error','fatal','info','warn','trace']:
    """Create functions for each log level dynamically"""
    exec(f"""def {level}(message: str, extra: dict={{}}, stream=sys.stderr):
        contents = {{'timestamp':int(time.time()), 'message': message, 'level': '{level}'}} | extra
        stream.write(json.dumps(contents))
    """)
