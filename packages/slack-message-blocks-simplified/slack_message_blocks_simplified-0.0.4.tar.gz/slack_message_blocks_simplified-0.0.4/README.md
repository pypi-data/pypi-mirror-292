
# Slack Message Blocks Simplified Package

## Overview

**slack_message_blocks_simplified** is a Python package that simplifies the process of creating and sending rich, structured messages to Slack channels using blocks. The package provides various classes to help you build and manage these blocks and interact with Slack's API efficiently.

## Installation
```
pip install slack-message-blocks-simplified
```

### Prerequisites

- **Python Version**: Ensure you are using Python 3.12 or higher.
- **Dependencies**:
  - `slack_sdk` (version 3.31.0)
  - `dataclasses` (built-in for Python 3.7+)
  - `typing` (for type hinting)


## Usage

### Importing the Package

```
from slack_message_blocks_simplified import  DividerBlock, HeaderBlock, ContextBlock, SectionBlock, ImageBlock, RichTextBlock, SlackBlock, SlackClient
```

# Initialize the Slack client and Slack Block
```
slack_client = SlackClient(bot_token="xoxb-your-slack-token")
slack_message = SlackBlock(client=slack_client)
```

# Create a message
```
header = HeaderBlock(title="Welcome to the Channel!")
divider = DividerBlock()
section = SectionBlock()
section.change_value(type="mrkdwn", text="This is a *section* with some _rich text_.")
section.add_image(image_url="https://example.com/image.png", alt_text="Example Image")
```

# Upload file
```
slack_message.upload_file("C:/path/to/file.extension", "file.extension")
```

# Post the message to a channel
```
slack_message.add_blocks([header, divider, section])
slack_message.post_message_block(channel_id="C1234567890")
```

# Final code
```
from slack_message_blocks_simplified import DividerBlock, HeaderBlock, ContextBlock, SectionBlock, ImageBlock, RichTextBlock, SlackBlock, SlackClient

slack_client = SlackClient(bot_token="xoxb-your-slack-token")
slack_message = SlackBlock(client=slack_client)

header = HeaderBlock(title="Welcome to the Channel!")
divider = DividerBlock()
section = SectionBlock()
section.change_value(type="mrkdwn", text="This is a *section* with some _rich text_.")
section.add_image(image_url="https://example.com/image.png", alt_text="Example Image")

slack_message.upload_file("C:/path/to/file.extension", "file.extension")

slack_message.add_blocks([header, divider, section])
slack_message.post_message_block(channel_id="C1234567890")
```


# Classes and Methods

## 1. SlackClient
A client for interacting with Slack's API.

### Attributes:

- `bot_token`: The token used for authenticating the bot with Slack's API. To get this token you must have a [Slack app](https://api.slack.com/docs/apps) created and it requires the following OAuth Scopes: 
`chat:write`, `files:write`

### Methods:

- `post_message_block(channel_id: str, blocks: Any | None, text: str = "")`:

  **Description**: Posts a message with optional blocks to a specific Slack channel.  
  **Required Keys**:  
  - `channel_id`: The ID of the Slack channel where the message will be posted.  
  - `blocks`: A list of blocks (formatted sections) to include in the message. Can be `None`.  
  - `text`: The plain text content of the message.

- `upload(file: str | bytes | IOBase | None, filename: str | None)`:

  **Description**: Uploads a file to Slack, optionally with a specified filename.  
  **Required Keys**:  
  - `file`: The file to upload. It can be a path to a file, bytes, or an IO stream.  
  - `filename`: The name to use for the file in Slack. If `None`, Slack determines the name automatically.

## 2. SlackBlock
Represents a message block to be sent via Slack.

### Attributes:

- `client`: An instance of `SlackClient`.
- `text`: Text content of the message.
- `blocks`: List of blocks to be included in the message.
- `files`: List of file URLs to be attached to the message.

### Methods:

- `add_blocks(blocks: list[BaseBlock])`:

  **Description**: Adds multiple blocks to the Slack message.  
  **Required Keys**:  
  - `blocks`: A list of `BaseBlock` objects (e.g., `HeaderBlock`, `SectionBlock`) to be added to the message.

- `upload_file(file_path: str, filename: str | None = None)`:

  **Description**: Uploads a file to Slack and stores its URL.  
  **Required Keys**:  
  - `file_path`: Path to the file that will be uploaded.  
  - `filename`: Optional. The name to use for the file in Slack. If `None`, Slack determines the name automatically.

- `add_message(new_text: str)`:

  **Description**: Appends additional text to the existing message.  
  **Required Keys**:  
  - `new_text`: The text to append to the current message.

- `change_message(new_text: str)`:

  **Description**: Replaces the existing message with new text.  
  **Required Keys**:  
  - `new_text`: The new text that will replace the current message content.

- `reset_message()`:

  **Description**: Resets the message text to an empty string.  
  **Required Keys**: None

