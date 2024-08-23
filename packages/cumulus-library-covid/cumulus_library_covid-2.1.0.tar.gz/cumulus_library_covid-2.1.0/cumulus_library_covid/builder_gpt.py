"""Builder for the ChatGPT symptoms tables."""

import os

import cumulus_library
import jinja2


class GptBuilder(cumulus_library.BaseTableBuilder):
    display_text = "Creating ChatGPT symptom tables..."

    def prepare_queries(self, *args, **kwargs):
        self.queries += [
            self.render_sql("builder_gpt", model="gpt35"),
            self.render_sql("builder_gpt", model="gpt4"),
        ]

    @staticmethod
    def render_sql(template: str, **kwargs) -> str:
        path = os.path.dirname(__file__)
        with open(f"{path}/{template}.jinja") as file:
            loader = jinja2.FileSystemLoader(path)
            env = jinja2.Environment(loader=loader, autoescape=True).from_string(file.read())
            return env.render(**kwargs)
