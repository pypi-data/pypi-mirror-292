import re

from bs4 import BeautifulSoup, Tag


class CustomSoup(BeautifulSoup):
    def find_element_str(self, locator: str, key: str) -> str:
        element = self.select_one(locator)
        if element is None:
            return ""
        return self.get_element_str(element, key)

    def find_element_num(self, locator: str, key: str) -> int:
        attr_value = self.find_element_str(locator, key)
        num_str = re.sub("[^\\d]", "", attr_value) or "0"
        return int(num_str)

    def find_elements_str(self, locator: str, key: str) -> list[str]:
        elements = self.select(locator)
        return [self.get_element_str(element, key) for element in elements]

    def get_element_str(self, element: Tag | None, key: str) -> str:
        if element is None:
            return ""
        value = element.get(key)
        if isinstance(value, str):
            return value
        elif isinstance(value, list):  # class values
            return " ".join(value)
        else:
            return ""

    def get_element_text(self, element: Tag | None) -> str:
        if element is None:
            return ""
        return element.text
