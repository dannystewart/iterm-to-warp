# iTerm to Warp

Convert an iTerm plist-based `.itermcolors` theme file to a YAML Warp theme.

## Usage

Just run the command with the iTerm theme as an argument:

```bash
poetry run python iterm_to_warp.py "Kali Linux.itermcolors"
```

You'll be prompted to name the new theme, and the file will be saved as `your_name.yaml`.
