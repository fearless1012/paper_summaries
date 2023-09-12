import PyPDF2
import os



from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

import re
import pandas as pd


import openai
from transformers import pipeline

import time

start = time.time()


# Import the necessary dependencies: PyPDF2 for PDF processing and OpenAI for interfacing with GPT-3.5-turbo.

pdf_summary_text = ""

# Initialize an empty string to store the summarized text.

pdf_file_path = "./temp_dir/"

summarizer = pipeline("summarization", model="t5-base", tokenizer="t5-base", framework="tf")

# Open the PDF file and create a PyPDF2 reader object.

paper_summaries = pd.DataFrame(columns=['FileName', 'Abstract', 'Introduction', 'Conclusion'])

for filename in os.listdir(pdf_file_path):
    print(filename)
    file_path = os.path.join(pdf_file_path, filename)
    if os.path.isfile(file_path):
        fp = open(file_path, 'rb')
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()
        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable=True):
            interpreter.process_page(page)
        pdf_text = retstr.getvalue()
        fp.close()

        pdf_text = str(pdf_text)

        pdf_text = pdf_text.replace(",", " ")
        pdf_text = pdf_text.replace("\n", " ")
        pdf_text = pdf_text.replace("'", " ")
        pdf_text = pdf_text.replace('"', " ")
        pdf_text = pdf_text.replace(".  ", ".")
        pdf_text = pdf_text.replace(". ", ".")
        try:
            abstract_text = re.search(r'.abstract(.*?).introduction', pdf_text.lower(), re.DOTALL).group(1)
        except:
            abstract_text = ""
            print("No abstract")

        try:
            introduction_text = re.search('.introduction(.*?)2.', pdf_text.lower(), re.DOTALL).group(1)
        except:
            print("No introduction")
            introduction_text = ""

        try:
            conclusions_text = re.search('.conclusions(.*?).references', pdf_text.lower(), re.DOTALL).group(1)
        except:
            print("No conclusion")
            conclusions_text = ""

        if len(abstract_text) > 5000:
            abstract_text = abstract_text[0: 5000]
        abstract = summarizer(abstract_text, max_length=1000, min_length=30, do_sample=False)[0]['summary_text']
        if len(introduction_text) > 5000:
            introduction_text = introduction_text[0: 5000]
        introduction = summarizer(introduction_text, max_length=1000, min_length=30, do_sample=False)[0]['summary_text']
        if len(conclusions_text) > 5000:
            conclusions_text = conclusions_text[0: 5000]
        conclusions = summarizer(conclusions_text, max_length=1000, min_length=30, do_sample=False)[0]['summary_text']
        print(time.time() - start)
        start = time.time()

        # new_row = {'FileName': filename, 'Abstract': abstract}
        new_row = {'FileName' : filename, 'Abstract' : abstract, 'Introduction':introduction, 'Conclusion': conclusions}

        paper_summaries = pd.concat([paper_summaries, pd.DataFrame([new_row])], ignore_index=True)

        # print(paper_summaries['Conclusion'])


        # for i in range(0, len(pdf_text)):
        #     text = pdf_text[i : i+10000]
        #     summary = summarizer(text, max_length=1000, min_length=30, do_sample=False)[0]['summary_text']
        #     print(summary)
        #     i = i +10000




paper_summaries.to_csv("paper_summaries.csv", escapechar ="\\")
device.close()
retstr.close()
print(time.time() - start)








    # Loop through all the pages in the PDF file, extracting the text from each page.

    # for page_num in range(pdf_reader.numPages):
    #     page_obj = pdf_reader.getPage(page_num)
    #     pdf_summary_text += page_obj.extractText()
    #
    # # Use GPT-3.5-turbo to generate a summary for each page’s text.
    #
    # openai.api_key = "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"
    # model_engine = "text-davinci-002"
    # prompt_text = f"Please summarize this text: {pdf_summary_text}"
    # completions = openai.Completion.create(engine=model_engine, prompt=prompt_text, max_tokens=1024)
    # message = completions.choices[0].text.strip()
    #
    # print(message)
    #
    #
    # input("yaya")