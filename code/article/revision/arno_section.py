import lxml

class Arno_Section:
  
  def __init__(self, revision, heading_html, text_html):
    self.revision = revision
    self.heading_html = heading_html
    self.heading = ''.join(lxml.html.fromstring(heading_html).itertext()) if heading_html else ''
    self.text_html = text_html
    self.text = ''.join(lxml.html.fromstring(text_html).itertext()) if text_html else ''
    self.level = int(heading_html.strip()[2:3]) # so far, ony one-digit levels

    self.children = []
    self.parent = None
    self.next = None
    self.previous = None
  
  def get_html(self):
    """
    Get the html of the section (excluding its subsections).

    Returns:
        The html as a string.
    """
    return self.heading_html + self.text_html

  def get_all_html(self):
    """
    Get the html of the section and all its subsections.

    Returns:
        The html as a string.
    """
    return self.heading_html + self.text_html + ''.join([''.join([child.heading_html, child.text_html]) for child in self.children])
  
  def get_text(self):
    """
    Get the full text of the section (excluding its subsections).

    Returns:
        The full text as a string.
    """
    return self.text

  def get_all_text(self):
    """
    Get the full text of the section and all its subsections.

    Returns:
        The full text as a string.
    """
    return self.text + '\n\n'.join(['\n\n'.join([child.heading, child.text]) for child in self.children])

  def get_hrefs(self):
    """
    Return all hrefs in the section (excluding its subsections).

    Returns:
        A list of hrefs as strings.
    """
    return [element.get("href") for element in lxml.html.fromstring(self.get_html()).xpath(".//a")]

  def get_all_hrefs(self):
    """
    Return all hrefs in the section and all its subsections.

    Returns:
        A list of hrefs as strings.
    """
    return [element.get("href") for element in lxml.html.fromstring(self.get_all_html()).xpath(".//a")]

  def get_references(self):
    """
    Return all references in the section (excluding its subsections).

    Returns:
        A list of hrefs as strings.
    """
    ref_ids = [href[1:] for href in self.get_hrefs() if href.startswith('#cite_note')]
    return sorted([ref for ref in self.revision.get_references() if ref.get_id() in ref_ids], key=lambda x: x.get_text())

  def get_all_references(self):
    """
    Return all references in the section and all its subsections.

    Returns:
        A list of hrefs as strings.
    """
    ref_ids = [href[1:] for href in self.get_all_hrefs() if href.startswith('#cite_note')]
    return sorted([ref for ref in self.revision.get_references() if ref.get_id() in ref_ids], key=lambda x: x.get_text())
    

    

