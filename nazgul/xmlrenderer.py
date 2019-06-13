from xml.dom import minidom


class XMLRenderer(object):
    """Render API data as XML"""

    def __init__(self):
        self.doc = minidom.Document()

    def toxml(self):
        return self.doc.toxml(encoding='utf-8')

    def render(self, status=200):
        """serve the XML to the user"""
        return self.toxml()

    def prepare_products(self, products):
        """Product List"""
        root = self.doc.createElement('products')
        self.doc.appendChild(root)
        for product in products:
            item = self.doc.createElement('product')
            item.setAttribute('id', str(product['id']))
            item.setAttribute('name', str(product['name']))
            for lang in product['languages']:
                lang_item = self.doc.createElement('language')
                lang_item.setAttribute('locale', str(lang))
                item.appendChild(lang_item)
            root.appendChild(item)

    def prepare_mirrors(self, mirrors):
        """Mirror List"""
        root = self.doc.createElement('mirrors')
        self.doc.appendChild(root)
        for mirror in mirrors:
            item = self.doc.createElement('mirror')
            item.setAttribute('baseurl', str(mirror['baseurl']))
            root.appendChild(item)

    def prepare_locations(self, product):
        """Prepare list of locations for a given product"""
        root = self.doc.documentElement
        if not root:
            root = self.doc.createElement('locations')
            self.doc.appendChild(root)
        prodnode = self.doc.createElement('product')
        prodnode.setAttribute('id', str(product['id']))
        prodnode.setAttribute('name', product['name'])
        root.appendChild(prodnode)

        for location in product['locations']:
            locnode = self.doc.createElement('location')
            locnode.setAttribute('id', str(location['id']))
            locnode.setAttribute('os', str(location['os_name']))
            locnode.appendChild(self.doc.createTextNode(location['path']))
            prodnode.appendChild(locnode)

    def prepare_uptake_fake(self, products, oses):
        root = self.doc.createElement('mirror_uptake')
        self.doc.appendChild(root)

        for product in products:
            for os_name in oses:
                item = self.doc.createElement('item')

                elem = self.doc.createElement('product')
                elem.appendChild(self.doc.createTextNode(str(product)))
                item.appendChild(elem)

                elem = self.doc.createElement('os')
                elem.appendChild(self.doc.createTextNode(str(os_name)))
                item.appendChild(elem)

                elem = self.doc.createElement('available')
                elem.appendChild(self.doc.createTextNode(str(2000000)))
                item.appendChild(elem)

                elem = self.doc.createElement('total')
                elem.appendChild(self.doc.createTextNode(str(2000000)))
                item.appendChild(elem)

                root.appendChild(item)

    def prepare_uptake(self, uptake):
        """Product uptake"""
        content_map = {
            'product': 'location__product__name',
            'os': 'location__os__name',
            'available': 'available',
            'total': 'total'
        }

        root = self.doc.createElement('mirror_uptake')
        self.doc.appendChild(root)
        for row in uptake:
            item = self.doc.createElement('item')
            for key, value in content_map.items():
                elem = self.doc.createElement(key)
                elem.appendChild(self.doc.createTextNode(str(row[value])))
                item.appendChild(elem)
            root.appendChild(item)

    def success(self, message, render=True):
        """Prepare a success message"""
        return self.message(message, type='success', render=render)

    def error(self, message, errno=0, render=True):
        """Prepare an error message"""
        return self.message(message,
                            type='error',
                            number=errno,
                            render=render,
                            status=400)

    def message(self,
                message,
                type='info',
                number=None,
                render=True,
                status=200):
        """Prepare a single message"""
        root = self.doc.createElement(type)
        root.appendChild(self.doc.createTextNode(str(message)))
        if number:
            root.setAttribute('number', str(number))
        self.doc.appendChild(root)
        if render:
            return self.render(status)
