import argparse
import os
import subprocess
from pathlib import Path

import inquirer
from dynaconf import Dynaconf
from openai import OpenAI
from pydantic import BaseModel
from rich import get_console
from rich.padding import Padding
from rich.panel import Panel
from rich.syntax import Syntax


class CommandRecommendation(BaseModel):
    cmd: str


console = get_console()

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
    parser.add_argument("--set-key", metavar="VALUE", help="Set configuration variable with the value.")

    args = parser.parse_args()

    if args.set_key:
        value = args.set_key
        save_api_key(value)
    elif args.messages:
        api_key = load_api_key()
        if not api_key:
            console.print(
                "[bold red]API key not configured.[/bold red] Use --set-key to set the API key or set the 'OPENAI_API_KEY' environment variable."
            )
            exit(1)

        client = OpenAI(api_key=api_key)
        combined_message = " ".join(args.messages)
        with console.status("[bold yellow]Generating...[/bold yellow]"):
            # 目标，将用户的输入的自然语言转换成命令，并解释。
            completion = client.beta.chat.completions.parse(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that can provide command recommendations. You should provide a command recommendation based on the user's input.",
                    },
                    {"role": "user", "content": combined_message},
                ],
                model="gpt-4o-mini",
                response_format=CommandRecommendation,
            )
            # Format the output using a Panel
            message_content = completion.choices[0].message.parsed
            if message_content:
                # print description
                console.print(
                    Panel.fit(
                        Syntax(
                            message_content.cmd,
                            "bash",
                            line_numbers=False,
                            theme="github-dark",
                            background_color="default",
                            word_wrap=True,
                        ),
                        title="Command Recommendation",
                        highlight=True,
                        border_style="cyan",
                        title_align="left",
                    )
                )
        # use inquirer to ask user if they want to run the command
        questions = [inquirer.Confirm("run_command", message="Would you like to run this command?", default=True)]
        answers = inquirer.prompt(questions)
        if answers and answers["run_command"]:
            try:
                result = subprocess.run(message_content.cmd, shell=True, check=True, text=True, capture_output=True)
                console.print(Padding(result.stdout, (1, 0, 0, 0)))
            except subprocess.CalledProcessError as e:
                console.print(f"[bold red]Error running command:[/bold red] \n{e}")
    else:
        parser.print_help()


def save_api_key(api_key, global_setting=True):
    # Determine the path to save the API key
    config_path = Path(os.path.expanduser("~/.config/suru/settings.toml") if global_setting else "suru.toml")
    config_dir = config_path.parent

    # Ensure the config directory exists for global settings
    if global_setting:
        config_dir.mkdir(parents=True, exist_ok=True)

    # Write the API key to the configuration file
    with open(config_path, "w") as configfile:
        configfile.write(f'OPENAI_API_KEY="{api_key}"\n')
    console.print(f"[bold green]API key saved to {config_path}[/bold green]")


def load_api_key(global_setting=True):
    # Attempt to get the API key from the environment variable first
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key

    # Determine the path to load the API key
    config_path = Path(os.path.expanduser("~/.config/suru/settings.toml") if global_setting else "settings.toml")

    if not config_path.exists():
        return None

    # Read the API key from the configuration file
    with open(config_path, "r") as configfile:
        for line in configfile:
            if line.startswith("OPENAI_API_KEY"):
                return line.split("=", 1)[1].strip().strip('"')

    return None


if __name__ == "__main__":
    main()
