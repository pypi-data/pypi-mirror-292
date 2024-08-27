from contextlib import suppress
from typing import Annotated, Any, Literal, Optional, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Discriminator,
    Field,
    RootModel,
    Tag,
    ValidationError,
    field_validator,
)

from bigdata.models.entities import (
    Company,
    Concept,
    Facility,
    Landmark,
    MacroEntity,
    Organization,
    OrganizationType,
    Person,
    Place,
    Product,
    ProductType,
)
from bigdata.models.languages import Language
from bigdata.models.sources import Source
from bigdata.models.topics import Topic
from bigdata.models.watchlists import Watchlist

MACRO_PREFIX = "macro_"


class AutosuggestedSavedSearch(BaseModel):
    """Class used only to parse the output from the Autosuggestion"""

    model_config = ConfigDict(populate_by_name=True)
    id: Optional[str] = Field(validation_alias="key", default=None)
    name: Optional[str] = Field(default=None)
    query_type: Literal["savedSearch"] = Field(
        default="savedSearch", validation_alias="queryType"
    )


def get_discriminator_knowledge_graph_value(v: Any) -> Optional[str]:
    if isinstance(v, dict):
        return v.get(
            "entityType", v.get("entity_type", v.get("queryType", v.get("query_type")))
        )
    return getattr(v, "entity_type", getattr(v, "query_type", None))


DiscriminatedEntityTypes = Union[
    Annotated[Company, Tag(Company.model_fields["entity_type"].default)],
    Annotated[Facility, Tag(Facility.model_fields["entity_type"].default)],
    Annotated[Landmark, Tag(Landmark.model_fields["entity_type"].default)],
    Annotated[Organization, Tag(Organization.model_fields["entity_type"].default)],
    Annotated[
        OrganizationType,
        Tag(OrganizationType.model_fields["entity_type"].default),
    ],
    Annotated[Person, Tag(Person.model_fields["entity_type"].default)],
    Annotated[Place, Tag(Place.model_fields["entity_type"].default)],
    Annotated[Product, Tag(Product.model_fields["entity_type"].default)],
    Annotated[ProductType, Tag(ProductType.model_fields["entity_type"].default)],
]

EntityTypes = Union[
    DiscriminatedEntityTypes,
    Concept,
]
DiscriminatedKnowledgeGraphTypes = Union[
    DiscriminatedEntityTypes,
    Annotated[Source, Tag(Source.model_fields["entity_type"].default)],
    Annotated[Topic, Tag(Topic.model_fields["entity_type"].default)],
    Annotated[Language, Tag(Language.model_fields["query_type"].default)],
    Annotated[
        AutosuggestedSavedSearch,
        Tag(AutosuggestedSavedSearch.model_fields["query_type"].default),
    ],
    Annotated[Watchlist, Tag(Watchlist.model_fields["query_type"].default)],
]

KnowledgeGraphTypes = Union[
    MacroEntity,
    EntityTypes,
    DiscriminatedKnowledgeGraphTypes,
]


class KnowledgeGraphAnnotated(BaseModel):
    root: Annotated[
        DiscriminatedKnowledgeGraphTypes,
        Discriminator(get_discriminator_knowledge_graph_value),
    ]


def parse_knowledge_graph_object(domain_obj: dict) -> KnowledgeGraphTypes:
    try:
        return KnowledgeGraphAnnotated.model_validate({"root": domain_obj}).root
    except ValidationError:
        # Macro keys are not part of KnowledGraphAnnotated, and we don't want them there to be visible to the user
        with suppress(ValidationError):
            if get_discriminator_knowledge_graph_value(domain_obj).startswith(
                MACRO_PREFIX
            ):
                return MacroEntity.model_validate(domain_obj)

        return Concept.model_validate(domain_obj)


class ByIdsResponse(RootModel[dict]):
    root: dict[str, Union[Source, Topic, Language, EntityTypes]]


class AutosuggestResponse(RootModel[dict]):
    root: dict[str, list[KnowledgeGraphTypes]]


class AutosuggestRequests(RootModel[list]):
    root: list[str]

    @field_validator("root")
    @classmethod
    def no_duplicates(cls, values):
        if len(values) != len(set(values)):
            raise ValueError("Values must be unique")
        return values


class ByIdsRequestItem(BaseModel):
    key: str
    queryType: str


class ByIdsRequest(RootModel[list]):
    root: list[ByIdsRequestItem]
