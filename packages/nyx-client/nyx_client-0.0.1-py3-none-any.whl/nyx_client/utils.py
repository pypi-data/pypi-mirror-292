"""
Module that contains utility functions, as well as tooling for manual parsing of data contained in Nyx products
"""

import logging
from io import StringIO
from typing import Any, List, Literal, Optional

import names_generator
import pandas as pd
from iotics.lib.identity.api.high_level_api import get_rest_high_level_identity_api
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine, engine

from .products import NyxProduct

logging.basicConfig(format="%(asctime)s %(levelname)s [%(module)s] %(message)s", level=logging.INFO)

log = logging.getLogger(__name__)


class VectorResult:
    def __init__(self, chunk: str, similarity: float, success: bool, message: str = ""):
        self.chunk = chunk
        self.similarity = similarity
        self.success = success
        self.message = message

    def __repr__(self):
        return self.chunk


class Utils:
    @staticmethod
    def with_sources(prompt: str) -> str:
        return Utils.build_query(
            prompt
            + (
                "and also using the table nyx_schema where table_name is the name of the table the "
                "information came from, retrieve the source and url of the relevant table queried."
                "When you go to say table, actually say sources. Output in HTML list format"
            )
        )

    @staticmethod
    def build_query(prompt: str) -> str:
        return prompt + (
            "Do not talk as if you are getting the results from a database, each table in the database is "
            "a file from a source. Do not make mention of any sources in your answer. If there are no tables "
            "in the schema, or you can't see relevant ones, JUST RESPOND WITH the text 'I don't know', nothing else."
        )

    @staticmethod
    def with_confidence(prompt: str) -> str:
        return prompt + (
            "Do not talk as if you are getting the results from a database, each table in the database is "
            "a file from a source. Do not make mention of any sources in your answer. If there are no tables "
            "in the schema, or you can't see relevant ones, JUST RESPOND WITH the text 'I don't know', nothing else."
            "Also, provide a confidence score between 0 and 1 for your answer. The response should be of the format: "
            '{"content": "<your response>", "confidence": <your confidence score>}'
        )


