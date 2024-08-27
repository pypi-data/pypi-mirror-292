import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Type, TypeVar

import yaml
from mashumaro import DataClassDictMixin
from mashumaro.mixins.json import DataClassJSONMixin

T = TypeVar('T', bound='JSONFileMixin')


class DataFileType(Enum):
    AUTO = 'AUTO'
    """Use file type based on file extension."""
    JSON = 'JSON'
    YAML = 'YAML'

    @classmethod
    def from_file(cls, file: str | Path) -> 'DataFileType':
        file_path = Path(file)
        if file_path.suffix.lower() == '.json':
            file_type = DataFileType.JSON
        elif file_path.suffix.lower() in ['.yaml', '.yml']:
            file_type = DataFileType.YAML
        else:
            raise ValueError(f'Unsupported file type: {file}')

        return file_type


class JSONFileMixin(DataClassJSONMixin):
    """
    Adds the ability to load from file and save to file.
    Files can be JSON or YAML.
    """

    def to_file(
        self,
        file: str | Path,
        file_type: DataFileType = DataFileType.AUTO,
        **from_dict_kwargs: Any,
    ):
        file_path = Path(file)
        if file_type is DataFileType.AUTO:
            file_type = DataFileType.from_file(file_path)
        data = self.to_dict(**from_dict_kwargs)

        with open(file_path, 'w') as f:
            if file_type is DataFileType.JSON:
                json.dump(data, f, indent=2)
            else:
                yaml.safe_dump(data, f, default_flow_style=False, indent=2)

    @classmethod
    def from_file(
        cls: Type[T],
        file: str | Path,
        file_type: DataFileType = DataFileType.AUTO,
        **from_dict_kwargs: Any,
    ) -> T:
        file_path = Path(file)
        if file_type is DataFileType.AUTO:
            file_type = DataFileType.from_file(file_path)

        with open(file_path) as f:
            if file_type is DataFileType.JSON:
                data = json.load(f)
            else:
                data = yaml.safe_load(f)
        return cls.from_dict(data, **from_dict_kwargs)


class DefaultsMixin(DataClassDictMixin):
    """
    Add factory-like functionality.
    """

    def create(self, new_instance: DataClassDictMixin):
        """
        Create a new instance with this instance's values as defaults.

        Note that boolean fields are never updated.
        """
        defaults = self.to_dict()
        new_values = {k: v for k, v in new_instance.to_dict().items() if v or isinstance(v, bool)}

        return self.__class__.from_dict(defaults | new_values)


@dataclass
class Inputs(JSONFileMixin, DefaultsMixin):
    """
    Inputs to the app.
    """

    dialog_title: str = ''
    """Title of the window."""
    title: str = ''
    description: str = ''
    """
    Text to display in the description section.

    Can be plain text or HTML. For markdown, set ``description_md`` to ``True``.
    """
    description_md: bool = False
    """
    Whether the text in the ``description`` field is markdown.

    Text in ``description`` can be plain text or HTML.
    """
    timeout: int = 0
    """
    Timeout in seconds for the dialog to be automatically dismissed.

    ``0`` for no timeout.
    """
    timeout_pass: bool = False
    """
    Result at the end of timeout: Pass (``True``) or fail (``False``).
    """
    timeout_text: str = '%v'
    """
    Text format for timeout.

    * ``%p`` is replaced by the percentage completed.
    * ``%v`` is replaced by the current value.
    * ``%m`` is replaced by the total number of steps.

    Blank string to not show text.

    Examples:

    * ``'%p%'`` to show percentage completed, ex '15%'
    * ``'%vs'`` to show the number of seconds elapsed, ex '15s'
    """
    pass_button_text: str = ''
    pass_button_icon: str = ''
    """
    Set the icon for the _Pass_ button.

    Can be a resource path, relative path or absolute path. See examples under ``assets/inputs``.
    """
    fail_button_text: str = ''
    fail_button_icon: str = ''
    """
    Set the icon for the _Fail_ button.

    Can be a resource path, relative path or absolute path. See examples under ``assets/inputs``.
    """
