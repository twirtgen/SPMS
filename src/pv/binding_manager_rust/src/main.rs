extern crate serde;
#[macro_use] extern crate serde_derive;
#[macro_use] extern crate rouille;
mod manager;

fn main() {
    let verifiers: Vec<String> = match std::env::var("VERIFIERS") {
        Ok(verifiers) => verifiers.split(',').map(String::from).collect(),
        Err(_e) => return
    };

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
                match manager::add_binding(&client, &verifiers, &plugin_name, input.source.as_bytes(), input.binding.as_bytes()) {
                    Ok(_) => rouille::Response::text(""),
                    Err(e) => rouille::Response::text(e).with_status_code(500)
                }
            },
            (GET) (/binding/{verifier: String}) => {
                match manager::get_binding(&client, &verifier) {
                    Ok((plugin, source)) => rouille::Response::from_data("application/octet-stream", source).with_additional_header("X-plugin_name", plugin),
                    Err(e) => { 
                        if e == "".to_string() { 
                            rouille::Response::empty_404()
                        } else {
                            rouille::Response::text(e).with_status_code(404)
                        }
                    }
                }
            },
            (GET) (/internal/dump) => {
                match manager::dump(&client) {
                    Ok(content) => rouille::Response::json(&content),
                    Err(e) => rouille::Response::text(e.to_string()).with_status_code(500)
                }
            },
            _ => rouille::Response::empty_404()
        )
    });
}
