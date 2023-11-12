from io import BytesIO
from fastapi import FastAPI
import requests as r
from utils import endpoints as end

from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
import xml.etree.ElementTree as ET
import csv
import pandas as pd
from datetime import datetime
from typing import Optional

# Initialize FastAPI
app = FastAPI()

# Scraper Methods
def get_politics_news(keyword=[], count=50):
  filtered = []
  if len(keyword) > 1:
      q = " OR ".join(keyword)
  q = keyword[0]
  response = r.get(f"https://newsapi.org/v2/everything?q={q}&apiKey=a0af95bb906b4db49e6e028589158730")

  for n in response.json()["articles"]:
        payload = {
          "tanggal" : n["publishedAt"].split("T")[0],
          "judul": n["title"],
          "isi_berita": n["content"],
        }
        filtered.append(payload)
  return filtered[:count]

# Function to generate JSON, XML, CSV, and XLSX responses
def generate_responses(news_data, file_format):
    if file_format == "json":
        return JSONResponse(content=news_data)
            
    elif file_format == "xml":
        root = ET.Element("news_data")
        for news in news_data:
            news_element = ET.SubElement(root, "news")
            for key, value in news.items():
                ET.SubElement(news_element, key).text = str(value)
        
        tree = ET.ElementTree(root)
        xml_string = ET.tostring(root, encoding="utf-8").decode("utf-8")
        return PlainTextResponse(content=xml_string, media_type="application/xml")
        
    elif file_format == "csv":
        csv_string = pd.DataFrame(news_data).to_csv(index=False)
        return PlainTextResponse(content=csv_string, media_type="text/csv")
            
    elif file_format == "xlsx":
        buffer = BytesIO()
        with pd.ExcelWriter(buffer) as writer:
            pd.DataFrame(news_data).to_excel(writer, index=False)
        return StreamingResponse(
            BytesIO(buffer.getvalue()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f"attachment; filename=news.csv"}
        )

@app.get("/news/{file_format}")
def get_news_data(file_format: str, q: Optional[str] = None):
    # Specify the keyword
    # Assume the parameter is Gibran%20Rakabuming
    if q:
        keyword = q.split("%20")
    else:
        keyword = ["gibran", "rakabuming"]

    # Fetch news data for each endpoint and category
    news_data = get_politics_news(keyword=keyword, count=50)

    # Generate responses in different formats
    response = generate_responses(news_data, file_format)
    return response

