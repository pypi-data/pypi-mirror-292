# OpenDBからデータを取得
import requests

async def get_book_data_opendb(isbn):
    url_opendb = f"https://api.openbd.jp/v1/get?isbn={isbn}&pretty" #OpenDBAPI
    response_opendb = requests.get(url_opendb).json() #情報の取得,json変換

    total_items = response_opendb[0]
    if total_items == None:
        print("Book not found in OpenDB.")
        opendb_fetch = False
        return {
            "opendb_data": False
        }

    # 追加部分
    title = response_opendb[0]['summary']['title']


    publisher = response_opendb[0]['summary']['publisher']
    date = response_opendb[0]['summary']['pubdate']
    if 'ProductSupply' in response_opendb[0]['onix']:
      price = response_opendb[0]['onix']['ProductSupply']['SupplyDetail']['Price'][0]['PriceAmount']
    else:
      price = ""
    opendb_fetch = True


    # 文庫本か単行本かを見分ける　2024/08/09　4:25
    if response_opendb[0]['summary']['series'] == "":
        book_type = "単行本"
    else:
        book_type = "文庫"

    return {
        # 文庫本か単行本かを見分ける　2024/08/09　4:28
        "book_type": book_type,

        # 追加部分
        "title": title,


        "opendb_data": True,
        "publisher": publisher,
        "sales_date": date,
        "price": price,
        "page_count": "",
    }
