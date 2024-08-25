from playwright.sync_api import sync_playwright


def get_page_source(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)
        page_source = page.content()
        browser.close()
        return page_source


if __name__ == "__main__":
    print(get_page_source("https://zeffmuks.com"))
