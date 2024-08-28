import re
import json
from typing import Dict, Any, Optional

from openai import OpenAI

class SQLiteLLMHandler:
    """Handler class for generating SQL queries using OpenAI's LLM and processing responses."""
    
    def __init__(self, client: Optional[OpenAI] = None) -> None:
        """
        Initialize the SQLiteLLMHandler.

        :param client: Optional instance of OpenAI client. If not provided, it will be instantiated later.
        """
        self.client = client

    def make_texttosql_llm_call(self, query: str, schema: Dict[str, Any], custom_prompt: str = "") -> Dict[str, Any]:
        """
        Generates an SQL query based on the provided natural language query and schema using OpenAI's LLM.

        :param query: The natural language query.
        :param schema: The database schema as a dictionary.
        :param custom_prompt: Additional instructions or context for the LLM.
        :return: A dictionary containing the generated SQL query and additional information.
        """

        return_dict = {
            "sql_generation_status": None, 
            "sql_generation_status_message": None, 
            "out_of_domain": None, 
            "out_of_domain_message": None,
            "sql_query_from_llm": None,
            "next_questions": None
            }
        
        if self.client is None:
            self.client = OpenAI()

        prompt = self._build_texttosql_llm_prompt(query, schema, custom_prompt)

        if not prompt.strip():
            return_dict["sql_generation_status"] = "error"
            return_dict["sql_generation_status_message"] = "Generated prompt is empty or None."
            return return_dict

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self._system_message_sql()},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                max_tokens=1024,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )

            result = response.choices[0].message.content.strip()
            "TODO: Add code to parse the response and return the SQL query and out_of_domain flag"

            # Try to parse the response into a JSON object
            try:
                json_result = json.loads(result)
                if isinstance(json_result, dict):
                    return_dict["sql_generation_status"] = True
                    return_dict["sql_generation_status_message"] = "SQL query generated successfully"
                    return_dict["out_of_domain"] = json_result.get('out_of_domain', False)
                    return_dict["out_of_domain_message"] = json_result.get('out_of_domain_message', "")
                    return_dict["sql_query_from_llm"] = json_result.get('sql_query')
                    return_dict["next_questions"] = json_result.get('next_questions')
                    return return_dict
                else:
                    return_dict["sql_generation_status"] = False
                    return_dict["sql_generation_status_message"] = "LLM response was not evaluated as a Python dictionary"
                    return return_dict

            except json.JSONDecodeError as e:
                return_dict["sql_generation_status"] = False
                return_dict["sql_generation_status_message"] = f"Failed to decode JSON: {str(e)}"
                return return_dict

        except Exception as e:
            return_dict["sql_generation_status"] = False
            return_dict["sql_generation_status_message"] = str(e)
            return return_dict

    def make_generative_llm_call(self, query: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a response based on the provided data using OpenAI's LLM.

        :param query: The natural language query.
        :param data: Data in JSON format.
        :return: A dictionary containing the LLM's response.
        """
        return_result = {"generative_llm_call_status": None, "generative_llm_call_status_message": None, "generative_llm_call_result": None}
        if self.client is None:
            self.client = OpenAI()  # Instantiate the client only when needed
        
        prompt = self._build_generative_llm_prompt(query, data)
        
        if not prompt:
            raise ValueError("Generated prompt is empty or None.")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self._system_message_generic()},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                max_tokens=1024,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            generative_result = response.choices[0].message.content.strip()
            return_result["generative_llm_call_status"] = True
            return_result["generative_llm_call_status_message"] = "Generative LLM call successful..."
            return_result["generative_llm_call_result"] = generative_result

        except Exception as e:
            return_result["generative_llm_call_status"] = False
            return_result["generative_llm_call_status_message"] = f"Unable to generate LLM response for SQL data\nError message: {str(e)}"
        return return_result

    def _build_texttosql_llm_prompt(self, query: str, schema: Dict[str, Any], custom_prompt: str = "") -> str:
        """
        Constructs a prompt for generating SQL queries from a natural language question.

        :param query: The natural language query.
        :param schema: The database schema as a dictionary.
        :param custom_prompt: Additional instructions or context for the LLM.
        :return: The prompt string for the LLM.
        """
        prompt_parts = []
        if custom_prompt:
            prompt_parts.append(f"{custom_prompt}\n\n")

        prompt_parts.append(
            "You are a SQLite expert tasked with returning a SQL query based on a user's natural language question, the data schema, and a few example rows of the data."
        )
        prompt_parts.append(f"\n\nThe data schema is as follows:\n\n{json.dumps(schema, indent=2)}")
        prompt_parts.append(f"\n\nThe user's question is: {query}")
        prompt_parts.append(
            "\n\n"
            "CONTEXTUAL INSTRUCTIONS:\n"
            "- Understand the context of the request to ensure the SQL query correctly identifies and filters for the relevant entities.\n"
            "- Maintain context from previous questions and ensure the current query builds on previous results when needed.\n"
            "- Be mindful of pronouns and ambiguous terms, ensuring they are mapped to the correct entities and columns.\n"
            "- Consider SQLite's specific limitations, as all queries will run on a SQLite database.\n"
            "SQL INSTRUCTIONS:\n"
            "- Do not use parameterized queries.\n"
            "- Avoid symbols when evaluating strings; use 'LIKE' for string comparisons.\n"
            "- Ensure case-insensitive comparisons using 'LOWER()' in queries.\n"
            "- Optimize the query to return only the necessary data using SQL clauses like 'DISTINCT', 'WHERE', 'GROUP BY', 'ORDER BY', 'LIMIT', etc.\n"

            "RESPONSE INSTRUCTIONS:\n"
            "- Return ONLY the following key-value pairs: 'sql_query': 'your sql query here', 'out_of_domain': 'boolean True or False if you think the query relates data in the database and will be answered with the SQL; True if the question is out of domain', 'out_of_domain_message': 'if question is out_of_domain, craft a message letting the user know, otherwise return an empty string', and 'next_questions': 'an ordered list of recommended next questions from the perspective of the user asking questions to the LLM'\n"
            "- Only include the dictionary in the response. Don't include '```python' or '```' in the response.\n"
            "- The response should be a python dictionary that returns 'dict' when evaluated: type(eval(response)) == dict"
        )
        
        return "".join(prompt_parts)

    def _build_generative_llm_prompt(self, query: str, data: Dict[str, Any]) -> str:
        """
        Constructs a prompt for generating natural language responses based on SQL data.

        :param query: The natural language query.
        :param data: Data in JSON format.
        :return: The prompt string for the LLM.
        """

        generative_llm_prompt = ""
        generative_llm_prompt += f"Based on the question:\n**{query}**\n the following data was found:\n"
        generative_llm_prompt += f"SQL Data in JSON format: {data}\n"
        generative_llm_prompt += "INSTRUCTIONS:\n"
        generative_llm_prompt += "- Respond directly with the answer based on the provided data.\n"
        generative_llm_prompt += "- Use clear and concise language, structuring the response with lists or paragraphs as needed.\n"
        generative_llm_prompt += "- Do not reference the data sources explicitly.\n"
        generative_llm_prompt += "- If any assumptions are made, clearly state them.\n"
        generative_llm_prompt += "- If the data is insufficient, state that explicitly.\n"
        return generative_llm_prompt

    def _system_message_sql(self) -> str:
        """
        Provides a system message for guiding the LLM in generating SQL queries.

        :return: The system message string.
        """
        return (
            "You are a helpful research assistant and a SQL expert for SQLite databases."
            "Respond ONLY with a valid JSON object containing the specified keys and values, without any additional text, code blocks, or formatting."
        )

    def _system_message_generic(self) -> str:
        """
        Provides a system message for guiding the LLM in generating generic responses.

        :return: The system message string.
        """
        system_message_generic = ""
        system_message_generic += "You are a helpful research assistant and a SQL expert for SQLite databases. "
        system_message_generic += "Respond ONLY with the answer to the user's question, without any additional text, code blocks, or formatting."
        return system_message_generic

    def _clean_llm_response(self, response: str) -> str:
        """
        Cleans the LLM response by removing unwanted characters and formatting.

        :param response: The raw response from the LLM.
        :return: The cleaned response string.
        """
        response = re.sub(r"```(\w+)?", "", response).strip()
        response = response.replace('true', 'True').replace('false', 'False')
        return response
