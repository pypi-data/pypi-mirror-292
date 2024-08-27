from typing import Dict, Any

from pytexttosql.sqlite.handlers.database.handler import SQLiteDatabaseHandler
from pytexttosql.sqlite.handlers.query.handler import SQLiteQueryHandler
from pytexttosql.sqlite.handlers.llm.handler import SQLiteLLMHandler

class SQLiteEngine(SQLiteDatabaseHandler, SQLiteQueryHandler, SQLiteLLMHandler):
    """
    SQLiteEngine class that combines database handling, query handling, and LLM interaction.
    Inherits from SQLiteDatabaseHandler, SQLiteQueryHandler, and SQLiteLLMHandler.
    """

    def __init__(self, db_name: str) -> None:
        """
        Initialize the SQLiteEngine with the specified database name.

        :param db_name: The name of the SQLite database (without .db extension).
        """
        SQLiteDatabaseHandler.__init__(self, db_name=db_name)
        SQLiteQueryHandler.__init__(self)
        SQLiteLLMHandler.__init__(self)

    def query(self, query: str, n_retries: int = 3) -> Dict[str, Any]:
        """
        Process a natural language query by cleaning it, generating an SQL query,
        executing it, and generating a human-readable result.

        :param query: The natural language query provided by the user.
        :param n_retries: The number of times to retry the query generation and execution.
        :return: A dictionary containing the SQL result and the generative LLM result.
        """
        return_result = {}
        custom_prompt = ""

        for attempt in range(n_retries):
            # print(f"Retry attempt: {attempt + 1}")  # Print the retry attempt number
            
            try:
                # Clean the query using the inherited handle_query method
                cleaned_query = self.handle_query(query)

                # Get the database schema using the inherited get_db_schema method
                schema = self.get_db_schema()
                if not schema:
                    raise ValueError("Failed to retrieve database schema.")

                # Generate SQL query using the inherited make_texttosql_llm_call method
                llm_sql_result = self.make_texttosql_llm_call(query=cleaned_query, schema=schema, custom_prompt=custom_prompt)

                # Check for out-of-domain question
                if llm_sql_result.get('out_of_domain'):
                    return_result['sql_result'] = []
                    out_of_domain_message = llm_sql_result.get('out_of_domain_message', "")
                    out_of_domain_message += "\n\nHere are some recommended questions:\n\n"
                    for i, question in enumerate(llm_sql_result.get('recommended_next_questions', []), 1):
                        out_of_domain_message += f"{i}. {question}\n"
                    return_result['generative_result'] = out_of_domain_message
                    return return_result

                # Ensure that an SQL query was generated
                sql_query = llm_sql_result.get('sql')
                if not sql_query:
                    custom_prompt = (
                        f"The LLM failed to generate a valid SQL query on attempt {attempt + 1}. "
                        "Ensure that the input query is clear and relevant to the database schema."
                    )
                    continue  # Retry with the updated prompt

                # Execute the SQL query
                data = self.execute_query(sql_query)
                if data:
                    return_result['sql_result'] = data
                    llm_generative_result = self.make_generative_llm_call(query=cleaned_query, data=data)
                    return_result['generative_result'] = llm_generative_result.get('result')
                    break  # Exit the loop on successful data retrieval

                # If no data returned, prepare a custom prompt for the next iteration
                custom_prompt = (
                    f"SQL query executed but returned no data on attempt {attempt + 1}. "
                    f"SQL: {sql_query}. Consider improving the query to fetch relevant data."
                )

            except Exception as e:
                # Log exception and prepare for the next attempt
                custom_prompt = f"An exception occurred: {str(e)}. Attempting to recover on attempt {attempt + 1}..."
                if attempt == n_retries - 1:
                    return {"error": str(e), "sql_result": [], "generative_result": ""}

        # Return the final result after retries or a successful attempt
        return return_result
