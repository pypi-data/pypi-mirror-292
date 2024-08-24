import sdb_connector as sdb_con
import time

print("Hello, World!")
x = sdb_con.sum_as_string(1, 2)
print(x)

start = time.time()
result = sdb_con.select_measurement_data_with_db_connect("192.168.2.63", "8000", 
            "root", "root","main", "data", "amv_tag_49", "run_info:01J4XRFVTY9XSBCECW2NHWHMGK")
end = time.time()
print("Time taken: ", end - start)