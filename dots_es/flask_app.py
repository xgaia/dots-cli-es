import argparse
import os

from dots_es.api import create_app


#################################################################
# Parse CLI argument --config (path to the YAML config file) #
#################################################################

parser = argparse.ArgumentParser(
    description='ES app for DoTS'
)
parser.add_argument(
    '--config',
    type=str,
    required=True,
    help='path to the YAML configuration file',
    metavar=''
)
args = parser.parse_args()

###############################################
# Launching app with the selected environment #
###############################################

flask_app = create_app(config_path=args.config)


def log_startup_config():
    """
    Name the configuration and the indices served. A wrong --config answers
    normally, with another corpus: the mistake is otherwise invisible.
    """
    print(
        f"dots-api configuration : {args.config}\n"
        f"  Elasticsearch : {flask_app.config.get('ELASTICSEARCH_URL')}\n"
        f"  documents     : {flask_app.config.get('DOCUMENT_INDEX')}\n"
        f"  collections   : {flask_app.config.get('COLLECTION_INDEX')}",
        flush=True
    )


# Under the development server the module is imported twice; only the reloaded
# process serves.
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    log_startup_config()


def main():
    """Run the Flask development server."""
    flask_app.run(debug=True, port=5003, host='localhost')


if __name__ == "__main__":
    main()
