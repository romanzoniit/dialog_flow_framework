import os
import importlib
from pathlib import Path

import pytest
from sklearn.feature_extraction.text import TfidfVectorizer
from dff.script.logic.extended_conditions.models.local.cosine_matchers.sklearn import SklearnMatcher
from dff.script.logic.extended_conditions.dataset import Dataset

import tests.utils as utils

@pytest.fixture(scope="session")
def testing_actor():
    actor = importlib.import_module(
        f"examples.{utils.get_path_from_tests_to_current_dir(__file__, separator='.')}.base_example"
    ).actor

    yield actor


@pytest.fixture(scope="session")
def testing_dataset():
    yield Dataset.parse_yaml(Path(__file__).parent.parent.parent / f"examples/{utils.get_path_from_tests_to_current_dir(__file__)}/data/example.yaml")


@pytest.fixture(scope="session")
def standard_model(testing_dataset):
    yield SklearnMatcher(tokenizer=TfidfVectorizer(stop_words=None), dataset=testing_dataset)


@pytest.fixture(scope="session")
def hf_api_key():
    yield os.getenv("HF_API_KEY", "")


@pytest.fixture(scope="session")
def gdf_json():
    yield os.getenv("GDF_ACCOUNT_JSON")


@pytest.fixture(scope="session")
def hf_model_name():
    yield "obsei-ai/sell-buy-intent-classifier-bert-mini"


@pytest.fixture(scope="session")
def rasa_url():
    yield os.getenv("RASA_URL") or ""


@pytest.fixture(scope="session")
def rasa_api_key():
    yield os.getenv("RASA_API_KEY") or ""


@pytest.fixture(scope="session")
def save_file(tmpdir_factory):
    file_name = tmpdir_factory.mktemp("testdir").join("testfile")
    return str(file_name)
