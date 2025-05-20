from mcp.server.fastmcp import FastMCP
import os
from datetime import datetime
import shutil
import re
import json
import subprocess
import psycopg2
from psycopg2 import sql


# Create an MCP server
mcp = FastMCP("MCP Server 1")
mcp.timeout = 600  # Set timeout to 60 seconds

# Our fist tool
@mcp.tool()
def hello_world(name: str) -> str:
    """
    Say hello to the world.
    Args:
        name (str): The name to greet.
    Returns:
        str: A greeting message.
    Example:
        Greet Alice
    """
    return f"Hello, {name}!"

# Our second tool
@mcp.tool()
def get_current_time() -> str:
    """
    Get the current time.
    Returns:
        str: The current time in YYYY-MM-DD HH:MM:SS format.
    Example:
        What time is it?
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Our third tool
@mcp.tool()
def list_files(directory: str) -> list:
    """
    List files in a directory.
    Args:
        directory (str): The directory to list files from.
    Returns:
        list: A list of files in the directory.
    Example:
        List files in /Users/deniz.duzgun/Documents/git/dduzgun-security/local-mcp-server/mcp-server-1
        List files in the current directory
    """
    try:
        return os.listdir(directory)
    except FileNotFoundError:
        return f"Directory {directory} not found."

@mcp.tool()
def create_terraform_file(file_name: str, content: str) -> str:
    """
    Create a Terraform file with the given content.
    Args:
        file_name (str): The name of the file to create.
        content (str): The content to write to the file.
    Returns:
        str: A message indicating success or failure.
    Example:
        Create a Terraform file in /Users/deniz.duzgun/Documents/git/dduzgun-security/local-mcp-server/mcp-server-1/main.tf that creates an ubuntu EC2 instance
    """
    try:
        with open(file_name, 'w') as f:
            f.write(content)
        return f"File {file_name} created successfully."
    except Exception as e:
        return f"Error creating file {file_name}: {e}"

@mcp.tool()
def security_review_terraform_file(file_name: str) -> str:
    """
    Perform a security review of a Terraform file.
    Args:
        file_name (str): The name of the file to review.
    Returns:
        str: A message indicating the result of the review.
    Example:
        Review the security of /Users/deniz.duzgun/Documents/git/dduzgun-security/local-mcp-server/mcp-server-1/main.tf
    """
    try:
        with open(file_name, 'r') as f:
            content = f.read()

        prompt = (
            "Act as an experienced security engineer and review the following terraform file content:\n\n"
            f"{content}\n\n"
            "Please provide a detailed security review."
        )

        # Call Ollama locally
        ollama_cmd = [
            "curl", "-s", "http://localhost:11434/api/generate",
            "-d", json.dumps({
                "model": "llama3.2",
                "prompt": prompt
            })
        ]
        result = subprocess.run(ollama_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return f"Error calling Ollama: {result.stderr}"

        # Parse Ollama's response
        try:
            response_json = json.loads(result.stdout)
            review = response_json.get("response", result.stdout)
        except Exception:
            review = result.stdout

        return f"Security review of {file_name}:\n{review}"
    except FileNotFoundError:
        return f"File {file_name} not found."
    except Exception as e:
        return f"Error reviewing file {file_name}: {e}"


@mcp.tool()
def create_postgresql_database(db_name: str) -> str:
    """
    Create a PostgreSQL database.
    Args:
        db_name (str): The name of the database to create.
    Returns:
        str: A message indicating success or failure.
    Example:
        Create a PostgreSQL database named my_database
    """
    try:
        # Replace with your actual PostgreSQL connection details
        conn = psycopg2.connect(
            dbname="postgres",
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            host="localhost",
            port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE {db_name};")
        cursor.close()
        conn.close()
        return f"Database {db_name} created successfully."
    except Exception as e:
        return f"Error creating database {db_name}: {e}"

@mcp.tool()
def create_postgresql_table(db_name: str, table_name: str) -> str:
    """
    Create a PostgreSQL table.
    Args:
        db_name (str): The name of the database.
        table_name (str): The name of the table to create.
    Returns:
        str: A message indicating success or failure.
    Example:
        Create a PostgreSQL table named my_table in my_database
    """
    try:
        # Replace with your actual PostgreSQL connection details
        conn = psycopg2.connect(
            dbname=db_name,
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        # SQL injection
        cursor.execute(f"CREATE TABLE {table_name} (id SERIAL PRIMARY KEY, data TEXT);")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return f"Table {table_name} created successfully in database {db_name}."
    except Exception as e:
        return f"Error creating table {table_name} in database {db_name}: {e}"

@mcp.tool()
def insert_data_to_postgresql(db_name: str, table_name: str, data: dict) -> str:
    """
    Insert data into a PostgreSQL database table.
    Args:
        db_name (str): The name of the database.
        table_name (str): The name of the table.
        data (dict): The data to insert.
    Returns:
        str: A message indicating success or failure.
    Example:
        Insert data into my_database.my_table
        
        {
           "data": "User2');INSERT into demo (data) VALUES('Something"
        }
    """
    try:
        # Replace with your actual PostgreSQL connection details
        conn = psycopg2.connect(
            dbname=db_name,
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        columns = ', '.join(data.keys())
        values = ', '.join([f"'{v}'" for v in data.values()])
        
        # SQL injection 
        cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({values});")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return f"Data inserted into {db_name}.{table_name} successfully."
    except Exception as e:
        return f"Error inserting data into {db_name}.{table_name}: {e}"

@mcp.tool()
def select_data_from_postgresql(db_name: str, table_name: str) -> str:
    """
    Select data from a PostgreSQL database table.
    Args:
        db_name (str): The name of the database.
        table_name (str): The name of the table.
    Returns:
        str: The selected data.
    Example:
        Select data from my_database.my_table
    """
    try:
        # Replace with your actual PostgreSQL connection details
        conn = psycopg2.connect(
            dbname=db_name,
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        # SQL injection
        cursor.execute(f"SELECT * FROM {table_name};")
        # cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return f"Data from {db_name}.{table_name}:\n{rows}"
    except Exception as e:
        return f"Error selecting data from {db_name}.{table_name}: {e}"

@mcp.resource("terraform://region")
def get_terraform_region() -> str:
    """
    Get the region from the Terraform file.
    Returns:
        str: The region specified in the Terraform file.
    """
    
    with open("/Users/deniz.duzgun/Documents/git/dduzgun-security/local-mcp-server/mcp-server-1/main.tf", 'r') as f:
        content = f.read()

    # Use regex to reliably extract the region value
    match = re.search(r'region\s*=\s*"([^"]+)"', content)
    if match:
        return match.group(1)
    else:
        return "No region found in the Terraform file."
    

@mcp.prompt()
def terraform_summary(file_name: str) -> str:
    """
    Prompt the user for a summary of the Terraform file.
    Returns:
        str: A summary of the Terraform file.
    """

    with open(file_name, 'r') as f:
        content = f.read().strip()

    if not content:
        return "Terraform file is empty."

    # Generate a summary of the Terraform file
    summary = f"Terraform file {file_name} contains {len(content.splitlines())} lines, please summarize it."
    
    return summary


if __name__ == "__main__":
    mcp.run(transport='stdio')
