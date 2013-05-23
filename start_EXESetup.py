
from distutils.core import setup
import py2exe

setup (zipfile=None,console=[{"script":r"F:\programing\python\app\CoolAnaylser\start.py","icon_resources": [(1, "F:\\programing\\python\\autoexetool\some.ico")]}],
options={"py2exe":{"compressed":True,"bundle_files":1,"packages": ["encodings"]}})

