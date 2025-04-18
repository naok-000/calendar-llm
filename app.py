import getpass
import os
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
import dotenv
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI

# 環境変数の読み込み
dotenv.load_dotenv()

def _set_if_undefined(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"Please provide your {var}")

_set_if_undefined("OPENAI_API_KEY")
_set_if_undefined("LANGCHAIN_API_KEY")

# 設定の追加
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Database Agent"

# DBを指定
db = SQLDatabase.from_uri("sqlite:///calendar.db", sample_rows_in_table_info=3)
# LLMの指定
llm = ChatOpenAI(model="gpt-3.5-turbo")
# SQLエージェントの作成
agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)

if __name__ == "__main__":
    # ユーザーからの質問を受け取り、エージェントに渡す
    prompt = input("質問を入力してください: ")
    agent_executor.invoke(prompt)
    