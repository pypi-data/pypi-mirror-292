import asyncio
import re
from individual.api.google_api import get_book_data_google
from individual.api.sru_api import get_book_data_sru
from individual.api.opendb_api import get_book_data_opendb
from individual.api.opensearch_api import get_book_data_opensearch
from individual.api.rakuten_api import fetch_rakuten_kari

# priceから数字を抽出する関数
def extract_numbers(text):
  return re.findall(r"\d+", text)


# 08/04
# 実行部分の関数
async def jikkou_kari(isbn, rakuten_id):
    rakuten_fetched = fetch_rakuten_kari(isbn, rakuten_id)
    google_fetched = get_book_data_google(isbn)
    sru_fetched = get_book_data_sru(isbn)
    opendb_fetched = get_book_data_opendb(isbn)
    opensearch_fetched = get_book_data_opensearch(isbn)

    results = await asyncio.gather(
      rakuten_fetched,
      google_fetched, 
      sru_fetched, 
      opendb_fetched, 
      opensearch_fetched
    )

    # rakuten_fetched_data, google_fetched_data, sru_fetched_data, opendb_fetched_data, opensearch_fetched_data = results
    rakuten_fetch, google_fetch, sru_fetch, opendb_fetch, opensearch_fetch = results

    print(f"rakuten_fetch: {rakuten_fetch}, google_fetch: {google_fetch}, sru_fetch: {sru_fetch}, opendb: {opendb_fetch}, opensearch: {opensearch_fetch}")

    # 試し用
    isbn = isbn
    #caption
    print("google_data", type(google_fetch['google_data']))
    print("rakuten_api_library", type(rakuten_fetch['rakuten_api_library']))
    caption = ""
    if google_fetch['google_data'] == True and google_fetch['description'] != "":
      caption = google_fetch['description']
    if rakuten_fetch['rakuten_api_library'] == True and rakuten_fetch['itemCaption'] != "":
      caption = rakuten_fetch['itemCaption']


    # publishedDate
    publishedDate = ""
    if opendb_fetch['opendb_data'] == True and opendb_fetch['sales_date'] != "":
      publishedDate = opendb_fetch['sales_date']
    if opensearch_fetch['opensearch_data'] == True and opensearch_fetch['sales_date'] != "":
      publishedDate = opensearch_fetch['sales_date']
    if sru_fetch['sru_data'] == True and sru_fetch['sales_date'] != "":
      publishedDate = sru_fetch['sales_date']
    if google_fetch['google_data'] == True and google_fetch['publishedDate'] != "":
      publishedDate = google_fetch['publishedDate']
    if rakuten_fetch['rakuten_api_library'] == True and rakuten_fetch['salesDate'] != "":
      publishedDate = rakuten_fetch['salesDate']

    
    # publisher
    publisher = ""
    if opensearch_fetch['opensearch_data'] == True and opensearch_fetch['publisher'] != "":
      publisher = opensearch_fetch['publisher']
    if opendb_fetch['opendb_data'] == True and opendb_fetch['publisher'] != "":
      publisher = opendb_fetch['publisher']
    if sru_fetch['sru_data'] == True and sru_fetch['publisher'] != "":
      publisher = sru_fetch['publisher']
    if rakuten_fetch['rakuten_api_library'] == True and rakuten_fetch['publisherName'] != "":
      publisher = rakuten_fetch['publisherName']


    # price
    price = "0"
    if rakuten_fetch['rakuten_api_library'] == True and rakuten_fetch['itemPrice'] != 0 and rakuten_fetch['itemPrice'] != "" and rakuten_fetch['itemPrice'] != None:
      price = rakuten_fetch['itemPrice']
    if opendb_fetch['opendb_data'] == True and opendb_fetch['price'] != "" and opendb_fetch['price'] != 0:
      price = opendb_fetch['price']
    if opensearch_fetch['opensearch_data'] == True and opensearch_fetch['price'] != "" and opensearch_fetch['price'] != 0:
      price = opensearch_fetch['price']
    if sru_fetch['sru_data'] == True and sru_fetch['price'] != "" and sru_fetch['price'] != 0:
      price = sru_fetch['price']

    extracted_price = extract_numbers(str(price))

    # page_count
    page_count = ""
    if google_fetch['google_data'] == True and google_fetch['page_count'] != "" and google_fetch['page_count'] != 0:
      page_count = google_fetch['page_count']
    if opendb_fetch['opendb_data'] == True and opendb_fetch['page_count'] != "" and opendb_fetch['page_count'] != 0:
      page_count = opendb_fetch['page_count']
    if sru_fetch['sru_data'] == True and sru_fetch['page_count'] != "" and sru_fetch['page_count'] != 0:
      page_count = sru_fetch['page_count']
    if opensearch_fetch['opensearch_data'] == True and opensearch_fetch['page_count'] and opensearch_fetch['page_count'] != 0:
      page_count = opensearch_fetch['page_count']
      
    

    # 追加部分
    # title
    title = ""
    if google_fetch['google_data'] == True and google_fetch['title'] != "" and google_fetch['title'] != 0:
      title = google_fetch['title']
    if opendb_fetch['opendb_data'] == True and opendb_fetch['title'] != "" and opendb_fetch['title'] != 0:
      title = opendb_fetch['title']
    if sru_fetch['sru_data'] == True and sru_fetch['title'] != "" and sru_fetch['title'] != 0:
      title = sru_fetch['title']
    if opensearch_fetch['opensearch_data'] == True and opensearch_fetch['title'] and opensearch_fetch['title'] != 0:
      title = opensearch_fetch['title']
    if rakuten_fetch['rakuten_api_library'] == True and rakuten_fetch['title'] and rakuten_fetch['title'] != 0:
      title = rakuten_fetch['title']


    # author
    author = ""
    if rakuten_fetch['rakuten_api_library'] == True and rakuten_fetch['author'] and rakuten_fetch['author'] != 0:
      author = rakuten_fetch['author']
    # if opendb_fetch['opendb_data'] == True and opendb_fetch['author'] != "" and opendb_fetch['author'] != 0:
    #   author = opendb_fetch['author']
    if sru_fetch['sru_data'] == True and sru_fetch['author'] != "" and sru_fetch['author'] != 0:
      author = sru_fetch['author']
    if opensearch_fetch['opensearch_data'] == True and opensearch_fetch['author'] and opensearch_fetch['author'] != 0:
      author = opensearch_fetch['author']
    if google_fetch['google_data'] == True and google_fetch['author'] != "" and google_fetch['author'] != 0:
      author = google_fetch['author']


    # 文庫本か単行本かを見分ける　2024/08/09　5:02
    # book_type
    book_type = ""
    if opensearch_fetch['opensearch_data'] == True and opensearch_fetch['book_type'] != "":
      book_type = opensearch_fetch['book_type']
    if opendb_fetch['opendb_data'] == True and opendb_fetch['book_type'] != "":
      book_type = opendb_fetch['book_type']
    if sru_fetch['sru_data'] == True and sru_fetch['book_type'] != "":
      book_type = sru_fetch['book_type']
    if rakuten_fetch['rakuten_api_library'] == True and rakuten_fetch['size'] != "":
      book_type = rakuten_fetch['size']


    # 画像を取得する
    # image
    if google_fetch['google_data'] == True and google_fetch['image'] != "" and google_fetch['image'] != 0:
      image = google_fetch['image']
    # 楽天には「largeImageUrl」、「mediumImageUrl」、「smallImageUrl」がある。
    if rakuten_fetch['rakuten_api_library'] == True and rakuten_fetch['mediumImageUrl'] != "":
      image = rakuten_fetch['mediumImageUrl']

    if rakuten_fetch['rakuten_api_library'] == True and rakuten_fetch['smallImageUrl'] != "":
      smallImage = rakuten_fetch['smallImageUrl']

    if rakuten_fetch['rakuten_api_library'] == True and rakuten_fetch['largeImageUrl'] != "":
      largeImage = rakuten_fetch['largeImageUrl']

    return {
        # 文庫本か単行本かを見分ける　2024/08/09　5:03
        "booktype": book_type,

        # 追加部分
        "title": title,
        "author": author,

        "image": image,
        "largeImage": largeImage,
        "smallImage": smallImage,


        "isbn": isbn,
        "caption": caption,
        "publishedDate": publishedDate,
        "publisher": publisher,
        "price": int(extracted_price[0]),
        "count": page_count,
    }