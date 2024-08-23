# flexiai/tests/test_assistant_youtube_search.py
import pytest
import subprocess
from user_flexiai_rag.user_functions_manager import FunctionsManager

@pytest.fixture
def task_manager():
    return FunctionsManager()

def test_search_youtube_with_valid_query(task_manager, mocker):
    mock_subprocess_run = mocker.patch('subprocess.run')
    query = "Python tutorials"
    result = task_manager.search_youtube(query)
    print("test_search_youtube_with_valid_query result:", result)
    assert result['status'] == True
    assert result['result'] == "https://www.youtube.com/results?search_query=Python%2Btutorials"
    assert result['message'] == "YouTube search page opened successfully."
    mock_subprocess_run.assert_called_once()

def test_search_youtube_with_empty_query(task_manager):
    query = ""
    result = task_manager.search_youtube(query)
    print("test_search_youtube_with_empty_query result:", result)
    assert result['status'] == False
    assert result['result'] is None
    assert result['message'] == "Query cannot be empty."

def test_search_youtube_with_subprocess_error(task_manager, mocker):
    mock_subprocess_run = mocker.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'cmd'))
    query = "Python tutorials"
    result = task_manager.search_youtube(query)
    print("test_search_youtube_with_subprocess_error result:", result)
    assert result['status'] == False
    assert result['result'] is None
    assert "Subprocess error" in result['message']
    mock_subprocess_run.assert_called_once()

def test_search_youtube_with_exception(task_manager, mocker):
    mock_subprocess_run = mocker.patch('subprocess.run', side_effect=Exception("Unexpected error"))
    query = "Python tutorials"
    result = task_manager.search_youtube(query)
    print("test_search_youtube_with_exception result:", result)
    assert result['status'] == False
    assert result['result'] is None
    assert "Failed to open YouTube search for query" in result['message']
    mock_subprocess_run.assert_called_once()

if __name__ == "__main__":
    pytest.main()
