from datetime import timedelta
from math import ceil
from random import shuffle
from re import sub
from typing import Dict
from typing import List

from libgen_api import LibgenSearch
from loguru import logger
from numpy import repeat
from requests import get
from requests.exceptions import Timeout
from tqdm import tqdm


def are_books_same(
        title1: str,
        title2: str,
        year1: str,
        year2: str,
) -> bool:
    if are_texts_same(title1, title2):
        return True

    if are_texts_similar(title1, title2):
        return are_texts_similar(year1, year2)

    return False


def filter_search_results(
        books: List[Dict],
        limit: int,
) -> List[Dict]:
    # TODO: sort books first
    filtered_books: List[Dict] = []
    for i, book in enumerate(books):
        if len(filtered_books) >= limit:
            break

        skip = False
        for filtered_book in filtered_books:
            if are_books_same(
                    title1=book['Title'],
                    title2=filtered_book['Title'],
                    year1=book['Year'],
                    year2=filtered_book['Year'],
            ):
                err = f"Skipping {book['Title']} because {filtered_book['Title']}"
                logger.warning(err)
                skip = True
                break

        if skip:
            continue

        filtered_books.append(book)
    return filtered_books


def download_link(
        link: str,
        timeout: timedelta,
) -> bytes:
    # Download link using requests
    try:
        response = get(url=link, timeout=timeout.total_seconds())

        if response.status_code != 200:
            err = f"Failed to download {link} because server returned {response.status_code}"
            raise Exception(err)

        return bytes(response.content)
    except Timeout:
        err = f"Failed to download {link} because request timed out"
        raise TimeoutError(err)
    except Exception as e:
        err = f"Failed to download {link} because {e}"
        raise Exception(err)


def best_effort_download(
        links: List[str],
        timeout: timedelta,
        max_timeout: timedelta,
        max_retries: int,
) -> bytes:
    links = repeat(links, ceil(max_retries / len(links))).tolist()
    shuffle(links)
    for link in links:
        try:
            return download_link(link=link, timeout=timeout)
        except TimeoutError:
            err = f"Failed to download {link} because of timeout, retrying..."
            logger.warning(err)
            timeout = min(timeout * 2, max_timeout)
        except Exception as e:
            err = f"Failed to download {link} because {e}"
            logger.error(err)
            continue  # Try next link without increasing timeout
    return b''


def get_download_links(
        name: str,
        limit: int,
        titles: List[str],
) -> List[Dict]:
    s = LibgenSearch()
    results = s.search_author_filtered(
        query=name,
        filters={
            "Extension": "epub",
            "Language": "English",
        },
        exact_match=False,
    )

    for title in titles:
        results.extend(s.search_title_filtered(
            query=title,
            filters={
                "Extension": "epub",
                "Language": "English",
            },
            exact_match=False,
        ))

    logger.info(f"Found {len(results)} book by {name}")

    results = filter_search_results(
        books=results,
        limit=limit,
    )

    logger.info(f"Filtered {len(results)} book by {name} for title {titles[0]}")

    books = []
    for result in results:
        links_data: Dict = s.resolve_download_links(result)

        links: List[str] = []
        for link in links_data.keys():
            links.append(links_data[link])

        data = {
            "id": result['ID'],
            "metadata": {
                "title": result['Title'],
                "authors": result['Author'],
                "kind": result['Extension'],
            },
            "spider": {
                "type": "libgen",
                "links": links,
            }
        }

        books.append(data)

    return books


def download_book(
        name: str,
        title: str,
) -> None:
    logger.info(f"Downloading {title} by {name}")

    try:
        datas = get_download_links(
            name=name,
            limit=1,
            titles=[title],
        )
    except Exception as e:
        err = f"Failed to get books for {name} due to {e}"
        logger.error(err)
        return

    # Now download all books
    total = len(datas)
    count = 0
    for i in tqdm(range(total)):
        data = datas[i]

        # Check if links present
        if 'links' not in data['spider'] or len(data['spider']['links']) == 0:
            err = f"Skipping {data['metadata']['title']} because empty spider links"
            logger.error(err)
            continue

        filename = data['metadata']['title']
        extension = data['metadata']['kind']

        script_bytes = best_effort_download(
            links=data['spider']['links'],
            timeout=timedelta(seconds=10),
            max_timeout=timedelta(seconds=60),
            max_retries=5,
        )
        if len(script_bytes) == 0:
            err = f"Skipping {data['metadata']['title']} because empty script"
            logger.error(err)
            continue

        with open(f"{filename}.{extension}", 'wb') as f:
            f.write(script_bytes)

        count += 1

    logger.info(f"Downloaded {count} books for {name}")
    return


def simplify_text(title: str) -> str:
    title = title.strip()  # Remove leading/trailing whitespace
    title = title.lower()  # Convert to lowercase (if standardization requires)
    title = sub(r'\([^)]*\)', '', title)  # Remove parentheses and contents
    title = sub(r'(\w)-(\w)', r'\1 \2', title)  # Replace hyphens with spaces
    title = sub(r'[^\w\s]', '', title)  # Remove special characters
    title = sub(r'\s+', ' ', title)  # Replace multiple spaces with a single space
    return title


def are_texts_same(text1: str, text2: str) -> bool:
    text1 = simplify_text(text1)
    text2 = simplify_text(text2)
    return text1 == text2


def are_texts_similar(text1: str, text2: str) -> bool:
    text1 = simplify_text(text1)
    text2 = simplify_text(text2)
    return text1 == text2 or text1 in text2 or text2 in text1


if __name__ == '__main__':
    download_book(
        name="Alex Hormozi",
        title="$100M Offers",
    )
