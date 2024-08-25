# FlaskForge

**FlaskForge** is a versatile CLI tool designed to streamline the development of Flask applications by automating the creation and management of essential resources. Inspired by Laravel's Artisan CLI, FlaskForge simplifies the setup and generation of various components in your Flask projects, allowing you to focus on building your application.

## Features

-   **Initialize a Flask Project**: Set up a new Flask project with customizable options using the `initapp` command. This command helps you quickly scaffold a new application with features like:

    -   **Project Name**: Specify the name for your new Flask project.
    -   **JWT Authentication**: Enable or disable JSON Web Token (JWT) authentication (default: enabled).
    -   **Swagger Documentation**: Enable or disable Swagger OpenAPI documentation (default: enabled).
    -   **Force Creation**: Overwrite existing files if a project with the same name already exists.

-   **Generate API Resources**: Use the `create` command to scaffold various API components, including models and their associated endpoints:

    -   **Model Creation**: Define the name of the model to generate a new model class.
    -   **Getter/Setter Methods**: Optionally include getter and setter methods for private properties.
    -   **Endpoint Methods**: Specify which HTTP methods (e.g., 'GET,POST') to include or exclude for your model's endpoints.
    -   **Model Only**: Generate only the model class without additional endpoints.
    -   **Search and Single Methods**: Configure the model to use search methods instead of the default `get_all`.

-   **Authentication Resources**: The `create:authentication` command generates authentication-related resources for a specified model:

    -   **Username Field**: Define the field in the model for storing usernames.
    -   **Password Field**: Define the field in the model for storing passwords.

-   **Resource Management**: The `create:resource` command sets up resource-related components for a specified model, including:
    -   **Resource Name**: Specify the name of the resource.
    -   **Endpoint Methods**: Define which HTTP methods to include or exclude.
    -   **URL Prefix**: Set a URL prefix for grouping related routes.
    -   **Search and Single Methods**: Configure methods for querying resources.
    -   **Query Parameters**: Define parameters and their types for filtering.

## Installation

To install FlaskForge, use pip:

```bash
pip install flaskforge
```

## Usage

Here are the commands available with FlaskForge:

### Initialize a New Project:

```bash
flaskforge initapp <project_name> [--jwt-enable] [--swagger-enable] [--force]
```

### Generate API Resources:

```bash
flaskforge create <model_name> [--getter-setter] [--endpoints <methods>] [--exclude-endpoints <methods>] [--model-only] [--use-search] [--use-single] [--param <param>] [--type <type>] [--force]
```

### Create Authentication Resource

```bash
flaskforge create:authentication <model_name> --username-field <field_name> --password-field <field_name>
```

### Create Resource Components:

```bash
flaskforge create:resource <model_name> --name <resource_name> [--endpoints <methods>] [--exclude-endpoints <methods>] [--url-prefix <prefix>] [--use-search] [--use-single] [--param <param>] [--type <type>]

```

## Contributing

We welcome contributions to FlaskForge! If you have suggestions, improvements, or bug reports, please submit an issue or a pull request on our GitHub repository.

## License

FlaskForge is licensed under the MIT License.
