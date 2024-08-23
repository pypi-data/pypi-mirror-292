# SRUからデータを取得
import xmltodict
import requests

async def convert_xml_to_json(xml_str):
    try:
        dict = xmltodict.parse(xml_str)
        return dict  # 直接ディクショナリを返す
    except Exception as e:
        print("XMLの解析エラー", e)
        return None



async def get_book_data_sru(isbn):
    url = f"https://ndlsearch.ndl.go.jp/api/sru?operation=searchRetrieve&maximumRecords=10&recordSchema=dcndl&recordPacking=xml&query=dpid=iss-ndl-opac-national%20AND%20isbn%3d{isbn}%20AND%20mediatype%3D%22books%22&onlyBib=true"
    response = requests.get(url)
    response.encoding = 'utf-8'
    parsed_data = await convert_xml_to_json(response.text)


    if parsed_data:
        try:
            # 追加部分
            title = parsed_data['searchRetrieveResponse']['records']['record']['recordData']['rdf:RDF']['dcndl:BibResource'][0]['dc:title'][0]['rdf:Description']['rdf:value']
            author = parsed_data['searchRetrieveResponse']['records']['record']['recordData']['rdf:RDF']['dcndl:BibResource'][0]['dc:creator'][0]


            # # titleへのパスを辿る
            # publisher = parsed_data['searchRetrieveResponse']['records']['record']['recordData']['rdf:RDF']['dcndl:BibResource'][0]['dcterms:publisher'][0]['foaf:Agent']['foaf:name']
            publisher_list = parsed_data['searchRetrieveResponse']['records']['record']['recordData']['rdf:RDF']['dcndl:BibResource'][0]['dcterms:publisher']
            if 'foaf:Agent' in publisher_list:
                publisher = publisher_list['foaf:Agent']['foaf:name']
            else:
                publisher = publisher_list[0]['foaf:Agent']['foaf:name']
            sales_date = parsed_data['searchRetrieveResponse']['records']['record']['recordData']['rdf:RDF']['dcndl:BibResource'][0]['dcterms:date']
            price = parsed_data['searchRetrieveResponse']['records']['record']['recordData']['rdf:RDF']['dcndl:BibResource'][0]['dcndl:price']
            page_count = parsed_data['searchRetrieveResponse']['records']['record']['recordData']['rdf:RDF']['dcndl:BibResource'][0]['dcterms:extent']


            # 単行本か文庫本かを見分ける　2024/08/09　3:14
            if "dcndl:seriesTitle" in parsed_data['searchRetrieveResponse']['records']['record']['recordData']['rdf:RDF']['dcndl:BibResource'][0]:
                book_type = "文庫"
            else:
                book_type = "単行本"

            return {
                "book_type":book_type,

                # 追加部分
                "title": title,
                "author": author,
                

                "sru_data": True,
                "publisher": publisher,
                "sales_date": sales_date,
                "price": price,
                "page_count": page_count,
            }

        except KeyError:
            print("指定されたパスで見つかりません。")
            return {
                "sru_data": False
            }
    else:
        print("データの解析に失敗しました。")
        return {
            "sru_data": False
        }