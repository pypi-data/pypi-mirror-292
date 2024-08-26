# Auto generated from federatedIdentifier.yaml by pythongen.py version: 0.0.1
# Generation date: 2024-08-26T08:59:56
# Schema: fedid
#
# id: https://w3id.org/byon/fedid/v1.0/
# description: Federated Id and Object for CDE
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import re
from jsonasobj2 import JsonObj, as_dict
from typing import Optional, List, Union, Dict, ClassVar, Any
from dataclasses import dataclass
from datetime import date, datetime
from linkml_runtime.linkml_model.meta import EnumDefinition, PermissibleValue, PvFormulaOptions

from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.metamodelcore import empty_list, empty_dict, bnode
from linkml_runtime.utils.yamlutils import YAMLRoot, extended_str, extended_float, extended_int
from linkml_runtime.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from linkml_runtime.utils.formatutils import camelcase, underscore, sfx
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from rdflib import Namespace, URIRef
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_dependencies.jsonLDObject import JsonLDObject, JsonLDObjectId
from linkml_runtime.linkml_model.types import String

metamodel_version = "1.7.0"
version = None

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
FEDID = CurieNamespace('fedid', 'https://w3id.org/byon/fedid/v1.0/#')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
DEFAULT_ = FEDID


# Types

# Class references
class FederatedObjectId(JsonLDObjectId):
    pass


class FederatedIdId(JsonLDObjectId):
    pass


class DomainIdentifierId(JsonLDObjectId):
    pass


@dataclass
class FederatedObject(JsonLDObject):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = FEDID["FederatedObject"]
    class_class_curie: ClassVar[str] = "fedid:FederatedObject"
    class_name: ClassVar[str] = "FederatedObject"
    class_model_uri: ClassVar[URIRef] = FEDID.FederatedObject

    id: Union[str, FederatedObjectId] = None
    belongsToDomain: str = None
    hasFederatedId: Optional[Union[Union[str, FederatedIdId], List[Union[str, FederatedIdId]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, FederatedObjectId):
            self.id = FederatedObjectId(self.id)

        if self._is_empty(self.belongsToDomain):
            self.MissingRequiredField("belongsToDomain")
        if not isinstance(self.belongsToDomain, str):
            self.belongsToDomain = str(self.belongsToDomain)

        if not isinstance(self.hasFederatedId, list):
            self.hasFederatedId = [self.hasFederatedId] if self.hasFederatedId is not None else []
        self.hasFederatedId = [v if isinstance(v, FederatedIdId) else FederatedIdId(v) for v in self.hasFederatedId]

        super().__post_init__(**kwargs)


@dataclass
class FederatedId(JsonLDObject):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = FEDID["FederatedId"]
    class_class_curie: ClassVar[str] = "fedid:FederatedId"
    class_name: ClassVar[str] = "FederatedId"
    class_model_uri: ClassVar[URIRef] = FEDID.FederatedId

    id: Union[str, FederatedIdId] = None
    knownAs: Optional[Union[Union[str, DomainIdentifierId], List[Union[str, DomainIdentifierId]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, FederatedIdId):
            self.id = FederatedIdId(self.id)

        if not isinstance(self.knownAs, list):
            self.knownAs = [self.knownAs] if self.knownAs is not None else []
        self.knownAs = [v if isinstance(v, DomainIdentifierId) else DomainIdentifierId(v) for v in self.knownAs]

        super().__post_init__(**kwargs)


@dataclass
class DomainIdentifier(JsonLDObject):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = FEDID["DomainIdentifier"]
    class_class_curie: ClassVar[str] = "fedid:DomainIdentifier"
    class_name: ClassVar[str] = "DomainIdentifier"
    class_model_uri: ClassVar[URIRef] = FEDID.DomainIdentifier

    id: Union[str, DomainIdentifierId] = None
    belongsToDomain: str = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, DomainIdentifierId):
            self.id = DomainIdentifierId(self.id)

        if self._is_empty(self.belongsToDomain):
            self.MissingRequiredField("belongsToDomain")
        if not isinstance(self.belongsToDomain, str):
            self.belongsToDomain = str(self.belongsToDomain)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.hasFederatedId = Slot(uri=FEDID.hasFederatedId, name="hasFederatedId", curie=FEDID.curie('hasFederatedId'),
                   model_uri=FEDID.hasFederatedId, domain=None, range=Optional[Union[Union[str, FederatedIdId], List[Union[str, FederatedIdId]]]])

slots.belongsToDomain = Slot(uri=FEDID.belongsToDomain, name="belongsToDomain", curie=FEDID.curie('belongsToDomain'),
                   model_uri=FEDID.belongsToDomain, domain=None, range=str)

slots.knownAs = Slot(uri=FEDID.knowAs, name="knownAs", curie=FEDID.curie('knowAs'),
                   model_uri=FEDID.knownAs, domain=None, range=Optional[Union[Union[str, DomainIdentifierId], List[Union[str, DomainIdentifierId]]]])
