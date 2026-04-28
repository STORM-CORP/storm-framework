# Storm Framework Module Guide Explanation 

Cara menambahkan module di Storm sedikit mudah seperti salin -> tulis -> jalan, dan module secara otomatis akan di load dan siap di gunakan. Kita menggunakan mekanisme Dynamic Loading di load hanya saat di panggil.

## information template

You just need to know that Storm uses the Python orchestrator, and the module is also dynamic because we can use even low-level languages for tool efficiency and run it as a subprocess or whatever, as long as Python is running it.

### 1. **Metadata module:**

This is important as metadata to make it easier to find descriptions of modules and other information.

```python
MOD_INFO = {
    "Name": "fill in the module name",
    "Description": """
For a complete explanation
""",
    "Author": ["fill in your name", "examples"],
    "Action": [
        ["Function name", {"Description": "Brief explanation of the function"}],
        ["Function name", {"Description": "Brief explanation of the function"}],
    ],
    "DefaultAction": "Main function",
    "License": "fill in your module license or match GPL-3.0",
}
```

### 2. **Standard Options:**

Just adjust it to what your module needs.

```python
REQUIRED_OPTIONS = {
    "IP": "",
    "PORT": "",
    "PASS": "",
    "URL": "",
    "EMAIL": "",
    "HASH": "",
    "MESSAGE": "",
    "USER": "",
    "ID": "",
    "COUNT": "",
    "PATH": "",
    "INTERFACE": "",
    "PROTOCOL": "",
    "THREAD": "",
    "DOMAIN": "",
    "HOSTNAME": "",
    "MODULE": "",
    "API": "",
    "SUBDOM": ""
}
```

### 3. **Module Function:**

Make sure to always consistently use the entry point function `def execute(options)`, otherwise you are free to use any function name.

```python
# --- Main function ---
def execute(options):

    example = options.get("IP")
    example = options.get("PORT")
    example = options.get("PASS")
    example = options.get("URL")
```

## Compiled Language Module

If you create a module with a compiled language, you need to follow these steps, so that the module can be used.

### 1. **Rust Language:**

You need to add Rust build dependencies in vendor cargo `external/source/dep/Cargo.toml` If the required dependencies are already available from the vendor but the versions are different, you need to follow the version according to the vendor, If there isn't one, you can just add it.

You are not allowed to change the dependency version or remove dependencies in the vendor because the core is afraid of using those dependencies with that version, so you need to follow existing standards.

### 2. **Golang & C Language:**

If this language is easier, you can just write the module with Go/C/C++ and create a Python file like the top step just for the loader.

### Custom Makefile

Make sure to add a Makefile to each compiled language module, whether it's Rust, Go, C/C++, because the compilation is run using a Makefile.

You can use the existing template in `example/Makefile/` and adjust it to your needs.

## Important Warning

When you submit a PR for a compiled language module, make sure you submit readable language source code. Don't submit a binary file because I will immediately reject it.
