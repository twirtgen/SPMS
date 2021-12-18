extern crate redis;
use std::collections::HashMap;

#[derive(Serialize, Deserialize)]
pub struct PluginEntry {
    binding: Vec<u8>,
    source: Vec<u8>,
    verifiers: HashMap<String, HashMap<String, String>>
}

pub fn add_binding(client: &redis::Client, verifiers: &Vec<String>, plugin_name: &str, source: &[u8], binding: &[u8]) -> Result<(), String>{
    let mut con = match client.get_connection() {
        Ok(con) => con,
        Err(e) => return Err(e.to_string())
    };
    let mut pipe = redis::pipe();
    pipe.atomic()
        .cmd("HSET").arg(plugin_name).arg("source").arg(source).ignore()
        .cmd("HSET").arg(plugin_name).arg("binding").arg(binding).ignore();
    for verifier in verifiers {
        pipe.cmd("HSET").arg(format!("{}##{}", plugin_name, verifier)).arg("status").arg("empty");
    }
    pipe.execute(&mut con);
    println!("add_binding");
    Ok(())
}

pub fn get_binding(client: &redis::Client, verifier: &str) -> Result<(String, Vec<u8>), String> {
    let mut con = match client.get_connection() {
        Ok(con) => con,
        Err(e) => return Err(e.to_string())
    };
    let keys: Vec<String> = match redis::cmd("KEYS").arg(format!("*##{}", verifier)).query(&mut con) {
        Ok(keys) => keys,
        Err(e) => return Err(e.to_string())
    };
    for key in keys {
        let verifier_result: HashMap<String, String> = match redis::cmd("HGETALL").arg(&key).query(&mut con) {
            Ok(result) => result,
            Err(e) => return Err(e.to_string()),
        };
        if verifier_result["status"] == "empty" {
            let key_split: Vec<&str> = key.split("##").collect();
            let plugin = key_split[0].to_string();
            match redis::cmd("HGET").arg(&plugin).arg("source").query(&mut con) {
                Ok(source) => return Ok((plugin, source)),
                Err(e) => return Err(e.to_string())
            }
        }
    }
    Err("".to_string())
}

pub fn dump(client: &redis::Client) -> Result<HashMap<String, PluginEntry>, redis::RedisError> {
    let mut con = match client.get_connection() {
        Ok(con) => con,
        Err(e) => return Err(e)
    };
    let keys: Vec<String> = match redis::cmd("KEYS").arg("*").query(&mut con) {
        Ok(keys) => keys,
        Err(e) => return Err(e)
    };
    let mut collect: HashMap<String, PluginEntry> = HashMap::new();
    for key in keys {
        let result: HashMap<String, String> = redis::cmd("HGETALL").arg(&key).query(&mut con).unwrap();
        if key.contains("##") {
            // entry is a verifier
            let splitted_entry: Vec<&str> = key.split("##").collect();
            match collect.get_mut(splitted_entry[0]) {
                Some(plugin_entry) => { 
                    plugin_entry.verifiers.insert(splitted_entry[1].to_string(), result.to_owned());
                },
                None => {
                    collect.insert(splitted_entry[0].to_string(), PluginEntry {
                        source: Vec::new(),
                        binding: Vec::new(),
                        verifiers: HashMap::from([(splitted_entry[1].to_string(), result.to_owned())])}
                    );
                }
            }
        } else {
            match collect.get_mut(&key) {
                None => {
                    collect.insert(key, PluginEntry {
                        binding: result["binding"].as_bytes().to_owned(),
                        source: result["source"].as_bytes().to_owned(),
                        verifiers: HashMap::new()
                    });
                },
                Some(plugin_entry) => {
                    plugin_entry.binding = result["binding"].as_bytes().to_owned();
                    plugin_entry.source = result["source"].as_bytes().to_owned();
                }
            }
        }
    }
    Ok(collect)
}
