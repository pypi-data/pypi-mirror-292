import pytest
from autochat.model import transform_to_openai, transform_to_anthropic

def test_transform_to_openai():
    # Sample input
    input_data = {
        "system": "You are a data analyst assistant...",
        "user": "DATABASE\n- name: bike\n- engine: postgres\nMEMORY: No memory\n\nShow stations in san jose installed in 2012",
        "assistant": "> SQL_QUERY(name=\"database tables\", query=```SELECT table_schema, table_name\nFROM information_schema.tables\nWHERE table_schema NOT IN ('pg_catalog', 'information_schema')```)",
        "function": "\"table_schema\",\"table_name\"\n\"public\",\"station\"\n\"public\",\"station_info\"\n\"public\",\"status\""
    }

    # Expected output
    expected_output = [
        {"role": "system", "content": "You are a data analyst assistant..."},
        {"role": "user", "content": "DATABASE\n- name: bike\n- engine: postgres\nMEMORY: No memory\n\nShow stations in san jose installed in 2012"},
        {"role": "assistant", "content": "> SQL_QUERY(name=\"database tables\", query=```SELECT table_schema, table_name\nFROM information_schema.tables\nWHERE table_schema NOT IN ('pg_catalog', 'information_schema')```)"},
        {"role": "function", "name": "SQL_QUERY", "content": "\"table_schema\",\"table_name\"\n\"public\",\"station\"\n\"public\",\"station_info\"\n\"public\",\"status\""}
    ]

    # Test the transformation
    result = transform_to_openai(input_data)
    assert result == expected_output

def test_transform_to_anthropic():
    # Sample input (same as OpenAI test)
    input_data = {
        "system": "You are a data analyst assistant...",
        "user": "DATABASE\n- name: bike\n- engine: postgres\nMEMORY: No memory\n\nShow stations in san jose installed in 2012",
        "assistant": "> SQL_QUERY(name=\"database tables\", query=```SELECT table_schema, table_name\nFROM information_schema.tables\nWHERE table_schema NOT IN ('pg_catalog', 'information_schema')```)",
        "function": "\"table_schema\",\"table_name\"\n\"public\",\"station\"\n\"public\",\"station_info\"\n\"public\",\"status\""
    }

    # Expected output
    expected_output = """Human: DATABASE
- name: bike
- engine: postgres
MEMORY: No memory

Show stations in san jose installed in 2012
