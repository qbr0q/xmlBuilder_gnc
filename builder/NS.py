from lxml.builder import ElementMaker


NS_MAP = {
    'xsd': 'http://www.w3.org/2001/XMLSchema',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}

root_ns = ElementMaker(nsmap=NS_MAP)
ns = ElementMaker()
xsi_type = f"{{{NS_MAP['xsi']}}}nil"
