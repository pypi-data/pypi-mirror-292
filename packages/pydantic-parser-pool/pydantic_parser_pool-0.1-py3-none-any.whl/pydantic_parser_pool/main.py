import json
import re
from typing import List, Type, Tuple

from langchain.output_parsers import PydanticOutputParser
from langchain_core.outputs import Generation
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.utils.pydantic import TBaseModel


_POOLED_PYDANTIC_INSTRUCTION_FORMAT_START = """The output should be formatted as a JSON instance that conforms to one of the JSON schemas below. Choose the schema that fits the situation the best. You must first think about the query properly and answer only in one of the provided schemas.

As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}
the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

And here are the schemas
"""


_POOLED_PYDANTIC_INSTRUCTION_FORMAT_END = """Must wrap the output json into the following json to create the final response.

{
    "schema": "Name of the chosen schema"
    "response": the output json goes here
}
""" 


class PoolBaseModel(BaseModel):
    
    @classmethod
    def _name_description(cls) -> Tuple[str, str]:
        
        doc_string = cls.__doc__.strip()

        content = re.search(r'xxxxxx\s*(.*?)\s*xxxxxx', doc_string, re.DOTALL)
        
        if content:
            # Extracted content between xxxxxx markers
            content = content.group(1).strip()
            
            # Split content into lines
            lines = content.split('\n')
            
            # Initialize variables
            schema_name = None
            schema_description = []
            
            # Iterate through lines to extract schema_name and schema_description
            in_description = False
            for line in lines:
                line = line.strip()
                if line.startswith('schema_name='):
                    schema_name = line[len('schema_name='):].strip()
                elif line.startswith('schema_description='):
                    in_description = True
                    schema_description.append(line[len('schema_description='):].strip())
                elif in_description:
                    # Collect all subsequent lines for schema_description
                    schema_description.append(line)
            
            # Join all parts of schema_description into a single string
            schema_description = '\n'.join(schema_description).strip()

            # Print results
            return (schema_name, schema_description)
        else:
            print("Name and Description not found")
    




class PydanticOutputParserPool(PydanticOutputParser):
    
    class_pool: List[Type[PoolBaseModel]] = Field(default_factory=list)

    def __init__(self, class_pool):
        super().__init__(pydantic_object=PoolBaseModel)
        self.class_pool = class_pool
    
    def parse_result(self, result: List[Generation], *, partial: bool = False) -> TBaseModel:
        data = json.loads(result[0].text)

        # Extract schema and response
        schema = data["schema"]
        response = data["response"]
        
        for class_item in self.class_pool:
            name, _ = class_item._name_description()
            if name == schema:
                super().__init__(pydantic_object=class_item)
                break
        
        if self.pydantic_object:
            generation = Generation(text=json.dumps(response))
            result = super().parse_result([generation])
            return result
        
    
    def get_format_instructions(self) -> str:
        
        schemas = ''
        i = 1
        
        for class_item in self.class_pool:
            name, description = class_item._name_description()
            
            class_item_pydantic_object = class_item
            # Copy schema to avoid altering original Pydantic schema.
            schema = {k: v for k, v in class_item_pydantic_object.schema().items()}

            schema.pop("description")

            # Remove extraneous fields.
            reduced_schema = schema
            if "title" in reduced_schema:
                del reduced_schema["title"]
            if "type" in reduced_schema:
                del reduced_schema["type"]
            # Ensure json in context is well-formed with double quotes.
            schema_str = json.dumps(reduced_schema, ensure_ascii=False)
            
            schema_str = f"Schema {i}\nSchema name: {name}\nSchema description: {description}\n\n{schema_str}"
            
            schemas = f"{schemas}{schema_str}\n\n"
            
            i += 1
            
        return f"{_POOLED_PYDANTIC_INSTRUCTION_FORMAT_START}\n{schemas}\n{_POOLED_PYDANTIC_INSTRUCTION_FORMAT_END}"
            


# Re-exporting types for backwards compatibility
__all__ = [
    "PoolBaseModel",
    "PydanticOutputParser",
    "PydanticOutputParserPool",
    "TBaseModel",
]