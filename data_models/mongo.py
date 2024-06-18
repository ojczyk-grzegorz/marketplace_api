from pydantic import BaseModel, ConfigDict, Field, field_serializer
import bson


class MongoDocument(BaseModel):
    model_config=ConfigDict(extra="allow", arbitrary_types_allowed=True)
    id: bson.ObjectId | str = Field(alias="_id")

    @field_serializer("id")
    def id_serialize(self, value: bson.ObjectId) -> str:
        return str(value)

class MongoCursor(BaseModel):
    records: list[MongoDocument]