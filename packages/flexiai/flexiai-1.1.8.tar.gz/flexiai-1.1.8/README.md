# FlexiAI

[![CI](https://github.com/SavinRazvan/flexiai/actions/workflows/workflow.yml/badge.svg)](https://github.com/SavinRazvan/flexiai/actions/workflows/workflow.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-000000.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/flexiai.svg)](https://pypi.org/project/flexiai/)
[![PyPI version](https://badge.fury.io/py/flexiai.svg?v=1.1.8)](https://badge.fury.io/py/flexiai)
[![Downloads](https://static.pepy.tech/badge/flexiai)](https://pepy.tech/project/flexiai)

FlexiAI is a dynamic and modular AI framework designed to leverage the power of Multi-Agent Systems and Retrieval Augmented Generation (RAG). This framework is ideal for developers seeking to integrate AI capabilities into their applications with ease and flexibility. With FlexiAI, you can harness the power of both OpenAI and Azure OpenAI services to create intelligent agents that can manage tasks, process data, and provide advanced AI-driven solutions.

## Introduction Video

Learn more about FlexiAI by watching the following introductory video:

[![Watch the video](https://img.youtube.com/vi/KveLqPBLhUE/0.jpg)](https://www.youtube.com/watch?v=XHkXnQcblPM)

## Table of Contents

- [Features](#features)
- [Installation](https://github.com/SavinRazvan/flexiai/blob/main/docs/setup.md#table-of-contents)
- [Documentation](#documentation)
- [Quick Start Examples](#quick-start-examples)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Flexible AI Management**: Central hub for managing AI operations including:
  - **Thread Management**: Handle and organize multiple threads of conversation.
  - **Message Management**: Manage messages within threads.
  - **Run Management**: Create and monitor runs for processing tasks.
  - **Session Management**: Maintain user sessions for continuity.
  - **Vector Store Management**: Manage vector stores, including local and external stores, for embedding and retrieval tasks.
  - **Image Generation**: Create and manipulate images using AI models.
  - **Audio Management**: Advanced audio handling including:
    - Speech-to-Text
    - Text-to-Speech
    - Audio Transcription
    - Audio Translation
  - **Embedding Management**: Handle text embeddings for various NLP tasks.
  - **Multi-Agent System**: Manage multiple AI agents concurrently to handle various tasks efficiently.
  - **Completions Management**: Interact with the OpenAI API to handle chat completions, structured completions, and function-calling completions.
  - **Assistant Management**: Manage AI assistants, including creating, updating, retrieving, and integrating them into threads using the OpenAI Assistants API.
  
- **Retrieval Augmented Generation (RAG)**: Enhance the AI's capabilities by integrating retrieval mechanisms to provide enriched and contextually relevant responses.
  - **Comprehensive Task Management**: Organize, execute, and manage a variety of tasks with the integrated `TaskManager`, enabling AI assistants to take actions and retrieve real-time data from your personal computer or cloud services.
- **Flexible Credential Management**: Seamlessly switch between OpenAI and Azure OpenAI credentials.
- **Extensible Architecture**: Easily extend and customize the framework with user-defined functions and tasks.
- **Robust Logging**: Comprehensive logging for effective debugging and monitoring.
- **Secure and Scalable**: Suitable for both small projects and large enterprise applications.
- **Actively Maintained**: Continuously improved and supported by the project's developer.
- **Parallel Execution**: Execute tasks and tool calls in parallel for improved performance.

## Installation

For setting up starter files and detailed installation instructions, please refer to the [Installation](docs/setup.md#table-of-contents).

## Documentation

The FlexiAI framework comes with comprehensive documentation to help you get started and make the most out of its capabilities:

- [Setup Guide](docs/setup.md)
- [Project Mapping](docs/project_mapping.md)
- [API Reference](docs/api_reference.md)
- [Usage Guide](docs/usage.md)
- [Contributing Guide](docs/contributing.md)

## Quick Start Examples

FlexiAI provides ready-to-use applications to help you quickly get started with integrating AI into your projects. These examples are designed to be flexible and modifiable, so you can adapt them to your specific needs:

- **FlexiAI Flask Application**: A web-based application built using Flask that demonstrates how to integrate the FlexiAI framework with a web server. This application includes endpoints for managing threads, messages, sessions, and more. It offers a great foundation for developers looking to build and customize AI-driven web applications quickly.

- **CLI Chat Application**: A command-line interface (CLI) based chat application that leverages FlexiAI to facilitate simple text-based interactions with AI agents. This example showcases how to set up a lightweight and efficient chat system using the FlexiAI framework.

These starter applications are designed to be easily extended and customized. Whether you're building a complex web application or a simple chatbot, these examples provide a solid foundation to help you jumpstart your AI-powered project.

## Contributing

We welcome contributions from the community. If you want to contribute to FlexiAI, please read our [Contributing Guide](docs/contributing.md) to get started.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.txt) file for details.

## Contact

For any inquiries or support, please contact Savin Ionut Razvan at [razvan.i.savin@gmail.com](mailto:razvan.i.savin@gmail.com).
