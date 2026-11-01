mod config;
mod validation;

use config::Config;
use std::error::Error;
use std::fs;

fn main() -> Result<(), Box<dyn Error>> {
    let config_text = fs::read_to_string("config.toml")?;
    let config: Config = toml::from_str(&config_text)?;
    validation::validate(&config).map_err(|error| {
        format!("Invalid configuration: {error}")
    })?;

    println!("=== Seven Speaking Automation ===");
    println!("Configuration loaded successfully.");
    println!("{config:#?}");

    Ok(())
}