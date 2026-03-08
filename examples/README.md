# Examples

This directory contains example scripts demonstrating how to use `argparse-usage`.

## Examples

- [basic_usage.py](./basic_usage.py) - Basic usage with flags, args, and subcommands
- [complex_usage.py](./complex_usage.py) Complex CLI with nested subcommands (config, database, deploy)

## Running the Examples

All examples are executable and use the `--usage` flag to generate a usage spec:

```bash
./basic_usage.py --usage
./complex_usage.py --usage
```

## Shell Completions

You can generate shell completions for your CLI tools using the `usage` CLI.

### Setting Up Completions for Zsh

There are two ways to set up completions in zsh:

#### Method 1: Source in .zshrc

First, make sure your CLI script is on your PATH:

```bash
# Add examples directory to PATH (or symlink your script)
export PATH="$PATH:$(pwd)"
```

Now you can source the completions directly:

```bash
# Source completions for basic_usage.py
source <(usage generate completion zsh basic_usage.py --usage-cmd "basic_usage.py --usage")

# Or for complex_usage.py
source <(usage generate completion zsh complex_usage.py --usage-cmd "complex_usage.py --usage")
```

**Important:** The completions require:

1. Your CLI script to be on your PATH
2. The `usage` CLI to be available at runtime

For persistent completions, add the `source` command to your `~/.zshrc`:

```bash
# ~/.zshrc
source <(usage generate completion zsh basic_usage.py --usage-cmd "basic_usage.py --usage")
```

#### Method 2: Install to Completion Directory

Alternatively, install the completion script to your zsh completion functions directory. Zsh will automatically load completions from directories in `$fpath`.

Common completion directories:

- `~/.local/share/zsh/site-functions/`
- `/usr/local/share/zsh/site-functions/` (requires sudo)

```bash
# Create the directory if needed
mkdir -p ~/.local/share/zsh/site-functions

# Ensure it's in your $fpath (add to ~/.zshrc if not)
fpath=(~/.local/share/zsh/site-functions $fpath)

# Generate and save the completion script
usage generate completion zsh basic_usage.py --usage-cmd "basic_usage.py --usage" > ~/.local/share/zsh/site-functions/_basic_usage_py

# Rebuild the completion cache
compinit
```

### Using Saved Spec Files

Alternatively, you can save the usage spec to a file and use it for completions:

```bash
# Generate and save the spec
./basic_usage.py --usage > basic_usage.usage.kdl

# Generate completions using the saved spec
usage generate completion zsh basic_usage.py --file basic_usage.usage.kdl > ~/.local/share/zsh/site-functions/_basic_usage.py
```

### Trying Completions

After sourcing, try out the completions:

```bash
# Basic completion
./basic_usage.py <TAB>  # Shows: create, delete, list

# Subcommand completion
./basic_usage.py create <TAB>  # Shows flags: --help, --type, --force, --verbose, --config

# Flag value completion
./basic_usage.py create --type <TAB>  # Shows: default (and any other types if specified)
```

### Other Shells

> [!WARNING]
>
> The following is mostly AI generated and untested. Contributions are welcome!

Completions work for bash, fish, powershell, and nu as well:

#### Bash

```bash
# Source directly
source <(usage generate completion bash basic_usage.py --usage-cmd "basic_usage.py --usage" --include-bash-completion-lib)

# Or install to /etc/bash_completion.d/ (requires sudo)
usage generate completion bash basic_usage.py --usage-cmd "basic_usage.py --usage" --include-bash-completion-lib | sudo tee /etc/bash_completion.d/basic_usage
```

Add to `~/.bashrc` for persistent sourcing.

#### Fish

```bash
# Source directly
source (usage generate completion fish basic_usage.py --usage-cmd "basic_usage.py --usage" | psub)

# Or install to ~/.config/fish/completions/
usage generate completion fish basic_usage.py --usage-cmd "basic_usage.py --usage" > ~/.config/fish/completions/basic_usage.py.fish
```

#### PowerShell

```powershell
# Add to your PowerShell profile
usage generate completion powershell basic_usage.py --usage-cmd "basic_usage.py --usage" | Out-File -Encoding utf8 (Join-Path $PROFILE 'completions.ps1')
```

Then add `. (Join-Path $PROFILE 'completions.ps1')` to your PowerShell profile.

#### Nushell

```nushell
# Add to your env.nu config
usage generate completion nu basic_usage.py --usage-cmd "basic_usage.py --usage" | save -f ~/.config/nushell/completions/basic_usage.nu
```

Then add `source ~/.config/nushell/completions/basic_usage.nu` to your Nushell config.
