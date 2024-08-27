from loguru import logger
import click

# Configure the logger to write to a file
logger.add("text.txt", format="{time} {level} {message}", level="INFO")

@click.command(
    short_help="making a tile-based classification on a sentinel-2 L1C data ",
    help="A selected model with the highest evaluation metrics will make an inference on a sentinel-2 L1C data",
)
@click.option(
    "--input_name",
    "input_name",
    help="A string which takes the name of a person",
    type=str,
    required=False,
)
@click.pass_context
def hello(ctx, **params):
    if params['input_name']:
        logger.info(f"Hello {params['input_name']}")
    else:
        logger.info("Hello World!")

def main():
    hello()

if __name__ == "__main__":
    main()
