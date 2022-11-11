import re
import copy
import json
import collections
import uuid
import datetime
from abc import ABCMeta, abstractproperty

import six

from .server_api import get_server_api_connection
from .utils import create_entity_id


PROJECT_NAME_ALLOWED_SYMBOLS = "a-zA-Z0-9_"
PROJECT_NAME_REGEX = re.compile(
    "^[{}]+$".format(PROJECT_NAME_ALLOWED_SYMBOLS)
)

REMOVED_VALUE = object()


def _create_or_convert_to_id(entity_id=None):
    if entity_id is None:
        return create_entity_id()

    # Validate if can be converted to uuid
    uuid.UUID(entity_id)
    return entity_id


def new_folder_entity(
    name,
    folder_type,
    parent_id=None,
    attribs=None,
    data=None,
    thumbnail_id=None,
    entity_id=None
):
    """Create skeleton data of folder entity.

    Args:
        name (str): Is considered as unique identifier of folder in project.
        parent_id (str): Id of parent folder.
        attribs (Dict[str, Any]): Explicitly set attributes of folder.
        data (Dict[str, Any]): Custom folder data. Empty dictionary is used
            if not passed.
        thumbnail_id (str): Id of thumbnail related to folder.
        entity_id (str): Predefined id of entity. New id is
            created if not passed.

    Returns:
        Dict[str, Any]: Skeleton of folder entity.
    """

    if attribs is None:
        attribs = {}

    if data is None:
        data = {}

    if parent_id is not None:
        parent_id = _create_or_convert_to_id(parent_id)

    return {
        "id": _create_or_convert_to_id(entity_id),
        "name": name,
        # This will be ignored
        "parentId": parent_id,
        "data": data,
        "attrib": attribs,
        "thumbnailId": thumbnail_id
    }


def new_subset_entity(
    name, family, folder_id, attribs=None, data=None, entity_id=None
):
    """Create skeleton data of subset entity.

    Args:
        name (str): Is considered as unique identifier of subset under folder.
        family (str): Subset's family.
        folder_id (str): Id of parent folder.
        attribs (Dict[str, Any]): Explicitly set attributes of subset.
        data (Dict[str, Any]): Subset entity data. Empty dictionary is used
            if not passed. Value of 'family' is used to fill 'family'.
        entity_id (str): Predefined id of entity. New id is
            created if not passed.

    Returns:
        Dict[str, Any]: Skeleton of subset entity.
    """

    if attribs is None:
        attribs = {}

    if data is None:
        data = {}

    return {
        "id": _create_or_convert_to_id(entity_id),
        "name": name,
        "family": family,
        "attrib": attribs,
        "data": data,
        "folderId": _create_or_convert_to_id(folder_id)
    }


def new_version_entity(
    version,
    subset_id,
    task_id=None,
    thumbnail_id=None,
    author=None,
    attribs=None,
    data=None,
    entity_id=None
):
    """Create skeleton data of version entity.

    Args:
        version (int): Is considered as unique identifier of version
            under subset.
        subset_id (str): Id of parent subset.
        task_id (str): Id of task under which subset was created.
        thumbnail_id (str): Thumbnail related to version.
        author (str): Name of version author.
        attribs (Dict[str, Any]): Explicitly set attributes of version.
        data (Dict[str, Any]): Version entity custom data.
        entity_id (str): Predefined id of entity. New id is
            created if not passed.

    Returns:
        Dict[str, Any]: Skeleton of version entity.
    """

    if attribs is None:
        attribs = {}

    if data is None:
        data = {}

    if data is None:
        data = {}

    return {
        "id": _create_or_convert_to_id(entity_id),
        "version": int(version),
        "subsetId": _create_or_convert_to_id(subset_id),
        "attrib": attribs,
        "data": data
    }


def new_hero_version_entity(
    version,
    subset_id,
    task_id=None,
    thumbnail_id=None,
    author=None,
    attribs=None,
    data=None,
    entity_id=None
):
    """Create skeleton data of hero version entity.

    Args:
        version (int): Is considered as unique identifier of version
            under subset. Should be same as standard version if there is any.
        subset_id (str): Id of parent subset.
        task_id (str): Id of task under which subset was created.
        thumbnail_id (str): Thumbnail related to version.
        author (str): Name of version author.
        attribs (Dict[str, Any]): Explicitly set attributes of version.
        data (Dict[str, Any]): Version entity data.
        entity_id (str): Predefined id of entity. New id is
            created if not passed.

    Returns:
        Dict[str, Any]: Skeleton of version entity.
    """

    if attribs is None:
        attribs = {}

    if data is None:
        data = {}

    return {
        "id": _create_or_convert_to_id(entity_id),
        "version": -abs(int(version)),
        "subsetId": subset_id,
        "attrib": attribs,
        "data": data
    }


