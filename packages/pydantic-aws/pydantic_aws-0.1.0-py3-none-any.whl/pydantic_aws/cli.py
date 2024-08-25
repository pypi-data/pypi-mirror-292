"""Console script for pydantic_aws."""
import pydantic_aws

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for pydantic_aws."""
    console.print("Replace this message by putting your code into "
               "pydantic_aws.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    


if __name__ == "__main__":
    app()
