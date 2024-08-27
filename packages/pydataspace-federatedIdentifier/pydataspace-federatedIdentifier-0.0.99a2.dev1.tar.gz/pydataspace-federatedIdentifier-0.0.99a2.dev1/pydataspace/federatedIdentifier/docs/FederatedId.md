

# Class: FederatedId



URI: [fedid:FederatedId](https://w3id.org/byon/fedid/v1.0/#FederatedId)






```mermaid
 classDiagram
    class FederatedId
    click FederatedId href "../FederatedId"
      JsonLDObject <|-- FederatedId
        click JsonLDObject href "../JsonLDObject"
      
      FederatedId : hasComment
        
      FederatedId : hasDescription
        
      FederatedId : hasLabel
        
      FederatedId : hasTitle
        
      FederatedId : id
        
      FederatedId : knownAs
        
          
    
    
    FederatedId --> "*" DomainIdentifier : knownAs
    click DomainIdentifier href "../DomainIdentifier"

        
      
```





## Inheritance
* [JsonLDObject](JsonLDObject.md)
    * **FederatedId**



## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [knownAs](knownAs.md) | * <br/> [DomainIdentifier](DomainIdentifier.md) |  | direct |
| [id](id.md) | 1 <br/> [String](String.md) |  | [JsonLDObject](JsonLDObject.md) |
| [hasLabel](hasLabel.md) | * <br/> [String](String.md) |  | [JsonLDObject](JsonLDObject.md) |
| [hasDescription](hasDescription.md) | * <br/> [String](String.md) |  | [JsonLDObject](JsonLDObject.md) |
| [hasComment](hasComment.md) | * <br/> [String](String.md) |  | [JsonLDObject](JsonLDObject.md) |
| [hasTitle](hasTitle.md) | * <br/> [String](String.md) |  | [JsonLDObject](JsonLDObject.md) |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [FederatedObject](FederatedObject.md) | [hasFederatedId](hasFederatedId.md) | range | [FederatedId](FederatedId.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: https://w3id.org/byon/fedid/v1.0/




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | fedid:FederatedId |
| native | fedid:FederatedId |







## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: FederatedId
from_schema: https://w3id.org/byon/fedid/v1.0/
is_a: JsonLDObject
slots:
- knownAs
class_uri: fedid:FederatedId

```
</details>

### Induced

<details>
```yaml
name: FederatedId
from_schema: https://w3id.org/byon/fedid/v1.0/
is_a: JsonLDObject
attributes:
  knownAs:
    name: knownAs
    from_schema: https://w3id.org/byon/fedid/v1.0/
    rank: 1000
    slot_uri: fedid:knowAs
    alias: knownAs
    owner: FederatedId
    domain_of:
    - FederatedId
    range: DomainIdentifier
    multivalued: true
  id:
    name: id
    from_schema: https://w3id.org/byon/fedid/v1.0/
    rank: 1000
    slot_uri: jsonld:id
    identifier: true
    alias: id
    owner: FederatedId
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
    owner: FederatedId
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
    owner: FederatedId
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
    owner: FederatedId
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
    owner: FederatedId
    domain_of:
    - JsonLDObject
    range: string
    multivalued: true
class_uri: fedid:FederatedId

```
</details>