from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
)


def safe_click(driver, element):
    """Scroll the element to the middle of the screen and click it.

    Falls back to a JavaScript click when something covers the element or
    Selenium refuses to click it.
    """
    try:
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            element,
        )
    except StaleElementReferenceException:
        raise
    except Exception:
        pass

    try:
        element.click()
    except (ElementClickInterceptedException, ElementNotInteractableException):
        driver.execute_script("arguments[0].click();", element)
