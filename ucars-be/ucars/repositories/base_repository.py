
import abc
import inspect
import math
from sqlalchemy.orm import Session

from ucars.models.base_model import BaseModel
from ucars.responses.pagination_response import PaginationResponse


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def to_dict(self, obj):
        raise NotImplementedError

    @abc.abstractmethod
    def to_list(self, l):
        raise NotImplementedError



class BaseRepository(AbstractRepository):

    model: object = NotImplementedError
    db: Session = NotImplementedError

    def __init__(self, db:Session):
        self.db = db


    def to_dict(self, obj):
        if obj is not None:
            return {c.key: getattr(obj, c.key)
                for c in inspect(obj).mapper.column_attrs}
        else:
            return {}


    def to_list(self, _list):
        if isinstance(_list, list) and len(_list):
            output = []
            for item in _list:
                output.append(self.to_dict(item))
            return output
        else:
            print("A list is reuired!")
            return []


    def _is_empty(self, value):
        if value is None:
            return True
        elif isinstance(value, str) and value.strip() == '':
            return True
        return False


    def find(self, id: int):
        item = self.db.objects(organization_id=id)
        if item is not None:
            return dict(item[0])
        return None  


    def get(self, offset: int = 0, limit: int = 10):
        return self.db.query(self.model).offset(offset).limit(limit).all()


    def filter(self, field: str, value):
        return self.db.query(self.model).filter(self.model[field] == value).first()


    def find(self, id: int):
        return self.db.query(self.model).filter(self.model.id == id).first()


    def create(self, data: BaseModel):
        obj = self.model(**data.dict())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj


    def update(self, db_model: BaseModel):
        self.db.add(db_model)
        self.db.commit()
        self.db.refresh(db_model)
        return db_model


    def delete(self, db_model: BaseModel):
        self.db.delete(db_model)
        self.db.commit()
        

    def paginate(self, limit: int = 10, skip: int = 0, search: str = ''):
        total = self.db.query(self.model).count()
        total_page = math.ceil(total / limit) if total > 0 else 0
        next_page = None
        data = []
        
        if total > 0:
            query = self.db.query(self.model).offset(skip).limit(limit)
            
            # if offset is not None:
            #     query = query.offset(offset)

            data = list(query)

            if len(data) > 0:
                last = data[-1]
                next_page = f'?limit={limit}&offset={last.id}&search={search}'
        
        return PaginationResponse(
            total=total,
            limit=limit,
            offset=skip,
            total_page=total_page,
            next_page_link=next_page,
            data=data
        )