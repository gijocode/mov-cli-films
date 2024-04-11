<div align="center">

  # mov-cli-films 
  <sub>A mov-cli v4 plugin for watching Films and Shows.</sub>

  <img src="https://github.com/mov-cli/mov-cli-vadapav/assets/132799819/6406133d-f840-424b-a1c9-04599fadb0a7">

</div>

> [!WARNING]
> We are on the lookout for maintainers and if we don't find any soon this project may become unmaintained! Please consider or nominate a friend. Thank you.

## Installation
Here's how to install and add the plugin to mov-cli.

1. Install the pip package.
```sh
pip install mov-cli-films 
```
2. Then add the plugin to your mov-cli config.
```sh
mov-cli -e
```
```toml
[mov-cli.plugins]
films = "mov-cli-films"
```

## Usage
```sh
mov-cli -s films the rookie
```
