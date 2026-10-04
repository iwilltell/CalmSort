from app.core.classification import (
    CATEGORIES,
    EXTENSION_CATEGORIES,
    KEYWORD_CATEGORIES,
)


def test_categories_exist():
    assert "College" in CATEGORIES
    assert "Work" in CATEGORIES
    assert "Personal" in CATEGORIES
    assert "Documents" in CATEGORIES
    assert "Images" in CATEGORIES
    assert "Videos" in CATEGORIES
    assert "Music" in CATEGORIES
    assert "Archives" in CATEGORIES


def test_document_extensions():
    assert ".pdf" in EXTENSION_CATEGORIES["Documents"]
    assert ".docx" in EXTENSION_CATEGORIES["Documents"]


def test_image_extensions():
    assert ".jpg" in EXTENSION_CATEGORIES["Images"]
    assert ".png" in EXTENSION_CATEGORIES["Images"]


def test_college_keywords():
    assert "assignment" in KEYWORD_CATEGORIES["College"]
    assert "dbms" in KEYWORD_CATEGORIES["College"]


def test_work_keywords():
    assert "invoice" in KEYWORD_CATEGORIES["Work"]
    assert "client" in KEYWORD_CATEGORIES["Work"]


def test_personal_keywords():
    assert "travel" in KEYWORD_CATEGORIES["Personal"]
    assert "passport" in KEYWORD_CATEGORIES["Personal"]