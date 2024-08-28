from dataclasses import dataclass, field
from typing import Any

from slack_client import SlackClient

def _check_type_keys(base_key: str, type_key_values: dict[str, list[str]], received_values: dict[str, Any]):
    """
    Checks for necessary keys in a dictionary based on a base key's value.

    Args:
    - base_key (str): The key in `received_values` whose value determines the required keys.
    - type_key_values (dict[str, list[str]]): A dictionary where keys correspond to possible values of `base_key`, 
      and values are lists of keys that are required when `base_key` has that specific value.
    - received_values (dict[str, Any]): The dictionary of received values to be checked.

    Raises:
    - KeyError: If the `base_key` is missing from `received_values` or if any of the necessary keys specified in 
      `type_key_values` are missing from `received_values`.

    Notes:
    - The function first checks if `base_key` is present in `received_values`.
    - If present, it checks if all required keys are also present, based on the value of `base_key`.
    - If `base_key` is missing or any necessary keys are missing, a `KeyError` is raised with a descriptive message.
    """
    if base_key in received_values.keys():
        for necessary_key in type_key_values[received_values[base_key]]:
            if necessary_key not in received_values.keys():
                raise KeyError(f'if {base_key} has a value of {received_values[base_key]} the following keys are required: {", ".join(type_key_values[received_values[base_key]])}')
    else:
        raise KeyError(f'A value is required for the "{base_key}" key. Possible values: {", ".join(type_key_values.keys())}')



