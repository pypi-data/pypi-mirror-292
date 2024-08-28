import glob
import os
import re
from typing import Any, Iterator

from langchain.document_loaders.base import BaseLoader
from langchain.schema import Document
from langchain_core.documents import Document
from pdf2image import convert_from_path
from tqdm import tqdm


class PDFParser(BaseLoader):
    """
    Class to parse and convert PDF files to images

    This class converts a PDF file to images, parses each page, and returns it as a Document object.
    """

    def __init__(
        self,
        file_path: str,
        multimodal,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Constructor for the PDFParser class

        :param file_path: PDF file path
        """
        super().__init__(*args, **kwargs)
        self.file_path = file_path
        self.parsing_llm = multimodal
        self.convert_pdf_to_images()

    def convert_pdf_to_images(self):
        """Convert PDF files to images and save them to a cache directory."""
        # Create a .pdf_cache folder
        cache_dir = ".pdf_cache"
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        # Get PDF file names and use them as folder names
        pdf_name = os.path.splitext(os.path.basename(self.file_path))[0]
        self.metadata = {"source": pdf_name}
        # Directory to store the images (.pdf_cache/pdf_name)
        self.output_dir = os.path.join(cache_dir, pdf_name)

        # If the output directory does not exist, click Create
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Convert PDFs to images
        images = convert_from_path(self.file_path)

        # Track the number of images converted
        converted_count = 0

        # Use TQDM to show progress
        for i, image in tqdm(
            enumerate(images), total=len(images), desc="Converting a page"
        ):
            image_path = os.path.join(self.output_dir, f"page_{i}.png")

            # Check if the image already exists
            if not os.path.exists(image_path):
                image.save(image_path, "PNG")
                converted_count += 1

        print(f"\n[Converted] Total Count: {len(images)} Pages.")
        self.total_pages = len(images)

    def get_image_path(self, page_number: int) -> str:
        """
        Returns the path to the image file corresponding to the given page number.

        :param page_number: page number
        :return: path to the image file
        """
        return os.path.join(self.output_dir, f"page_{page_number}.png")

    def parse_pdf_by_page(self, page_number: int) -> Document:
        """
        Parses a PDF page with the given page number and returns it as a Document object.

        :param page_number: page number to parse
        :return: Document object containing the parsed content
        """
        metadata = self.metadata.copy()
        metadata["page_number"] = page_number
        return Document(
            page_content=self.parsing_llm.invoke(
                self.get_image_path(page_number), display_image=False
            ),
            metadata=metadata,
        )

    def parse_pdf(self, image_path: str) -> Document:
        return self.parsing_llm.invoke(image_path, display_image=False)

    def lazy_load(self) -> Iterator[Document]:
        """
        Lazily loads and parses each page of the PDF to create a Document object.
        If an already parsed .md file exists, fetch the contents from it.

        :return: an iterator on the Document object
        """
        # Create a .pdf_cache_output folder
        output_dir = ".pdf_cache_output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Get PDF file names and use them as folder names
        pdf_name = os.path.splitext(os.path.basename(self.file_path))[0]
        pdf_output_dir = os.path.join(output_dir, pdf_name)

        # Create a PDF output directory if it doesn't exist
        if not os.path.exists(pdf_output_dir):
            os.makedirs(pdf_output_dir)

        files = sorted(glob.glob(self.output_dir + "/*.png"))

        for file in tqdm(files, total=len(files), desc="Processing PDF"):
            # Extract page numbers from file names
            page_number = int(re.search(r"page_(\d+)", os.path.basename(file)).group(1))

            md_filename = os.path.splitext(os.path.basename(file))[0] + ".md"
            md_filepath = os.path.join(pdf_output_dir, md_filename)
            metadata = self.metadata.copy() if hasattr(self, "metadata") else {}
            metadata["page"] = page_number

            if os.path.exists(md_filepath):
                # Reads the contents of the .md file if it already exists
                with open(md_filepath, "r", encoding="utf-8") as md_file:
                    content = md_file.read()
                yield Document(page_content=content, metadata=metadata)
            else:
                # If there is no .md file, parse the page and save the result
                parsed_document = self.parse_pdf(file)

                with open(md_filepath, "w", encoding="utf-8") as md_file:
                    md_file.write(parsed_document)

                yield Document(page_content=parsed_document, metadata=metadata)
