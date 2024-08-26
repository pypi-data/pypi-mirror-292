

# Class: JsonLDObject



URI: [jsonld:JsonLDObject](https://w3id.org/cde/jsonld/v1.0/#JsonLDObject)






```mermaid
 classDiagram
    class JsonLDObject
    click JsonLDObject href "../JsonLDObject"
      JsonLDObject <|-- FederatedObject
        click FederatedObject href "../FederatedObject"
      JsonLDObject <|-- FederatedId
        click FederatedId href "../FederatedId"
      JsonLDObject <|-- DomainIdentifier
        click DomainIdentifier href "../DomainIdentifier"
      
      JsonLDObject : hasComment
        
      JsonLDObject : hasDescription
        
      JsonLDObject : hasLabel
        
      JsonLDObject : hasTitle
        
      JsonLDObject : id
        
      
```





## Inheritance
* **JsonLDObject**
    * [FederatedObject](FederatedObject.md)
    * [FederatedId](FederatedId.md)
    * [DomainIdentifier](DomainIdentifier.md)



## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [id](id.md) | 1 <br/> [String](String.md) |  | direct |
| [hasLabel](hasLabel.md) | * <br/> [String](String.md) |  | direct |
| [hasDescription](hasDescription.md) | * <br/> [String](String.md) |  | direct |
| [hasComment](hasComment.md) | * <br/> [String](String.md) |  | direct |
| [hasTitle](hasTitle.md) | * <br/> [String](String.md) |  | direct |









## Identifier and Mapping Information







### Schema Source


* from schema: https://w3id.org/byon/fedid/v1.0/




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | jsonld:JsonLDObject |
| native | fedid:JsonLDObject |







## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: JsonLDObject
from_schema: https://w3id.org/byon/fedid/v1.0/
slots:
- id
- hasLabel
- hasDescription
- hasComment
- hasTitle
class_uri: jsonld:JsonLDObject

```
</details>

### Induced

<details>
```yaml
name: JsonLDObject
from_schema: https://w3id.org/byon/fedid/v1.0/
attributes:
  id:
    name: id
    from_schema: https://w3id.org/byon/fedid/v1.0/
    rank: 1000
    slot_uri: jsonld:id
    identifier: true
    alias: id
    owner: JsonLDObject
    domain_of:
    - JsonLDObject
    range: string
    required: true
  hasLabel:
    name: hasLabel
    from_schema: https://w3id.org/byon/fedid/v1.0/
    rank: 1000
    slot_uri: rdfs:label
    alias: hasLabel
    owner: JsonLDObject
    domain_of:
    - JsonLDObject
    range: string
    multivalued: true
  hasDescription:
    name: hasDescription
    from_schema: https://w3id.org/byon/fedid/v1.0/
    rank: 1000
    slot_uri: dc:description
    alias: hasDescription
    owner: JsonLDObject
    domain_of:
    - JsonLDObject
    range: string
    multivalued: true
  hasComment:
    name: hasComment
    from_schema: https://w3id.org/byon/fedid/v1.0/
    rank: 1000
    slot_uri: rdfs:comment
    alias: hasComment
    owner: JsonLDObject
    domain_of:
    - JsonLDObject
    range: string
    multivalued: true
  hasTitle:
    name: hasTitle
    from_schema: https://w3id.org/byon/fedid/v1.0/
    rank: 1000
    slot_uri: dc:title
    alias: hasTitle
    owner: JsonLDObject
    domain_of:
    - JsonLDObject
    range: string
    multivalued: true
class_uri: jsonld:JsonLDObject

```
</details>