@dataclass
class BaseBlock:
    """
    Base class for Slack blocks.

    Provides a template for different types of Slack blocks to implement.
    """

    def reset_value(self) -> None:
        """
        Resets the value of the block to its default state.

        Notes:
        - Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method")
    
    def change_value(self, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        """
        Changes the value of the block.

        Args:
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments.

        Notes:
        - Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method")

    def append(self, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        """
        Appends data to the block.

        Args:
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments.

        Notes:
        - Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method")

    def value(self) -> dict[str, Any]:
        """
        Retrieves the value of the block in dictionary form.

        Returns:
        - dict[str, Any]: Dictionary representation of the block.

        Notes:
        - Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method")
    
@dataclass
class DividerBlock(BaseBlock):
    """
    Divider block class.

    Represents a Slack divider block.
    """

    def value(self) -> dict[str, Any]:
        """
        Retrieves the value of the divider block.

        Returns:
        - dict[str, Any]: Dictionary with divider type.
        """
        return {
			"type": "divider"
		}
    
@dataclass
class HeaderBlock(BaseBlock):
    """
    Header block class.

    Represents a Slack header block.

    Attributes:
    - title (str): Title of the header.
    """
    title: str = ""

    def reset_value(self) -> None:
        """
        Resets the title of the header block.
        """
        self.title = ""

    def change_value(self, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        """
        Changes the title of the header block.

        Args:
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments, e.g., 'title' to change the title.
        """
        _check_type_keys("title", {}, kwargs)
        self.title = str(kwargs.get("title", self.title))
    
    def append(self, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        """
        Appends text to the existing title.

        Args:
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments, e.g., 'title' to append to the title.
        """
        _check_type_keys("title", {}, kwargs)
        new_data: str = str(kwargs.get("title", ""))
        self.title = f"{self.title} {new_data}"

    def value(self) -> dict[str, Any]:
        """
        Retrieves the value of the header block.

        Returns:
        - dict[str, Any]: Dictionary with header type and title.
        """
        return {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": self.title,
				"emoji": True
			}
		}

@dataclass
class ContextBlock(BaseBlock):
    """
    Context block class.

    Represents a Slack context block.

    Attributes:
    - elements (list[dict[str, Any]]): List of elements within the context block.
    """
    elements: list[dict[str, Any]] = field(default_factory=list)

    def reset_value(self) -> None:
        """
        Resets the elements of the context block.
        """
        self.elements = []

    def append(self, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        """
        Appends an element to the context block.

        Args:
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments, e.g., 'image_url', 'alt_text', 'type', 'text'.
        """
        _check_type_keys("type", {"image":["image_url", "alt_text"], "plain_text":["text"], "mrkdwn":["text"]}, kwargs)
        self.elements.append(
            {
                "type": "image",
                "image_url": str(kwargs.get("image_url", "")),
                "alt_text": str(kwargs.get("alt_text", ""))
            }
            if "image_url" in kwargs.keys() else
            {
                "type": str(kwargs.get("type", "plain_text")),
                "text": str(kwargs.get("text", "plain_text")),
                "emoji": True 
            }
        )
    
    def value(self) -> dict[str, Any]:
        """
        Retrieves the value of the context block.

        Returns:
        - dict[str, Any]: Dictionary with context type and elements.
        """
        return {
            "type": "context",
            "elements": [
                element for element in self.elements
            ]
        }

@dataclass
class SectionBlock(BaseBlock):
    """
    Section block class.

    Represents a Slack section block.

    Attributes:
    - element (dict[str, Any]): Dictionary containing the section content.
    """
    element: dict[str, Any] = field(default_factory=dict)

    def reset_value(self) -> None:
        """
        Resets the section block to its default state.
        """
        self.element = {}

    def change_value(self, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        """
        Changes the content of the section block.

        Args:
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments, e.g., 'type', 'text'.
        """
        _check_type_keys("type", {"plain_text":["text"], "mrkdwn":["text"]}, kwargs)
        self.element = {
            "type": str(kwargs.get("type", "plain_text")),
            "text": str(kwargs.get("text", "plain_text")),
        }
    
    def add_image(self, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        """
        Adds an image to the section block.

        Args:
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments, e.g., 'image_url', 'alt_text'.
        """
        _check_type_keys("type", {"image":["image_url", "alt_text"]}, kwargs)
        self.element["accessory"] = {
            "type": "image",
            "image_url": str(kwargs.get("image_url", "")),
            "alt_text": str(kwargs.get("alt_text", ""))
        }
    
    def value(self) -> dict[str, Any]:
        """
        Retrieves the value of the section block.

        Returns:
        - dict[str, Any]: Dictionary with section type and content.
        """
        return {
            "type": "section",
            "text": self.element
        }

@dataclass
class ImageBlock(BaseBlock):
    """
    Image block class.

    Represents a Slack image block.

    Attributes:
    - image_url (str): URL of the image.
    - title (str | None): Optional. Title of the image block.
    - alt_text (str): Alternative text for the image.
    - is_markdown (bool): Indicates if the title is in Markdown format.
    """
    image_url: str
    title: str | None = None
    alt_text: str = ""
    is_markdown: bool = False

    def reset_value(self) -> None:
        """
        Resets the image block to its default state.
        """
        self.title = None
        self.alt_text = ""
        self.is_markdown = False

    def change_value(self, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        """
        Changes the properties of the image block.

        Args:
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments, e.g., 'image_url', 'title', 'alt_text', 'is_markdown'.
        """
        self.image_url = str(kwargs.get("image_url", self.image_url))
        self.title = kwargs.get("title", self.title)  # type: ignore
        self.alt_text = str(kwargs.get("alt_text", self.alt_text))
        self.is_markdown = bool(kwargs.get("is_markdown", self.is_markdown))

    def value(self) -> dict[str, Any]:
        """
        Retrieves the value of the image block.

        Returns:
        - dict[str, Any]: Dictionary with image block details.
        """
        if self.title is not None:
            return {
                "type": "image",
                "title": {
                    "type": "mrkdwn" if self.is_markdown else "plain_text",
                    "text": self.title
                },
                "image_url": self.image_url,
                "alt_text": self.alt_text
            }
        else:
            return {
                "type": "image",
                "image_url": self.image_url,
                "alt_text": self.alt_text
            }

@dataclass
class RichTextBlock(BaseBlock):
    """
    Rich text block class.

    Represents a Slack rich text block.

    Attributes:
    - sections (list[dict[str, Any]]): List of rich text sections.
    """
    sections: list[dict[str, Any]] = field(default_factory=list)

    def reset_value(self) -> None:
        """
        Resets the sections of the rich text block.
        """
        self.sections = []

    def _create_section(self, text_list: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Creates a rich text section.

        Args:
        - text_list (list[dict[str, Any]]): List of text elements.

        Returns:
        - dict[str, Any]: Dictionary representing a rich text section.
        """
        for element in text_list:
            _check_type_keys("type", {"text":["text"], "emoji":["name"]}, element)
        return {
                "type": "rich_text_section",
                "elements": [
                    {
                        "type": "text",
                        "text": element.get("text", ""),
                        "style": {
                            "bold": element.get("bold", False),
                            "italic": element.get("italic", False),
                            "strike": element.get("strike", False),
                        }
                    } 
                    if "text" in element.keys() else 
                    {
                        "type": "emoji",
                        "name": element.get("name", "")
                    } 
                    for element in text_list
                ]
            }

    def add_section(self, text_list: list[dict[str, Any]]) -> None:
        """
        Adds a new section to the rich text block.

        Args:
        - text_list (list[dict[str, Any]]): List of text elements.
        """
        self.sections.append(
            self._create_section(text_list)
        )

    def add_list(self, list_style: str, text_list: list[list[dict[str, Any]]]) -> None:
        """
        Adds a list to the rich text block.

        Args:
        - list_style (str): Style of the list (e.g., 'bullet', 'ordered').
        - text_list (list[list[dict[str, Any]]]): List of text elements grouped by list items.
        """
        self.sections.append(
            {
                "type": "rich_text_list",
                "style": list_style,
                "elements": [
                    self._create_section(element) for element in text_list
                ]
            }
        )

    def value(self) -> dict[str, Any]:
        """
        Retrieves the value of the rich text block.

        Returns:
        - dict[str, Any]: Dictionary with rich text block details.
        """
        return {
            "type": "rich_text",
            "elements": [
                element for element in self.sections
            ]
        }

@dataclass
class SlackBlock:
    """
    Slack block class.

    Represents a message block to be sent via Slack.

    Attributes:
    - client (SlackClient): Slack client used to send the message.
    - text (str): Text content of the message.
    - blocks (list[dict[str, Any]]): List of blocks to be included in the message.
    - files (list[str]): List of file URLs to be attached to the message.
    """
    client: SlackClient
    text: str = ""
    blocks: list[dict[str, Any]] = field(default_factory=list)
    files: list[str] = field(default_factory=list)

    def add_blocks(self, blocks: list[BaseBlock]) -> None:
        """
        Adds multiple blocks to the Slack message.

        Args:
        - blocks (list[BaseBlock]): List of block objects to be added.
        """
        for block in blocks:
            self.blocks.append(
                block.value() 
            )

    def upload_file(self, file_path: str, filename: str | None = None) -> None:
        """
        Uploads a file to Slack and stores its URL.

        Args:
        - file_path (str): Path to the file to be uploaded.
        """
        upload = self.client.upload(file= file_path, filename= filename) # type: ignore
        self.files.append(f"<{upload['file']['permalink']}>")

    def add_message(self, new_text: str) -> None:
        """
        Appends additional text to the existing message.

        Args:
        - new_text (str): Text to be appended.
        """
        self.text = f"{self.text}{new_text}"
    
    def change_message(self, new_text: str) -> None:
        """
        Replaces the existing message with new text.

        Args:
        - new_text (str): New text for the message.
        """
        self.text = new_text

    def reset_message(self) -> None:
        """
        Resets the message text to an empty string.
        """
        self.text = ""

    def post_message_block(self, channel_id: str) -> None:
        """
        Posts the message block to a specified Slack channel.

        Args:
        - channel_id (str): ID of the Slack channel where the message will be posted.
        """
        self.client.post_message_block(
            channel_id=channel_id,
            blocks=self.blocks,
            text=f"{self.text} \n {'\n'.join(self.files)}"
        )


