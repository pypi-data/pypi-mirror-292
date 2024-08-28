import yaml
from typing import Dict


class VariantSchema:
    def __init__(self, variants: Dict[str, int], remove_first_column: bool):
        self.variants = variants
        self.remove_first_column = remove_first_column

        self.used_wells = sum(variants.values())
        print(f"Your schema uses {self.used_wells} wells.")

    @classmethod
    def from_yaml_content(cls, yaml_content: str):
        schema_data = yaml.safe_load(yaml_content)
        return cls(**schema_data)

    def __repr__(self):
        return f"VariantSchema(variants={self.variants}, remove_first_column={self.remove_first_column})"


if __name__ == "__main__":
    schema_path = "example_schema.yaml"
    with open("example_schema.yaml", 'r') as file:
        yaml_content_ = file.read()

    schema = VariantSchema.from_yaml_content(yaml_content_)
    print(schema)
