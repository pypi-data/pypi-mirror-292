<p align="center">
    <a href="https://pypi.org/project/bbc-news"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Sayad-Uddin-Tahsin/BBC-News-API/main/Assets/Dark%20Logo.png"><img alt="Logo" src="https://raw.githubusercontent.com/Sayad-Uddin-Tahsin/BBC-News-API/main/Assets/Light%20Logo.png" height=100 width=100></picture></a>
</p>

# bbc-news

The `bbc-news` Python library provides a simple and intuitive interface for accessing the BBC News API, allowing developers to fetch the latest news articles from the British Broadcasting Corporation (BBC) programmatically. This library aims to streamline the integration of BBC news content into Python applications with ease.

<a href="https://pypi.org/project/bbc-news"><img src="https://img.shields.io/pypi/status/bbc-news?label=Status&logo=pypi&logoColor=ffffff" height=22></a>
<a href="https://pypi.org/project/bbc-news"><img src="https://img.shields.io/pypi/v/bbc-news?label=PyPI Version&logo=pypi&logoColor=ffffff" height=22></a>
<a href="https://python.org"><img src="https://img.shields.io/pypi/pyversions/bbc-news?label=Python&logo=python&logoColor=ffdd54" height=22></a>

<picture><source media="(prefers-color-scheme: dark)" srcset="https://web-badge-psi.vercel.app/latency-badge?theme=dark"><img alt="Latency Badge" src="https://web-badge-psi.vercel.app/latency-badge?theme=light"></picture>

## Features
- **Easy-to-use Interface:** The library offers a straightforward interface for accessing the BBC News API.
- **Language Support:** Users can retrieve news content in over 30 languages supported by the BBC.
- **Customizable Queries:** Developers can tailor their queries to fetch news articles based on specific topics, regions, or categories.
- **Error Handling:** The library includes built-in error handling mechanisms to handle API errors gracefully.

## Installation
You can install the bbc-news library via pip:

```console
python -m pip install bbc-news
```
`bbc-news` requires Python 3.7 or later.

## Quick Start

<!-- Example: Printing Categories -->
<details open>
<summary>Printing section titles</summary>

<!-- Code: Start -->
<details open>
<summary>Code</summary>


```python
# Import the Library
import bbc

# Get the News for Chinese
news = bbc.news.get_news(bbc.Languages.Chinese)

# Get the Category Titles
categories = news.news_categories()

# Print the category titles
print(categories)

```

</details>
<!-- Code: End -->

<!-- Output: Start -->
<details>
<summary>Output</summary>

```console
['Top story - Zhongwen', '必看', '深度报道', '新闻时事 趋势动态', '知识资讯 观点角度', '特别推荐', '台湾大选2024']
```

</details>
</details>

<!-- Example: Printing Category News -->
<details>
<summary>Printing category news' title, image link and news link</summary>

<!-- Code: Start -->
<details open>
<summary>Code</summary>


```python
# Import the Library
import bbc

# Get the News for Bengali
news = bbc.news.get_news(bbc.Languages.Bengali)

# Get the Category Titles
categories = news.news_categories()

# Loop through the category titles
for category in categories:
    # Get the Category News
    section_news = news.news_category(category)

    # Loop through the news dictionary
    for news_dict in section_news:
        # Print the Title
        print(news_dict['title'])

        # Print the Image Link
        print(news_dict['image_link'])

        # Print the News Link
        print(news_dict["news_link"])
                
        # Print a Separator Line
        print("---")
```

</details>
<!-- Code: End -->

<!-- Output: Start -->
<details>
<summary>Output</summary>

```console
ভারতের মুহাম্মদ আসফান যেভাবে রাশিয়া-ইউক্রেন যুদ্ধে মারা গেলেন
https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/fd83/live/b9cd1d20-dc91-11ee-9a5b-e35447f6c53b.jpg
https://www.bbc.com/bengali/articles/c720rl118yro
---
গাজায় বিমান থেকে ফেলা ত্রাণের বস্তার নিচে চাপা পড়ে পাঁচ ফিলিস্তিনি নিহত
https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/4f7d/live/a3523c10-ddc7-11ee-8bf3-195418ba9285.jpg
https://www.bbc.com/bengali/articles/cd1841llw6eo
---
'বৈশ্বিক গণতান্ত্রিক সূচকে অবনতি বাংলাদেশের'
https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/d1ea/live/7af76d90-ddbc-11ee-9080-d35818d60ed3.jpg
https://www.bbc.com/bengali/articles/cpv0wvkprwvo
---
গাজার মাঝ বরাবর ইসরায়েল রাস্তা তৈরি করছে কেন ?
https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/3927/live/81f882d0-dd55-11ee-b292-af90e1cb0639.jpg
https://www.bbc.com/bengali/articles/c1e8zxwqwyno
---
জনসংখ্যা কমায় বিপাকে থাকা দেশগুলো থেকে ভারত, পাকিস্তান, বাংলাদেশ কী পেতে পারে?
https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/3400/live/a073cc20-dd36-11ee-9a5b-e35447f6c53b.jpg
https://www.bbc.com/bengali/articles/c280gpg8wexo

...
...
...
```

</details>
</details>

<!-- Example: Printing Latest News -->
<details>
<summary>Printing Latest News</summary>

<!-- Code: Start -->
<details open>
<summary>Code</summary>


```python
# Import the Library
import bbc

# Get the Latest News for Arabic
news_list = bbc.news.get_latest_news(bbc.Languages.Arabic)

# Loop through the list
for news_dict in news_list:
    # Print the Title
    print(news_dict['title'])

    # Print the Image Link
    print(news_dict['image_link'])

    # Print the News Link
    print(news_dict["news_link"])
            
    # Print a Separator Line
    print("---")

```

