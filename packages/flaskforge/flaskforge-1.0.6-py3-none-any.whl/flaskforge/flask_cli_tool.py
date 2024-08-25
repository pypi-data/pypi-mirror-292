#!/usr/bin/env python

from flaskforge.flask_cli import FlaskCli


def main():
    """
    Main function to initialize and configure the Flask CLI tool.

    TODO:
    - Add support for configuring environment variables during project initialization.
    - Implement a command to generate or update configuration files for various environments.
    - Create commands for adding and managing database migrations.
    - Provide detailed documentation for each command and argument.
    - Add validation for argument inputs to ensure correct usage.

    """
    # Create an instance of the FlaskCli
    flask_cli = FlaskCli()

    # Define the "initapp" command for initializing a new Flask project
    flask_cli.create_command(
        "initapp",
        "Initialize a new Flask project with optional configurations. This command sets up a basic Flask application structure with the ability to customize certain features.",
    )
    flask_cli.add_argument(
        "initapp",
        "project",
        help="The name of the new Flask project you wish to create. This will be used to name the project directory and other initial files.",
    )
    flask_cli.add_argument(
        "initapp",
        "--jwt-enable",
        help="Enable or disable JSON Web Token (JWT) authentication for the new project. Defaults to True (enabled). Set to False to disable JWT authentication.",
        type=bool,
        default=True,
    )
    flask_cli.add_argument(
        "initapp",
        "--swagger-enable",
        help="Enable or disable Swagger OpenAPI documentation for the new project. Defaults to True (enabled). Set to False to disable Swagger documentation.",
        type=bool,
        default=True,
    )
    flask_cli.add_argument(
        "initapp",
        "--use-docker",
        action="store_true",
        help="Forcefully overwrite existing project files if they already exist. Use this option to create the project even if it conflicts with existing files or directories.",
    )

    flask_cli.add_argument(
        "initapp",
        "--force",
        action="store_true",
        help="Forcefully overwrite existing project files if they already exist. Use this option to create the project even if it conflicts with existing files or directories.",
    )

    # Define the "create" command for generating API resources
    flask_cli.create_command(
        "create",
        "Generate API resources, including models and their associated endpoints. This command helps you quickly scaffold out the essential components for your API.",
    )
    flask_cli.add_argument(
        "create",
        "model",
        help="The name of the model to be generated. This will create a model class and optionally generate associated endpoints based on your specifications.",
    )
    flask_cli.add_argument(
        "create",
        "--getter-setter",
        help="Automatically generate getter and setter methods for private properties in the model class. Use this flag to include these methods in the generated model.",
        action="store_true",
    )
    flask_cli.add_argument(
        "create",
        "--endpoints",
        help="Specify a list of HTTP methods (e.g., 'GET,POST') for which endpoints should be generated for the model. Provide comma-separated values for multiple methods.",
        type=str,  # Use type=str to handle comma-separated values
        nargs="+",  # Optional argument
    )
    flask_cli.add_argument(
        "create",
        "--exclude-endpoints",
        help="Specify a list of HTTP methods (e.g., 'DELETE') to exclude from the generated endpoints for the model. Provide comma-separated values for multiple methods.",
        type=str,  # Use type=str to handle comma-separated values
        nargs="+",  # Optional argument
    )
    flask_cli.add_argument(
        "create",
        "--model-only",
        help="Generate only the model class without creating additional resources such as endpoints. Use this flag to limit the generation to the model only.",
        action="store_true",
        default=False,
    )
    flask_cli.add_argument(
        "create",
        "--use-search",
        action="store_true",
        help="Use a search method instead of the default get_all method for querying records.",
    )

    flask_cli.add_argument(
        "create",
        "--use-docker",
        action="store_true",
        help="Use a search method instead of the default get_all method for querying records.",
    )

    flask_cli.add_argument(
        "create",
        "--use-single",
        action="store_true",
        help="Use a search method instead of the default get_all method for querying a single record.",
    )

    flask_cli.add_argument(
        "create",
        "--param",
        help="Specify the name of the query string parameter used for filtering results.",
    )

    flask_cli.add_argument(
        "create",
        "--type",
        help="Specify the type of the query string parameter (e.g., 'int', 'string').",
    )
    flask_cli.add_argument(
        "create",
        "--force",
        action="store_true",
        help="Overwrite existing model files if they already exist. Use this option to regenerate model files, replacing any existing files.",
    )

    # Define the "create:authentication" command for setting up authentication resources
    flask_cli.create_command(
        "create:authentication",
        "Generate authentication-related resources for a specified model. This command sets up the necessary components to support authentication features for the given model.",
    )
    flask_cli.add_argument(
        "create:authentication",
        "model",
        help="The name of the model to be used for authentication. This model will be configured to handle authentication-related operations.",
    )
    flask_cli.add_argument(
        "create:authentication",
        "--username-field",
        required=True,
        help="Specify the name of the field in the model that will be used to store the username for authentication purposes.",
    )
    flask_cli.add_argument(
        "create:authentication",
        "--password-field",
        required=True,
        help="Specify the name of the field in the model that will be used to store the password for authentication purposes.",
    )

    # Define the "create:resource" command for generating resource-related resources
    flask_cli.create_command(
        "create:resource",
        "Generate resource-related components for a specified model. This includes setting up routes and endpoints for managing resources related to the model.",
    )
    flask_cli.add_argument(
        "create:resource",
        "model",
        help="The name of the model for which resource-related components should be generated. This will set up the necessary infrastructure for managing resources of the specified model.",
    )
    flask_cli.add_argument(
        "create:resource",
        "--name",
        help="Specify the name of the resource to be created. This name will be used for the resource and its associated components.",
        required=True,
    )
    flask_cli.add_argument(
        "create:resource",
        "--endpoints",
        help="Specify a list of HTTP methods (e.g., 'GET,POST') for which endpoints should be generated for the resource. Provide comma-separated values for multiple methods.",
        type=str,
        nargs="+",
    )
    flask_cli.add_argument(
        "create:resource",
        "--exclude-endpoints",
        help="Specify a list of HTTP methods (e.g., 'DELETE') to exclude from the generated endpoints for the resource. Provide comma-separated values for multiple methods.",
        type=str,
        nargs="+",
    )
    flask_cli.add_argument(
        "create:resource",
        "--url-prefix",
        help="Specify the URL prefix for the resource routes. This is useful for grouping related routes under a common prefix.",
    )
    flask_cli.add_argument(
        "create:resource",
        "--use-search",
        action="store_true",
        help="Use a search method instead of the default get_all method for querying resources.",
    )
    flask_cli.add_argument(
        "create:resource",
        "--use-single",
        action="store_true",
        help="Use a search method instead of the default get_all method for querying a single resource.",
    )
    flask_cli.add_argument(
        "create:resource",
        "--param",
        help="Specify the name of the query string parameter used for filtering resources.",
    )
    flask_cli.add_argument(
        "create:resource",
        "--type",
        help="Specify the type of the query string parameter (e.g., 'int', 'string').",
    )

    # Parse arguments and execute the appropriate command
    flask_cli.init()


if __name__ == "__main__":
    main()