- `post_message_block(channel_id: str)`:

  **Description**: Posts the message block to a specified Slack channel.  
  **Required Keys**:  
  - `channel_id`: The ID of the Slack channel where the message will be posted.

## 3. HeaderBlock
Represents a Slack header block.

### Attributes:

- `title`: Title of the header.

### Methods:

- `reset_value()`:

  **Description**: Resets the title of the header block.  
  **Required Keys**: None

- `change_value(*args: list[Any], **kwargs: dict[str, Any])`:

  **Description**: Changes the title of the header block.  
  **Required Keys**:  
  - `title`: The new title for the header block.

- `append(*args: list[Any], **kwargs: dict[str, Any])`:

  **Description**: Appends text to the existing title.  
  **Required Keys**:  
  - `title`: The text to append to the existing title.

- `value() -> dict[str, Any]`:

  **Description**: Retrieves the value of the header block.  
  **Required Keys**: None (Returns a dictionary with the header type and title)

## 4. DividerBlock
Represents a Slack divider block.

### Methods:

- `value() -> dict[str, Any]`:

  **Description**: Retrieves the value of the divider block.  
  **Required Keys**: None (Returns a dictionary with the divider type)

## 5. SectionBlock
Represents a Slack section block.

### Attributes:

- `element`: Dictionary containing the section content.

### Methods:

- `reset_value()`:

  **Description**: Resets the section block to its default state.  
  **Required Keys**: None

- `change_value(*args: list[Any], **kwargs: dict[str, Any])`:

  **Description**: Changes the content of the section block.  
  **Required Keys**:  
  - `type`: The type of the section block content (e.g., `plain_text`, `mrkdwn`).  
  - `text`: The text content of the section block.

- `add_image(*args: list[Any], **kwargs: dict[str, Any])`:

  **Description**: Adds an image to the section block.  
  **Required Keys**:  
  - `image_url`: The URL of the image to be added.  
  - `alt_text`: The alternative text for the image.

- `value() -> dict[str, Any]`:

  **Description**: Retrieves the value of the section block.  
  **Required Keys**: None (Returns a dictionary with section type and content)

## 6. ImageBlock
Represents a Slack image block.

### Attributes:

- `image_url`: URL of the image.
- `title`: Optional. Title of the image block.
- `alt_text`: Alternative text for the image.
- `is_markdown`: Indicates if the title is in Markdown format.

### Methods:

- `reset_value()`:

  **Description**: Resets the image block to its default state.  
  **Required Keys**: None

- `change_value(*args: list[Any], **kwargs: dict[str, Any])`:

  **Description**: Changes the properties of the image block.  
  **Required Keys**:  
  - `image_url`: The new URL of the image.  
  - `title`: The new title for the image block.  
  - `alt_text`: The new alternative text for the image.  
  - `is_markdown`: Boolean indicating if the title should be in Markdown format.

- `value() -> dict[str, Any]`:

  **Description**: Retrieves the value of the image block.  
  **Required Keys**: None (Returns a dictionary with image block details)

## 7. ContextBlock
Represents a Slack context block.

### Attributes:

- `elements`: List of elements within the context block.

### Methods:

- `reset_value()`:

  **Description**: Resets the elements of the context block.  
  **Required Keys**: None

- `append(*args: list[Any], **kwargs: dict[str, Any])`:

  **Description**: Appends an element to the context block.  
  **Required Keys**:  
  - `type`: The type of the element (e.g., `image`, `plain_text`, `mrkdwn`).  
    - For `image` type:  
      - `image_url`: The URL of the image.  
      - `alt_text`: The alternative text for the image.  
    - For `plain_text` and `mrkdwn` types:  
      - `text`: The text content of the element.

- `value() -> dict[str, Any]`:

  **Description**: Retrieves the value of the context block.  
  **Required Keys**: None (Returns a dictionary with context type and elements)

## 8. RichTextBlock
Represents a Slack rich text block.

### Attributes:

- `sections`: List of rich text sections.

### Methods:

- `reset_value()`:

  **Description**: Resets the sections of the rich text block.  
  **Required Keys**: None

- `add_section(text_list: list[dict[str, Any]])`:

  **Description**: Adds a new section to the rich text block.  
  **Required Keys**:  
  - `text_list`: A list of dictionaries, each representing a text element with keys like `type`, `text`, `bold`, `italic`, `strike`, etc.

- `add_list(list_style: str, text_list: list[list[dict[str, Any]]])`:

  **Description**: Adds a list to the rich text block.  
  **Required Keys**:  
  - `list_style`: The style of the list (e.g., `bullet`, `ordered`).  
  - `text_list`: A list of lists, where each inner list represents items in the list with text elements.

- `value() -> dict[str, Any]`:

  **Description**: Retrieves the value of the rich text block.  
  **Required Keys**: None (Returns a dictionary with rich text block details)


If you'd like to contribute to this project, please fork the repository and submit a pull request. All contributions are welcome!

## License

This project is licensed under the MIT License.
