import sdb_connector as sdb_conn
import time
import pandas as pd

start = time.time()
result = sdb_conn.select_additional_info_data("192.168.2.63", "8000", 
            "root", "root","main", "data", "amv_tag_49", "run_info:01J4XRFVTY9XSBCECW2NHWHMGK")

#print(result)
df = pd.DataFrame(result, columns=['Column1', 'Column2', 'Column3', 'Column4'])
print(df)

end = time.time()
print("Time taken result: ", end - start)