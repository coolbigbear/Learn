# Lesson 20: Handling XML in APIs

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Understand XML as a data format and how it compares to JSON
> - Parse XML data from API responses using `xml.etree.ElementTree`
> - Generate XML payloads for API requests
> - Use `xmltodict` for simpler XML-to-Python conversion
> - Send and receive XML data over HTTP
> - Understand when SOAP is used and how it differs from REST

---

## XML vs JSON

Before diving into code, let's compare XML and JSON — the two most common data formats used in web APIs.

### Quick Comparison

| Feature | JSON | XML |
|---------|------|-----|
| **Readability** | Compact, easy on the eyes | More verbose, but self-describing |
| **Data types** | Supports strings, numbers, booleans, arrays, objects | Everything is text — types must be inferred |
| **Attributes** | No native attributes | Elements can have attributes (`<user id="5">`) |
| **Metadata** | Harder to add metadata | Easy to mix metadata (attributes) with data (text) |
| **Namespaces** | Not supported | Built-in namespace support |
| **Validation** | JSON Schema (separate spec) | XML Schema (XSD) — built-in ecosystem |
| **Parsing speed** | Faster | Slower, more complex parser |
| **Browser support** | Native `JSON.parse()`/`JSON.stringify()` | Needs `DOMParser` — more code |

### When to Use Which

