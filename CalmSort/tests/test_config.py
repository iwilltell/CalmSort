from app.core.config import CONFIG


def test_default_confidence_threshold() -> None:
    assert CONFIG.confidence_threshold == 0.70


def test_database_path_is_inside_data_directory() -> None:
    assert CONFIG.database_path.name == "calmsort.db"
    assert CONFIG.database_path.parent == CONFIG.data_dir
