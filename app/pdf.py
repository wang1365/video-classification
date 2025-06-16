import pdfplumber
from pypdf import DocumentInformation


def extract(pdf_path):
    from pypdf import PdfReader

    reader = PdfReader(pdf_path)

    for page in reader.pages:
        if "/Annots" in page:
            for annotation in page["/Annots"]:
                obj = annotation.get_object()
                print({"subtype": obj["/Subtype"], "location": obj["/Rect"]})

if __name__ == '__main__':
    extract(r'C:\Users\86180\Downloads\Aeons Shoot 30-05_ All Scripts-Direction.pdf')