- **JSON is the default for modern REST APIs.** It's lighter, faster, and maps directly to Python dictionaries.
- **XML is still common** in enterprise systems, SOAP APIs, payment gateways (like Stripe's older API), RSS feeds, and configuration files.
- **Some APIs support both** — you pick by setting the `Accept` header.

> **Rule of thumb:** If you're building a new API today, choose JSON. If you're integrating with a legacy enterprise system, government service, or financial institution, you'll likely encounter XML.

---

## XML Basics

An XML document is a tree of **elements** (also called tags). Elements can contain:
- **Text content** — the raw data inside an element
- **Attributes** — key-value pairs in the opening tag
- **Child elements** — nested elements

Here's a simple XML document:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
  <book id="1">
    <title>The Pragmatic Programmer</title>
    <author>Andy Hunt</author>
    <price currency="USD">49.99</price>
  </book>
  <book id="2">
    <title>Clean Code</title>
    <author>Robert C. Martin</author>
    <price currency="USD">39.99</price>
  </book>
</bookstore>
```

Key points to notice:
- **`<bookstore>`** is the **root element** — it wraps everything
- **`<book>`** has an **attribute** `id="1"`
- **`<title>`, `<author>`, `<price>`** are **child elements** of `<book>`
- **`<price>`** has an attribute `currency="USD"` **and** text content `49.99`
- The **`<?xml ...?>`** line is an XML declaration (optional but recommended)

---

## Parsing XML with ElementTree

Python's standard library includes `xml.etree.ElementTree` — no extra installation needed.

### Parse from a String

```python
import xml.etree.ElementTree as ET

xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
  <book id="1">
    <title>The Pragmatic Programmer</title>
    <author>Andy Hunt</author>
  </book>
  <book id="2">
    <title>Clean Code</title>
    <author>Robert C. Martin</author>
  </book>
</bookstore>"""

root = ET.fromstring(xml_data)

# Print the root tag
print(root.tag)  # bookstore

# Iterate over all <book> elements
for book in root.findall("book"):
    book_id = book.get("id")  # Access attribute
    title = book.find("title").text  # Access child element text
    author = book.find("author").text
    print(f"Book {book_id}: {title} by {author}")
```

Output:
```
bookstore
Book 1: The Pragmatic Programmer by Andy Hunt
Book 2: Clean Code by Robert C. Martin
```

### Parse from a URL (API Response)

When an API returns XML, you parse the response text the same way:

```python
import requests
import xml.etree.ElementTree as ET

# Some APIs return XML instead of JSON
url = "https://example.com/api/books"
response = requests.get(url, headers={"Accept": "application/xml"})

root = ET.fromstring(response.text)

for book in root.findall("book"):
    print(book.find("title").text)
```

### Important ElementTree Methods

| Method | Description |
|--------|-------------|
| `root.find("tag")` | Finds the **first** child matching `tag` |
| `root.findall("tag")` | Finds **all** children matching `tag` |
| `root.find(".//tag")` | Finds first matching descendant (recursive) |
| `root.findall(".//tag")` | Finds all descendants matching `tag` |
| `elem.get("attr")` | Gets attribute value (or `None` if missing) |
| `elem.text` | Gets the text content of an element |
| `elem.attrib` | Returns a dict of all attributes |
| `elem.iter("tag")` | Iterator over all descendants matching `tag` |

> **Note:** The `.//` prefix means "search recursively" — without it, `find` only looks at direct children.

### Exercise: Navigate an XML Tree

```python
import xml.etree.ElementTree as ET

xml_data = """<users>
  <user role="admin">
    <name>Alice</name>
    <email>alice@example.com</email>
  </user>
  <user role="editor">
    <name>Bob</name>
    <email>bob@example.com</email>
  </user>
</users>"""

root = ET.fromstring(xml_data)

# Find all users and print their role + name
for user in root.findall("user"):
    role = user.get("role")
    name = user.find("name").text
    print(f"{name} ({role})")
```

---

## Generating XML with ElementTree

You can also build XML documents from scratch and serialize them to strings.

### Build from Scratch

```python
import xml.etree.ElementTree as ET

# Create root element
root = ET.Element("bookstore")

# Add a child element
book1 = ET.SubElement(root, "book")
book1.set("id", "1")  # Add attribute

# Add sub-elements
title1 = ET.SubElement(book1, "title")
title1.text = "The Pragmatic Programmer"

author1 = ET.SubElement(book1, "author")
author1.text = "Andy Hunt"

# Add another book
book2 = ET.SubElement(root, "book")
book2.set("id", "2")
ET.SubElement(book2, "title").text = "Clean Code"
ET.SubElement(book2, "author").text = "Robert C. Martin"

# Serialize to string
xml_string = ET.tostring(root, encoding="unicode", xml_declaration=True)
print(xml_string)
```

Output:
```xml
<?xml version='1.0' encoding='UTF-8'?>
<bookstore><book id="1"><title>The Pragmatic Programmer</title><author>Andy Hunt</author></book><book id="2"><title>Clean Code</title><author>Robert C. Martin</author></book></bookstore>
```

> **Note:** The output is compact (no indentation). For pretty-printing, you can use `xml.dom.minidom` or a third-party library like `lxml`.

### From a Dictionary (Using a Helper)

Building XML element-by-element is tedious. Here's a helper that converts a nested dict to XML:

```python
def dict_to_xml(tag, d):
    """Convert a dictionary to an XML element."""
    elem = ET.Element(tag)
    for key, val in d.items():
        if isinstance(val, dict):
            child = dict_to_xml(key, val)
            elem.append(child)
        elif isinstance(val, list):
            for item in val:
                child = dict_to_xml(key, item)
                elem.append(child)
        else:
            child = ET.SubElement(elem, key)
            child.text = str(val)
    return elem

# Example
data = {
    "name": "Alice",
    "email": "alice@example.com",
    "address": {
        "city": "Paris",
        "zip": "75001"
    },
    "tags": ["premium", "active"]
}

root = dict_to_xml("user", data)
print(ET.tostring(root, encoding="unicode"))
```

Output:
```xml
<user><name>Alice</name><email>alice@example.com</email><address><city>Paris</city><zip>75001</zip></address><tags>premium</tags><tags>active</tags></user>
```

### Exercise: Build a Product XML Payload

```python
import xml.etree.ElementTree as ET

def dict_to_xml(tag, d):
    elem = ET.Element(tag)
    for key, val in d.items():
        if isinstance(val, dict):
            child = dict_to_xml(key, val)
            elem.append(child)
        elif isinstance(val, list):
            for item in val:
                child = dict_to_xml(key, item)
                elem.append(child)
        else:
            child = ET.SubElement(elem, key)
            child.text = str(val)
    return elem

product = {
    "name": "Wireless Mouse",
    "price": "29.99",
    "currency": "USD",
    "in_stock": "true",
    "category": {
        "id": "101",
        "name": "Electronics"
    }
}

root = dict_to_xml("product", product)
xml_output = ET.tostring(root, encoding="unicode")
print(xml_output)
```

---

## Simpler XML with xmltodict

The ElementTree API is powerful but verbose. If you want to treat XML more like JSON, install `xmltodict`:

```bash
pip install xmltodict
```

### Convert XML to a Dictionary

```python
import xmltodict

xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
  <book id="1">
    <title>The Pragmatic Programmer</title>
    <author>Andy Hunt</author>
  </book>
</bookstore>"""

result = xmltodict.parse(xml_data)

# Now you have a regular Python dict
book = result["bookstore"]["book"]  # Note: if there's only one, it's not a list!
print(book["title"])  # The Pragmatic Programmer
print(book["@id"])    # Attributes are prefixed with @
```

### Convert a Dictionary to XML

```python
import xmltodict

data = {
    "bookstore": {
        "book": {
            "@id": "1",
            "title": "The Pragmatic Programmer",
            "author": "Andy Hunt"
        }
    }
}

xml_output = xmltodict.unparse(data, pretty=True)
print(xml_output)
```

### Important xmltodict Rules

| Rule | Example |
|------|---------|
| Attributes are prefixed with `@` | `@id`, `@currency` |
| Text content is under `#text` | `{"#text": "49.99"}` |
| A single child element is NOT a list | Access directly |
| Multiple children with the same tag ARE a list | Access by index |

### Exercise: Parse API XML with xmltodict

```python
import xmltodict

# Simulating an API response
api_response = """<?xml version="1.0" encoding="UTF-8"?>
<products>
  <product sku="WM-001">
    <name>Wireless Mouse</name>
    <price>29.99</price>
  </product>
  <product sku="KB-002">
    <name>Mechanical Keyboard</name>
    <price>89.99</price>
  </product>
</products>"""

data = xmltodict.parse(api_response)
products = data["products"]["product"]  # This is a list (2+ elements)

for p in products:
    print(f"{p['name']} — ${p['price']} (SKU: {p['@sku']})")
```

---

## Sending XML in HTTP Requests

When an API expects XML, you send it just like JSON — but with a different `Content-Type`.

### POST XML Data with requests

```python
import requests
import xml.etree.ElementTree as ET

# Build XML payload
root = ET.Element("user")
ET.SubElement(root, "name").text = "Alice"
ET.SubElement(root, "email").text = "alice@example.com"
ET.SubElement(root, "age").text = "25"

xml_payload = ET.tostring(root, encoding="unicode")

# Send it
url = "https://httpbin.org/post"  # Test endpoint
response = requests.post(
    url,
    data=xml_payload,
    headers={"Content-Type": "application/xml"}
)

print(response.status_code)
print(response.text)
```

### Accepting XML Responses

```python
import requests

url = "https://httpbin.org/xml"  # Returns XML
response = requests.get(url, headers={"Accept": "application/xml"})

print(response.status_code)
print(response.headers["Content-Type"])
print(response.text)
```

### Exercise: Send XML and Parse Response

```python
import requests
import xml.etree.ElementTree as ET

# Build a product XML payload
def dict_to_xml(tag, d):
    elem = ET.Element(tag)
    for key, val in d.items():
        if isinstance(val, dict):
            child = dict_to_xml(key, val)
            elem.append(child)
        elif isinstance(val, list):
            for item in val:
                child = dict_to_xml(key, item)
                elem.append(child)
        else:
            child = ET.SubElement(elem, key)
            child.text = str(val)
    return elem

product = {
    "name": "Wireless Mouse",
    "price": "29.99",
    "currency": "USD",
    "in_stock": "true"
}

root = dict_to_xml("product", product)
xml_payload = ET.tostring(root, encoding="unicode")

response = requests.post(
    "https://httpbin.org/post",
    data=xml_payload,
    headers={"Content-Type": "application/xml"}
)

# httpbin echoes back what you sent in the "data" field
print(response.json()["data"])  # The raw XML we sent
```

---

## Parsing XML API Responses in Practice

Let's work through a realistic example. We'll parse a real RSS feed, which is an XML format:

```python
import requests
import xml.etree.ElementTree as ET

# Fetch a real RSS feed (Hacker News)
url = "https://hnrss.org/frontpage?count=5"
response = requests.get(url)

root = ET.fromstring(response.text)

# RSS feeds have namespaces — we need to handle that
# The namespace is declared in the <rss> tag
ns = {"": "http://www.w3.org/2005/Atom"}  # Simplified — real RSS uses different ns

# Find all items
items = root.findall(".//item")
# Or without namespace:
items = root.findall(".//{http://www.w3.org/2005/Atom}item")

for item in items[:3]:
    title = item.find("title").text
    link = item.find("link").text
    print(f"{title}\n  {link}\n")
```

> **Pro tip:** RSS/Atom feeds are still widely XML-based. Parsing them is one of the most common real-world uses of XML in APIs.

---

## Validating XML

When you receive XML from an API, you may want to validate its structure before processing it. Python's `xml.etree.ElementTree` doesn't include a validator, but you can do basic structural checks yourself.

### Manual Validation

```python
import xml.etree.ElementTree as ET

def validate_user_xml(xml_string):
    """Check that the XML has the expected structure."""
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError as e:
        return False, f"Invalid XML: {e}"

    if root.tag != "user":
        return False, f"Expected root 'user', got '{root.tag}'"

    required = ["name", "email"]
    for tag in required:
        if root.find(tag) is None:
            return False, f"Missing required field: {tag}"

    return True, "Valid"

# Test
valid_xml = "<user><name>Alice</name><email>a@b.com</email></user>"
print(validate_user_xml(valid_xml))  # (True, 'Valid')

invalid_xml = "<user><name>Alice</name></user>"
print(validate_user_xml(invalid_xml))  # (False, 'Missing required field: email')
```

### XSD Validation (Advanced)

For robust validation, you typically use `lxml` (third-party) which supports XML Schema (XSD):

```python
from lxml import etree

# Load schema
xsd_doc = etree.parse("schema.xsd")
schema = etree.XMLSchema(xsd_doc)

# Parse and validate
xml_doc = etree.parse("data.xml")
if schema.validate(xml_doc):
    print("Valid!")
else:
    print(schema.error_log)
```

> This level of validation is typically needed in enterprise SOAP APIs.

---

## SOAP vs REST with XML

### REST with XML

In REST APIs, XML is just a data format — you send and receive XML documents over standard HTTP methods (GET, POST, PUT, DELETE). The API is designed around **resources** (URLs), not operations.

```http
POST /api/users HTTP/1.1
Content-Type: application/xml

<user>
  <name>Alice</name>
  <email>alice@example.com</email>
</user>
```

### SOAP (Simple Object Access Protocol)

SOAP is an older protocol that always uses XML. Instead of resources, it defines **operations** (functions) you can call.

A SOAP request looks like this:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope
  xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:ns="http://example.com/users">
  <soap:Header>
    <ns:AuthToken>abc123</ns:AuthToken>
  </soap:Header>
  <soap:Body>
    <ns:CreateUser>
      <ns:name>Alice</ns:name>
      <ns:email>alice@example.com</ns:email>
    </ns:CreateUser>
  </soap:Body>
</soap:Envelope>
```

Key SOAP concepts:
- **Envelope** — required root element
- **Header** — optional metadata (auth tokens, etc.)
- **Body** — the actual request/response data
- **WSDL** — Web Services Description Language; defines the API contract (like OpenAPI for REST)

> **When you'll encounter SOAP:** Banking APIs, payment gateways (some), government systems, enterprise CRM (Salesforce, SAP). Most modern APIs have moved to REST or GraphQL.

### REST vs SOAP Quick Reference

| Feature | REST with XML | SOAP |
|---------|---------------|------|
| **Transport** | HTTP only | HTTP, SMTP, JMS |
| **Data format** | XML, JSON, or anything | XML only |
| **State** | Stateless | Can be stateful |
| **Caching** | Built-in HTTP caching | Must implement separately |
| **Contract** | Optional (OpenAPI) | Required (WSDL) |
| **Complexity** | Low | High |
| **Tooling** | Standard HTTP tools | Specialised SOAP clients |
| **Modern adoption** | Dominant | Legacy/enterprise only |

---

## Putting It All Together

Here's a complete example that fetches XML from an API, parses it, and extracts specific data:

```python
import requests
import xml.etree.ElementTree as ET

def fetch_products_as_xml(api_url):
    """Fetch products from an API that returns XML."""
    response = requests.get(api_url, headers={"Accept": "application/xml"})
    response.raise_for_status()
    return response.text

def parse_products(xml_string):
    """Extract product names and prices from XML."""
    root = ET.fromstring(xml_string)
    products = []
    for product in root.findall("product"):
        products.append({
            "name": product.find("name").text,
            "price": product.find("price").text,
            "sku": product.get("sku", "N/A")
        })
    return products

# Example usage (using httpbin's XML endpoint)
xml_data = fetch_products_as_xml("https://httpbin.org/xml")
print("Raw XML:", xml_data[:200])

# Parse would work here if httpbin's XML endpoint had products
# In practice, you'd use a real XML API endpoint
```

---

## Summary

- **XML** is a markup language for structured data — more verbose than JSON but richer in features (attributes, namespaces, schemas)
- **`xml.etree.ElementTree`** is Python's built-in XML library — use `fromstring()` to parse, `Element()`/`SubElement()` to build, and `tostring()` to serialize
- **`xmltodict`** provides a simpler API that converts XML to/from Python dictionaries
- **Send XML** to APIs with `Content-Type: application/xml` and `requests.post(data=xml_string)`
- **Accept XML** from APIs with `Accept: application/xml` header
- **SOAP** is a legacy XML-only protocol still used in enterprise systems — it uses Envelope/Header/Body structure
- **Validation** can be done manually for simple cases or with XSD/lxml for production

### What's Next?

In the next lesson, you'll learn how to build your own API with FastAPI — handling JSON data, path parameters, query parameters, and more.

---

## Exercises

Now it's your turn! Complete the exercises below to practice XML handling in APIs.
