include!("src/settings/schema.rs");

use schemars::schema_for;
use std::fs;

// generated by `sqlx migrate build-script`
fn main() {
    // trigger recompilation when a new migration is added
    println!("cargo:rerun-if-changed=migrations");
    println!("cargo:rerun-if-changed=cli/src/settings/schema.rs");

    let schema_dest_path = get_cargo_target_dir().unwrap().join("settings.schema.json");

    let schema = schema_for!(Settings);

    fs::write(
        schema_dest_path,
        serde_json::to_string_pretty(&schema).unwrap(),
    )
    .unwrap();
}

fn get_cargo_target_dir() -> Result<std::path::PathBuf, Box<dyn std::error::Error>> {
    let out_dir = std::path::PathBuf::from(std::env::var("OUT_DIR")?);
    let profile = std::env::var("PROFILE")?;
    let mut target_dir = None;
    let mut sub_path = out_dir.as_path();
    while let Some(parent) = sub_path.parent() {
        if parent.ends_with(&profile) {
            target_dir = Some(parent);
            break;
        }
        sub_path = parent;
    }
    let target_dir = target_dir.ok_or("not found")?;
    Ok(target_dir.to_path_buf())
}
