# OpenSearchからデータを取得
import xmltodict
import requests

async def convert_xml_to_json(xml_str):
    try:
        dict = xmltodict.parse(xml_str)
        return dict  # 直接ディクショナリを返す
    except Exception as e:
        print("XMLの解析エラー", e)
        return None


async def get_book_data_opensearch(isbn):
    url_opensearch = f"https://ndlsearch.ndl.go.jp/api/opensearch?isbn={isbn}"
    response_opensearch = requests.get(url_opensearch)
    response_opensearch.encoding = 'utf-8'
    parsed_data_opensearch = await convert_xml_to_json(response_opensearch.text)


    if parsed_data_opensearch:
        try:
            rss = parsed_data_opensearch['rss']
            channel = rss['channel']
            item = channel['item']
            item_length = len(item)

            if item_length == 2:
              # 追加部分
              title = parsed_data_opensearch['rss']['channel']['item'][item_length - 1]['dc:title']
              author = parsed_data_opensearch['rss']['channel']['item'][item_length - 1]['dc:creator']

              publisher = parsed_data_opensearch['rss']['channel']['item'][item_length - 1]['dc:publisher']
              price = parsed_data_opensearch['rss']['channel']['item'][item_length - 1]['dcndl:price']
              page_count = parsed_data_opensearch['rss']['channel']['item'][item_length - 1]['dc:extent']
              if 'dcterms:issued' in parsed_data_opensearch['rss']['channel']['item'][item_length - 1]:
                date = parsed_data_opensearch['rss']['channel']['item'][item_length - 1]['dcterms:issued']
              else:
                date = parsed_data_opensearch['rss']['channel']['item'][item_length - 1]['dc:description']

              # 文庫本か単行本かを見分ける　2024/08/09　4:18
              if "dcndl:seriesTitle" in parsed_data_opensearch['rss']['channel']['item'][item_length - 1]:
                book_type = "文庫"
              else:
                book_type = "単行本"

            elif item_length > 10:
              # 追加部分
              title = parsed_data_opensearch['rss']['channel']['item']['dc:title']
              author = parsed_data_opensearch['rss']['channel']['item']['dc:creator']


              if 'dcterms:issued' in parsed_data_opensearch['rss']['channel']['item']:
                date = parsed_data_opensearch['rss']['channel']['item']['dcterms:issued']
              else:
                date = parsed_data_opensearch['rss']['channel']['item']['dc:description']
                if date == None:
                   date = None
                if date != None:
                  if len(date) >1:
                    date = date[len(date) - 1]

              if 'dc:publisher' in parsed_data_opensearch['rss']['channel']['item']:
                publisher = parsed_data_opensearch['rss']['channel']['item']['dc:publisher']
                if type(publisher)is not str:
                  publisher = publisher[len(publisher) - 1]
              else:
                publisher = ""

              if 'dcndl:price' in parsed_data_opensearch['rss']['channel']['item']:
                price = parsed_data_opensearch['rss']['channel']['item']['dcndl:price']
              else:
                price = 0

              if 'dc:extent' in parsed_data_opensearch['rss']['channel']['item']:
                page_count = parsed_data_opensearch['rss']['channel']['item']['dc:extent']
              else:
                page_count = ""

              # 文庫本か単行本かを見分ける　2024/08/09　4:15
              if 'dcndl:seriesTitle' in parsed_data_opensearch['rss']['channel']['item']:
                book_type = "文庫"
              else:
                book_type = "単行本"

            else:
              # 追加部分
              title = parsed_data_opensearch['rss']['channel']['item'][0]['dc:title']
              author = parsed_data_opensearch['rss']['channel']['item'][0]['dc:creator']


              publisher = parsed_data_opensearch['rss']['channel']['item'][0]['dc:publisher']
              print("Publisher:", publisher)
              price = ""
              page_count = ""
              date = parsed_data_opensearch['rss']['channel']['item'][0]['dcterms:issued']

              #　文庫本か単行本かを見分ける 2024/08/09　4:10
              book_type = ""

            return {
               "book_type":book_type,

                # 追加部分
                "title": title,
                "author": author,
                

                "opensearch_data": True,
                "publisher": publisher,
                "price": price,
                "page_count": page_count,
                "sales_date": date,
            }
        except KeyError:
            print("指定されたパスが見つかりません[open_search]")
            return {
                "opensearch_data": False
            }
    else:
        print("データの解析に失敗しました。[open_search]")
        return {
            "opensearch_data": False
        }