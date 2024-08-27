import argparse
import os
from pathlib import Path

from cryptography.fernet import Fernet
from dynaconf import Dynaconf
from openai import OpenAI


# Generate and save encryption key to file
def generate_and_save_key(filepath):
    key = Fernet.generate_key()
    with open(filepath, "wb") as keyfile:
        keyfile.write(key)
    return key


# Load encryption key from file
def load_encryption_key(filepath):
    keyfile_path = Path(filepath)
    if not keyfile_path.exists():
        key = generate_and_save_key(filepath)
    else:
        with open(filepath, "rb") as keyfile:
            key = keyfile.read()
    return Fernet(key)


keyfile_path = os.path.expanduser("~/.config/suru/keyfile")
cipher = load_encryption_key(keyfile_path)

# Setup Dynaconf with specified settings files
settings = Dynaconf(
    environments=False,
    envvar_prefix="",
    settings_files=[
        os.path.expanduser("~/.config/suru/settings.toml"),
        "suru.toml",
    ],
)


def main():
    parser = argparse.ArgumentParser(description="Suru CLI application.")
    parser.add_argument("messages", nargs="*", help="Messages to be printed.")
    parser.add_argument(
        "--set-key", metavar="VALUE", help="Set configuration variable with the value."
    )

    args = parser.parse_args()

    if args.set_key:
        value = args.set_key
        save_api_key(value)
    elif args.messages:
        # Read and decrypt the current API key
        api_key = load_api_key()
        client = OpenAI(
            # This is the default and can be omitted
            api_key=api_key,
        )
        combined_message = " ".join(args.messages)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": combined_message,
                }
            ],
            model="gpt-3.5-turbo",
        )
        print(chat_completion.choices[0].message.content)
    else:
        parser.print_help()


def save_api_key(api_key, global_setting=True):
    encrypted_api_key = cipher.encrypt(api_key.encode()).decode()

    # Determine the path to save the API key
    config_path = Path(
        os.path.expanduser("~/.config/suru/settings.toml")
        if global_setting
        else "settings.toml"
    )
    config_dir = config_path.parent

    # Ensure the config directory exists for global settings
    if global_setting:
        config_dir.mkdir(parents=True, exist_ok=True)

    # Write the encrypted API key to the configuration file
    with open(config_path, "w") as configfile:
        configfile.write(f'OPENAI_API_KEY="{encrypted_api_key}"\n')
    print(f"Encrypted API key saved to {config_path}")


def load_api_key(global_setting=True):
    # Determine the path to load the API key
    config_path = Path(
        os.path.expanduser("~/.config/suru/settings.toml")
        if global_setting
        else "settings.toml"
    )

    if not config_path.exists():
        print(f"Config file {config_path} does not exist.")
        exit(1)

    # Read the encrypted API key from the configuration file
    with open(config_path, "r") as configfile:
        encrypted_api_key = None
        for line in configfile:
            if line.startswith("OPENAI_API_KEY"):
                encrypted_api_key = line.split("=", 1)[1].strip().strip('"')

    if encrypted_api_key is None:
        print("API key not found in the configuration file.")
        exit(1)

    # Decrypt and return the API key
    return cipher.decrypt(encrypted_api_key.encode()).decode()


if __name__ == "__main__":
    main()