def new_representation_entity(
    name, version_id, attribs=None, data=None, entity_id=None
):
    """Create skeleton data of representation entity.

    Args:
        name (str): Representation name considered as unique identifier
            of representation under version.
        version_id (str): Id of parent version.
        context (Dict[str, Any]): Representation context used to fill template.
        attribs (Dict[str, Any]): Explicitly set attributes of representation.
        data (Dict[str, Any]): Representation entity data.
        entity_id (str): Predefined id of entity. New id is created
            if not passed.

    Returns:
        Dict[str, Any]: Skeleton of representation entity.
    """

    if attribs is None:
        attribs = {}

    if data is None:
        data = {}

    return {
        "id": _create_or_convert_to_id(entity_id),
        "versionId": _create_or_convert_to_id(version_id),
        "name": name,
        "data": data,
        "attrib": attribs
    }


def new_workfile_info_doc(
    filename, folder_id, task_name, files, data=None, entity_id=None
):
    """Create skeleton data of workfile info entity.

    Workfile entity is at this moment used primarily for artist notes.

    Args:
        filename (str): Filename of workfile.
        folder_id (str): Id of folder under which workfile live.
        task_name (str): Task under which was workfile created.
        files (List[str]): List of rootless filepaths related to workfile.
        data (Dict[str, Any]): Additional metadata.

    Returns:
        Dict[str, Any]: Skeleton of workfile info entity.
    """

    if not data:
        data = {}

    return {
        "id": _create_or_convert_to_id(entity_id),
        "parent": _create_or_convert_to_id(folder_id),
        "task_name": task_name,
        "filename": filename,
        "data": data,
        "files": files
    }


def _prepare_update_data(old_doc, new_doc, replace):
    changes = {}
    for key, value in new_doc.items():
        if key not in old_doc or value != old_doc[key]:
            changes[key] = value

    if replace:
        for key in old_doc.keys():
            if key not in new_doc:
                changes[key] = REMOVED_VALUE
    return changes


def prepare_folder_update_data(old_doc, new_doc, replace=True):
    """Compare two folder entities and prepare update data.

    Based on compared values will create update data for
    'UpdateOperation'.

    Empty output means that entities data are identical.

    Returns:
        Dict[str, Any]: Changes between old and new entity.
    """

    # changes = {}
    # for key, value in new_doc.items():
    #     if key in ("data", ):
    #         continue
    #
    #     if key not in old_doc or value != old_doc[key]:
    #         changes[key] = value
    #
    # return _prepare_update_data(old_doc, new_doc, replace)

    raise NotImplementedError(
        "'prepare_folder_update_data' not yet implemented"
    )


def prepare_subset_update_data(old_doc, new_doc, replace=True):
    """Compare two subset entities and prepare update data.

    Based on compared values will create update data for
    'UpdateOperation'.

    Empty output means that entities are identical.

    Returns:
        Dict[str, Any]: Changes between old and new entity.
    """

    # return _prepare_update_data(old_doc, new_doc, replace)

    raise NotImplementedError(
        "'prepare_folder_update_data' not yet implemented"
    )


def prepare_version_update_data(old_doc, new_doc, replace=True):
    """Compare two version entities and prepare update data.

    Based on compared values will create update data for
    'UpdateOperation'.

    Empty output means that entities are identical.

    Returns:
        Dict[str, Any]: Changes between old and new entity.
    """

    # return _prepare_update_data(old_doc, new_doc, replace)

    raise NotImplementedError(
        "'prepare_folder_update_data' not yet implemented"
    )


def prepare_hero_version_update_data(old_doc, new_doc, replace=True):
    """Compare two hero version entities and prepare update data.

    Based on compared values will create update data for 'UpdateOperation'.

    Empty output means that entities are identical.

    Returns:
        Dict[str, Any]: Changes between old and new entity.
    """

    # return _prepare_update_data(old_doc, new_doc, replace)

    raise NotImplementedError(
        "'prepare_folder_update_data' not yet implemented"
    )


