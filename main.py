import fitz
import json
import re
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from PIL import Image

#get file path of document
Tk().withdraw()
file_path = askopenfilename()

#open the document with pymupdf
document = fitz.Document(file_path)

#extract text from the first page of the document
text = ""
for page in document:
    text = text + page.get_text("text", None, 1, None, False)

#function for using regular expression to search the text that was extracted from the document.
def search_text(pattern: str, text: str):
    match = re.search(pattern, text)
    if match is None:
        return ""
    else:
        #does some formatting to remove double spaces and any \n characters, also removes leading/trailing whitespace
        return match.group(2).strip().replace("  ", " ").replace("\n", " ")

#function for extracting and saving an image
def save_image(page: int, img_number: int, name: str):
    xref = document.get_page_images(page)[img_number][0]
    image = document.extract_image(xref)
    imgout = open(f"output/{name}.{image['ext']}", "wb")
    imgout.write(image["image"])
    imgout.close()
    return image

# If the text includes T-score the pdf is DXA scan result page 1
if text.find("T-score") != -1:
    #template file with regular expression strings
    with open("DXABMD.json") as template:
        input = json.load(template)
    template.close()

    save_image(0, 0, "BMDTScoreGraph")

    image = save_image(0, 1, "BMDScan")
    #Resize BMDScan image because it is distorted
    img = Image.open(f"output/BMDScan.{image['ext']}")
    img = img.resize((140, 318))
    img.save(f"output/BMDScan.{image['ext']}")
    img.close()

    document.close()

# If the text includes Body Composition then the pdf is DXA scan result page 2
elif text.find("Body Composition Results") != -1:
    with open('DXABodyComp.json') as template:
        input = json.load(template)
    template.close()

    save_image(0, 0, "TotalBodyPercentFatGraph")

    #Resize BodyComp images because they are distorted
    image = save_image(0, 1, "BodyCompColor")
    img = Image.open(f"output/BodyCompColor.{image['ext']}")
    img = img.resize((140, 318))
    img.save(f"output/BodyCompColor.{image['ext']}")
    img.close()

    image = save_image(0, 2, "BodyCompBW")
    img = Image.open(f"output/BodyCompBW.{image['ext']}")
    img = img.resize((140, 318))
    img.save(f"output/BodyCompBW.{image['ext']}")
    img.close()

    document.close()

elif text.find("DXA Results Summary:") != -1:
    with open("DXABodyTable.json") as template:
        input = json.load(template)
    template.close()

elif text.find("SUCCESS HUB") != -1:
    with open("Fit3d.json") as template:
        input = json.load(template)
    template.close()

    save_image(0, 0, "FrontBody")
    save_image(0, 1, "SideFrontBody")
    save_image(0, 2, "BackBody")
    save_image(0, 3, "SideBody")

    save_image(3, 0, "FrontPosture")
    save_image(3, 1, "SidePosture")

    document.close()

# If none of the previous if statements were true then the pdf is one that I haven't added code for yet.
else:
    print("not a valid pdf file.")
    exit()

#go through template and copy all values from <regular expression string> to search_text(<regular expression string>) in output.
output = {}
for i in input:
    output[i] = search_text(input[i], text)

#export output to json file.
with open ("output/output.json", "w") as outfile:
    json.dump(output, outfile)
outfile.close()