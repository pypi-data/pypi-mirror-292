from typing import List, Tuple
import os
import fitz
import logging

logger = logging.getLogger(__name__)


class PdfHighlightExtractor:
    def _parse_highlight(
        self,
        annot: fitz.Annot,
        wordlist: List[Tuple[float, float, float, float, str, int, int, int]],
    ) -> str:
        points = annot.vertices
        quad_count = int(len(points) / 4)
        sentences = []
        for i in range(quad_count):
            # where the highlighted part is
            r = fitz.Quad(points[i * 4 : i * 4 + 4]).rect

            words = [w for w in wordlist if fitz.Rect(w[:4]).intersects(r)]
            sentences.append(" ".join(w[4] for w in words))
        sentence = " ".join(sentences)
        return sentence

    def handle_page(self, page):
        wordlist = page.get_text("words")  # list of words on page
        wordlist.sort(key=lambda w: (w[3], w[0]))  # ascending y, then x

        highlights = []
        annot = page.first_annot
        while annot:
            if annot.type[0] == 8:
                highlights.append(self._parse_highlight(annot, wordlist))
            annot = annot.next
        return highlights

    def read_one_file(self, filepath: str) -> List:
        doc = fitz.open(filepath)

        highlights = []
        for page in doc:
            highlights += self.handle_page(page)

        return highlights

    def read_directory(self, path_to_directory: str) -> List[str]:
        """
        Reads all PDF files in a directory (including subdirectories) and extracts highlights.

        Args:
            path_to_directory: The path to the directory to read.

        Returns:
            A list of all extracted highlights from all PDF files in the directory.
        """
        for root, _, files in os.walk(path_to_directory):
            for file in files:
                highlights = []
                logger.info(f"Processing {file}")
                if file.endswith(".pdf"):
                    filepath = os.path.join(root, file)
                    highlights += self.read_one_file(filepath)
                    self.serialize_highlights_per_file(highlights, root, filepath)

    def serialize_highlights_per_file(
        self, highlights: List[str], root: str, filepath: str
    ):
        base_path = os.path.join(root, f"highlights/")
        fid = os.path.join(
            base_path, f'{os.path.basename(filepath).split(".pdf")[0]}.md'
        )
        if not os.path.exists(base_path):
            os.mkdir(base_path)
        with open(fid, "w+") as f:
            f.write("\n".join(highlights))


def main(input_dir: str):
    hex = PdfHighlightExtractor()
    hex.read_directory(input_dir)


if __name__ == "__main__":
    main("Pose/")
