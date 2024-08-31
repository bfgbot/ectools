from ectools import new_instances
from pathlib import Path

user_data = Path("setup.sh").read_text()
new_instances("my-launch-template", 10, group_name="my-group", UserData=user_data)