def prepare_representation_update_data(old_doc, new_doc, replace=True):
    """Compare two representation entities and prepare update data.

    Based on compared values will create update data for
    'UpdateOperation'.

    Empty output means that entities are identical.

    Returns:
        Dict[str, Any]: Changes between old and new entity.
    """

    # return _prepare_update_data(old_doc, new_doc, replace)

    raise NotImplementedError(
        "'prepare_folder_update_data' not yet implemented"
    )


def prepare_workfile_info_update_data(old_doc, new_doc, replace=True):
    """Compare two workfile info entities and prepare update data.

    Based on compared values will create update data for
    'UpdateOperation'.

    Empty output means that entities are identical.

    Returns:
        Dict[str, Any]: Changes between old and new entity.
    """

    # return _prepare_update_data(old_doc, new_doc, replace)

    raise NotImplementedError(
        "'prepare_folder_update_data' not yet implemented"
    )


class FailedOperations(Exception):
    pass


@six.add_metaclass(ABCMeta)
class AbstractOperation(object):
    """Base operation class.

    Opration represent a call into database. The call can create, change or
    remove data.

    Args:
        project_name (str): On which project operation will happen.
        entity_type (str): Type of entity on which change happens.
            e.g. 'folder', 'representation' etc.
    """

    def __init__(self, project_name, entity_type, session):
        self._project_name = project_name
        self._entity_type = entity_type
        self._session = session
        self._id = str(uuid.uuid4())

    @property
    def project_name(self):
        return self._project_name

    @property
    def id(self):
        """Identifier of operation."""

        return self._id

    @property
    def entity_type(self):
        return self._entity_type

    @abstractproperty
    def operation_name(self):
        """Stringified type of operation."""

        pass

    def to_data(self):
        """Convert opration to data that can be converted to json or others.

        Returns:
            Dict[str, Any]: Description of operation.
        """

        return {
            "id": self._id,
            "entity_type": self.entity_type,
            "project_name": self.project_name,
            "operation": self.operation_name
        }


class CreateOperation(AbstractOperation):
    """Opeartion to create an entity.

    Args:
        project_name (str): On which project operation will happen.
        entity_type (str): Type of entity on which change happens.
            e.g. 'folder', 'representation' etc.
        data (Dict[str, Any]): Data of entity that will be created.
    """

    operation_name = "create"

    def __init__(self, project_name, entity_type, data, session):
        if not data:
            data = {}
        else:
            data = copy.deepcopy(dict(data))

        if "id" not in data:
            data["id"] = create_entity_id()

        self._data = data
        super(CreateOperation, self).__init__(
            project_name, entity_type, session
        )

    def __setitem__(self, key, value):
        self.set_value(key, value)

    def __getitem__(self, key):
        return self.data[key]

    def set_value(self, key, value):
        self.data[key] = value

    def get(self, key, *args, **kwargs):
        return self.data.get(key, *args, **kwargs)

    @property
    def con(self):
        return self.session.con

    @property
    def session(self):
        return self._session

    @property
    def entity_id(self):
        return self._data["id"]

    @property
    def data(self):
        return self._data

    def to_data(self):
        output = super(CreateOperation, self).to_data()
        output["data"] = copy.deepcopy(self.data)
        return output

    def to_server_operation(self):
        return {
            "id": self.id,
            "type": "create",
            "entityType": self.entity_type,
            "entityId": self.entity_id,
            "data": self._data
        }


