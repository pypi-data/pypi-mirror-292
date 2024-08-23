import subprocess
import os

runtime_script = os.path.join(os.path.dirname(__file__), 'runtime.sh')
subprocess.call(runtime_script)