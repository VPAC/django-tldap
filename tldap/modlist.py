"""
ldap.modlist - create add/modify modlist's

See http://www.python-ldap.org/ for details.

$Id: modlist.py,v 1.17 2009/07/26 11:09:58 stroeder Exp $

Python compability note:
This module is known to work with Python 2.0+ but should work
with Python 1.5.2 as well.
"""

from ldap import __version__

import string,ldap

from ldap.modlist import *

def modifyModlist(
  old_entry,new_entry,ignore_attr_types=None,ignore_oldexistent=0
):
  """
  Build differential modify list for calling LDAPObject.modify()/modify_s()

  old_entry
      Dictionary holding the old entry
  new_entry
      Dictionary holding what the new entry should be
  ignore_attr_types
      List of attribute type names to be ignored completely
  ignore_oldexistent
      If non-zero attribute type names which are in old_entry
      but are not found in new_entry at all are not deleted.
      This is handy for situations where your application
      sets attribute value to '' for deleting an attribute.
      In most cases leave zero.
  """
  ignore_attr_types = list_dict(map(string.lower,(ignore_attr_types or [])))
  modlist = []
  attrtype_lower_map = {}
  for a in old_entry.keys():
    attrtype_lower_map[string.lower(a)]=a
  for attrtype in new_entry.keys():
    attrtype_lower = string.lower(attrtype)
    if ignore_attr_types.has_key(attrtype_lower):
      # This attribute type is ignored
      continue
    # Filter away null-strings
    new_value = filter(lambda x:x!=None,new_entry[attrtype])
    if attrtype_lower_map.has_key(attrtype_lower):
      old_value = old_entry.get(attrtype_lower_map[attrtype_lower],[])
      old_value = filter(lambda x:x!=None,old_value)
      del attrtype_lower_map[attrtype_lower]
    else:
      old_value = []
    if not old_value and new_value:
      # Add a new attribute to entry
      modlist.append((ldap.MOD_ADD,attrtype,new_value))
    elif old_value and new_value:
      # Replace existing attribute
      if True:
        old_value_dict=list_dict(old_value)
        new_value_dict=list_dict(new_value)
        delete_values = []
        for v in old_value:
          if not new_value_dict.has_key(v):
            delete_values.append(v)
        add_values = []
        for v in new_value:
          if not old_value_dict.has_key(v):
            add_values.append(v)
      if len(delete_values) > 0:
        modlist.append((ldap.MOD_DELETE,attrtype,delete_values))
      if len(add_values) > 0:
        modlist.append((ldap.MOD_ADD,attrtype,add_values))
    elif old_value and not new_value:
      # Completely delete an existing attribute
      modlist.append((ldap.MOD_DELETE,attrtype,None))
  if not ignore_oldexistent:
    # Remove all attributes of old_entry which are not present
    # in new_entry at all
    for a in attrtype_lower_map.keys():
      if ignore_attr_types.has_key(a):
        # This attribute type is ignored
        continue
      attrtype = attrtype_lower_map[a]
      modlist.append((ldap.MOD_DELETE,attrtype,None))
  return modlist # modifyModlist()
