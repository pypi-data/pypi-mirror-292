

# Slot: hasLabel

URI: [rdfs:label](http://www.w3.org/2000/01/rdf-schema#label)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DomainIdentifier](DomainIdentifier.md) |  |  no  |
| [FederatedObject](FederatedObject.md) |  |  no  |
| [JsonLDObject](JsonLDObject.md) |  |  no  |
| [FederatedId](FederatedId.md) |  |  no  |







## Properties

* Range: [String](String.md)

* Multivalued: True





## Identifier and Mapping Information







### Schema Source


* from schema: https://w3id.org/byon/fedid/v1.0/




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | rdfs:label |
| native | fedid:hasLabel |




## LinkML Source

<details>
```yaml
name: hasLabel
from_schema: https://w3id.org/byon/fedid/v1.0/
rank: 1000
slot_uri: rdfs:label
alias: hasLabel
domain_of:
- JsonLDObject
range: string
multivalued: true

```
</details>