class UpdateOperation(AbstractOperation):
    """Operation to update an entity.

    Args:
        project_name (str): On which project operation will happen.
        entity_type (str): Type of entity on which change happens.
            e.g. 'folder', 'representation' etc.
        entity_id (str): Identifier of an entity.
        update_data (Dict[str, Any]): Key -> value changes that will be set in
            database. If value is set to 'REMOVED_VALUE' the key will be
            removed. Only first level of dictionary is checked (on purpose).
    """

    operation_name = "update"

    def __init__(
        self, project_name, entity_type, entity_id, update_data, session
    ):
        super(UpdateOperation, self).__init__(
            project_name, entity_type, session
        )

        self._entity_id = entity_id
        self._update_data = update_data

    @property
    def entity_id(self):
        return self._entity_id

    @property
    def update_data(self):
        return self._update_data

    @property
    def con(self):
        return self.session.con

    @property
    def session(self):
        return self._session

    def to_data(self):
        changes = {}
        for key, value in self._update_data.items():
            if value is REMOVED_VALUE:
                value = None
            changes[key] = value

        output = super(UpdateOperation, self).to_data()
        output.update({
            "entity_id": self.entity_id,
            "changes": changes
        })
        return output

    def to_server_operation(self):
        if not self._update_data:
            return None

        update_data = {}
        for key, value in self._update_data.items():
            if value is REMOVED_VALUE:
                value = None
            update_data[key] = value

        return {
            "id": self.id,
            "type": "update",
            "entityType": self.entity_type,
            "entityId": self.entity_id,
            "data": update_data
        }


class DeleteOperation(AbstractOperation):
    """Opeartion to delete an entity.

    Args:
        project_name (str): On which project operation will happen.
        entity_type (str): Type of entity on which change happens.
            e.g. 'folder', 'representation' etc.
        entity_id (str): Entity id that will be removed.
    """

    operation_name = "delete"

    def __init__(self, project_name, entity_type, entity_id, session):
        self._entity_id = entity_id

        super(DeleteOperation, self).__init__(
            project_name, entity_type, session
        )

    @property
    def entity_id(self):
        return self._entity_id

    @property
    def con(self):
        return self.session.con

    @property
    def session(self):
        return self._session

    def to_data(self):
        output = super(DeleteOperation, self).to_data()
        output["entity_id"] = self.entity_id
        return output

    def to_server_operation(self):
        return {
            "id": self.id,
            "type": self.operation_name,
            "entityId": self.entity_id,
            "entityType": self.entity_type,
        }


class OperationsSession(object):
    """Session storing operations that should happen in an order.

    At this moment does not handle anything special can be sonsidered as
    stupid list of operations that will happen after each other. If creation
    of same entity is there multiple times it's handled in any way and entity
    values are not validated.

    All operations must be related to single project.

    Args:
        project_name (str): Project name to which are operations related.
    """

    def __init__(self, con=None):
        if con is None:
            con = get_server_api_connection()
        self._con = con
        self._project_cache = {}
        self._operations = []
        self._nested_operations = collections.defaultdict(list)

    @property
    def con(self):
        return self._con

    def get_project(self, project_name):
        if project_name not in self._project_cache:
            self._project_cache[project_name] = self.con.get_project(
                project_name)
        return copy.deepcopy(self._project_cache[project_name])

    def __len__(self):
        return len(self._operations)

    def add(self, operation):
        """Add operation to be processed.

        Args:
            operation (BaseOperation): Operation that should be processed.
        """
        if not isinstance(
            operation,
            (CreateOperation, UpdateOperation, DeleteOperation)
        ):
            raise TypeError("Expected Operation object got {}".format(
                str(type(operation))
            ))

        self._operations.append(operation)

    def append(self, operation):
        """Add operation to be processed.

        Args:
            operation (BaseOperation): Operation that should be processed.
        """

        self.add(operation)

    def extend(self, operations):
        """Add operations to be processed.

        Args:
            operations (List[BaseOperation]): Operations that should be
                processed.
        """

        for operation in operations:
            self.add(operation)

    def remove(self, operation):
        """Remove operation."""

        self._operations.remove(operation)

    def clear(self):
        """Clear all registered operations."""

        self._operations = []

    def to_data(self):
        return [
            operation.to_data()
            for operation in self._operations
        ]

    def commit(self):
        """Commit session operations."""

        operations, self._operations = self._operations, []
        if not operations:
            return

        operations_by_project = collections.defaultdict(list)
        for operation in operations:
            operations_by_project[operation.project_name].append(operation)

        body_by_id = {}
        results = []
        for project_name, operations in operations_by_project.items():
            operations_body = []
            for operation in operations:
                body = operation.to_server_operation()
                if body is not None:
                    body_by_id[operation.id] = body
                    operations_body.append(body)

            if operations_body:
                result = self._con.post(
                    "projects/{}/operations".format(project_name),
                    operations=operations_body,
                    canFail=False
                )
                results.append(result.data)

        for result in results:
            if result.get("success"):
                continue

            if "operations" not in result:
                raise FailedOperations(
                    "Operation failed. Content: {}".format(str(result))
                )

            for op_result in result["operations"]:
                if not op_result["success"]:
                    operation_id = op_result["id"]
                    raise FailedOperations((
                        "Operation \"{}\" failed with data:\n{}\nError: {}."
                    ).format(
                        operation_id,
                        json.dumps(body_by_id[operation_id], indent=4),
                        op_result["error"],
                    ))

    def create_entity(self, project_name, entity_type, data, nested_id=None):
        """Fast access to 'CreateOperation'.

        Args:
            project_name (str): On which project the creation happens.
            entity_type (str): Which entity type will be created.
            data (Dicst[str, Any]): Entity data.
            nested_id (str): Id of other operation from which is triggered
                operation -> Operations can trigger suboperations but they
                must be added to operations list after it's parent is added.

        Returns:
            CreateOperation: Object of update operation.
        """

        operation = CreateOperation(
            project_name, entity_type, data, self
        )

        if nested_id:
            self._nested_operations[nested_id].append(operation)
        else:
            self.add(operation)
            if operation.id in self._nested_operations:
                self.extend(self._nested_operations.pop(operation.id))

        return operation

    def update_entity(
        self, project_name, entity_type, entity_id, update_data, nested_id=None
    ):
        """Fast access to 'UpdateOperation'.

        Returns:
            UpdateOperation: Object of update operation.
        """

        operation = UpdateOperation(
            project_name, entity_type, entity_id, update_data, self
        )
        if nested_id:
            self._nested_operations[nested_id].append(operation)
        else:
            self.add(operation)
            if operation.id in self._nested_operations:
                self.extend(self._nested_operations.pop(operation.id))
        return operation

    def delete_entity(
        self, project_name, entity_type, entity_id, nested_id=None
    ):
        """Fast access to 'DeleteOperation'.

        Returns:
            DeleteOperation: Object of delete operation.
        """

        operation = DeleteOperation(
            project_name, entity_type, entity_id, self
        )
        if nested_id:
            self._nested_operations[nested_id].append(operation)
        else:
            self.add(operation)
            if operation.id in self._nested_operations:
                self.extend(self._nested_operations.pop(operation.id))
        return operation


