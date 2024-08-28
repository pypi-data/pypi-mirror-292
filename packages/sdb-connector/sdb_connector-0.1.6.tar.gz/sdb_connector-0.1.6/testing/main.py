import sdb_connector as sdb_conn
from sdb_connector import sdb_con
import time

start = time.time()
result = sdb_conn.select_measurement_data_with_db_connect("192.168.2.63", "8000", 
            "root", "root","main", "data", "amv_tag_49", "run_info:01J4XRFVTY9XSBCECW2NHWHMGK")
end = time.time()
print("Time taken: ", end - start)