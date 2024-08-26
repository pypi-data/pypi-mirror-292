

# Slot: belongsToDomain

URI: [fedid:belongsToDomain](https://w3id.org/byon/fedid/v1.0/#belongsToDomain)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DomainIdentifier](DomainIdentifier.md) |  |  no  |
| [FederatedObject](FederatedObject.md) |  |  no  |







## Properties

* Range: [String](String.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: https://w3id.org/byon/fedid/v1.0/




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | fedid:belongsToDomain |
| native | fedid:belongsToDomain |




## LinkML Source

<details>
```yaml
name: belongsToDomain
from_schema: https://w3id.org/byon/fedid/v1.0/
rank: 1000
slot_uri: fedid:belongsToDomain
alias: belongsToDomain
domain_of:
- FederatedObject
- DomainIdentifier
range: string
required: true
multivalued: false

```
</details>