from user_agents import parse


def parse_user_agent(user_agent: str) -> str:
    if user_agent:
        user_agent = parse(user_agent)
        browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
        return browser
    return "Unknown"
