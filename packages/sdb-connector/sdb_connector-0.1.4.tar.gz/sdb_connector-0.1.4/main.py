import sdb_connector as sdb_con
import time
import pandas as pd

print("Hello, World!")
x = sdb_con.return_data()
print(x)

start = time.time()
result = sdb_con.select_measurement_data_with_db_connect("192.168.2.63", "8000", 
                "root", "root","main", "data", "amv_tag_49", "run_info:01J4XRFVTY9XSBCECW2NHWHMGK")
print(result)
df = pd.DataFrame(result, columns=['Column1', 'Column2', 'Column3', 'Column4'])

# Display the DataFrame
print(df)
end = time.time()
print("Time taken: ", end - start)