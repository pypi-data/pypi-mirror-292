

# Class: DomainIdentifier



URI: [fedid:DomainIdentifier](https://w3id.org/byon/fedid/v1.0/#DomainIdentifier)






```mermaid
 classDiagram
    class DomainIdentifier
    click DomainIdentifier href "../DomainIdentifier"
      JsonLDObject <|-- DomainIdentifier
        click JsonLDObject href "../JsonLDObject"
      
      DomainIdentifier : belongsToDomain
        
      DomainIdentifier : hasComment
        
      DomainIdentifier : hasDescription
        
      DomainIdentifier : hasLabel
        
      DomainIdentifier : hasTitle
        
      DomainIdentifier : id
        
      
```





## Inheritance
* [JsonLDObject](JsonLDObject.md)
    * **DomainIdentifier**



## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [belongsToDomain](belongsToDomain.md) | 1 <br/> [String](String.md) |  | direct |
| [id](id.md) | 1 <br/> [String](String.md) |  | [JsonLDObject](JsonLDObject.md) |
| [hasLabel](hasLabel.md) | * <br/> [String](String.md) |  | [JsonLDObject](JsonLDObject.md) |
| [hasDescription](hasDescription.md) | * <br/> [String](String.md) |  | [JsonLDObject](JsonLDObject.md) |
| [hasComment](hasComment.md) | * <br/> [String](String.md) |  | [JsonLDObject](JsonLDObject.md) |
| [hasTitle](hasTitle.md) | * <br/> [String](String.md) |  | [JsonLDObject](JsonLDObject.md) |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [FederatedId](FederatedId.md) | [knownAs](knownAs.md) | range | [DomainIdentifier](DomainIdentifier.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: https://w3id.org/byon/fedid/v1.0/




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | fedid:DomainIdentifier |
| native | fedid:DomainIdentifier |







## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: DomainIdentifier
from_schema: https://w3id.org/byon/fedid/v1.0/
is_a: JsonLDObject
slots:
- belongsToDomain
class_uri: fedid:DomainIdentifier

```
</details>

### Induced

<details>
```yaml
name: DomainIdentifier
from_schema: https://w3id.org/byon/fedid/v1.0/
is_a: JsonLDObject
attributes:
  belongsToDomain:
    name: belongsToDomain
    from_schema: https://w3id.org/byon/fedid/v1.0/
    rank: 1000
    slot_uri: fedid:belongsToDomain
    alias: belongsToDomain
    owner: DomainIdentifier
    domain_of:
    - FederatedObject
    - DomainIdentifier
    range: string
    required: true
    multivalued: false
  id:
    name: id
    from_schema: https://w3id.org/byon/fedid/v1.0/
    rank: 1000
    slot_uri: jsonld:id
    identifier: true
    alias: id
    owner: DomainIdentifier
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
    owner: DomainIdentifier
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
    owner: DomainIdentifier
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
    owner: DomainIdentifier
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
    owner: DomainIdentifier
    domain_of:
    - JsonLDObject
    range: string
    multivalued: true
class_uri: fedid:DomainIdentifier

```
</details>