</details>
<!-- Code: End -->

<!-- Output: Start -->
<details>
<summary>Output</summary>

```console
الأمم المتحدة تنتقد إنشاء ممر بحري لإيصال المساعدات في غزة وخمسة قتلى خلال إنزال جوي
https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/1cc9/live/6e28cad0-ddaa-11ee-be08-970469947e0a.jpg
https://www.bbc.com/arabic/articles/ce9rn7l6r1lo
---
كندا تستأنف تمويل وكالة الأونروا بعد قرار تعليقها
https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/536e/live/69575680-ddb3-11ee-8bf3-195418ba9285.jpg
https://www.bbc.com/arabic/articles/c9945z477k8o
---
مبادرة إنسانية لغزة من أول بلد أوروبي يعترف بالدولة الفلسطينية
https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/e629/live/0f753c40-dca5-11ee-b83b-0f87a864f372.jpg
https://www.bbc.com/arabic/articles/cv2ymd20rzjo
---
الضفة الغربية: "رغم محاولتي حماية طفلي إلا أنه قُتِل"!
https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/98db/live/f707d570-dd97-11ee-8bf3-195418ba9285.jpg
https://www.bbc.com/arabic/articles/c3gm1eg1deko
---
ما الذي نعرفه عن الممر البحري الذي يشرف الجيش الأمريكي على إنشائه قبالة غزة؟
https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/a783/live/9130c4a0-dd3d-11ee-b83b-0f87a864f372.png
https://www.bbc.com/arabic/articles/clejnlz58x1o
---
صور الأقمار الصناعية تظهر اكتمال الطريق الذي أنشأه الجيش الإسرائيلي عبر غزة
https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/3dfd/live/3c82b530-dce3-11ee-8f28-259790e80bba.jpg
https://www.bbc.com/arabic/articles/ckk7y2k5117o
---
"مؤامرة إجرامية" يكشف عنها الجيش الأمريكي حاكها أحد جنوده مع الصين
https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/9cdb/live/66b71d80-dd21-11ee-b83b-0f87a864f372.jpg
https://www.bbc.com/arabic/articles/cj7ve1mr9v9o
---
بياناتك الشخصية متاحة للجميع، فهل هناك طريقة أفضل للحفاظ على خصوصيتها؟
https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/0cf2/live/c5be7b30-dd93-11ee-8be9-db11b274404f.jpg
https://www.bbc.com/arabic/articles/c3gq1kxjp72o
---
اكتشاف بقايا أحفورية لأقدم غابة في العالم تعود لنحو 400 مليون سنة
https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/0008/live/18a10cf0-dd3f-11ee-9a5b-e35447f6c53b.jpg
https://www.bbc.com/arabic/articles/c723xvpkplko
```

</details>
</details>

<!-- Example: Printing News of English -->
<details>
<summary>Printing News of English</summary>

<!-- Code: Start -->
<details open>
<summary>Code</summary>


```python
# Import the Library
import bbc
# Get the Latest News for English
news = bbc.news.get_news(bbc.Languages.English)
# Get the Category Titles
categories = news.news_categories()
# Loop through the category titles
for category in categories:
    # Get the Category News
    section_news = news.news_category(category)

    # Loop through the news dictionary
    for news_dict in section_news:
        # Print the Title
        print(news_dict['title'])
        # Print the News Description according to availability  (Returns None if unavailable)
        print(news_dict['summary'])
        # Print the News Image according to availability (Returns None if unavailable)
        print(news_dict['image_link'])
        # Print the News Link
        print(news_dict["news_link"])
        
        # Print a Blank Line
        print("---")

```

</details>
<!-- Code: End -->

<!-- Output: Start -->
<details>
<summary>Output</summary>

```console
Israel and Hezbollah exchange heavy fire in major escalation
Hezbollah says it fired hundreds of rockets after Israel says it launched pre-emptive strikes on Sunday morning.
https://ichef.bbci.co.uk/news/240/cpsprodpb/c16f/live/604e1f70-6354-11ef-8665-19cd0ac0261f.jpg.webp
https://bbc.com/news/articles/cq6rzvyz9p6o
---
Matthew Perry's death reveals Hollywood's ketamine 'wild west'
Doctors say ketamine has become "super easy" to get through a network of online clinics that exploit government loopholes.
https://ichef.bbci.co.uk/news/240/cpsprodpb/11ab/live/fa8ebf00-617d-11ef-8c32-f3c2bc7494c6.jpg.webp
https://bbc.com/news/articles/czrgp7pj4g2o
---
Israel and Hezbollah exchange heavy fire in major escalation
Hezbollah says it fired hundreds of rockets after Israel says it launched pre-emptive strikes on Sunday morning.
https://ichef.bbci.co.uk/news/240/cpsprodpb/c16f/live/604e1f70-6354-11ef-8665-19cd0ac0261f.jpg.webp
https://bbc.com/news/articles/cq6rzvyz9p6o
---
Matthew Perry's death reveals Hollywood's ketamine 'wild west'
Doctors say ketamine has become "super easy" to get through a network of online clinics that exploit government loopholes.
https://ichef.bbci.co.uk/news/240/cpsprodpb/11ab/live/fa8ebf00-617d-11ef-8c32-f3c2bc7494c6.jpg.webp
https://bbc.com/news/articles/czrgp7pj4g2o

...
...
...
```

</details>
</details>

## Contributing
Contributions to the bbc-news Python library are welcome! If you encounter any issues, have suggestions for improvements, or would like to contribute new features, feel free to open an issue or submit a pull request on the [GitHub repository](https://github.com/Sayad-Uddin-Tahsin/BBC-News-API).

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/Sayad-Uddin-Tahsin/BBC-News-API/blob/main/LICENSE) file for details.
