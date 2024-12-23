import pytest
import warnings
import io
from src.utils.assignment0 import loadpdf, extract

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Mocking URL and File for Tests
INVALID_PDF_URL = "https://www.normanok.gov/sites/default/files/documents/2024-12/2024-12-11_daily_summary.pdf"

@pytest.fixture
def VALID_PDF_URL():
    """Fixture for providing a valid PDF URL."""
    return "test.pdf"


def test_invalid(mocker):
    """Test loading a PDF from an invalid URL."""
    mocker.patch("urllib.request.urlopen", side_effect=Exception("Invalid URL"))

    pdf_data = loadpdf(INVALID_PDF_URL)
    assert pdf_data is None, "Invalid URL should return None."


def test_extract():
    """Test extracting incidents from a real PDF file."""
    VALID_PDF_PATH = "test.pdf" 

    try:
        with open(VALID_PDF_PATH, "rb") as pdf_file:
            pdf_data = io.BytesIO(pdf_file.read())
    except FileNotFoundError:
        pytest.fail(f"Test file not found: {VALID_PDF_PATH}")

    extracted_data = extract(pdf_data)

    assert not extracted_data.empty, "No data was extracted from the PDF."
