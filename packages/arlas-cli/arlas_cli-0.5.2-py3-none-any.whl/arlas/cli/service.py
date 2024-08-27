from enum import Enum
import json
import os
import sys
from alive_progress import alive_bar
import requests

from arlas.cli.settings import ARLAS, Configuration, Resource, AuthorizationService

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


class RequestException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message


class Services(Enum):
    arlas_server = "server"
    persistence_server = "persistence"
    iam = "iam"


class Service:

    def create_user(arlas: str, email: str):
        return Service.__arlas__(arlas, "users", post=json.dumps({"email": email}), service=Services.iam)

    def delete_user(arlas: str, id: str):
        return Service.__arlas__(arlas, "/".join(["users", id]), delete=True, service=Services.iam)

    def activate(arlas: str, id: str):
        return Service.__arlas__(arlas, "/".join(["users", id, "activate"]), post="{}", service=Services.iam)
    
    def deactivate(arlas: str, id: str):
        return Service.__arlas__(arlas, "/".join(["users", id, "deactivate"]), post="{}", service=Services.iam)

    def list_organisations(arlas: str) -> list[list[str]]:
        data = Service.__arlas__(arlas, "organisations", service=Services.iam)
        table = [["id", "name", "Am I owner?"]]
        for org in data:
            table.append([
                org.get("id"),
                org.get("name") + " (" + org.get("displayName") + ")",
                org.get("isOwner"),
            ])
        return table

    def create_organisation(arlas: str, org: str):
        return Service.__arlas__(arlas, "/".join(["organisations", org]), post="{}", service=Services.iam)

    def delete_organisation(arlas: str, oid: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid]), delete="{}", service=Services.iam)

    def list_organisation_collections(arlas: str, oid: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "collections"]), service=Services.iam)

    def list_organisation_users(arlas: str, oid: str):
        users: list = Service.__arlas__(arlas, "/".join(["organisations", oid, "users"]), service=Services.iam)
        print(users)
        return list(map(lambda user: [user.get("member").get("id"),
                                      user.get("member").get("email"),
                                      user.get("isOwner"),
                                      "\n".join(list(map(lambda role: role.get("fullName"), user.get("member").get("roles"))))],
                        users))

    def list_organisation_groups(arlas: str, oid: str):
        groups: list = Service.__arlas__(arlas, "/".join(["organisations", oid, "groups"]), service=Services.iam)
        return list(map(lambda user: [user.get("id"),
                                      user.get("fullName"),
                                      user.get("description"),
                                      user.get("isTechnical"),
                                      "group"
                                      ],
                        groups))

    def add_group_in_organisation(arlas: str, oid: str, group_name: str, group_description: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "groups"]), post=json.dumps({"name": group_name, "description": group_description}), service=Services.iam)

    def delete_group_in_organisation(arlas: str, oid: str, group_id: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "groups", group_id]), delete=True, service=Services.iam)

    def add_permission_in_organisation(arlas: str, oid: str, permission_value: str, permission_description: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "permissions"]), post=json.dumps({"value": permission_value, "description": permission_description}), service=Services.iam)

    def delete_permission_in_organisation(arlas: str, oid: str, permission_id: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "permissions", permission_id]), delete=True, service=Services.iam)

    def add_permission_to_group_in_organisation(arlas: str, oid: str, role_id: str, permission_id: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "roles", role_id, "permissions", permission_id]), post="{}", service=Services.iam)

    def delete_permission_from_group_in_organisation(arlas: str, oid: str, role_id: str, permission_id: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "roles", role_id, "permissions", permission_id]), delete=True, service=Services.iam)

    def add_role_in_organisation(arlas: str, oid: str, role_name: str, role_description: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "roles"]), post=json.dumps({"name": role_name, "description": role_description}), service=Services.iam)

    def delete_role_in_organisation(arlas: str, oid: str, role_id: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "roles", role_id]), delete=True, service=Services.iam)

    def list_organisation_roles(arlas: str, oid: str):
        roles: list = Service.__arlas__(arlas, "/".join(["organisations", oid, "roles"]), service=Services.iam)
        return list(map(lambda user: [user.get("id"),
                                      user.get("name"),
                                      user.get("description"),
                                      user.get("isTechnical"),
                                      "role"
                                      ],
                        roles))

    def list_organisation_permissions(arlas: str, oid: str):
        permissions: list = Service.__arlas__(arlas, "/".join(["organisations", oid, "permissions"]), service=Services.iam)
        return list(map(lambda perm: [perm.get("id"),
                                      perm.get("description"),
                                      perm.get("value"),
                                      "\n".join(list(map(lambda role: role.get("fullName"), perm.get("roles"))))
                                      ],
                        permissions))

    def list_collections(arlas: str) -> list[list[str]]:
        data = Service.__arlas__(arlas, "explore/_list")
        table = [["name", "index"]]
        for collection in data:
            table.append([
                collection.get("collection_name"),
                collection.get("params", {}).get("index_name"),
            ])
        return table

    def list_indices(arlas: str) -> list[list[str]]:
        data = json.loads(Service.__es__(arlas, "_cat/indices?format=json"))
        table = [["name", "status", "count", "size"]]
        for index in data:
            table.append([
                index.get("index"),
                index.get("status"),
                index.get("docs.count"),
                index.get("store.size")
            ])
        return table

    def describe_collection(arlas: str, collection: str) -> list[list[str]]:
        description = Service.__arlas__(arlas, "/".join(["explore", collection, "_describe"]))
        table = [["field name", "type"]]
        table.extend(Service.__get_fields__([], description.get("properties", {})))
        return table

    def metadata_collection(arlas: str, collection: str) -> list[list[str]]:
        d = Service.__arlas__(arlas, "/".join(["explore", collection, "_describe"]))
        table = [["metadata", "value"]]
        table.append(["index name", d.get("params", {}).get("index_name", {})])
        table.append(["id path", d.get("params", {}).get("id_path", "")])
        table.append(["geometry path", d.get("params", {}).get("geometry_path", "")])
        table.append(["centroid path", d.get("params", {}).get("centroid_path", "")])
        table.append(["timestamp path", d.get("params", {}).get("timestamp_path", "")])
        table.append(["display name", d.get("params", {}).get("display_names", {}).get("collection", "")])
        table.append(["owner", d.get("params", {}).get("organisations", {}).get("owner", "")])
        table.append(["is public", str(d.get("params", {}).get("organisations", {}).get("shared", []))])
        table.append(["organisations", d.get("params", {}).get("organisations", {}).get("public", False)])
        return table
    
    def describe_index(arlas: str, index: str) -> list[list[str]]:
        description = json.loads(Service.__es__(arlas, "/".join([index, "_mapping"])))
        table = [["field name", "type"]]
        table.extend(Service.__get_fields__([], description.get(index, {}).get("mappings", {}).get("properties", {})))
        return table
    
    def sample_collection(arlas: str, collection: str, pretty: bool, size: int) -> dict:
        sample = Service.__arlas__(arlas, "/".join(["explore", collection, "_search"]) + "?size={}".format(size))
        return sample

    def sample_index(arlas: str, collection: str, pretty: bool, size: int) -> dict:
        sample = json.loads(Service.__es__(arlas, "/".join([collection, "_search"]) + "?size={}".format(size)))
        return sample
    
    def create_collection(arlas: str, collection: str, model_resource: str, index: str, display_name: str, owner: str, orgs: list[str], is_public: bool, id_path: str, centroid_path: str, geometry_path: str, date_path: str):
        if model_resource:
            model = json.loads(Service.__fetch__(model_resource))
        else:
            model = {}
        if index:
            model["index_name"] = index
        if owner:
            model["organisations"] = {
                "owner": owner,
                "shared": orgs,
                "public": is_public
            }
        if id_path:
            model["id_path"] = id_path
        if centroid_path:
            model["centroid_path"] = centroid_path
        if geometry_path:
            model["geometry_path"] = geometry_path
        if date_path:
            model["timestamp_path"] = date_path
        if display_name:
            display_names = model.get("display_names", {})
            display_names["collection"] = display_name
            model["display_names"] = display_names
        Service.__arlas__(arlas, "/".join(["collections", collection]), put=json.dumps(model))

    def create_index_from_resource(arlas: str, index: str, mapping_resource: str, number_of_shards: int):
        mapping = json.loads(Service.__fetch__(mapping_resource))
        if not mapping.get("mappings"):
            print("Error: mapping {} does not contain \"mappings\" at its root.".format(mapping_resource), file=sys.stderr)
            exit(1)
        Service.create_index(arlas, index, mapping, number_of_shards)

    def create_index(arlas: str, index: str, mapping: str, number_of_shards: int = 1):
        index_doc = {"mappings": mapping.get("mappings"), "settings": {"number_of_shards": number_of_shards}}
        Service.__es__(arlas, "/".join([index]), put=json.dumps(index_doc))

    def delete_collection(arlas: str, collection: str):
        Service.__arlas__(arlas, "/".join(["collections", collection]), delete=True)

    def delete_index(arlas: str, index: str):
        Service.__es__(arlas, "/".join([index]), delete=True)

    def count_collection(arlas: str, collection: str) -> list[list[str]]:
        collections = []
        if collection:
            collections.append(collection)
        else:
            for line in Service.list_collections(arlas)[1:]:
                collections.append(line[0])
        table = [["collection name", "count"]]
        for collection in collections:
            count = Service.__arlas__(arlas, "/".join(["explore", collection, "_count"]))
            table.append([collection, count.get("totalnb", "UNKNOWN")])
        return table

    def count_hits(file_path: str) -> int:
        line_number = 0
        with open(file_path) as f:
            for line in f:
                line_number = line_number + 1
        return line_number

    def persistence_add_file(arlas: str, file: Resource, zone: str, name: str, encode: bool = False, readers: list[str] = [], writers: list[str] = []):
        content = Service.__fetch__(file, bytes=True)
        url = "/".join(["persist", "resource", zone, name]) + "?" + "&readers=".join(readers) + "&writers=".join(writers)
        return Service.__arlas__(arlas, url, post=content, service=Services.persistence_server).get("id")

    def persistence_delete(arlas: str, id: str):
        url = "/".join(["persist", "resource", "id", id])
        return Service.__arlas__(arlas, url, delete=True, service=Services.persistence_server)

    def persistence_get(arlas: str, id: str):
        url = "/".join(["persist", "resource", "id", id])
        return Service.__arlas__(arlas, url, service=Services.persistence_server)
    
    def persistence_zone(arlas: str, zone: str):
        url = "/".join(["persist", "resources", zone]) + "?size=10000&page=1&order=desc&pretty=false"
        table = [["id", "name", "zone", "last_update_date", "owner"]]
        entries = Service.__arlas__(arlas, url, service=Services.persistence_server).get("data", [])
        for entry in entries:
            table.append([entry["id"], entry["doc_key"], entry["doc_zone"], entry["last_update_date"], entry["doc_owner"]])
        return table

    def persistence_groups(arlas: str, zone: str):
        url = "/".join(["persist", "groups", zone])
        table = [["group"]]
        groups = Service.__arlas__(arlas, url, service=Services.persistence_server)
        for group in groups:
            table.append([group])
        return table

    def persistence_describe(arlas: str, id: str):
        url = "/".join(["persist", "resource", "id", id])
        r = Service.__arlas__(arlas, url, service=Services.persistence_server)
        table = [["metadata", "value"]]
        table.append(["ID", r.get("id")])
        table.append(["name", r.get("doc_key")])
        table.append(["zone", r.get("doc_zone")])
        table.append(["last_update_date", r.get("last_update_date")])
        table.append(["owner", r.get("doc_owner")])
        table.append(["organization", r.get("doc_organization")])
        table.append(["ispublic", r.get("ispublic")])
        table.append(["updatable", r.get("updatable")])
        return table

    def __index_bulk__(arlas: str, index: str, bulk: []):
        data = os.linesep.join([json.dumps(line) for line in bulk]) + os.linesep
        result = json.loads(Service.__es__(arlas, "/".join([index, "_bulk"]), post=data, exit_on_failure=False, headers={"Content-Type": "application/x-ndjson"}))
        if result["errors"] is True:
            print("ERROR: " + json.dumps(result))

    def index_hits(arlas: str, index: str, file_path: str, bulk_size: int = 100, count: int = -1) -> dict[str, int]:
        line_number = 0
        line_in_bulk = 0
        bulk = []
        with open(file_path) as f:
            with alive_bar(count) as bar:
                for line in f:
                    line_number = line_number + 1
                    line_in_bulk = line_in_bulk + 1
                    bulk.append({
                        "index": {
                            "_index": index
                        }
                    })
                    bulk.append(json.loads(line))
                    if line_in_bulk == bulk_size:
                        try:
                            Service.__index_bulk__(arlas, index, bulk)
                        except RequestException as e:
                            print("Error on bulk insert between line {} and {} with code {}: {}".format(line_number, line_number - bulk_size, e.code, e.message))
                        bulk = []
                        line_in_bulk = 0
                    bar()
        if len(bulk) > 0:
            try:
                Service.__index_bulk__(arlas, index, bulk)
            except RequestException as e:
                print("Error on bulk insert between line {} and {} with code {}: {}".format(line_number, line_number - bulk_size, e.code, e.message))

    def __get_fields__(origin: list[str], properties: dict[str:dict]):
        fields = []
        for field, desc in properties.items():
            type = desc.get("type", "UNKNOWN")
            if type == "OBJECT" or type == "UNKNOWN":
                o = origin.copy()
                o.append(field)
                fields.extend(Service.__get_fields__(o, desc.get("properties", {})))
            else:
                o = origin.copy()
                o.append(field)
                fields.append([".".join(o), type])
        return fields
    
    def __arlas__(arlas: str, suffix, post=None, put=None, delete=None, service=Services.arlas_server):
        configuration: ARLAS = Configuration.settings.arlas.get(arlas, None)
        if configuration is None:
            print("Error: arlas configuration ({}) not found among [{}] for {}.".format(arlas, ", ".join(Configuration.settings.arlas.keys()), service.name), file=sys.stderr)
            exit(1)
        if service == Services.arlas_server:
            __headers__ = configuration.server.headers.copy()
            endpoint: Resource = configuration.server
        else:
            if service == Services.persistence_server:
                __headers__ = configuration.persistence.headers.copy()
                endpoint: Resource = configuration.persistence
            else:
                if service == Services.iam:
                    __headers__ = configuration.authorization.token_url.headers.copy()
                    endpoint: Resource = configuration.authorization.token_url.model_copy()
                    endpoint.location = endpoint.location.rsplit('/', 1)[0]

        if Configuration.settings.arlas.get(arlas).authorization is not None:
            __headers__["Authorization"] = "Bearer " + Service.__get_token__(arlas)
        url = "/".join([endpoint.location, suffix])
        try:
            if post:
                r = requests.post(url, data=post, headers=__headers__, verify=False)
            else:
                if put:
                    r = requests.put(url, data=put, headers=__headers__, verify=False)
                else:
                    if delete:
                        r = requests.delete(url, headers=__headers__, verify=False)
                    else:
                        r = requests.get(url, headers=__headers__, verify=False)
            if r.ok:
                return r.json()
            else:
                print("Error: request failed with status {}: {}".format(str(r.status_code), r.content), file=sys.stderr)
                print("   url: {}".format(url), file=sys.stderr)
                exit(1)
        except Exception as e:
            print("Error: request failed: {}".format(e), file=sys.stderr)
            print("   url: {}".format(url), file=sys.stderr)
            exit(1)

    def __es__(arlas: str, suffix, post=None, put=None, delete=None, exit_on_failure: bool = True, headers: dict[str, str] = {}):
        endpoint = Configuration.settings.arlas.get(arlas)
        if endpoint is None:
            print("Error: arlas configuration ({}) not found among [{}].".format(arlas, ", ".join(Configuration.settings.arlas.keys())), file=sys.stderr)
            exit(1)
        if endpoint.elastic is None:
            print("Error: arlas configuration ({}) misses an elasticsearch configuration.".format(arlas), file=sys.stderr)
            exit(1)
        url = "/".join([endpoint.elastic.location, suffix])
        __headers = endpoint.elastic.headers
        __headers.update(headers)
        auth = (endpoint.elastic.login, endpoint.elastic.password) if endpoint.elastic.login else None
        if post:
            r = requests.post(url, data=post, headers=__headers, auth=auth, verify=False)
        else:
            if put:
                r = requests.put(url, data=put, headers=__headers, auth=auth, verify=False)
            else:
                if delete:
                    r = requests.delete(url, headers=__headers, auth=auth, verify=False)
                else:
                    r = requests.get(url, headers=__headers, auth=auth, verify=False)
        if r.ok:
            return r.content
        else:
            if exit_on_failure:
                print("Error: request failed with status {}: {}".format(str(r.status_code), r.content), file=sys.stderr)
                print("   url: {}".format(url), file=sys.stderr)
                exit(1)
            else:
                raise RequestException(r.status_code, r.content)

    def __fetch__(resource: Resource, bytes: bool = False):
        if os.path.exists(resource.location):
            content = None
            mode = "r"
            if bytes:
                mode = "rb"
            with open(resource.location, mode) as f:
                content = f.read()
            return content
        r = requests.get(resource.location, headers=resource.headers, verify=False)
        if r.ok:
            return r.content
        else:
            print("Error: request failed with status {}: {}".format(str(r.status_code), r.content), file=sys.stderr)
            print("   url: {}".format(resource.location), file=sys.stderr)
            exit(1)

    def __get_token__(arlas: str) -> str:
        auth: AuthorizationService = Configuration.settings.arlas[arlas].authorization
        if auth.arlas_iam:
            data = {
                "email": auth.token_url.login,
                "password": auth.token_url.password
            }
        else:
            data = {
                "client_id": auth.client_id,
                "client_secret": auth.client_secret,
                "username": auth.token_url.login,
                "password": auth.token_url.password
            }
            if auth.grant_type:
                data["grant_type"] = auth.grant_type
        r = requests.post(
            headers=auth.token_url.headers,
            data=json.dumps(data),
            url=auth.token_url.location,
            verify=False)
        if r.status_code >= 200 and r.status_code < 300:
            if r.json().get("accessToken"):
                return r.json()["accessToken"]
            else:
                if r.json().get("access_token"):
                    return r.json()["access_token"]
                else:
                    print("Error: Failed to find access token in response {}".format(r.content), file=sys.stderr)
                    print("   url: {}".format(auth.token_url.location), file=sys.stderr)
                    exit(1)
        else:
            print("Error: request to get token failed with status {}: {}".format(str(r.status_code), r.content), file=sys.stderr)
            print("   url: {}".format(auth.token_url.location), file=sys.stderr)
            exit(1)
