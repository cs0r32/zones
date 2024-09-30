import boto3
import json
import os
from botocore.exceptions import ClientError
from trp.trp2 import TDocument, TDocumentSchema,TextractBlockTypes
from trp.t_pipeline import order_blocks_by_geo
import textractcaller as tc
import trp
import json

# define textract and comprehend client
textract = boto3.client("textract", region_name='us-east-1')
#bucket_name = "genai-poc-bucket"
#bucket_name_output = "bucket-name-output"

def get_parents(blocks, id):
    #print(blocks)
    parent_ids=[]
    #print(id)
    for block in blocks:
        if block["BlockType"] in ["LINE","CELL"]:
            #print(block["BlockType"])
            children = block["Relationships"]
            #print(children)
            if id in children[0]["Ids"]:
                parent_ids.append(block["Id"])

    return parent_ids


# define function that uses textract to extract text from a document
def extract_text(bucket_name, document_name, transpose_table=True):
    # define the document
    input_document = "s3://{}/{}".format(bucket_name, document_name)
    q1 = tc.Query(text="What is the title for the document", alias="title", pages=["1"])
    q2 = tc.Query(text="What are the section headings in the document", alias="section", pages=["1"])
    
    #document = {"S3Object": {"Bucket": bucket_name, "Name": document_name}}
    # extract the text
    #response = textract.analyze_document(Document=document, FeatureTypes=["TABLES"])
    #print(response)
    markdown_content = []
    response = tc.call_textract(
        input_document=input_document,
        queries_config=tc.QueriesConfig(queries=[q1, q2]),
        features=[tc.Textract_Features.TABLES,tc.Textract_Features.QUERIES],
        boto3_textract_client=textract)
    t_doc = TDocumentSchema().load(response)
    title = ""
    section_headings = ""
    ordered_doc = order_blocks_by_geo(t_doc)
    page = ordered_doc.get_blocks_by_type(TextractBlockTypes.PAGE)[0]
    # the ordered_doc has elements ordered by y-coordinate (top to bottom of page)
    query_answers = ordered_doc.get_query_answers(page=page)
    for x in query_answers:
        if x[1] == "title":
            title = x[2]
        elif x[1] == "section":
            section_headings=x[2].split(",")
    section_headings = [str.strip(' ')  for str in section_headings]
    doc = trp.Document(TDocumentSchema().dump(ordered_doc))
    blocks = TDocumentSchema().dump(ordered_doc)["Blocks"]
    for block in blocks:
       if block["BlockType"] in ["TABLE"]:
        table = doc.pages[0].tables[0]
        row_count = len(table.rows)
        column_count = len(table.rows[0].cells)
        print(row_count,column_count)
        col_data =[]
        if transpose_table:
            for col in range(0, column_count):
                row_data=[]
                for rows in range(0,row_count):
                    if rows == 0:
                        content = {"Type": "Header" ,"Text":table.rows[rows].cells[col].text }
                    else:
                        content = {"Type": "Table_data","Text":table.rows[rows].cells[col].text }
                    row_data.append(content)
                
                col_data.append(row_data)
            content = {"Type": "Table" , "Text":col_data }
            markdown_content.append(content)
        else:
            for rows in range(0, row_count):
                row_data=[]
                for col in range(0,column_count):
                    if col == 0:
                        content = {"Type": "Header" , "Text":table.rows[rows].cells[col].text }
                    else:
                        content = {"Type": "Table_data", "Text":table.rows[rows].cells[col].text }
                    row_data.append(content)
                
                col_data.append(row_data)
            content = {"Type": "Table" , "Text":col_data }
            markdown_content.append(content)

       if block["BlockType"] in ["LINE"]:
            id = block["Id"]
            child_id = ordered_doc.get_block_by_id(id).relationships[0].ids[0]
            parent_ids = get_parents(blocks,child_id)
            #print(parent_ids)
            if(len(parent_ids) == 1):
                text = block['Text']
                print(text)
                if text == title:
                    content = {"Type": "Title" , "Text":text }
                elif  text in section_headings:
                    content = {"Type": "Section" , "Text":text }
                else:
                    content = {"Type": "Normal" , "Text":text }
                markdown_content.append(content)
    return markdown_content
    
        


# define the document
# document_name = "IDC PeerScape.png"
# # extract the text
# response = extract_text(bucket_name, document_name)
# print(json.dumps(response))
    
