from PyPDF2 import PdfReader
import os

class PDFManager:
    def __init__(self):
        self.current_pdf = None
        self.reader = None

    def read_pdf(self, file_path, page_number=None):
        """
        Read a PDF file and return its content.
        If page_number is specified, read only that page.
        """
        try:
            # Always create a new reader instance for reliability
            self.reader = PdfReader(file_path)
            self.current_pdf = file_path
            
            if not self.reader.pages:
                return False, "PDF has no pages or is corrupted"
                
            total_pages = len(self.reader.pages)
            
            if page_number is not None:
                # Adjust page number to 0-based index
                page_idx = page_number - 1
                if page_idx < 0 or page_idx >= total_pages:
                    return False, f"Error: Page {page_number} does not exist. PDF has {total_pages} pages."
                
                # Extract text from the specific page
                page = self.reader.pages[page_idx]
                text = page.extract_text()
                if not text or not text.strip():
                    return False, f"Page {page_number} appears to be empty or unreadable"
                return True, text.strip()
            
            else:
                # Read all pages
                text = ""
                for i, page in enumerate(self.reader.pages):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text += f"\n--- Page {i+1} ---\n{page_text.strip()}\n"
                
                if not text.strip():
                    return False, "No readable content found in the PDF"
                return True, text
                
        except Exception as e:
            self.reader = None
            self.current_pdf = None
            return False, f"Error reading PDF: {str(e)}"

    def get_total_pages(self):
        """
        Get the total number of pages in the currently opened PDF.
        """
        try:
            if self.reader and self.reader.pages:
                return len(self.reader.pages)
        except Exception:
            pass
        return 0

    def close_pdf(self):
        """
        Close the current PDF file.
        """
        try:
            self.reader = None
            self.current_pdf = None
            return True, "PDF closed successfully"
        except Exception as e:
            return False, f"Error closing PDF: {str(e)}"

    def validate_file_path(self, file_path):
        """
        Validate if the given file path exists and is a PDF.
        """
        if not os.path.exists(file_path):
            return False, "File not found"
        if not file_path.lower().endswith('.pdf'):
            return False, "File is not a PDF"
        return True, "File path is valid" 