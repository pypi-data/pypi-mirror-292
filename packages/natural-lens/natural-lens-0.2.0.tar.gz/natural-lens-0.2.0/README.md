# Natural Lens

Unlock the power of your database schema with **Natural Lens**! This innovative command-line interface (CLI) tool allows you to interactively explore your database schemas, generating insightful profiles and facilitating intelligent queries. Say goodbye to tedious data analysis and hello to a seamless dialogue with your database!

<img src="./logo.png" alt="Natural Lens Logo" width="200" height="200">

## Features

- **Effortlessly Download Schemas**: Quickly connect to your PostgreSQL or Trino database and fetch the schema with a single command.
- **Instant Sample Data**: Automatically retrieve and save sample data for each table, ready for in-depth analysis.
- **AI-Powered Table Profiles**: Generate detailed profiles for each table, revealing their structure, purpose, and significant insights.
- **Interactive Query Interface**: Engage in a conversational manner with your database schema, asking questions and receiving AI-generated responses based on the profiles.
- **User-Friendly CLI**: Enjoy a seamless command-line experience designed for both beginners and experts, making database exploration intuitive and efficient.
- **Future Database Support**: We plan to support additional databases in the future, expanding the capabilities of **Natural Lens**.

## Current Database Support

- **PostgreSQL**
- **Trino** (currently supports OAuth only)

## Requirements

- Python 3.6 or higher
- OpenAI API key

## Installation

1. Install the package using pip:
   ```bash
   pip install natural-lens
   ```
2. Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY='your_openai_api_key'  # On Windows use: set OPENAI_API_KEY='your_openai_api_key'
   ```

## Usage

The CLI will be available as `nlens`. Run the following command to see the available options:

```bash
nlens --help
```

Refer to the [Northwind Example](./examples/northwind/README.md) to test **Natural Lens** with a sample PostgreSQL or Trino database.

## Troubleshooting

- **Error: Connection failed**: Ensure that your database credentials are correct and that the database server is running.
- **Error: OpenAI API key not set**: Make sure you have set your OpenAI API key as an environment variable.

## Contributing

We love contributions! Whether you have a bug fix, a new feature, or just a suggestion, your input is invaluable. Join our community and help us make **Natural Lens** even better!

1. Fork the repository.
2. Create a new branch.
3. Make your changes and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. The MIT License allows for reuse within proprietary software, as long as the license is distributed with that software.

## Acknowledgments

- [OpenAI](https://openai.com/) for providing the AI capabilities.

## Get Started Today!

Ready to unlock the potential of your database? Clone the repository, set up your environment, and start exploring the world of intelligent data analysis with **Natural Lens**!
