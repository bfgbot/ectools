from ectools import new_instances, get_latest_status
from pathlib import Path
import time
import pandas as pd

user_data = (Path(__file__).parent / "setup.sh").read_text()
new_instances = new_instances("devserver", 2, group_name="my-group", UserData=user_data)
print("created instances", new_instances)

time.sleep(10)

df_instances = pd.DataFrame(get_latest_status())
print(df_instances)
