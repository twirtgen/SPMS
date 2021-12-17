extern crate redis;
extern crate serde;
#[macro_use] extern crate serde_derive;
#[macro_use] extern crate rouille;

mod manager {
    static VERIFIERS: [&str; 3] = ["P0", "P1", "P2"];

    pub fn add_binding(client: &redis::Client, plugin_name: &str, source: &[u8], binding: &[u8]) -> redis::RedisResult<()>{
        let mut con = client.get_connection()?;
        let mut pipe = redis::pipe();
        pipe.atomic()
            .cmd("HSET").arg(plugin_name).arg("source").arg(source).ignore()
            .cmd("HSET").arg(plugin_name).arg("binding").arg(binding).ignore();
        for verifier in VERIFIERS {
            pipe.cmd("HSET").arg(format!("{}##{}", plugin_name, verifier)).arg("status").arg("empty");
        }
        pipe.execute(&mut con);
        println!("add_binding");
        Ok(())
    }

    pub fn get_binding(client: &redis::Client, verifier: &str) -> redis::RedisResult<()> {
        let mut con = client.get_connection()?;
        let mut pipe = redis::pipe();
        let result: redis::Value = redis::cmd("KEYS").arg(format!("*##{}", verifier)).query(&mut con)?;
        let a: Vec<String> = redis::from_redis_value(&result)?;
        let res: redis::Value = redis::transaction(&mut con, &a, |con, pipe| {
            pipe.atomic();
            for key in a.iter() {
                println!("{}", key);
                pipe.cmd("HGET").arg(key).arg("status");
            }
            pipe.query(con)
        })?;
        let b :Vec<String> = redis::from_redis_value(&res)? ;
        for i in  b {
            println!("{}", i);
        }
        println!("get_binding");
        Ok(())
    }
}


fn main() {
    let a = std::env::var("VERIFIERS").unwrap();
    let verifiers: Vec<&str> = a.split(',').collect();
    println!("{:#?}", verifiers);

    let redis_url: String = std::env::var("REDIS").unwrap();
    let client = redis::Client::open(format!("redis://{}", redis_url)).unwrap();

    rouille::start_server("localhost:8000", move |request| {
        router!(request,
            (POST) (/binding/{plugin_name: String}) => {
                #[derive(Deserialize)]
                struct Data {
                    binding: String,
                    source: String
                }
                let input: Data = try_or_404!(rouille::input::json_input(request));
                let _ = manager::add_binding(&client, &plugin_name, input.source.as_bytes(), input.binding.as_bytes());
                rouille::Response::empty_204()
            },
            /*(GET) (/binding/{verifier: String}) => {
                if verifiers.iter().any(|e| *e == verifier) {
                    rouille::Response::empty_404()
                }
                let _ = manager::get_binding(&client, &verifier);
                rouille::Response::empty_204()
            },*/
            _ => rouille::Response::empty_404()
        )
    });
}
