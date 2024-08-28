import logging
from typing import Dict, Any

from pytexttosql.sqlite.handlers.database.handler import SQLiteDatabaseHandler
from pytexttosql.sqlite.handlers.query.handler import SQLiteQueryHandler
from pytexttosql.sqlite.handlers.llm.handler import SQLiteLLMHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    )

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

    def query(self, query: str, n_attempts: int = 3, generate: bool = True, include_recommendations_in_generation: bool = False) -> Dict[str, Any]:
        """
        Process a natural language query by cleaning it, generating an SQL query,
        executing it, and generating a human-readable result.

        :param query: The natural language query provided by the user.
        :param n_attempts: The number of times to retry the query generation and execution.
        :param generate: A boolean indicating whether to generate a generative result.
        :return: A dictionary containing the SQL result and the generative LLM result.
        """

        return_result = {'sql': None, 'data': None, 'next_questions': None, 'generative_result': None}

        if not generate:
            non_generative_message = ""
            non_generative_message += "If you would like to generate a response based on the SQL query execution results, do one of the following:\n"
            non_generative_message += "  1. Don't pass the 'generate' parameter in the 'query' method\n"
            non_generative_message += "  2. Set the 'generate' parameter to True in the 'query' method\n"
            return_result['generative_result'] = non_generative_message

        custom_prompt = ""

        for attempt in range(n_attempts):
            if attempt > 0:
                print(f"Retry attempt {attempt} of {n_attempts-1}...")
            
            try:
                # Clean the query using the inherited handle_query method
                cleaned_query = self.handle_query(query)

                # Get the database schema using the inherited get_db_schema method
                schema = self.get_db_schema()
                if not schema:
                    raise ValueError("Failed to retrieve database schema. Make sure the data exists and that you've loaded tables into the database.")

                # Generate SQL query using the inherited make_texttosql_llm_call method
                """
                Returns a dictionary containing the following key-values:
                - 'sql_generation_status': boolean indicating success or failure
                - 'sql_generation_status_message': A message describing the status
                - 'out_of_domain': boolean indicating if the query is out-of-domain
                - 'out_of_domain_message': A message for out-of-domain queries
                - 'sql_query_from_llm': The generated SQL query
                - 'next_questions': A list of recommended next questions
                """
                llm_sql_result = self.make_texttosql_llm_call(query=cleaned_query, schema=schema, custom_prompt=custom_prompt)

                # unpack the dictionary
                sql_generation_status = llm_sql_result.get('sql_generation_status')
                sql_generation_status_message = llm_sql_result.get('sql_generation_status_message')
                out_of_domain = llm_sql_result.get('out_of_domain')
                out_of_domain_message = llm_sql_result.get('out_of_domain_message')
                sql_query = llm_sql_result.get('sql_query_from_llm')
                next_questions = llm_sql_result.get('next_questions')

                # if the sql_generation_status is False, raise an exception with the status message and break the loop
                if not sql_generation_status:
                    logging.ERROR(f"Error generating SQL from the LLM...")
                    raise ValueError(f"Unable to generate a SQL query from the LLM\nError message: {sql_generation_status_message}")
                # if the query is out-of-domain, set generative_result to out_of_domain_message + next_questions, log the out_of_domain_message so the user can see it, and return the return_result dictionary
                else:
                    if out_of_domain:
                        combined_message = ""
                        combined_message += out_of_domain_message
                        combined_message += "\n\nHere are some recommended next questions:\n\n"
                        for i, question in enumerate(next_questions, 1):
                            combined_message += f"{i}. {question}\n"
                        return_result['sql'] = ""
                        return_result['data'] = []
                        return_result['next_questions'] = next_questions
                        return_result['generative_result'] = combined_message
                        logging.ERROR(f"Out of domain question detected...")
                        # logging.info(f"\n{combined_message}")
                        return return_result
                    else:
                        """
                        Executes the SQL query on the SQLite database and returns the following dictionary:

                        - 'sql_execution_status': boolean indicating success or failure
                        - 'sql_execution_message': A string message describing the status
                        - 'sql_execution_result': The query result as a JSON string
                        """
                        sql_execution = self._execute_query_on_db(sql_query)
                        
                        # unpack the sql_execution result
                        sql_execution_status = sql_execution.get('sql_execution_status')
                        sql_execution_message = sql_execution.get('sql_execution_message')
                        sql_execution_result = sql_execution.get('sql_execution_result')
                        if not sql_execution_status:
                            custom_prompt = ""
                            custom_prompt += "I'm running a Text-to-SQL model to generate SQL queries based on user questions, which will ultimately be run on a SQLite database."
                            custom_prompt += "The SQL generated by the LLM in the initial attempt resulted in an error while executing on a SQLite database:"
                            custom_prompt += f"Original user question that led to the LLM-generated SQL that failed: {query}"
                            custom_prompt += f"Original LLM-generated SQL query that failed: {sql_query}"
                            custom_prompt += f"SQLite error message: {sql_execution_message}"
                            custom_prompt += f"Based on this error message, create a SQL query that accounts for the error, which will be retried on the SQLite database. Here is the prompt for the next attempt."
                            # Go to the next iteration in the loop, using the custom_prompt with the error
                            continue
                        else:
                            # Success!
                            return_result['sql'] = sql_query
                            return_result['data'] = sql_execution_result
                            return_result['next_questions'] = next_questions
                            if generate:
                                """
                                make_generative_llm_call results in a dictionary with the follow key-values:
                                - generative_llm_call_status: 
                                - generative_llm_call_status_message
                                - generative_llm_call_result
                                """
                                generative_result = self.make_generative_llm_call(query=cleaned_query, data=sql_execution_result)
                                generative_llm_call_status = generative_result.get('generative_llm_call_status')
                                generative_llm_call_status_message = generative_result.get('generative_llm_call_status_message')
                                generation = generative_result.get('generative_llm_call_result')

                                if not generative_llm_call_status:
                                    logging.ERROR(f"Error generating response from the LLM...")
                                    return_result['generative_result'] = f"Unable to generate a response from the LLM\nError message: {generative_llm_call_status_message}"
                                else:
                                    logging.info(f"Successfully generated a response from the LLM...")
                                    combined_message = ""
                                    combined_message += generation
                                    combined_message += "\n\nHere are recommended questions:\n\n"
                                    for i, question in enumerate(next_questions, 1):
                                        combined_message += f"{i}. {question}\n"
                                    return_result['generative_result'] = combined_message if include_recommendations_in_generation else generation
                            return return_result
            except Exception as e:
                raise e

        return return_result