def create_project(
    project_name,
    project_code,
    library_project=False,
    preset_name=None,
    con=None
):
    """Create project using OpenPype settings.

    This project creation function is not validating project entity on
    creation. It is because project entity is created blindly with only
    minimum required information about project which is it's name, code, type
    and schema.

    Entered project name must be unique and project must not exist yet.

    Note:
        This function is here to be OP v4 ready but in v3 has more logic
            to do. That's why inner imports are in the body.

    Args:
        project_name (str): New project name. Should be unique.
        project_code (str): Project's code should be unique too.
        library_project (bool): Project is library project.
        preset_name (str): Name of anatomy preset. Default is used if not
            passed.
        con (ServerAPI): Connection to server with logged user.

    Raises:
        ValueError: When project name already exists.

    Returns:
        Dict[str, Any]: Created project entity.
    """

    if con is None:
        con = get_server_api_connection()

    if con.get_project(project_name, fields=["name"]):
        raise ValueError("Project with name \"{}\" already exists".format(
            project_name
        ))

    if not PROJECT_NAME_REGEX.match(project_name):
        raise ValueError((
            "Project name \"{}\" contain invalid characters"
        ).format(project_name))

    preset = con.get_project_anatomy_preset(preset_name)

    result = con.post(
        "projects",
        name=project_name,
        code=project_code,
        anatomy=preset,
        library=library_project
    )
    if result.status != 201:
        details = "Unknown details ({})".format(result.status)
        if result.data:
            details = result.data.get("detail") or details
        raise ValueError("Failed to create project \"{}\": {}".format(
            project_name, details
        ))

    return con.get_project(project_name)


def delete_project(project_name, con=None):
    if con is None:
        con = get_server_api_connection()

    if not con.get_project(project_name, fields=["name"]):
        raise ValueError("Project with name \"{}\" was not found".format(
            project_name
        ))

    result = con.delete("projects/{}".format(project_name))
    if result.status_code != 204:
        raise ValueError(
            "Failed to delete project \"{}\". {}".format(
                project_name, result.data["detail"]
            )
        )
