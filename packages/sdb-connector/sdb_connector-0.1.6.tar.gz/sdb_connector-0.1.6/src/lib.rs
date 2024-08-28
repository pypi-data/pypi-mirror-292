use surrealdb::Surreal;
use surrealdb::opt::auth::Root;
use surrealdb::sql::Value;
use surrealdb::engine::remote::ws::Client;
use surrealdb::engine::remote::ws::Ws;
use std::collections::HashMap;
use serde_json::Value as JsonValue;
use std::error::Error;
use std::time::Instant;
use pyo3::prelude::*;
use pyo3::types::PyAny;
use serde::{Deserialize, Serialize};


#[derive(Debug, Serialize, Deserialize)]
struct UdpTag49 {
    len_trigger: u16,
    run_counter: u64,
    channel: Vec<u8>,
    peak: Vec<u16>,
}

#[pymodule]
fn sdb_connector(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(select_measurement_data_with_db_connect, m)?)?;
    m.add_function(wrap_pyfunction!(return_data, m)?)?;
    Ok(())
}


#[pyfunction]
fn select_measurement_data_with_db_connect(ip: &str, port: &str,
    user: &str, pw:&str, namespace: &str, db_name: &str,
    table_name: &str, run_id: &str) -> PyResult<Vec<(u16, u64, u8, u16)>> {
    // Create a Tokio runtime and block on the async function
    let rt = tokio::runtime::Runtime::new().unwrap();
    let data = rt.block_on(select_data_with_db_connect_async_exe(ip, port,user, pw, namespace, db_name, table_name,run_id)).unwrap();
    Ok(data)
}

// Function to connect to the database
async fn connect_to_db(
    ip: &str,
    port: &str,
    user: &str,
    pw: &str,
    namespace: &str,
    db_name: &str
) -> Result<Surreal<Client>, Box<dyn Error>> {
    let db = Surreal::new::<Ws>(format!("{}:{}", ip, port)).await?;
    db.signin(Root {
        username: &format!("{}", user),
        password: &format!("{}", pw),
    })
    .await?;
    db.use_ns(&format!("{}", namespace)).use_db(&format!("{}", db_name)).await?;
    Ok(db)
}


// Function to query data and process it
async fn query_and_process_data(
    db: &Surreal<Client>,
    table_name: &str,
    run_id: &str
) -> Result<Vec<(u16, u64, u8, u16)>, Box<dyn Error>> {
    let result_query = format!(
        "SELECT run_counter, len_trigger, channel, peak FROM {} WHERE run_id = {} ORDER BY run_counter ASC",
        table_name, run_id
    );
    let result = db.query(&result_query).await?;
    let mut ddata = result;
    let data: Vec<UdpTag49> = ddata.take(0).unwrap();
    let exploded_data: Vec<(u16, u64, u8, u16)> = data
        .into_iter()
        .flat_map(|tag| {
            tag.channel.into_iter()
                .zip(tag.peak.into_iter()) // Combine the channel and peak vectors
                .map(move |(channel_value, peak_value)| {
                    (tag.len_trigger, tag.run_counter, channel_value, peak_value)
                })
        })
        .collect();
    Ok(exploded_data)
}

// Main function that uses both helper functions
async fn select_data_with_db_connect_async_exe(
    ip: &str,
    port: &str,
    user: &str,
    pw: &str,
    namespace: &str,
    db_name: &str,
    table_name: &str,
    run_id: &str
) -> Result<Vec<(u16, u64, u8, u16)>, Box<dyn Error>> {
    let db = connect_to_db(ip, port, user, pw, namespace, db_name).await?;
    query_and_process_data(&db, table_name, run_id).await
}


#[pyfunction]
fn return_data() -> PyResult<(Vec<i64>, Vec<&'static str>)> {
    // Generate data in Rust
    let column1 = vec![1, 2, 3];
    let column2 = vec!["a", "b", "c"];
    // Return the data as a tuple of vectors
    Ok((column1, column2))
}
