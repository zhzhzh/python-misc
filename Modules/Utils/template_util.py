from jinja2 import Environment, PackageLoader, select_autoescape


class TemplateUtil:
    
    def __init__(self, module_name: str = 'Utils', package_path: str = 'templates') -> None:
        self.package_name = module_name
        self.package_path = package_path

        self.env = Environment(
            loader=PackageLoader(self.package_name, self.package_path),
            autoescape=select_autoescape(enabled_extensions=('html'))
        )
    
    def render(self, tpl_name: str, context: dict[str, object]) -> str:
        template = self.env.get_template(tpl_name)
        rendered_context = template.render(**context)
        return rendered_context