class Parser:
    """A class for processing and querying datasets from NyxProduct instances.

    This class provides methods to convert datasets into SQL databases or vector representations,
    and to perform queries on the processed data.

    Attributes:
        vectors: The TF-IDF vector representations of the processed content.
        vectorizer: The TfidfVectorizer instance used for creating vectors.
        chunks: The text chunks created from the processed content.
    """

    def __init__(self):
        """Initialize a Parser instance."""
        self.vectors = None
        self.vectorizer = None
        self.chunks = None

    @staticmethod
    def dataset_as_db(
        twins: List[NyxProduct],
        sqlite_file: Optional[str] = None,
        if_exists: Literal["fail", "replace", "append"] = "fail",
    ) -> "engine.Engine":
        """Process the content of multiple NyxProduct instances into an in-memory SQLite database.

        This method downloads the content of each product (if it's a CSV) and converts it to an in-memory
        SQLite database. The resulting database engine is then returned for use with language models.

        Args:
            twins (List[NyxProduct]): A list of NyxProduct instances to process.
            sqlite_file (Optional[str]) Provide a file for the database to reside in
            if_exists (str): What to do if a table already exists Defaults to "fail" can be "fail", "append", "replace"

        Returns:
            engine.Engine: An SQLAlchemy engine instance for the in-memory SQLite database.

        Note:
            If the list of twins is empty, an empty database engine is returned.
        """
        connection_str = "sqlite:///:memory:"
        if sqlite_file:
            connection_str = f"sqlite:///{sqlite_file}"

        db_engine = create_engine(connection_str)

        if len(twins) == 0:
            return db_engine
        tables = []
        for twin in twins:
            # TODO: check content type
            content = twin.download()
            tables.append([twin.title, twin.url, twin.title.replace(" ", "_")])
            if content:
                try:
                    data = pd.read_csv(StringIO(content))
                    data.to_sql(twin.title.replace(" ", "_"), db_engine, index=False)
                except pd.errors.ParserError:
                    if twin.content_type == "csv":
                        log.warning(f"{twin.title} could not be processed as a CSV")
                    pass
                except Exception as e:
                    print(f"unexpected error for {twin.title}")
                    print(e)

        df = pd.DataFrame(tables)
        df.columns = ["file title", "url", "table_name"]
        df.to_sql("nyx_schema", db_engine, index=False, if_exists=if_exists)
        return db_engine

    def dataset_as_vectors(self, twins: List[NyxProduct], chunk_size: int = 1000):
        """Process the content of multiple NyxProduct instances into vector representations.

        This method downloads the content of each product, combines it, chunks it,
        and creates a TF-IDF vectorizer for the chunks.

        Args:
            twins (List[NyxProduct]): A list of NyxProduct instances to process.
            chunk_size (int, optional): The size of each chunk when splitting the content. Defaults to 1000.

        Returns:
            Parser: The current Parser instance with updated vectors, vectorizer, and chunks.

        Note:
            If no content is found in any of the twins, the method returns without processing.
        """
        contents = ""
        for twin in twins:
            content = twin.download()
            if content:
                contents += content
        if contents == "":
            return

        self.chunks = self._chunk_text(contents, chunk_size)

        self.vectorizer = TfidfVectorizer()
        self.vectors = self.vectorizer.fit_transform(self.chunks)

        return self

    @staticmethod
    def _chunk_text(text: str, chunk_size: int) -> List[str]:
        """Split a text into chunks of a specified size.

        Args:
            text (str): The text to be chunked.
            chunk_size (int): The maximum number of words in each chunk.

        Returns:
            List[str]: A list of text chunks.
        """
        words = text.split()
        return [" ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)]

    def find_matching_chunk(self, query_vector: Any) -> VectorResult:
        """Find the best matching chunk for a given query vector.

        Args:
            query_vector (Any): The vector representation of the query.

        Returns:
            VectorResult: An object containing the best matching chunk, its similarity score, and success status.

        Raises:
            ValueError: If the content has not been processed yet.
        """
        if self.vectors is None:
            raise ValueError("Content has not been processed. Call dataset_as_vectors() first.")
        similarities = cosine_similarity(query_vector, self.vectors)
        best_match_index = similarities.argmax()
        return VectorResult(
            chunk=self.chunks[best_match_index],
            similarity=similarities[0][best_match_index],
            success=True,
        )

    def query(self, text: str) -> VectorResult:
        """Query the processed content with a text string.

        Args:
            text (str): The query text.

        Returns:
            VectorResult: An object containing the best matching chunk and related information,
                          or an error message if the content has not been processed.
        """
        if self.vectorizer is None:
            return VectorResult(
                chunk="",
                similarity=0,
                success=False,
                message="content not processed, or not present on the twin (do you have access?)",
            )
        query_vector = self.vectorizer.transform([text])
        return self.find_matching_chunk(query_vector)


class Helpers:
    @staticmethod
    def generate_config(resolver: str) -> str:
        """
        Create new user and agent with auth delegation.
        """

        high_level_api = get_rest_high_level_identity_api(resolver_url=resolver)
        user_seed = high_level_api.create_seed()
        agent_seed = high_level_api.create_seed()
        user_key = f"#user-{names_generator.generate_name()}"
        agent_key = f"#agent-{names_generator.generate_name()}"
        if len(user_key) > 24:
            user_key = user_key[0:23]
        if len(agent_key) > 24:
            agent_key = agent_key[0:23]

        user_deleg = "#testagent"

        if len(user_key) > 24:
            user_key = user_key[0:23]
        if len(agent_key) > 24:
            agent_key = agent_key[0:23]

        user, agent = high_level_api.create_user_and_agent_with_auth_delegation(
            user_seed=user_seed,
            user_key_name=user_key,
            agent_seed=agent_seed,
            agent_key_name=agent_key,
            delegation_name=user_deleg,
            user_name=user_key,
            agent_name=agent_key,
        )

        return f"""
#### Generated by utils.generate_config.py - do not edit manually
DID_USER_DID={user.did}
DID_AGENT_DID={agent.did}
DID_AGENT_KEY_NAME="{agent_key}"
DID_AGENT_NAME="{agent_key}"
DID_AGENT_SECRET={agent_seed.hex()}
HOST_VERIFY_SSL=true # Set to false for development
####

NYX_URL=<ENTER NYX_URL>
NYX_USERNAME=<ENTER USERNAME>
NYX_EMAIL=<ENTER EMAIL>
NYX_PASSWORD=<ENTER PASSWORD>
OPENAI_API_KEY=<ENTER KEY IF REQUIRED (using NyxClientLangChain)>
"""
