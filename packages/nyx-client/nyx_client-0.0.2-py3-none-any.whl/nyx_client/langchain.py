"""
Optional module for tight integration between LangChain and Nyx
"""

import os
from typing import Optional

from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from .client import NyxClient, NyxConfig
from .products import NyxProduct
from .utils import Parser, Utils


class NyxLangChain(NyxClient):
    """An opinionated client wrapping langChain to evaluate user queries against contents of a Nyx network.

    This class extends NyxClient to provide LangChain-based functionality for querying Nyx network contents.

    Args:
        config (Optional[NyxConfig], optional): Configuration for the Nyx client. Defaults to None.
        env_file (str, optional): Path to the environment file. Defaults to None.
        llm (Optional[BaseChatModel], optional): Language model to use. Defaults to None.

    Attributes:
        llm (BaseChatModel): The language model used for querying. If not provided, defaults to gpt-3.5-turbo.

    Note:
        The LLM must support tool calling.
    """

    def __init__(
        self,
        config: Optional[NyxConfig] = None,
        env_file: str = None,
        llm: Optional[BaseChatModel] = None,
    ):
        super().__init__(env_file, config)

        if not llm:
            llm = ChatOpenAI(model_name="gpt-3.5-turbo")
        self.llm = llm

    def query(
        self,
        prompt: str,
        products: Optional[list[NyxProduct]] = None,
        sqlite_file: Optional[str] = None,
        update_subscribed: bool = False,
    ) -> str:
        """Query the LLM with a user prompt and context from Nyx.

        This method takes a user prompt and invokes it against the LLM associated with this instance,
        using context from Nyx.

        Args:
            prompt (str): The user prompt.
            products (Optional[list[NyxProduct]], optional): List of products to use for context.
                If None, uses all subscribed products. Defaults to None.
            sqlite_file (Optional[str]): A file location to write the sql_lite file to.
            update_subscribed (bool): if set to true this will re-poll Nyx for subscribed products

        Returns:
            str: The answer from the LLM.

        Note:
            If products are not provided, this method updates subscriptions and retrieves all subscribed datasets.
        """
        if update_subscribed:
            self.update_subscriptions()
        if not products:
            products = self.get_subscribed_datasets()
        engine = Parser.dataset_as_db(products, sqlite_file=sqlite_file, if_exists="replace")

        db = SQLDatabase(engine=engine)
        agent_executor = create_sql_agent(self.llm, db=db, agent_type="tool-calling")
        res = agent_executor.invoke({"input": Utils.build_query(prompt)})

        if sqlite_file:
            os.remove(sqlite_file)

        return res["output"]
