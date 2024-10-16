import utils.astree_log_utils.log_monitor as LogMonitor
from utils.log import Logger
import click

@click.command()
@click.option('--output_path', prompt='Output folder path', help='Output folder path')
def main(output_path):
    logger = Logger()
    if not output_path:
        logger.error("Output path is required")
        return
    astree_log_monitor = LogMonitor.LogMonitor(output_path)
    astree_log_monitor.monitor()

if __name__ == "__main__":
    main()
