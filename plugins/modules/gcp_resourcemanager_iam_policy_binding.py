#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Google
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# ----------------------------------------------------------------------------
#
#     ***     AUTO GENERATED CODE    ***    Type: MMv1     ***
#
# ----------------------------------------------------------------------------
#
#     This file is automatically generated by Magic Modules and manual
#     changes will be clobbered when the file is regenerated.
#
#     Please read more about how to change this file at
#     https://www.github.com/GoogleCloudPlatform/magic-modules
#
# ----------------------------------------------------------------------------

from __future__ import absolute_import, division, print_function
import json
from ansible_collections.google.cloud.plugins.module_utils.gcp_utils import (
    navigate_hash,
    GcpSession,
    GcpModule,
    GcpRequest,
    replace_resource_dict,
)

__metaclass__ = type

################################################################################
# Documentation
################################################################################

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: gcp_resourcemanager_iam_policy_binding
description:
- Configure policy bindings of a project.
short_description: Add or remove policy bindings
author: Alexander Brook Perry (@alexgeek)
requirements:
- python >= 2.6
- requests >= 2.18.4
- google-auth >= 1.3.0
options:
  state:
    description:
    - Whether the given object should exist in GCP
    choices:
    - present
    - absent
    default: present
    type: str
  member:
    description:
    - The principal to add the binding for. 
      Should be of the form user|group|serviceAccount:email or domain:domain.
    required: true
    type: str
  role:
    description:
    - Role name to assign to the principal.
      The role name is the complete path of a predefined role, such as roles/logging.viewer, 
      or the role ID for a custom role, such as organizations/{ORGANIZATION_ID}/roles/logging.viewer.
    required: false
    type: str
  project:
    description:
    - The Google Cloud Platform project to use.
    type: str
  auth_kind:
    description:
    - The type of credential used.
    type: str
    required: true
    choices:
    - application
    - machineaccount
    - serviceaccount
  service_account_contents:
    description:
    - The contents of a Service Account JSON file, either in a dictionary or as a
      JSON string that represents it.
    type: jsonarg
  service_account_file:
    description:
    - The path of a Service Account JSON file if serviceaccount is selected as type.
    type: path
  service_account_email:
    description:
    - An optional service account email address if machineaccount is selected and
      the user does not wish to use the default email.
    type: str
  scopes:
    description:
    - Array of scopes to be used
    type: list
    elements: str
  env_type:
    description:
    - Specifies which Ansible environment you're running this module within.
    - This should not be set unless you know what you're doing.
    - This only alters the User Agent string for any API requests.
    type: str
"""

EXAMPLES = """
- name: Bind a member to a role
  google.cloud.gcp_resource_manager_iam_policy_binding:
    member: some-service-account@some-project.gserviceaccount.com
    role: roles/dns.admin
    project: test_project
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
    state: present
"""

RETURN = """
bindings:
  description:
  - List of bindings each having a list of members and a single role
  returned: success
  type: list
etag:
  description:
  - Used to handle simultanaeous updates safely.
  returned: success
  type: str
version:
  description:
  - The format of the policy either 0, 1, or 3
  returned: success
  type: str
"""

################################################################################
# Imports
################################################################################


################################################################################
# Main
################################################################################


def main():
    """Main function"""

    module = GcpModule(
        argument_spec=dict(
            state=dict(default="present", choices=[
                       "present", "absent"], type="str"),
            member=dict(required=True, type="str"),
            role=dict(required=True, type="str"),
        )
    )

    if not module.params["scopes"]:
        module.params["scopes"] = [
            "https://www.googleapis.com/auth/cloud-platform"]

    state = module.params["state"]

    fetch = fetch_resource(module, self_link(module) + ':getIamPolicy')
    changed = False

    if fetch:
        if state == "present":
            fetch["bindings"], changed = add_binding(
                fetch["bindings"], module.params["role"], module.params["member"])
        else:
            fetch["bindings"], changed = remove_binding(
                fetch["bindings"], module.params["role"], module.params["member"])

    if changed:
      fetch = update(module, self_link(module) + ":setIamPolicy", fetch)

    fetch.update({"changed": changed})

    module.exit_json(**fetch)


def add_binding(bindings, role, member):
    for binding in bindings:
        if binding['role'] == role:
            # role exists but member not in it, add member
            if member not in binding['members']:
                binding['members'].append(member)
                return bindings, True
            return bindings, False
    # no binding with role, add the binding
    bindings.append({'role': role, 'members': [member]})
    return bindings, True


def remove_binding(bindings, role, member):
    for i, binding in enumerate(bindings):
        if binding['role'] == role:
            # the role exists and only has the given member, delete the whole binding
            if len(binding['members']) == 1 and binding['members'][0] == member:
                del bindings[i]
            # role exists but has other members, remove member from binding
            elif member in binding['members']:
                binding['members'].remove(member)
            return bindings, True
    # already no role with this member
    return bindings, False


def update(module, link, fetch):
    auth = GcpSession(module, "resourcemanager")
    request = {
        "policy": fetch
    }
    return return_if_object(module, auth.post(link, request))


def fetch_resource(module, link, allow_not_found=True):
    auth = GcpSession(module, "resourcemanager")
    return return_if_object(module, auth.post(link))


def self_link(module):

    return "https://cloudresourcemanager.googleapis.com/v1/projects/{project}".format(
        **module.params
    )


def return_if_object(module, response):
    if response.status_code == 404:
        module.fail_json(msg="Project not found.")

    if response.status_code == 403:
        module.fail_json(msg="Not authorized for project.")

    try:
        module.raise_for_status(response)
        result = response.json()
    except getattr(json.decoder, "JSONDecodeError", ValueError):
        module.fail_json(
            msg="Invalid JSON response with error: %s" % response.text)

    if navigate_hash(result, ["error", "errors"]):
        module.fail_json(msg=navigate_hash(result, ["error", "errors"]))

    return result


if __name__ == "__main__":
    main()