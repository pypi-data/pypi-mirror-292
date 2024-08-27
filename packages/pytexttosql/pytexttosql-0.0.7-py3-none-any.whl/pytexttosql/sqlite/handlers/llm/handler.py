from openai import OpenAI
import re
import json
from typing import Dict, Any, Optional

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
        if self.client is None:
            self.client = OpenAI()  # Instantiate the client only when needed

        prompt = self._build_texttosql_llm_prompt(query, schema, custom_prompt)

        if not prompt.strip():
            return {"error": "Generated prompt is empty or None.", "response": ""}

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
            result = self._clean_llm_response(result)

            # Try to parse the response into a JSON object
            try:
                json_result = json.loads(result)
                if isinstance(json_result, dict):
                    return json_result
                else:
                    return {"error": "Response is not a dictionary", "response": result}

            except json.JSONDecodeError as e:
                return {"error": f"Failed to decode JSON: {str(e)}", "response": result}

        except Exception as e:
            return {"error": str(e), "response": ""}

    def make_generative_llm_call(self, query: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a response based on the provided data using OpenAI's LLM.

        :param query: The natural language query.
        :param data: Data in JSON format.
        :return: A dictionary containing the LLM's response.
        """
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
            return {"result": generative_result}

        except Exception as e:
            return {"error": str(e), "result": ""}

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
            "- Return results in a dictionary format that can be safely evaluated in Python.\n"
        )
        
        return "".join(prompt_parts)

    def _build_generative_llm_prompt(self, query: str, data: Dict[str, Any]) -> str:
        """
        Constructs a prompt for generating natural language responses based on SQL data.

        :param query: The natural language query.
        :param data: Data in JSON format.
        :return: The prompt string for the LLM.
        """
        return (
            f"Based on the question:\n\n**{query}**\n\n the following data was found:\n\n"
            f"SQL Data in JSON format: {data}\n"
            "INSTRUCTIONS:\n"
            "- Respond directly with the answer based on the provided data.\n"
            "- Use clear and concise language, structuring the response with lists or paragraphs as needed.\n"
            "- Do not reference the data sources explicitly.\n"
            "- If any assumptions are made, clearly state them.\n"
            "- If the data is insufficient, state that explicitly.\n"
        )

    def _system_message_sql(self) -> str:
        """
        Provides a system message for guiding the LLM in generating SQL queries.

        :return: The system message string.
        """
        return (
            "You are a helpful research assistant and a SQL expert for SQLite databases. "
            "Respond ONLY with a valid JSON object containing the specified keys and values, without any additional text, code blocks, or formatting."
        )

    def _system_message_generic(self) -> str:
        """
        Provides a system message for guiding the LLM in generating generic responses.

        :return: The system message string.
        """
        return (
            "You are a helpful research assistant and a SQL expert for SQLite databases. "
            "Respond ONLY with the answer to the user's question, without any additional text, code blocks, or formatting."
        )

    def _clean_llm_response(self, response: str) -> str:
        """
        Cleans the LLM response by removing unwanted characters and formatting.

        :param response: The raw response from the LLM.
        :return: The cleaned response string.
        """
        response = re.sub(r"```(\w+)?", "", response).strip()
        response = response.replace('true', 'True').replace('false', 'False')
        return response
