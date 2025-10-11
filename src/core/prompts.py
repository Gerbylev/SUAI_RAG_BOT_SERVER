from datetime import datetime
from functools import cache
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Template

from core.models import SourceData
from core.tools.base import BaseTool


class PromptLoader:

    @classmethod
    def _get_prompts_dir(cls) -> Path:
        return Path(__file__).parent / "prompts"

    @classmethod
    @cache
    def _load_yaml_prompts(cls) -> dict[str, Any]:
        prompts_file = cls._get_prompts_dir() / "system_prompts.yml"

        if not prompts_file.exists():
            raise FileNotFoundError(f"Prompts file not found: {prompts_file}")

        try:
            with open(prompts_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if not data:
                    raise ValueError("Prompts YAML file is empty")
                return data
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file {prompts_file}: {e}") from e
        except IOError as e:
            raise IOError(f"Error reading prompts file {prompts_file}: {e}") from e

    @classmethod
    def _prepare_tools_data(cls, available_tools: list[BaseTool]) -> list[dict[str, str]]:
        return [{"name": tool.tool_name, "description": tool.description} for tool in available_tools]

    @classmethod
    def get_system_prompt(cls, sources: list[SourceData], available_tools: list[BaseTool]) -> str:
        prompts_data = cls._load_yaml_prompts()

        system_prompt_template = prompts_data.get("system_prompt")
        if not system_prompt_template:
            raise ValueError("system_prompt not found in YAML file")

        tools_data = cls._prepare_tools_data(available_tools)

        context = {
            "current_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "date_format": "d-m-Y HH:MM:SS",
            "available_tools": tools_data,
            "sources": sources,
        }

        try:
            template = Template(system_prompt_template)
            result = template.render(**context)
            return result.strip()
        except Exception as e:
            raise RuntimeError(f"Error rendering system prompt template: {e}") from e

    @classmethod
    def get_custom_prompt(cls, prompt_name: str, **kwargs) -> str:
        prompts_data = cls._load_yaml_prompts()

        prompt_template = prompts_data.get(prompt_name)
        if not prompt_template:
            raise ValueError(f"Prompt '{prompt_name}' not found in YAML file")

        try:
            template = Template(prompt_template)
            result = template.render(**kwargs)
            return result.strip()
        except Exception as e:
            raise RuntimeError(f"Error rendering prompt '{prompt_name}': {e}") from e
