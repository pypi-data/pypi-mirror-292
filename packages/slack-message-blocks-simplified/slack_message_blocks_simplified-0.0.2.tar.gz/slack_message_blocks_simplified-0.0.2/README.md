
# Slack Message Blocks Simplified Package

## Overview

This package provides a set of classes and functions for creating and managing Slack message blocks programmatically. It includes various block types such as headers, sections, images, dividers, and context blocks, which can be used to construct complex Slack messages. The package also provides utility functions for validating key-value pairs to ensure that all necessary data is present for constructing these blocks.

## Installation

### Prerequisites

- **Python Version**: Ensure you are using Python 3.7 or higher.
- **Dependencies**:
  - `dataclasses` (built-in for Python 3.7+)
  - `typing` (for type hinting)
  - `python-dotenv` (for environment variable management)

### Setup

1. **Install Dependencies**: 
   - Install the required Python packages using `pip`:
     \`\`\`bash
     pip install python-dotenv
     \`\`\`

2. **Slack Client**:
   - The package assumes the existence of a `SlackClient` class in a module named `slack_client`. This class should handle the interaction with Slack's API. Ensure you have implemented or imported this class.

3. **Environment Setup**:
   - If you're using environment variables for Slack credentials or other settings, create a `.env` file in the root of your project:
     ```
     SLACK_API_TOKEN=xoxb-your-slack-token
     ```

## Usage

### Importing the Package

\`\`\`python
from your_package_name import BaseBlock, DividerBlock, HeaderBlock, ContextBlock, SectionBlock, ImageBlock, RichTextBlock, SlackBlock, check_type_keys
\`\`\`

### Creating a Simple Message Block

Here’s an example of how to create and send a simple message block using this package:

\`\`\`python
from slack_client import SlackClient
from your_package_name import SlackBlock, HeaderBlock, DividerBlock, SectionBlock

# Initialize the Slack client
client = SlackClient(api_token="xoxb-your-slack-token")

# Create a header block
header = HeaderBlock(title="Welcome to the Channel!")

# Create a section block
section = SectionBlock()
section.change_value(type="plain_text", text="We're glad you're here!")

# Create a divider block
divider = DividerBlock()

# Create the Slack block and add the blocks
slack_message = SlackBlock(client=client)
slack_message.add_blocks([header, section, divider])

# Post the message to a channel
slack_message.post_message_block(channel_id="C1234567890")
\`\`\`

### Using `check_type_keys` for Validation

The `check_type_keys` function is used to validate that all necessary keys are present in your input data:

\`\`\`python
from your_package_name import check_type_keys

required_keys = {
    "image": ["image_url", "alt_text"],
    "plain_text": ["text"]
}

received_values = {
    "type": "image",
    "image_url": "https://example.com/image.png"
}

check_type_keys("type", required_keys, received_values)
\`\`\`

## Available Classes and Functions

### Classes

- **BaseBlock**: Abstract base class for all Slack blocks.
- **DividerBlock**: Represents a Slack divider block.
- **HeaderBlock**: Represents a header block in a Slack message.
- **ContextBlock**: Represents a context block in a Slack message.
- **SectionBlock**: Represents a section block in a Slack message.
- **ImageBlock**: Represents an image block in a Slack message.
- **RichTextBlock**: Represents a rich text block in a Slack message.
- **SlackBlock**: Represents a complete message block to be sent via Slack.

### Functions

- **check_type_keys**: Validates that necessary keys are present in the input data based on a base key's value.

## Contributing

If you'd like to contribute to this project, please fork the repository and submit a pull request. All contributions are welcome!

## License

This project is licensed under the MIT License.
